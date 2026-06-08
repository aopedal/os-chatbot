import os

# Inference config
LLM_HOST = os.getenv("LLM_HOST", "localhost")
LLM_PORT = int(os.getenv("LLM_PORT", 8000))
LLM_BASE = f"http://{LLM_HOST}:{LLM_PORT}/v1"

# Vector db config
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "localhost")
WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT", 6444))
WEAVIATE_PORT_GRPC = int(os.getenv("WEAVIATE_PORT_GRPC", 50051))

# Server config
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8080))
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
STATIC_FILES_URI_PATH = "https://os.cs.oslomet.no/ose/Forelesning"
STATIC_VIDEOS_URI_PATH = f"{STATIC_FILES_URI_PATH}/video/2021"

# Embedding models
EMBEDDING_MODELS = [
    {"id": "Alibaba-NLP/gte-multilingual-base", "name": "GTE Multilingual Base"},
    {"id": "intfloat/multilingual-e5-large", "name": "Multilingual E5 Large"},
    {"id": "BAAI/bge-m3", "name": "BGE-M3"},
]

# Chatbot config
CHATBOT_NAME = "OS-bot"
