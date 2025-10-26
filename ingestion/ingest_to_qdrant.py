from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from bs4 import BeautifulSoup
import os, uuid, json, torch

DATA_DIR = "./knowledge"
POSTPROCESSED_DIR = "./knowledge_postprocessed"  # save postprocessed HTML/text
os.makedirs(POSTPROCESSED_DIR, exist_ok=True)

COLLECTION_NAME = "os-pensum"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

def extract_html_sections(path, save_postprocessed=True):
    """
    Parse HTML, skip sections under headings containing any of skip_heading_substrings,
    return list of strings, optionally save postprocessed HTML/text.
    """
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    allowed_texts = []

    headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for i, header in enumerate(headers):
        content = []
        for sib in header.find_next_siblings():
            if sib.name and sib.name.startswith("h"):
                next_level = int(sib.name[1])
                cur_level = int(header.name[1])
                if next_level <= cur_level:
                    break
            content.append(sib.get_text(" ", strip=True))
        section_text = " ".join(content).strip()
        if section_text:
            allowed_texts.append(section_text)

    # Optionally save postprocessed HTML/text for verification
    if save_postprocessed:
        out_name = os.path.join(POSTPROCESSED_DIR, os.path.basename(path))
        with open(out_name + ".txt", "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(allowed_texts))
        print(f"Saved postprocessed text to {out_name}.txt")

    return allowed_texts

def load_docs(data_dir):
    docs = []
    for root, _, files in os.walk(data_dir):
        for fn in files:
            path = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()

            print(f"Loading {path}...")

            if ext == ".html":
                sections = extract_html_sections(path)
                print(f"  -> {len(sections)} sections after skipping headings")
                for sec in sections:
                    docs.append(Document(page_content=sec, metadata={"source": fn}))
    return docs


# Chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

# Embeddings
embed_model_name = "Alibaba-NLP/gte-multilingual-base"
embedder = SentenceTransformer(
    embed_model_name,
    device="cuda" if torch.cuda.is_available() else "cpu",
    trust_remote_code=True)

# Qdrant
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
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
    batch_size = 128
    for i in range(0, len(points), batch_size):
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points[i:i+batch_size])

if __name__ == "__main__":
    docs = load_docs(DATA_DIR)
    print(f"Loaded {len(docs)} docs")
    upsert_documents(docs)
    print("Done indexing to Qdrant.")
