from typing import Any, Dict, List, Optional
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

from memory import ConversationMemoryStore, ConversationMemoryManager

# ============================================================
#  LOCALE / LOGGING
# ============================================================
locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s [%(levelname)s] %(message)s")
logger = logging.getLogger("retrieval")


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
    memory_store,
    recent_turns=3,
    summary_max_tokens=800,
    recent_max_tokens=1500
)

# ============================================================
#  INIT CLIENTS
# ============================================================
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


# ============================================================
#  FASTAPI APP
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    try:
        weaviate_client.close()
        logger.info("Weaviate client closed cleanly.")
    except Exception as e:
        logger.warning(f"Weaviate close error: {e}")

app = FastAPI(lifespan=lifespan)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FILES_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "ingestion", "knowledge"))
app.mount(config.STATIC_FILES_URI_PATH, StaticFiles(directory=STATIC_FILES_DIR))

# ============================================================
#  REQUEST SCHEMA
# ============================================================
class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    inference_model: Optional[str] = None
    embedding_model: Optional[str] = None
    vector_db: Optional[str] = None


# ============================================================
#  EMBEDDER CACHE
# ============================================================
@lru_cache(maxsize=None)
def load_embedder(model_id: str):
    logger.info(f"Loading embedder model: {model_id}")
    model = SentenceTransformer(model_id, trust_remote_code=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    return model

@app.get("/config")
async def get_config():
    return AVAILABLE_OPTIONS

# ============================================================
#  RETRIEVAL
# ============================================================
async def retrieve_context(db_id: str, embed_text: str, embedding_model_id: str) -> List[Dict[str, Any]]:
    embedder = load_embedder(embedding_model_id)
    vector = embedder.encode(embed_text, normalize_embeddings=True).tolist()
    embedding_model_name = next((opt['name'] for opt in AVAILABLE_EMBEDDERS if opt['id'] == embedding_model_id))
    all_payloads = []
    
    for type in ['course_page', 'video_transcript']:
        payloads = []
        if db_id == "qdrant":
            collection = to_qdrant_name(f"{embedding_model_name}_{type}s")
            res = qdrant.query_points(collection_name=collection, query=vector, limit=10)
            payloads = [point.payload for point in res.points]            

        elif db_id == "weaviate":
            class_name = to_weaviate_class(f"{embedding_model_name}_{type}s")
            collection = weaviate_client.collections.get(class_name)
            res = collection.query.near_vector(
                near_vector=vector,
                limit=10,
                return_metadata=MetadataQuery(distance=True, score=True)
            )
            payloads = [obj.properties for obj in res.objects]

        else:
            raise ValueError("Unknown vector DB")
        
        for payload in payloads:
            payload["type"] = type
            all_payloads.append(payload)
        
    return all_payloads


# ============================================================
#  CONTEXT BUILDER
# ============================================================
def build_context_docs(payloads: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], str]:
    sources = []
    context_blocks = []

    for payload in payloads:
        type = payload.get("type") or ""
        if type == 'course_page':
            identifier = payload.get("identifier") or str(uuid.uuid4())
            source = f"{config.STATIC_FILES_HOST}{config.STATIC_FILES_URI_PATH}{payload['source']}"
            text = payload.get("text") or ""
            
            anchor = payload.get("anchor") or ""
            url = f"{source}#{anchor}" if anchor else source
            
        elif type == 'video_transcript':
            identifier = payload.get("chunk_id") or str(uuid.uuid4())
            source = f"https://os.cs.oslomet.no/os/Forelesning/video/2021/{payload['lecture_id']}.mp4"
            text = payload.get("text") or ""
            
            start = payload.get("start")
            url = f"{source}#t={start}" if start else source
            
        else:
            raise ValueError


        sources.append({
            "type": type,
            "identifier": identifier,
            "url": url,
            "text": text,
        })

        context_blocks.append(
            f"Kildereferanse: {identifier}\nURL: {url}\nTekst:\n{text}"
        )

    return sources, "\n\n---\n\n".join(context_blocks)


# ============================================================
#  MAIN CHAT STREAM ENDPOINT
# ============================================================
@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):

    # ---------------- VALIDATION ----------------
    # Require user_id for memory
    if not req.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
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

    logger.info(f"\n\n\n{'=' * 50}\nIncoming message: {req.message}")
    logger.info(f"Using model={req.inference_model}, embedder={req.embedding_model}, db={req.vector_db}")

    # ---------------- RAG RETRIEVAL ----------------
    summary = await memory_store.get_summary(req.user_id)
    recent_msgs = await memory_store.get_recent_messages(req.user_id)

    retrieval_query = "\n".join([
        summary,
        *[m["content"] for m in recent_msgs[-2:] if m["role"] == "user"],
        req.message
    ])

    logger.info(
        f"Retrieval query tokens: {len(retrieval_query.split())}"
    )

    payloads = await retrieve_context(
        req.vector_db,
        retrieval_query,
        req.embedding_model
    )
    
    sources, context = build_context_docs(payloads)

    # ---------------- PROMPT BUILDER ----------------    
    now = datetime.now().strftime("%A %d. %B %Y kl. %H:%M")

    user_prompt = req.message
    system_prompt = (
        f"{config.SYSTEM_PROMPT}\n\n"
        f"Du har en pågående samtale med brukeren. Samtalehistorikk er vedlagt og skal brukes hvis relevant.\n"
        f"Nåværende tidspunkt: {now}\n\n"
        f"---\n\n"
        f"RELEVANT PENSUMMATERIALE:\n\n"
        f"{context}"
    )
    
    memory_messages = await memory_manager.build_messages(req.user_id)

    messages = [
        {"role": "system", "content": system_prompt},
        *memory_messages,
        {"role": "user", "content": user_prompt},
    ]
    
    prompt_tokens = sum(
        len(m["content"].split()) for m in messages
    )
    context_tokens = len(context.split())

    logger.info(
        f"Prompt token estimate: {prompt_tokens}, "
        f"RAG context size: {context_tokens}"
    )
    
    logger.info(f"Memory:\n{memory_messages}")
    
    sources_text = "\n".join(
        f"{source['identifier']}: {source['url']}\n{source['text']}"
        if source['type'] == 'video_transcript' else
        f"{source['identifier']}: {source['url']}"
        for source in sources
    )
    logger.info(f"Sources:\n{sources_text}")

    # ---------------- STREAMING RESPONSE ----------------
    async def event_stream():
        # Send sources first
        yield json.dumps({"type": "sources", "sources": sources}) + "\n\n"

        # Keep track of full response for logging purposes
        full_response = ""

        # Stream LLM deltas
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{config.LLM_BASE}/chat/completions",
                json={
                    "model": req.inference_model,
                    "messages": messages,
                    "max_tokens": config.MAX_TOKENS,
                    "temperature": config.TEMPERATURE,
                    "stream": True
                }
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

        # Log full response
        logger.info(f"LLM full response:\n{full_response}")
        
        # Add to conversation memory
        await memory_manager.update(
            req.user_id,
            user_prompt,
            full_response,
            sources
        )

        # Signal to client that response is complete
        yield json.dumps({"type": "done"}) + "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
