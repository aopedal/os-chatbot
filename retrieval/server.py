# server.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from functools import lru_cache
import httpx
import os
import logging
import torch

# ------------------- CONFIG -------------------
AVAILABLE_INFERENCE_MODELS = [
    {"id": "models/gpt-oss-20b", "name": "GPT-OSS 20B"},
    {"id": "models/mistral-7b", "name": "Mistral 7B"},
]

AVAILABLE_EMBEDDERS = [
    {"id": "Alibaba-NLP/gte-multilingual-base", "name": "GTE Multilingual Base"},
    {"id": "sentence-transformers/all-MiniLM-L6-v2", "name": "MiniLM-L6-v2"},
]

AVAILABLE_VECTOR_DBS = [
    {"id": "qdrant", "name": "Qdrant (local)"},
    {"id": "pinecone", "name": "Pinecone (cloud)"}
]

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "os-pensum"

LLM_BASE = os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:8000/v1")

# RERANKER MODEL CONFIG
RERANKER_MODEL_ID = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ------------------- LOGGING -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retrieval")

# --- STATIC FILE CONFIG ---
# The parent directory of the current script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# The 'knowledge' folder is one level up from the script's directory
STATIC_FILES_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "ingestion", "knowledge"))
logger.info(f"Serving static files from: {STATIC_FILES_DIR}")

# ------------------- APP -------------------
app = FastAPI()

# --- ADD STATIC FILE SERVING ---
# Mount the 'knowledge' directory to the /docs path on the backend server.
# Files can be accessed at http://localhost:8080/docs/os_node14.html
app.mount("/docs", StaticFiles(directory=STATIC_FILES_DIR), name="static_docs")

# -------------------------------

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- CLIENTS -------------------
# Qdrant Client
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Initialize the Reranker Model globally (as it's often the most stable one)
logger.info(f"Loading reranker model: {RERANKER_MODEL_ID}")
reranker = CrossEncoder(
    RERANKER_MODEL_ID,
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# ------------------- SCHEMA -------------------
class ChatRequest(BaseModel):
    user_id: str | None = None
    message: str
    inference_model: str | None = None
    embedding_model: str | None = None
    vector_db: str | None = None

# ------------------- UTIL -------------------
@lru_cache(maxsize=None)
def load_embedder(model_id: str):
    """Loads and caches the SentenceTransformer embedding model."""
    logger.info(f"Loading embedder model: {model_id}")
    return SentenceTransformer(model_id, device="cuda" if torch.cuda.is_available() else "cpu", trust_remote_code=True)

def rerank_hits(query: str, hits: list, top_k: int = 5):
    """
    Reranks the retrieved hits based on the query using the Cross-Encoder.
    Returns the top_k most relevant hits.
    """
    # 1. Prepare pairs of (query, document_text)
    pairs = [(query, h.payload.get("text", "")) for h in hits]
    
    # 2. Predict scores using the CrossEncoder
    scores = reranker.predict(pairs)
    
    # 3. Combine hits and scores, then sort by score (highest first)
    reranked_combined = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)
    
    # 4. Return the top_k hits
    reranked_hits = [h for h, _ in reranked_combined[:top_k]]
    
    # Log the top score for visibility
    if reranked_combined:
        logger.info(f"Reranking done. Top score: {reranked_combined[0][1]:.4f}")
        
    return reranked_hits

# ------------------- ENDPOINT -------------------
@app.get("/config")
async def get_config():
    """Returns the available models and vector databases."""
    return {
        "inference_models": AVAILABLE_INFERENCE_MODELS,
        "embedding_models": AVAILABLE_EMBEDDERS,
        "vector_dbs": AVAILABLE_VECTOR_DBS,
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    """Handles the RAG chat logic: embedding, retrieval, deduplication, reranking, and LLM call."""
    logger.info(f"Incoming message: {req.message}")

    # Select and load embedder (cached)
    model_id = req.embedding_model or "Alibaba-NLP/gte-multilingual-base"
    embedder = load_embedder(model_id)

    # Vector DB selection
    if req.vector_db == "pinecone":
        raise NotImplementedError("Pinecone not yet integrated")
    else:
        db = qdrant

    # Embed query
    qvec = embedder.encode(req.message, normalize_embeddings=True).tolist()

    # 1. Retrieve a larger set of candidates for reranking (e.g., top 20)
    hits = db.search(collection_name=COLLECTION_NAME, query_vector=qvec, limit=20) 
    
    # 2. Context De-duplication (to ensure unique candidates before costly reranking)
    unique_contexts = {}
    for h in hits:
        # Use the relevant text (trimmed/cleaned) as the key for de-duplication
        txt = (h.payload.get("text") or h.payload.get("content") or "").strip()
        if txt not in unique_contexts:
            unique_contexts[txt] = h
    
    # Final list of unique candidates
    unique_candidates = list(unique_contexts.values())

    logger.info(f"Retrieved {len(hits)} total documents. {len(unique_candidates)} are unique candidates.")

    # 3. Reranking (Keep the top 5 documents after reranking)
    final_hits = rerank_hits(req.message, unique_candidates, top_k=5)
    
    logger.info(f"Reranked and selected {len(final_hits)} final documents.")

    # Build contexts list for the prompt
    contexts = []
    for i, h in enumerate(final_hits, 1):
        payload = h.payload or {}
        txt = payload.get("text") or payload.get("content") or ""
        source = payload.get("source", "")
        logger.info(f"Final Hit {i}: source={source}, text={txt[:200]}...")
        contexts.append(f"Source: {source}\n{txt}")

    sources = "\n\n---\n\n".join(contexts)

    # 4. Build prompt
    system_prompt = (
        "Du er HårekBot, en hjelpsom assistent som gir nøyaktige svar om operativsystemer og Linux, basert på konteksten du får. "
        "Du skal, så langt det er mulig, bruke konteksten til å svare på brukerens spørsmål. "
        "Oppgi kildene du bruker i svaret ditt ved å referere til dem. "
    )
    user_prompt = f"CONTEXTS:\n{sources}\n\nUSER QUESTION:\n{req.message}"

    # Log final prompt
    logger.info(f"Prompt sent to LLM:\n{user_prompt}")

    # 5. Call LLM
    inference_model = req.inference_model or "models/gpt-oss-20b"
    payload = {
        "model": inference_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 2048,
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{LLM_BASE}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()


    # Return response
    assistant_text = data["choices"][0]["message"]["content"]
    logger.info(f"LLM Response:\n{assistant_text}")

    # Return sources from the final, reranked list
    return {"answer": assistant_text, "sources": [h.payload.get("source") for h in final_hits]}