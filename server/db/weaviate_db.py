import logging
from importlib.metadata import version

import weaviate
from weaviate.classes.query import MetadataQuery

import utils.config as config
from utils.naming import to_weaviate_class

from .base import VectorDB

logger = logging.getLogger("server")


class WeaviateVectorDB(VectorDB):
    def __init__(self):
        self.client = weaviate.connect_to_custom(
            http_host=config.WEAVIATE_HOST,
            http_port=config.WEAVIATE_PORT,
            http_secure=False,
            grpc_host=config.WEAVIATE_HOST,
            grpc_port=config.WEAVIATE_PORT_GRPC,
            grpc_secure=False,
            skip_init_checks=True,
        )
        logger.info(
            f"Weaviate client (version {version('weaviate-client')}) initialized "
            f"on {config.WEAVIATE_HOST}:{config.WEAVIATE_PORT}"
        )

    def query(
        self, collection_name: str, vector: list[float], limit: int
    ) -> list[dict]:
        class_name = to_weaviate_class(collection_name)
        collection = self.client.collections.get(class_name)
        res = collection.query.near_vector(
            near_vector=vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True, score=True),
        )
        return [dict(obj.properties) for obj in res.objects if obj.properties]

    def close(self):
        self.client.close()
