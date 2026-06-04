import logging
from importlib.metadata import version

from qdrant_client import QdrantClient

import utils.config as config
from utils.naming import to_qdrant_name
from .base import VectorDB

logger = logging.getLogger("server")


class QdrantVectorDB(VectorDB):
    def __init__(self):
        self.client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        logger.info(
            f"Qdrant client (version {version('qdrant-client')}) initialized "
            f"on {config.QDRANT_HOST}:{config.QDRANT_PORT}"
        )

    def query(self, collection_name: str, vector: list[float], limit: int) -> list[dict]:
        normalized = to_qdrant_name(collection_name)
        res = self.client.query_points(collection_name=normalized, query=vector, limit=limit)
        return [point.payload for point in res.points]

    def close(self):
        pass
