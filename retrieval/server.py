# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer, CrossEncoder
import httpx
import os
import logging
import torch

# ------------------- CONFIG -------------------
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "os-pensum"

LLM_BASE = os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:8000/v1")  # Local LLM
API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Toggle cross-encoder reranker
USE_RERANKER = True

# ------------------- LOGGING -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retrieval")

# ------------------- APP -------------------
app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- CLIENTS -------------------
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

embedder = SentenceTransformer(
    "Alibaba-NLP/gte-multilingual-base",
    device="cuda" if torch.cuda.is_available() else "cpu",
    trust_remote_code=True
)

if USE_RERANKER:
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# ------------------- SCHEMA -------------------
class ChatRequest(BaseModel):
    user_id: str | None = None
    message: str

# ------------------- UTIL -------------------
def rerank_hits(query: str, hits: list):
    pairs = [(query, h.payload.get("text", "")) for h in hits]
    scores = reranker.predict(pairs)
    reranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)
    return [h for h, _ in reranked]

# ------------------- ENDPOINT -------------------
@app.post("/chat")
async def chat(req: ChatRequest):
    # Log incoming user message
    logger.info(f"Incoming user message: {req.message}")

    # 1) Embed query
    qvec = embedder.encode(req.message, normalize_embeddings=True).tolist()

    # 2) Retrieve from Qdrant
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=qvec,
        limit=10,  # retrieve more to allow LLM/reranker to select best
    )

    # Log retrieved hits
    logger.info(f"Retrieved {len(hits)} documents from Qdrant:")
    contexts = []
    for i, h in enumerate(hits, 1):
        payload = h.payload or {}
        txt = payload.get("text") or payload.get("content") or ""
        source = payload.get("source", "")
        logger.info(f"Hit {i}: source={source}, text={txt[:200]}...")
        contexts.append(f"Source: {source}\n{txt}")

    # 3) Optional reranking
    if USE_RERANKER and hits:
        hits = rerank_hits(req.message, hits)
        logger.info("After reranking, top hits:")
        for i, h in enumerate(hits[:5], 1):
            txt = h.payload.get("text", "")
            source = h.payload.get("source", "")
            logger.info(f"Rank {i}: source={source}, text={txt[:200]}...")

    # Rebuild context after reranking (top 5)
    retrieved_contexts = "\n\n---\n\n".join(
        [f"Source: {h.payload.get('source', '')}\n{h.payload.get('text', '')}" for h in hits[:5]]
    )

    # 4) Build prompt
    system_prompt = (
        "You are an assistant that answers in Norwegian when the user uses Norwegian. "
        "Use only the provided sources and cite 'Source:' lines when appropriate."
    )
    user_prompt = f"CONTEXTS:\n{retrieved_contexts}\n\nUSER QUESTION:\n{req.message}"

    # Log final prompt
    logger.info(f"Prompt sent to LLM:\n{user_prompt[:1000]}...")

    # 5) Forward to local LLM
    payload = {
        "model": "/app/models/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 512,
        "temperature": 0.0,
    }
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{LLM_BASE}/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    assistant_text = data["choices"][0]["message"]["content"]
    return {"answer": assistant_text, "sources": [h.payload.get("source") for h in hits[:5]]}
