# Just so local inclusion will work. Find a nicer way later...
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import uuid
import torch
from typing import List, Dict, Any
from utils.naming import to_qdrant_name, to_weaviate_class
import utils.config as config

# Utilities
from sentence_transformers import SentenceTransformer

# Vector Databases
from qdrant_client import QdrantClient
from qdrant_client.http.models import models
import weaviate
from weaviate.classes.config import (
    Configure,
    Property,
    DataType,
    VectorDistances,
)
from weaviate import WeaviateClient
from weaviate.classes.data import DataObject

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
    texts = [chunk["text"] for chunk in chunks]
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
        payload = {
            "identifier": data.get("identifier"),
            "text": data.get("text"),
            "source": data.get("source"),
            "anchor": data.get("anchor")
        }
        
        stable_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, data["identifier"])) 
        
        qdrant_points.append({
            "id": stable_uuid,
            "vector": data["vector"],
            "payload": payload
        })

    batch_size = 128
    for i in range(0, len(qdrant_points), batch_size):
        qdrant_client.upsert(
            collection_name=collection_name, 
            points=qdrant_points[i:i+batch_size], 
            wait=True
            )
    print(f"  -> Successfully indexed {len(chunk_data)} chunks to Qdrant/{collection_name}")

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
            Property(name="identifier", data_type=DataType.TEXT),
            Property(name="text", data_type=DataType.TEXT),
            Property(name="source", data_type=DataType.TEXT),
            Property(name="anchor", data_type=DataType.TEXT)
        ],
    )
    
def upsert_to_weaviate(weaviate_client: WeaviateClient, class_name: str, chunk_data: List[Dict[str, Any]]):
    """Upserts data to Weaviate using v4 client's insert_many."""
    
    # 1. Get the collection client
    collection = weaviate_client.collections.get(class_name)

    data_objects = []
    for data in chunk_data:
        # Weaviate properties object from chunk payload
        properties = {
            "identifier": data.get("identifier"),
            "text": data.get("text"),
            "source": data.get("source"),
            "anchor": data.get("anchor")
        }
        
        stable_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, data["identifier"]))
        
        # 2. Create the DataObject for batch insertion
        data_object = DataObject(
            properties=properties,
            uuid=stable_uuid,
            vector=data["vector"]
        )
        data_objects.append(data_object)
    
    # 3. Insert the list of DataObjects.
    result = collection.data.insert_many(data_objects)
    
    # Optional: Check the result for errors
    if result.errors:
        print(f"  -> WARNING: {len(result.errors)} errors encountered during Weaviate batch import.")
        print(result.errors)
        
    print(f"  -> Successfully indexed {len(chunk_data)} chunks to Weaviate/{class_name}")


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    
    # 1. Load Pre-processed Chunks
    print("--- LOADING PRE-PROCESSED CHUNKS ---")
    chunks = load_chunks(config.CHUNK_INPUT_FILE)
    
    if not chunks:
        print("No chunks loaded, exiting")
        exit(1) # Stop if no chunks are loaded
    
    print("--- CONNECTING TO VECTOR DATABASES ---")
    # 2. Setup Clients
    QDRANT_TIMEOUT_SECONDS = 600
    qdrant_client = QdrantClient(
        host=config.QDRANT_HOST, 
        port=config.QDRANT_PORT,
        timeout=QDRANT_TIMEOUT_SECONDS
    )

    try:
        # Connect using the explicit connect_to_custom helper for non-default ports
        weaviate_client = weaviate.connect_to_custom(
            http_host=config.WEAVIATE_HOST,
            http_port=config.WEAVIATE_PORT,
            http_secure=False,
            grpc_host=config.WEAVIATE_HOST,
            grpc_port=config.WEAVIATE_PORT_GRPC,
            grpc_secure=False,
        )
    except Exception as e:
        raise ConnectionError(f"Weaviate client failed to connect. Error: {e}")

    # Check connection status (readiness)
    if not weaviate_client.is_ready():
        raise ConnectionError(f"Weaviate client failed the readiness check. Check your Docker containers.")

    print("Successfully connected to Qdrant (6333) and Weaviate (6444).")
    
    # 3. Loop through Models, Embed, and Ingest
    print("\n--- STARTING EMBEDDING AND INDEXING LOOP ---")
    
    for model in config.EMBEDDING_MODELS:
        model_name = model.get('name', 'UNKNOWN_MODEL')
        try:
            model_id = model['id']
            print(f"\n[MODEL: {model_name}] Starting ingestion for {model_id}")
            
            # 3a. Initialize Embedder and Define Collection Names
            Q_COLLECTION_NAME = to_qdrant_name(model_name)
            W_CLASS_NAME = to_weaviate_class(model_name)
            
            embedder = SentenceTransformer(
                model_id,
                device=DEVICE,
                trust_remote_code=True
            )
            vector_size = embedder.get_sentence_embedding_dimension()
            if vector_size is None:
                raise ValueError(f"Could not determine vector size for model {model_name}")
            
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

    try:
        if 'weaviate_client' in locals() and weaviate_client:
            weaviate_client.close()
    except Exception as e:
        print(f"Warning: Failed to gracefully close Weaviate client: {e}")