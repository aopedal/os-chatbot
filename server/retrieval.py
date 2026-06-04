from typing import Any

import utils.config as config
from collection_types import COLLECTION_TYPES
from db.base import VectorDB
from embedder import load_embedder


async def retrieve_context(db: VectorDB, embed_text: str, embedding_model_id: str) -> list[dict[str, Any]]:
    embedder = load_embedder(embedding_model_id)
    vector = embedder.encode(embed_text, normalize_embeddings=True).tolist()
    embedding_model_name = next(opt["name"] for opt in config.EMBEDDING_MODELS if opt["id"] == embedding_model_id)

    all_payloads = []
    for collection_type in COLLECTION_TYPES:
        collection_name = f"{embedding_model_name}_{collection_type.plural}"
        payloads = db.query(collection_name, vector, limit=10)
        for payload in payloads:
            if payload is not None:
                payload["type"] = collection_type.id
                all_payloads.append(payload)

    return all_payloads
