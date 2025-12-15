# Just so local inclusion will work. Find a nicer way later...
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import uuid
import torch
import argparse
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
    """Upserts data to Qdrant with all available fields except the vector itself."""
    qdrant_points = []
    for data in chunk_data:
        # Copy all fields except the vector (Qdrant separates vectors from payload)
        payload = {k: v for k, v in data.items() if k != "vector"}
        
        # Use a deterministic UUID (based on identifier or text)
        stable_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, data.get("identifier", data.get("text", str(uuid.uuid4())))))
        
        qdrant_points.append({
            "id": stable_uuid,
            "vector": data["vector"],
            "payload": payload
        })

    batch_size = 128
    for i in range(0, len(qdrant_points), batch_size):
        qdrant_client.upsert(
            collection_name=collection_name, 
            points=qdrant_points[i:i + batch_size],
            wait=True
        )

    print(f"  -> Successfully indexed {len(chunk_data)} chunks to Qdrant/{collection_name}")

# --- WEAVIATE FUNCTIONS ---

def setup_weaviate_class(
    weaviate_client: WeaviateClient,
    class_name: str,
    vector_size: int,
    sample_chunk: Dict[str, Any]
):
    """Sets up a Weaviate class dynamically based on chunk fields."""
    print(f"Setting up Weaviate class: {class_name}")

    # 1. DELETE existing class for clean recreation
    if weaviate_client.collections.exists(class_name):
        print(f"  -> Deleting existing class: {class_name}")
        weaviate_client.collections.delete(class_name)

    # 2. Dynamically infer property schema from the sample chunk
    properties = []
    for key, value in sample_chunk.items():
        if key == "vector":
            continue  # skip vector field
        # Infer Weaviate data type based on Python type
        if isinstance(value, (str, type(None))):
            dtype = DataType.TEXT
        elif isinstance(value, bool):
            dtype = DataType.BOOL
        elif isinstance(value, int):
            dtype = DataType.INT
        elif isinstance(value, float):
            dtype = DataType.NUMBER
        elif isinstance(value, list):
            # You can refine this logic further (list of strings vs numbers)
            dtype = DataType.TEXT_ARRAY
        else:
            dtype = DataType.TEXT  # fallback

        properties.append(Property(name=key, data_type=dtype))

    # 3. CREATE the new Weaviate class
    weaviate_client.collections.create(
        name=class_name,
        vector_config=Configure.Vectors.self_provided(
            vector_index_config=Configure.VectorIndex.hnsw(
                distance_metric=VectorDistances.COSINE
            )
        ),
        properties=properties,
    )

    print(f"  -> Created dynamic Weaviate class with {len(properties)} properties.")

    
def upsert_to_weaviate(weaviate_client: WeaviateClient, class_name: str, chunk_data: List[Dict[str, Any]]):
    """Upserts data to Weaviate with all available fields except the vector itself."""
    collection = weaviate_client.collections.get(class_name)
    data_objects = []

    for data in chunk_data:
        # Include all fields except the vector
        properties = {k: v for k, v in data.items() if k != "vector"}
        
        stable_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, data.get("identifier", data.get("text", str(uuid.uuid4())))))
        
        data_object = DataObject(
            properties=properties,
            uuid=stable_uuid,
            vector=data["vector"]
        )
        data_objects.append(data_object)

    result = collection.data.insert_many(data_objects)

    if result.errors:
        print(f"  -> WARNING: {len(result.errors)} errors encountered during Weaviate batch import.")
        print(result.errors)
        
    print(f"  -> Successfully indexed {len(chunk_data)} chunks to Weaviate/{class_name}")


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest data into vector databases.")
    parser.add_argument(
        "source",
        choices=["course_pages", "video_transcripts"],
        help="Data source to ingest: 'course_pages' for HTML pages, 'video_transcripts' for video transcripts."
    )
    args = parser.parse_args()

    # Set input file based on source
    if args.source == "course_pages":
        chunk_input_file = "processed_chunks.jsonl"
    elif args.source == "video_transcripts":
        chunk_input_file = "knowledge_processed/os/Forelesning/video/transcripts_processed.jsonl"
    
    # 1. Load Pre-processed Chunks
    print("--- LOADING PRE-PROCESSED CHUNKS ---")
    chunks = load_chunks(chunk_input_file)
    
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
            Q_COLLECTION_NAME = to_qdrant_name(f"{model_name}_{args.source}")
            W_CLASS_NAME = to_weaviate_class(f"{model_name}_{args.source}")
            
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
            setup_weaviate_class(weaviate_client, W_CLASS_NAME, vector_size, chunks_with_vectors[0])
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