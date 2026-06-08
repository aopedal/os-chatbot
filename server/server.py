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

import settings
import utils.config as config
from db import QdrantVectorDB, WeaviateVectorDB, VectorDB
from embedder import load_embedder
from memory import ConversationMemoryStore, ConversationMemoryManager
from intent import classify_intent
from prompt import build_context_docs, build_system_prompt, socratic_mode_active
from retrieval import retrieve_context


async def _sse(gen):
    async for chunk in gen:
        yield json.dumps(chunk) + "\n\n"


# ============================================================
#  LOCALE / LOGGING
# ============================================================
locale.setlocale(locale.LC_TIME, "nb_NO.UTF-8")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)s [%(levelname)s] %(message)s"
)
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
memory_manager = ConversationMemoryManager(
    memory_store, recent_turns=3, memory_max_tokens=6000
)

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
_REQUIRED_SETTINGS_KEYS = [
    "temperature",
    "repetition_penalty",
    "max_tokens",
    "direct_intro",
    "socratic_intro",
    "shared_instructions",
    "socratic_categories",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = settings.load()
    missing = [k for k in _REQUIRED_SETTINGS_KEYS if k not in cfg]
    if missing:
        logger.error("settings.toml is missing required keys: %s", missing)
    else:
        logger.info("settings.toml loaded successfully.")

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
    logger.info(
        f"Using model={req.inference_model}, embedder={req.embedding_model}, db={req.vector_db}"
    )

    # ---------------- RAG RETRIEVAL + INTENT CLASSIFICATION ----------------
    db = DB_REGISTRY[req.vector_db]
    if req.socratic_mode:
        payloads, intent_result = await asyncio.gather(
            retrieve_context(db, req.message, req.embedding_model),
            classify_intent(req.message, req.inference_model, config.LLM_BASE),
        )
    else:
        payloads = await retrieve_context(db, req.message, req.embedding_model)
        intent_result = None
    logger.info(f"Retrieval completed in {time.time() - start_time:.2f}s")
    if intent_result:
        logger.info(f"Intent: {intent_result}")
    sources, context = build_context_docs(payloads)

    # ---------------- PROMPT BUILDER ----------------
    now = datetime.now().strftime("%A %d. %B %Y kl. %H:%M")
    system_prompt = build_system_prompt(context, now, intent_result, req.socratic_mode)

    memory_messages = await memory_manager.build_messages(user_id)
    messages = [
        {"role": "system", "content": system_prompt},
        *memory_messages,
        {"role": "user", "content": req.message},
    ]

    logger.info(f"Memory:\n{memory_messages}")
    sources_log = "\n".join(
        f"{s['identifier']}: {s['url']}\n{s['text']}"
        if s["type"] == "video_transcript"
        else f"{s['identifier']}: {s['url']}"
        for s in sources
    )
    logger.info(f"Sources:\n{sources_log}")

    # ---------------- STREAMING RESPONSE ----------------
    async def event_stream():
        cfg = settings.load()
        yield {
            "type": "debug",
            "step": "config",
            "data": {"loaded_at": settings.mtime()},
        }
        yield {
            "type": "debug",
            "step": "retrieval",
            "data": payloads,
        }
        yield {
            "type": "debug",
            "step": "memory",
            "data": memory_messages,
        }
        if intent_result is not None:
            yield {
                "type": "debug",
                "step": "intent",
                "data": {
                    **intent_result,
                    "socratic_mode_active": socratic_mode_active(
                        intent_result, req.socratic_mode
                    ),
                },
            }

        yield {"type": "sources", "sources": sources}
        full_response = ""

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{config.LLM_BASE}/chat/completions",
                json={
                    "model": req.inference_model,
                    "messages": messages,
                    "max_tokens": cfg.get("max_tokens"),
                    "temperature": cfg.get("temperature"),
                    "repetition_penalty": cfg.get("repetition_penalty"),
                    "stream": True,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line or line.startswith("data: [DONE]"):
                        continue
                    if line.startswith("data: "):
                        data = json.loads(line[len("data: ") :])
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            full_response += content
                            yield {"type": "delta", "text": content}

        logger.info(f"LLM full response:\n{full_response}")
        logger.info(f"Time elapsed: {time.time() - start_time:.2f}s")

        await memory_store.append_message(user_id, "user", req.message)
        await memory_store.append_message(user_id, "assistant", full_response)

        yield {"type": "done"}

    return StreamingResponse(_sse(event_stream()), media_type="text/event-stream")
