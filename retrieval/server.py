# Just so local inclusion will work. Find a nicer way later...
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
import weaviate
from weaviate.classes.query import MetadataQuery
from sentence_transformers import SentenceTransformer, CrossEncoder

import httpx
import os
import logging
import torch
import uuid
from functools import lru_cache
from utils.naming import to_qdrant_name, to_weaviate_class
from contextlib import asynccontextmanager
from http.client import HTTPException
import utils.config as config

# ------------------- CONFIG -------------------
AVAILABLE_INFERENCE_MODELS = [
    {"id": "gpt-oss-20b", "name": "GPT-OSS 20B"}
]

AVAILABLE_EMBEDDERS = config.EMBEDDING_MODELS

AVAILABLE_VECTOR_DBS = [
    {"id": "qdrant", "name": "Qdrant (6333)"},
    {"id": "weaviate", "name": "Weaviate (6444)"}
]

RERANKER_MODEL_ID = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ------------------- LOGGING -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retrieval")

# ------------------- CLIENTS -------------------
# Qdrant Client
qdrant = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
logger.info(f"Qdrant client initialized on {config.QDRANT_HOST}:{config.QDRANT_PORT}")

weaviate_client = weaviate.connect_to_custom(
    http_host=config.WEAVIATE_HOST,
    http_port=config.WEAVIATE_PORT,
    http_secure=False,  # Set to True if using HTTPS
    grpc_host=config.WEAVIATE_HOST,
    grpc_port=config.WEAVIATE_PORT_GRPC,
    grpc_secure=False,  # Set to True if using HTTPS/gRPC
)
logger.info(f"Weaviate client initialized on {config.WEAVIATE_HOST}:{config.WEAVIATE_PORT}")

# ------------------- APP -------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (optional)
    yield
    # Shutdown logic
    if weaviate_client:
        weaviate_client.close()
        logger.info("Weaviate client connection closed gracefully.")

app = FastAPI(lifespan=lifespan)

# --- STATIC FILE SERVING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FILES_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "ingestion", "knowledge"))
REMOTE_BASE_URL = "https://os.cs.oslomet.no"

# Ensure the static directory exists
os.makedirs(STATIC_FILES_DIR, exist_ok=True)

