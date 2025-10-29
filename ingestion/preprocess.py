import json
from pathlib import Path
from typing import List, Dict
from urllib.parse import quote

# LangChain/Utilities
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
DATA_DIR = Path("./knowledge")
POSTPROCESSED_DIR = Path("./knowledge_processed")
CHUNK_OUTPUT_FILE = "processed_chunks.jsonl"  # File to store all chunks

# Chunking
TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

# --- HELPER FUNCTIONS ---

def generate_text_fragment_anchor(chunk_text: str, max_chars: int = 60) -> str:
    """
    Generates a #:~:text= style anchor for a chunk.
    Takes the first max_chars of the chunk as the highlight text.
    """
    snippet = chunk_text.strip().replace("\n", " ")
    if len(snippet) > max_chars:
        snippet = snippet[:max_chars] + "…"  # ellipsis if truncated
    encoded = quote(snippet, safe="")
    return f"#:~:text={encoded}"


def extract_content(path: Path, save_path: Path) -> str:
    """
    Extracts text content from a single file (HTML or TXT) and saves postprocessed text.
    Returns the cleaned text content as a string.
    """
    print(f"Loading {path}...")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    text_content = ""

    if path.suffix.lower() == ".html":
        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        # Flatten the page text
        text_content = soup.get_text(" ", strip=True)

    elif path.suffix.lower() == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            text_content = f.read().strip()
    else:
        return None  # skip unsupported file types

    # Save postprocessed text as .txt
    if text_content:
        with open(save_path.with_suffix(".txt"), "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"  -> Saved postprocessed text to {save_path.with_suffix('.txt')}")

    return text_content


def load_and_split_documents(data_dir: Path, postprocessed_dir: Path) -> List[Dict]:
    """
    Walks through data_dir recursively, extracts content, splits into chunks,
    and generates text-fragment anchors for HTML files.
    Returns a list of flattened chunk dictionaries.
    """
    all_chunks = []

    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in [".html", ".txt"]:
            relative_path = path.relative_to(data_dir)
            save_path = postprocessed_dir / relative_path

            content = extract_content(path, save_path)
            if not content:
                continue

            chunks = TEXT_SPLITTER.split_text(content)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{relative_path.stem}_{i}_{len(chunk)}"
                anchor = generate_text_fragment_anchor(chunk) if path.suffix.lower() == ".html" else None

                all_chunks.append({
                    "id": chunk_id,
                    "chunk_text": chunk,
                    "anchor": anchor,
                    "source": str(relative_path),
                    # Optionally keep chunk_index if you want
                    # "chunk_index": i
                })

    return all_chunks


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    POSTPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("--- 1. STARTING DOCUMENT PREPROCESSING ---")
    
    all_chunks = load_and_split_documents(DATA_DIR, POSTPROCESSED_DIR)
    
    if not all_chunks:
        print("Error: No chunks were generated. Check DATA_DIR and file types.")
    else:
        print(f"\nSuccessfully generated {len(all_chunks)} total chunks.")

        # Save the chunks to a JSON Lines file
        with open(CHUNK_OUTPUT_FILE, "w", encoding="utf-8") as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        
        print(f"--- CHUNKS SAVED TO {CHUNK_OUTPUT_FILE} ---")