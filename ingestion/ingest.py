import os
import json
import uuid
import torch
from pathlib import Path
from typing import List, Dict, Any

# Utilities
from sentence_transformers import SentenceTransformer

# Vector Databases
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, models
import weaviate
from weaviate.classes.config import (
    Configure,
    Property,
    DataType,
    VectorDistances,
)
from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams
from weaviate.classes.data import DataObject

# --- CONFIGURATION ---
CHUNK_INPUT_FILE = "processed_chunks.jsonl" # File created by preprocess.py
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
WEAVIATE_URL = "http://localhost:6444" 

# The 5 models for the A/B test
EMBEDDING_MODELS = {
    "norbert3-base": "ltg/norbert3-base",
    "nb-sbert-base": "NbAiLab/nb-sbert-base",
    "multilingual-e5-large": "intfloat/multilingual-e5-large",
    "bge-m3": "BAAI/bge-m3",
    "gte-multilingual-base": "Alibaba-NLP/gte-multilingual-base",
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- HELPER FUNCTIONS ---

def load_chunks(file_path: str) -> List[Dict[str, Any]]:
    """Loads chunk data from the JSON Lines file."""
    chunks = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                chunks.append(json.loads(line))
        return chunks
    except FileNotFoundError:
        print(f"Error: Chunk input file '{file_path}' not found. Run preprocess.py first.")
        return []

def get_embeddings(chunks: List[Dict[str, Any]], embedder: SentenceTransformer) -> List[Dict[str, Any]]:
    """Generates embeddings for all chunks."""
    texts = [chunk["chunk_text"] for chunk in chunks]
    print(f"  -> Generating {len(texts)} embeddings on {DEVICE}...")
    
    # Encode all texts in one batch for efficiency
    vectors = embedder.encode(texts, convert_to_tensor=True, device=DEVICE).tolist()
    
    # Combine chunk data with new vectors
    for i, chunk in enumerate(chunks):
        chunk["vector"] = vectors[i]
        
    return chunks

# --- QDRANT FUNCTIONS ---

def setup_qdrant_collection(qdrant_client: QdrantClient, collection_name: str, vector_size: int):
    """Sets up a Qdrant collection (v1.8+ compliant)."""
    print(f"Setting up Qdrant collection: {collection_name}")
    
    # 1. Check if the collection exists and delete it (replaces deprecated recreate_collection)
    if qdrant_client.collection_exists(collection_name):
        qdrant_client.delete_collection(collection_name=collection_name)

    # 2. Create the new collection
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
    )

def upsert_to_qdrant(qdrant_client: QdrantClient, collection_name: str, chunk_data: List[Dict[str, Any]]):
    """Upserts data to Qdrant."""
    qdrant_points = []
    for data in chunk_data:
        # Use the stored metadata and vector
        payload = data["metadata"].copy()
        payload["text"] = data["chunk_text"] # Keep the text in the payload for retrieval
        
        stable_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, data["id"])) 
        
        qdrant_points.append({
            "id": stable_uuid,
            "vector": data["vector"],
            "payload": payload
        })
    
    batch_size = 128
    for i in range(0, len(qdrant_points), batch_size):
        qdrant_client.upsert(collection_name=collection_name, 
                             points=qdrant_points[i:i+batch_size], 
                             wait=True)
    print(f"  -> Successfully indexed {len(chunk_data)} chunks to Qdrant/{collection_name}")

# --- WEAVIATE FUNCTIONS ---

# --- WEAVIATE FUNCTIONS ---

def setup_weaviate_class(weaviate_client: WeaviateClient, class_name: str, vector_size: int):
    """Sets up a Weaviate class (collection) for pre-computed vectors (v4)."""
    print(f"Setting up Weaviate class: {class_name}")

    # 1. DELETE the collection if it exists (for recreation/idempotency)
    if weaviate_client.collections.exists(class_name):
        print(f"  -> Deleting existing class: {class_name}")
        weaviate_client.collections.delete(class_name)

    # 2. CREATE the new collection using v4 configuration classes
    weaviate_client.collections.create(
        name=class_name,
        vector_config=Configure.Vectors.self_provided(
            vector_index_config=Configure.VectorIndex.hnsw(
                distance_metric=VectorDistances.COSINE 
            )
        ),
        
        # Define the properties
        properties=[
            Property(name="source", data_type=DataType.TEXT),
            Property(name="filename", data_type=DataType.TEXT),
            Property(name="chunk_index", data_type=DataType.INT),
            Property(name="text", data_type=DataType.TEXT),
        ],
    )
    
