# Just so local inclusion will work. Find a nicer way later...
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from qdrant_client import QdrantClient
import weaviate
from weaviate.classes.query import MetadataQuery
from sentence_transformers import SentenceTransformer, CrossEncoder

import httpx
import logging
import torch
import uuid
from functools import lru_cache
from utils.naming import to_qdrant_name, to_weaviate_class
from contextlib import asynccontextmanager
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
app.mount(config.STATIC_FILES_URI_PATH, StaticFiles(directory=STATIC_FILES_DIR))

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
                return_properties=["identifier", "text", "source", "anchor"],
                return_metadata=MetadataQuery(distance=True, score=True)
            )
            
            for obj in response.objects:
                payload = {
                    "identifier": obj.properties.get("identifier"),
                    "text": obj.properties.get("text"),
                    "source": obj.properties.get("source"),
                    "anchor": obj.properties.get("anchor")
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
        payload = getattr(h, "payload", {}) or {}
        text_value = payload.get("text") or ""
        txt = text_value.strip()
        if txt and txt not in unique_contexts:
            logger.info(h)
            unique_contexts[txt] = h
    
    final_hits = list(unique_contexts.values())

    logger.info(f"Retrieved {len(hits)} total documents. {len(final_hits)} are unique candidates.")

    # Build sources
    # Build sources for frontend replacement
    sources = []
    for h in final_hits:
        payload = h.payload or {}
        chunk_id = payload.get("identifier") or str(uuid.uuid4())
        source_file = payload.get("source") or "N/A"
        anchor = payload.get("anchor")

        if anchor:
            url = f"http://localhost:8080{config.STATIC_FILES_URI_PATH}{source_file}#{anchor}"
        else:
            url = f"http://localhost:8080{config.STATIC_FILES_URI_PATH}{source_file}"
        
        # Store mapping: id -> URL (text is optional)
        sources.append({
            "identifier": chunk_id,
            "url": url,
            "text": payload.get("text", "")
        })

    context = "\n\n---\n\n".join(
        (
            f"Kildereferanse: {s['identifier']}\n"
            f"URL: {s['url']}\n"
            f"Tekst: {s['text']}"
        )
        for s in sources
    )

    logger.info(context)

    user_prompt = req.message
    system_prompt = (
        f"{config.SYSTEM_PROMPT}\n\n"
        f"---\n\n"
        f"RELEVANT PENSUMMATERIALE:\n\n"
        f"{context}"
    )

    logger.info(f"Prompt sent to LLM:\n{user_prompt}")

    # 5. Call LLM
    payload = {
        "model": inference_model,
        "messages": [
            {"role": "system", "content": system_prompt},
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