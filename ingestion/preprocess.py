import os
import json
from pathlib import Path
from typing import List, Dict, Any

# LangChain/Utilities
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
DATA_DIR = Path("./knowledge")
POSTPROCESSED_DIR = Path("./knowledge_processed")
CHUNK_OUTPUT_FILE = "processed_chunks.jsonl" # New file to store all chunks

# Chunking
TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

# --- DOCUMENT PROCESSING FUNCTIONS ---

def extract_content(path: Path, save_path: Path):
    """
    Extracts text content from a single file (HTML or TXT).
    Saves postprocessed text to maintain directory structure.
    Returns the cleaned text content as a string.
    """
    print(f"Loading {path}...")
    
    # Create the postprocessed subdirectory if it doesn't exist
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    text_content = ""

    if path.suffix.lower() == ".html":
        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        allowed_texts = []
        # Section extraction logic (retains original HTML parsing approach)
        headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        for header in headers:
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
        
        text_content = "\n\n---\n\n".join(allowed_texts)
        
    elif path.suffix.lower() == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            text_content = f.read().strip()
            
    else:
        # Skip unsupported file types
        return None
    
    # Save postprocessed text to the mirrored directory structure
    if text_content:
        with open(save_path.with_suffix(".txt"), "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"  -> Saved postprocessed text to {save_path.with_suffix('.txt')}")

    return text_content


def load_and_split_documents(data_dir: Path, postprocessed_dir: Path) -> List[Dict[str, Any]]:
    """
    Walks through data_dir recursively, extracts content, and splits into chunks.
    """
    all_chunks = []
    
    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in [".html", ".txt"]:
            
            # Determine the relative path for mirroring the directory structure
            relative_path = path.relative_to(data_dir)
            save_path = postprocessed_dir / relative_path
            
            # 1. Extract content and save post-processed file
            content = extract_content(path, save_path)
            
            if content:
                # 2. Split the full document content into chunks
                chunks = TEXT_SPLITTER.split_text(content)
                
                # 3. Store each chunk with metadata
                for i, chunk in enumerate(chunks):
                    # Use a stable ID for the chunk based on file path and index
                    chunk_id = f"{relative_path.stem}_{i}_{len(chunk)}"
                    
                    all_chunks.append({
                        "id": chunk_id,
                        "chunk_text": chunk,
                        "metadata": {
                            "source": str(relative_path),
                            "filename": path.name,
                            "chunk_index": i
                        }
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
                f.write(json.dumps(chunk) + "\n")
        
        print(f"--- CHUNKS SAVED TO {CHUNK_OUTPUT_FILE} ---")