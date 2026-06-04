import logging
from functools import lru_cache

import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("server")


@lru_cache(maxsize=None)
def load_embedder(model_id: str) -> SentenceTransformer:
    logger.info(f"Loading embedder model: {model_id}")
    model = SentenceTransformer(model_id, trust_remote_code=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return model.to(device)
