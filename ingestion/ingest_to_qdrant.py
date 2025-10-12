# ingest_to_qdrant.py
from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader, UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os, uuid, json, torch

DATA_DIR = "./knowledge"
COLLECTION_NAME = "os-pensum"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# 1) Load documents (simple DirectoryLoader for .txt/.md, PDF loader for PDFs)
def load_docs(data_dir):
    docs = []
    for root, _, files in os.walk(data_dir):
        for fn in files:
            path = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()

            print(f"Loading {path}...")

            if ext == ".html":
                loader = UnstructuredHTMLLoader(path)
            else:
                continue

            docs.extend(loader.load())
    return docs

# 2) Chunk: ~512 token chunks (approx. 400-800 characters depending)
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

# 3) Embedding model - Norwegian SBERT
embed_model_name = "NbAiLab/nb-sbert-base"  # tuned for Norwegian
embedder = SentenceTransformer(embed_model_name, device="cpu")

# 4) Qdrant client
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# create collection if not exists
if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=embedder.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    )

def upsert_documents(docs):
    points = []
    for d in docs:
        chunks = splitter.split_text(d.page_content)
        for chunk in chunks:
            vec = embedder.encode(chunk).tolist()
            meta = {"source": getattr(d, "metadata", {}).get("source", "unknown"), "text": chunk[:1000]}
            points.append({
                "id": str(uuid.uuid4()),
                "vector": vec,
                "payload": meta
            })
    # batch upsert
    batch_size = 128
    for i in range(0, len(points), batch_size):
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points[i:i+batch_size])

if __name__ == "__main__":
    docs = load_docs(DATA_DIR)
    print(f"Loaded {len(docs)} docs")
    upsert_documents(docs)
    print("Done indexing to Qdrant.")
