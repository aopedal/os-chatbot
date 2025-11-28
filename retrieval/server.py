from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from qdrant_client import QdrantClient
import weaviate
from weaviate.classes.query import MetadataQuery
from sentence_transformers import SentenceTransformer
import torch

import os
import httpx
import logging
import uuid
import locale
import json
from datetime import datetime
from functools import lru_cache
from contextlib import asynccontextmanager
from importlib.metadata import version

from utils.naming import to_qdrant_name, to_weaviate_class
import utils.config as config

# ------------------- CONFIG -------------------
locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')

AVAILABLE_INFERENCE_MODELS = [
    {"id": "gpt-oss-20b", "name": "GPT-OSS 20B"}
]

AVAILABLE_EMBEDDERS = config.EMBEDDING_MODELS

AVAILABLE_VECTOR_DBS = [
    {"id": "qdrant", "name": "Qdrant (6333)"},
    {"id": "weaviate", "name": "Weaviate (6444)"}
]

# ------------------- LOGGING -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retrieval")

# ------------------- CLIENTS -------------------
qdrant = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
logger.info(f"Qdrant client (version {version('qdrant-client')}) initialized on {config.QDRANT_HOST}:{config.QDRANT_PORT}")

weaviate_client = weaviate.connect_to_custom(
    http_host=config.WEAVIATE_HOST,
    http_port=config.WEAVIATE_PORT,
    http_secure=False,
    grpc_host=config.WEAVIATE_HOST,
    grpc_port=config.WEAVIATE_PORT_GRPC,
    grpc_secure=False,
)
logger.info(f"Weaviate client (version {version('weaviate-client')}) initialized on {config.WEAVIATE_HOST}:{config.WEAVIATE_PORT}")

# ------------------- APP -------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if weaviate_client:
        weaviate_client.close()
        logger.info("Weaviate client connection closed gracefully.")

app = FastAPI(lifespan=lifespan)

# Static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FILES_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "ingestion", "knowledge"))
app.mount(config.STATIC_FILES_URI_PATH, StaticFiles(directory=STATIC_FILES_DIR))

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
    logger.info(f"Loading embedder model: {model_id}")
    return SentenceTransformer(
        model_id,
        device="cuda" if torch.cuda.is_available() else "cpu",
        trust_remote_code=True
    )

AVAILABLE_OPTIONS = {
    "inference_model": AVAILABLE_INFERENCE_MODELS,
    "embedding_model": AVAILABLE_EMBEDDERS,
    "vector_db": AVAILABLE_VECTOR_DBS,
}

@app.get("/config")
async def get_config():
    return AVAILABLE_OPTIONS

# ------------------- STREAMING CHAT -------------------
@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    logger.info(f"Incoming message: {req.message}")

    # Validate options
    for field_name, available_options in AVAILABLE_OPTIONS.items():
        value = getattr(req, field_name)
        if value and not any(opt["id"] == value for opt in available_options):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field_name}: {value}. Available: {[opt['id'] for opt in available_options]}"
            )

    embedding_model_name = next((opt['name'] for opt in AVAILABLE_EMBEDDERS if opt['id'] == req.embedding_model))

    logger.info(f"Using DB: {req.vector_db}, embedding model: {embedding_model_name}, inference model: {req.inference_model}")
    embedder = load_embedder(req.embedding_model)
    qvec = embedder.encode(req.message, normalize_embeddings=True).tolist()

    # Vector DB retrieval
    payloads: list[Any] = []
    if req.vector_db == "qdrant":
        collection_name = to_qdrant_name(embedding_model_name)
        response = qdrant.query_points(collection_name=collection_name, query=qvec, limit=20)
        payloads = [point.payload for point in response.points]

    elif req.vector_db == "weaviate":
        collection_name = to_weaviate_class(embedding_model_name)
        collection = weaviate_client.collections.get(collection_name)
        response = collection.query.near_vector(
            near_vector=qvec,
            limit=20,
            return_properties=["identifier", "text", "source", "anchor"],
            return_metadata=MetadataQuery(distance=True, score=True)
        )
        payloads = [obj.properties for obj in response.objects]
    else:
        raise ValueError

    # Build sources and context
    sources = []
    context_texts = []
    for payload in payloads:
        identifier = payload.get("identifier") or str(uuid.uuid4())
        source_file = payload.get("source") or "N/A"
        anchor = payload.get("anchor") or ""
        text = payload.get("text") or ""

        url = f"{config.STATIC_FILES_HOST}{config.STATIC_FILES_URI_PATH}{source_file}"
        if anchor:
            url += f"#{anchor}"
        
        sources.append({
            "identifier": identifier,
            "url": url,
            "text": text
        })
        context_texts.append(f"Kildereferanse: {identifier}\nURL: {url}\nTekst: {payload.get('text', '')}")

    context = "\n\n---\n\n".join(context_texts)
    current_time = datetime.now().strftime("%A %d. %B %Y kl. %H:%M")
    user_prompt = req.message
    system_prompt = (
        f"{config.SYSTEM_PROMPT}\n\n"
        f"Nåværende tidspunkt: {current_time}\n\n"
        f"---\n\n"
        f"RELEVANT PENSUMMATERIALE:\n\n"
        f"{context}"
    )

    logger.info(f"Prompt sent to LLM:\n{system_prompt}")

    # Streaming generator
    async def event_stream():
        # 1. Send sources first
        yield f"{json.dumps({'type': 'sources', 'sources': sources})}\n\n"

        # 2. Stream LLM deltas
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{config.LLM_BASE}/chat/completions",
                json={
                    "model": req.inference_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": config.MAX_TOKENS,
                    "temperature": config.TEMPERATURE,
                    "stream": True
                }
            ) as resp:
                async for line in resp.aiter_lines():
                    line = line.strip()

                    # Skip empty lines or stream control lines
                    if not line or line.startswith("data: [DONE]"):
                        continue

                    if line.startswith("data: "):
                        # Parse JSON
                        data = json.loads(line[len("data: "):])

                        # Extract text delta
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")

                        if content:
                            # Send ONLY the text (plain string), as the frontend expects
                            yield f"{json.dumps({'type': 'delta', 'text': content})}\n\n"

        # 3. Signal end
        yield f"{json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
