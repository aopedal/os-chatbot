# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import httpx
import os
import logging

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "os-pensum"
LLM_BASE = os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:8000/v1")  # your local LLM base
API_KEY = os.environ.get("OPENAI_API_KEY", "")  # add if your server expects a key

app = FastAPI()

# Allow your frontend origin (Vite default: http://localhost:5173)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] for development
    allow_credentials=True,
    allow_methods=["*"],          # <- allows POST, OPTIONS, etc.
    allow_headers=["*"],
)

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
embedder = SentenceTransformer("NbAiLab/nb-sbert-base", device="cpu")

class ChatRequest(BaseModel):
    user_id: str | None = None
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    # 1) embed query
    qvec = embedder.encode(req.message).tolist()

    # 2) search Qdrant
    hits = qdrant.search(collection_name=COLLECTION_NAME, query_vector=qvec, limit=5)
    
    # Log what is retrieved
    print("Retrieved documents from Qdrant:")
    contexts = []
    for i, h in enumerate(hits, 1):
        payload = h.payload or {}
        txt = payload.get("text") or payload.get("content") or ""
        source = payload.get("source", "")
        print(f"Hit {i}: source={source}, text={txt[:200]}...")  # show first 200 chars
        contexts.append(f"Source: {source}\n{txt}")

    # 3) build prompt
    system = "You are an assistant that answers in Norwegian when the user uses Norwegian. Use only the provided sources and cite 'Source:' lines when appropriate."
    retrieved = "\n\n---\n\n".join(contexts)
    prompt = f"{system}\n\nCONTEXTS:\n{retrieved}\n\nUSER: {req.message}\n\nAnswer concisely, and mention which sources you used."

    # Log the final prompt
    print(f"Prompt sent to LLM:\n{prompt[:1000]}...")  # truncate for readability

    # 4) forward to local LLM (OpenAI-like ChatCompletion)
    payload = {
        "model": "/app/models/gpt-oss-20b",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.0
    }
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{LLM_BASE}/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    assistant_text = data["choices"][0]["message"]["content"]
    return {"answer": assistant_text, "sources": [h.payload.get("source") for h in hits]}