@app.get(config.STATIC_FILES_URI_PATH + "{file_path:path}")
async def serve_docs(file_path: str):
    local_path = os.path.join(STATIC_FILES_DIR, file_path)
    
    # Serve local file if it exists
    if os.path.exists(local_path) and os.path.isfile(local_path):
        return FileResponse(local_path)
    
    # File not found locally, fetch from remote
    remote_url = f"{REMOTE_BASE_URL}/{file_path}"
    async with httpx.AsyncClient() as client:
        r = await client.get(remote_url)
        if r.status_code == 200:
            # Ensure parent directories exist before saving
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            # Save file locally for future requests
            with open(local_path, "wb") as f:
                f.write(r.content)
            return Response(content=r.content, media_type=r.headers.get("content-type"))
        else:
            return Response(status_code=404, content="File not found")

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Reranker Model globally
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
    Handles both Qdrant PointStruct objects and Weaviate-adapted objects (with .payload).
    """
    pairs = []
    for h in hits:
        # Assuming h has a .payload attribute
        payload = h.payload
        text = payload.get("text") or payload.get("content") or ""
        pairs.append((query, text))
    
    scores = reranker.predict(pairs)
    reranked_combined = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)
    reranked_hits = [h for h, _ in reranked_combined[:top_k]]
    
    if reranked_combined:
        logger.info(f"Reranking done. Top score: {reranked_combined[0][1]:.4f}")
        
    return reranked_hits

# ------------------- ENDPOINT -------------------

# Map request fields to their available options
AVAILABLE_OPTIONS = {
    "inference_model": AVAILABLE_INFERENCE_MODELS,
    "embedding_model": AVAILABLE_EMBEDDERS,
    "vector_db": AVAILABLE_VECTOR_DBS,
}

@app.get("/config")
async def get_config():
    """Returns the available models and vector databases."""
    return AVAILABLE_OPTIONS

@app.post("/chat")
async def chat(req: ChatRequest):
    """Handles the RAG chat logic: embedding, retrieval, deduplication, reranking, and LLM call."""
    logger.info(f"Incoming message: {req.message}")
    
    # Validate params
    errors = []
    for field_name, available_options in AVAILABLE_OPTIONS.items():
        value = getattr(req, field_name)
        if value is None:
            continue  # Optional: skip if no value provided
        if not any(opt["id"] == value for opt in available_options):
            errors.append(f"Invalid {field_name}: {value}. Available: {[opt['id'] for opt in available_options]}")

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    # Now you can safely use the validated values
    inference_model = req.inference_model
    embedding_model = req.embedding_model
    vector_db = req.vector_db
    embedding_model_name = next((opt['name'] for opt in AVAILABLE_EMBEDDERS if opt['id'] == embedding_model))
    
    logger.info(f"Using DB: {vector_db}, embedding model: {embedding_model_name}, inference model: {inference_model}")

    embedder = load_embedder(embedding_model)
    qvec = embedder.encode(req.message, normalize_embeddings=True).tolist()
    
    hits = []
    
    # 1. Retrieve a larger set of candidates for reranking (e.g., top 20)
    if vector_db == "qdrant":
        collection_name = to_qdrant_name(embedding_model_name)
        hits = qdrant.search(collection_name=collection_name, query_vector=qvec, limit=20) 
        
    elif vector_db == "weaviate":
        if not weaviate_client: # Use the correctly named client variable
            return {"answer": "Weaviate client is not initialized or failed connection. Cannot perform retrieval.", "sources": []}
            
        try:
            # Get the collection object
            collection_name = to_weaviate_class(embedding_model_name)
            collection = weaviate_client.collections.get(collection_name)
            
            # Perform a vector-based query (NearVector)
            response = collection.query.near_vector(
                near_vector=qvec,
                limit=20,
                return_properties=["text", "source", "filename"],
                return_metadata=MetadataQuery(distance=True, score=True)
            )
            
            for obj in response.objects:
                payload = {
                    "text": obj.properties.get("text"),
                    "content": obj.properties.get("text"), # Map 'text' to 'content' for compatibility
                    "source": obj.properties.get("source"),
                    "filename": obj.properties.get("filename")
                }
                # Create a simple object wrapper to maintain compatibility with the rerank_hits function
                # This works because the rerank_hits function only expects a .payload attribute
                hits.append(type('WeaviateHit', (object,), {'payload': payload}))

        except Exception as e:
            logger.error(f"Weaviate search failed: {e}")
            return {"answer": f"Error during Weaviate retrieval: {e}", "sources": []}
            
    # 2. Context De-duplication
    unique_contexts = {}
    for h in hits:
        payload = h.payload
        txt = (payload.get("text") or payload.get("content") or "").strip()
        if txt and txt not in unique_contexts:
            unique_contexts[txt] = h
    
    unique_candidates = list(unique_contexts.values())

    logger.info(f"Retrieved {len(hits)} total documents. {len(unique_candidates)} are unique candidates.")

    # 3. Reranking (Keep the top 5 documents after reranking)
    final_hits = rerank_hits(req.message, unique_candidates, top_k=5)
    
    logger.info(f"Reranked and selected {len(final_hits)} final documents.")

    # Build sources
    # Build sources for frontend replacement
    sources = []
    for h in final_hits:
        payload = h.payload or {}
        chunk_id = payload.get("id") or str(uuid.uuid4())
        source_file = payload.get("source") or "N/A"
        anchor = payload.get("anchor")

        if anchor:
            url = f"http://localhost:8080{config.STATIC_FILES_URI_PATH}{source_file}{anchor}"
        else:
            url = f"http://localhost:8080{config.STATIC_FILES_URI_PATH}{source_file}"
        
        # Store mapping: id -> URL (text is optional)
        sources.append({
            "id": chunk_id,
            "url": url,
            "text": payload.get("text", "")
        })

    # Build prompt: instruct LLM to reference sources by their IDs
    source_ids = ", ".join([s["id"] for s in sources])
    user_prompt = (
        f"KONTEKST:\n{source_ids}\n\n"
        f"BRUKERENS SPØRSMÅL:\n{req.message}\n\n"
    )

    logger.info(sources)

    # 4. Build prompt
    user_prompt = f"KONTEKST:\n{sources}\n\nBRUKERENS SPØRSMÅL:\n{req.message}"

    logger.info(f"Prompt sent to LLM:\n{user_prompt}")

    # 5. Call LLM
    payload = {
        "model": inference_model,
        "messages": [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": config.MAX_TOKENS,
        "temperature": config.TEMPERATURE,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{config.LLM_BASE}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

    assistant_text = data["choices"][0]["message"]["content"]
    logger.info(f"LLM Response:\n{assistant_text}")

    # Return sources from the final, reranked list
    return {
        "answer": assistant_text,
        "sources": sources  # now each item is a dict with 'text' and 'url'
    }