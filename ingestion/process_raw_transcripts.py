import os
import json
from typing import List, Dict, Tuple
import tiktoken  # OpenAI tokenizer library

# --- CONFIG ---
MIN_TOKENS = 350
MAX_TOKENS = 600
OVERLAP_TOKENS = 100  # approximate, adjusted dynamically
EMBEDDING_MODEL = "text-embedding-3-small"

# --- TOKENIZER ---
enc = tiktoken.encoding_for_model(EMBEDDING_MODEL)

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

def merge_transcript_chunks(chunks: List[Dict], min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS, overlap_tokens=OVERLAP_TOKENS):
    """Merge timestamped transcript fragments into token-bounded chunks with overlap."""
    merged = []
    i = 0
    n = len(chunks)

    while i < n:
        current_texts = []
        current_start = chunks[i]["timestamp"][0]
        current_tokens = 0
        j = i

        # --- Build up one chunk ---
        while j < n and current_tokens < max_tokens:
            seg_text = chunks[j]["text"].strip()
            seg_tokens = count_tokens(seg_text)
            if current_tokens + seg_tokens > max_tokens and current_tokens >= min_tokens:
                break
            current_texts.append(seg_text)
            current_tokens += seg_tokens
            j += 1

        # --- Determine chunk range ---
        current_end = chunks[j - 1]["timestamp"][1]
        chunk_text = " ".join(current_texts).strip()

        merged.append({
            "text": chunk_text,
            "timestamp": (current_start, current_end),
            "token_count": current_tokens,
        })

        # --- Determine overlap window ---
        # Move pointer back to include ~overlap_tokens worth of text
        if j < n:
            overlap_back = 0
            k = j - 1
            while k > i and overlap_back < overlap_tokens:
                overlap_back += count_tokens(chunks[k]["text"])
                k -= 1
            i = max(k, 0)  # restart at overlap boundary
        else:
            break

    return merged

def process_folder(folder_path: str, output_folder: str):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        #if not filename.endswith(".json"):
        #    continue

        input_path = os.path.join(folder_path, filename)
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        merged_chunks = merge_transcript_chunks(data["chunks"])

        # Write out new file
        output_path = os.path.join(output_folder, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "lecture_id": filename,
                "merged_chunks": merged_chunks
            }, f, ensure_ascii=False, indent=2)

        print(f"Processed {filename} → {len(merged_chunks)} merged chunks")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    process_folder("knowledge/os/Forelesning/video", "knowledge_processed/os/Forelesning/video")