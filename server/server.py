import asyncio
import json
import locale
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import utils.config as config
from db import QdrantVectorDB, WeaviateVectorDB, VectorDB
from embedder import load_embedder
from memory import ConversationMemoryStore, ConversationMemoryManager
from prompt import build_context_docs
from retrieval import retrieve_context

# ============================================================
#  LOCALE / LOGGING
# ============================================================
locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s [%(levelname)s] %(message)s")
logger = logging.getLogger("server")

# ============================================================
#  AVAILABLE OPTIONS
# ============================================================
AVAILABLE_INFERENCE_MODELS = [
    {"id": "gpt-oss-20b", "name": "GPT-OSS 20B"},
]
AVAILABLE_EMBEDDERS = config.EMBEDDING_MODELS
AVAILABLE_VECTOR_DBS = [
    {"id": "qdrant", "name": "Qdrant"},
    {"id": "weaviate", "name": "Weaviate"},
]
AVAILABLE_OPTIONS = {
    "inference_model": AVAILABLE_INFERENCE_MODELS,
    "embedding_model": AVAILABLE_EMBEDDERS,
    "vector_db": AVAILABLE_VECTOR_DBS,
}

# ============================================================
#  MEMORY
# ============================================================
memory_store = ConversationMemoryStore()
memory_manager = ConversationMemoryManager(memory_store, recent_turns=3, memory_max_tokens=6000)

# ============================================================
#  DB REGISTRY
# ============================================================
DB_REGISTRY: dict[str, VectorDB] = {
    "qdrant": QdrantVectorDB(),
    "weaviate": WeaviateVectorDB(),
}

# ============================================================
#  FASTAPI APP
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Preloading embedding models on startup...")
    for emb in AVAILABLE_EMBEDDERS:
        model_id = emb.get("id")
        if not model_id:
            continue
        try:
            await asyncio.to_thread(load_embedder, model_id)
            logger.info(f"Preloaded embedder: {model_id}")
        except Exception as e:
            logger.error(f"Failed to preload embedder {model_id}: {e}")

    yield

    for db_id, db in DB_REGISTRY.items():
        try:
            db.close()
            logger.info(f"{db_id} client closed cleanly.")
        except Exception as e:
            logger.warning(f"{db_id} close error: {e}")

app = FastAPI(lifespan=lifespan)

# ============================================================
#  REQUEST SCHEMA
# ============================================================
class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    inference_model: Optional[str] = None
    embedding_model: Optional[str] = None
    vector_db: Optional[str] = None
    socratic_mode: bool = False
    active_collections: Optional[list[str]] = None
    debug: bool = False


@app.get("/config")
async def get_config():
    return AVAILABLE_OPTIONS


# ============================================================
#  MAIN CHAT STREAM ENDPOINT
# ============================================================
@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):

    # ---------------- VALIDATION ----------------
    if not req.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    user_id: str = req.user_id

    for field, opts in AVAILABLE_OPTIONS.items():
        val = getattr(req, field)
        if val and not any(obj["id"] == val for obj in opts):
            raise HTTPException(status_code=400, detail=f"Invalid {field}: {val}")

    if not req.inference_model:
        raise HTTPException(400, "Missing inference_model")
    if not req.embedding_model:
        raise HTTPException(400, "Missing embedding_model")
    if not req.vector_db:
        raise HTTPException(400, "Missing vector_db")

    start_time = time.time()
    logger.info(f"\n\n\n{'=' * 50}\nIncoming message: {req.message}")
    logger.info(f"Using model={req.inference_model}, embedder={req.embedding_model}, db={req.vector_db}")

    # ---------------- RAG RETRIEVAL ----------------
    db = DB_REGISTRY[req.vector_db]
    payloads = await retrieve_context(db, req.message, req.embedding_model)
    logger.info(f"Retrieval completed in {time.time() - start_time:.2f}s")
    sources, context = build_context_docs(payloads)

    # ---------------- PROMPT BUILDER ----------------
    now = datetime.now().strftime("%A %d. %B %Y kl. %H:%M")
    system_prompt = (
        f"{config.SYSTEM_PROMPT}\n\n"
        f"Du har en pågående samtale med brukeren. Samtalehistorikk er vedlagt og skal brukes hvis relevant.\n"
        f"Nåværende tidspunkt: {now}\n\n"
        f"---\n\n"
        f"RELEVANT PENSUMMATERIALE:\n\n"
        f"{context}"
    )

    memory_messages = await memory_manager.build_messages(user_id)
    messages = [
        {"role": "system", "content": system_prompt},
        *memory_messages,
        {"role": "user", "content": req.message},
    ]

    logger.info(f"Memory:\n{memory_messages}")
    sources_log = "\n".join(
        f"{s['identifier']}: {s['url']}\n{s['text']}"
        if s["type"] == "video_transcript" else
        f"{s['identifier']}: {s['url']}"
        for s in sources
    )
    logger.info(f"Sources:\n{sources_log}")

    # ---------------- STREAMING RESPONSE ----------------
    async def event_stream():
        if req.debug:
            yield json.dumps({"type": "debug", "step": "retrieval", "data": payloads}) + "\n\n"
            yield json.dumps({"type": "debug", "step": "memory", "data": memory_messages}) + "\n\n"

        yield json.dumps({"type": "sources", "sources": sources}) + "\n\n"
        full_response = ""

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{config.LLM_BASE}/chat/completions",
                json={
                    "model": req.inference_model,
                    "messages": messages,
                    "max_tokens": config.MAX_TOKENS,
                    "temperature": config.TEMPERATURE,
                    "repetition_penalty": config.REPETITION_PENALTY,
                    "stream": True,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line or line.startswith("data: [DONE]"):
                        continue
                    if line.startswith("data: "):
                        data = json.loads(line[len("data: "):])
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            full_response += content
                            yield json.dumps({"type": "delta", "text": content}) + "\n\n"

        logger.info(f"LLM full response:\n{full_response}")
        logger.info(f"Time elapsed: {time.time() - start_time:.2f}s")

        await memory_store.append_message(user_id, "user", req.message)
        await memory_store.append_message(user_id, "assistant", full_response)

        yield json.dumps({"type": "done"}) + "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
