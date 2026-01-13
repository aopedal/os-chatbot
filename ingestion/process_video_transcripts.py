import os
import json
import ast
from typing import List, Dict
import tiktoken

# --- CONFIG ---
MIN_TOKENS = 150
MAX_TOKENS = 300
OVERLAP_TOKENS = 50
EMBEDDING_MODEL = "text-embedding-3-small"
input_folder = "./knowledge/video"
output_path = "./chunks_video_transcripts.jsonl"

# --- TOKENIZER ---
enc = tiktoken.encoding_for_model(EMBEDDING_MODEL)

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

def merge_transcript_chunks(
    chunks: List[Dict],
    min_tokens=MIN_TOKENS,
    max_tokens=MAX_TOKENS,
    overlap_tokens=OVERLAP_TOKENS,
):
    merged = []
    i = 0
    n = len(chunks)

    while i < n:
        current_texts = []
        current_start = chunks[i]["timestamp"][0]
        current_tokens = 0
        j = i

        # Build chunk up to token budget
        while j < n:
            seg_text = chunks[j]["text"].strip()
            seg_tokens = count_tokens(seg_text)

            if (
                current_tokens + seg_tokens > max_tokens
                and current_tokens >= min_tokens
            ):
                break

            current_texts.append(seg_text)
            current_tokens += seg_tokens
            j += 1

        current_end = chunks[j - 1]["timestamp"][1]

        merged.append({
            "start": current_start,
            "end": current_end,
            "text": " ".join(current_texts),
            "token_count": current_tokens,
        })

        # Calculate overlap (walk backwards by token count)
        if j < n:
            overlap_back = 0
            k = j - 1
            while k > i and overlap_back < overlap_tokens:
                overlap_back += count_tokens(chunks[k]["text"])
                k -= 1
            i = max(k, 0)
        else:
            break

    return merged


def process_folder(input_folder: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    total_chunks = 0

    with open(output_path, "w", encoding="utf-8") as out:
        for filename in os.listdir(input_folder):
            if not filename.endswith(".txt"):
                continue

            lecture_id = os.path.splitext(filename)[0]
            input_path = os.path.join(input_folder, filename)

            with open(input_path, "r", encoding="utf-8") as f:
                raw = f.read().strip()

            try:
                data = ast.literal_eval(raw)
            except Exception as e:
                print(f"❌ Failed to parse {filename}: {e}")
                continue

            merged_chunks = merge_transcript_chunks(data["chunks"])

            for idx, chunk in enumerate(merged_chunks):
                record = {
                    "lecture_id": lecture_id,
                    "chunk_id": f"{lecture_id}_{idx:04d}",
                    "start": chunk["start"],
                    "end": chunk["end"],
                    "token_count": chunk["token_count"],
                    "text": chunk["text"],
                    "source": "lecture",
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_chunks += 1

            print(f"{lecture_id}: wrote {len(merged_chunks)} chunks")

    print(f"\n✅ Done. Wrote {total_chunks} total chunks to {output_path}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    process_folder(input_folder, output_path)