from abc import ABC, abstractmethod


class VectorDB(ABC):
    @abstractmethod
    def query(self, collection_name: str, vector: list[float], limit: int) -> list[dict]:
        ...

    @abstractmethod
    def close(self):
        ...