def upsert_to_weaviate(weaviate_client: WeaviateClient, class_name: str, chunk_data: List[Dict[str, Any]]):
    """Upserts data to Weaviate using v4 client's insert_many."""
    
    # 1. Get the collection client (v4 concept)
    collection = weaviate_client.collections.get(class_name)

    data_objects = []
    for data in chunk_data:
        # Weaviate properties object from chunk payload
        properties = {
            "source": data["metadata"].get("source"),
            "filename": data["metadata"].get("filename"),
            "chunk_index": data["metadata"].get("chunk_index"),
            "text": data["chunk_text"],
        }
        
        stable_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, data["id"]))
        
        # 2. Create the V4 DataObject for batch insertion
        data_object = DataObject(
            properties=properties,
            uuid=stable_uuid,
            vector=data["vector"]
        )
        data_objects.append(data_object)
    
    # 3. Insert the list of DataObjects. V4 client handles efficient batching internally.
    result = collection.data.insert_many(data_objects)
    
    # Optional: Check the result for errors
    if result.errors:
        print(f"  -> WARNING: {len(result.errors)} errors encountered during Weaviate batch import.")
        # If you need to see the errors: print(result.errors)
        
    print(f"  -> Successfully indexed {len(chunk_data)} chunks to Weaviate/{class_name}")


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    
    # 1. Load Pre-processed Chunks
    print("--- 1. LOADING PRE-PROCESSED CHUNKS ---")
    chunks = load_chunks(CHUNK_INPUT_FILE)
    
    if not chunks:
        exit(1) # Stop if no chunks are loaded
    
    # 2. Setup Clients
    print("\n--- 2. CONNECTING TO VECTOR DATABASES ---")
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    WEAVIATE_HOST_ONLY = WEAVIATE_URL.split('//')[-1].split(':')[0] # 'localhost'
    WEAVIATE_PORT_ONLY = int(WEAVIATE_URL.split(':')[-1])           # 6444
    WEAVIATE_GRPC_PORT = 50051 # Default gRPC port - check your docker-compose if connection fails!

    try:
        # Connect using the explicit connect_to_custom helper for non-default ports
        weaviate_client = weaviate.connect_to_custom(
            http_host=WEAVIATE_HOST_ONLY,
            http_port=WEAVIATE_PORT_ONLY,
            http_secure=False,      # Use True for HTTPS
            grpc_host=WEAVIATE_HOST_ONLY,
            grpc_port=WEAVIATE_GRPC_PORT,
            grpc_secure=False,      # Use True for secure gRPC
        )
    except Exception as e:
        # Note: The old v3 fallback is removed as it caused a second TypeError.
        raise ConnectionError(f"Weaviate client failed to connect to {WEAVIATE_URL} (and gRPC port {WEAVIATE_GRPC_PORT}). Error: {e}")

    # Optional: Check connection status (Good practice)
    # The connect_to_custom method already connects, so we check readiness.
    if not weaviate_client.is_ready():
        raise ConnectionError(f"Weaviate client failed the readiness check at {WEAVIATE_URL}. Check your Docker containers.")

    print("Successfully connected to Qdrant (6333) and Weaviate (6444).")
    
    # 3. Loop through Models, Embed, and Ingest
    print("\n--- 3. STARTING EMBEDDING AND INDEXING LOOP ---")
    
    for nickname, model_name in EMBEDDING_MODELS.items():
        try:
            print(f"\n[MODEL: {nickname}] Starting ingestion with model: {model_name}")
            
            # 3a. Initialize Embedder and Define Collection Names
            Q_COLLECTION_NAME = f"qdrant_{nickname.replace('-', '_')}"
            W_CLASS_NAME = f"OsPensum_{nickname.replace('-', '')}"
            
            embedder = SentenceTransformer(
                model_name,
                device=DEVICE,
                trust_remote_code=True
            )
            vector_size = embedder.get_sentence_embedding_dimension()
            
            # 3b. Generate Embeddings for all chunks
            # Pass a copy to avoid contaminating the original 'chunks' list with vectors
            chunks_with_vectors = get_embeddings(chunks.copy(), embedder) 
            
            # 3c. QDRANT Ingestion
            setup_qdrant_collection(qdrant_client, Q_COLLECTION_NAME, vector_size)
            upsert_to_qdrant(qdrant_client, Q_COLLECTION_NAME, chunks_with_vectors)
            
            # 3d. WEAVIATE Ingestion
            setup_weaviate_class(weaviate_client, W_CLASS_NAME, vector_size)
            upsert_to_weaviate(weaviate_client, W_CLASS_NAME, chunks_with_vectors)

        except Exception as e:
            print(f"FATAL ERROR during ingestion for model {model_name}: {e}")
            continue

    print("\n--- ALL INGESTION JOBS COMPLETE ---")