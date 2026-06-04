# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Keeping this file updated

When the user reveals new information about how the project works or how it should be developed — architecture decisions, conventions, constraints, tooling choices — update this file immediately to reflect that. Do not wait to be asked.

The user values modularity and clean separation of concerns. Proactively flag situations where a file is growing large enough to split, where a new abstraction would make future changes easier, or where repeated patterns suggest a missing layer. Raise it as a suggestion before acting.

## Project overview

OS-bot is a RAG chatbot for the DATA2500 Operating Systems course at Oslo Metropolitan University, designed to run locally on university-owned hardware. The inference stack is vLLM + gpt-oss-20b.

## Architecture

The project has five main components orchestrated via Docker Compose:

- **`/inference`** — vLLM server exposing an OpenAI-compatible API on port 8000 with gpt-oss-20b weights.
- **`/vectordb`** — Docker Compose for Qdrant (port 6333) and Weaviate (port 6444 HTTP, 50051 gRPC).
- **`/ingestion`** — Standalone scripts (not containerized) for knowledge preprocessing and ingestion:
  - `scrape_course_pages.py` → scrapes HTML from course site
  - `process_course_pages.py` → converts HTML/TXT to plaintext chunks → `chunks_course_pages.jsonl`
  - `process_video_transcripts.py` → processes transcripts → `chunks_video_transcripts.jsonl`
  - `ingest.py` → embeds and ingests chunks into both Qdrant and Weaviate for each of the configured embedding models (10 total configurations)
- **`/server`** — FastAPI backend (port 8080). Split into focused modules; `server.py` is a thin entry point that wires them together.
- **`/frontend`** — Streamlit app (`app.py`) that streams from the server and renders markdown with LaTeX and `{ref:ID}` citation placeholders replaced by links.

### Server module layout

```
server/
├── server.py            # FastAPI app, lifespan, DB_REGISTRY, /chat/stream endpoint
├── embedder.py          # load_embedder() with lru_cache — shared by retrieval and lifespan preload
├── retrieval.py         # retrieve_context() — iterates COLLECTION_TYPES, delegates to VectorDB
├── prompt.py            # build_context_docs() — maps payloads to sources list + context string
├── collection_types.py  # CollectionType ABC, concrete types, COLLECTION_TYPES + COLLECTION_TYPE_MAP
├── memory.py            # ConversationMemoryStore + ConversationMemoryManager
└── db/
    ├── base.py          # VectorDB ABC: query() + close()
    ├── qdrant_db.py     # QdrantVectorDB
    └── weaviate_db.py   # WeaviateVectorDB
```

**Design rationale:**

- `VectorDB` is an ABC so new backends (e.g. pgvector, Chroma) can be added by creating one file and registering an instance in `DB_REGISTRY` in `server.py`. Each DB normalizes the collection name internally using `utils/naming.py`.

- `CollectionType` is an ABC that owns two things: the `plural` suffix used to build collection names, and `extract_source()` which unpacks the DB payload into `(identifier, url, text)`. This pairing is intentional — both change together when a new knowledge source type is added. To add a new type, subclass `CollectionType` and append an instance to `COLLECTION_TYPES`; no other files need to change.

- Collection names passed to `VectorDB.query()` follow the pattern `<embedding_model_name>_<collection_type.plural>` (e.g. `GTE Multilingual Base_course_pages`). Each DB class normalizes this to its required format.

- The `db/` package is named to avoid collision with Python's stdlib `collections` module, which is why collection types live in `collection_types.py` rather than `collections.py`.

### Shared utilities

`/utils/config.py` — all environment-variable-driven config (LLM, vector DB hosts/ports, embedding model list, system prompt). Both server and frontend import from here.

`/utils/naming.py` — converts embedding model names to valid Qdrant collection names (`to_qdrant_name`) and Weaviate class names (`to_weaviate_class`).

### Data flow

1. User message → frontend → `POST /chat/stream`
2. Server embeds the query using the selected embedding model (cached via `lru_cache`)
3. Server queries all registered `COLLECTION_TYPES` (currently `course_page`, `video_transcript`) in the selected vector DB
4. Retrieved chunks + conversation memory are assembled into a prompt and streamed to vLLM
5. LLM response streams back to the frontend as SSE-style newline-delimited JSON
6. Frontend postprocesses: LaTeX normalization, `{ref:ID}` → Markdown links

### Conversation memory

`server/memory.py` implements in-memory per-user conversation history (`ConversationMemoryStore`) and a `ConversationMemoryManager` that injects the last 3 turns plus an optional rolling summary (capped at ~6000 tokens) into each request.

### Vector DB collection naming

Collections are named `<embedding_model_name>_<collection_type.plural>` and normalized per DB by `utils/naming.py`:
- Qdrant: lowercase, only `a-z0-9-_` (`to_qdrant_name`)
- Weaviate: CamelCase, letters and digits only (`to_weaviate_class`)

## Key environment variables

| Variable | Default | Purpose |
|---|---|---|
| `LLM_HOST` / `LLM_PORT` | `localhost:8000` | vLLM inference server |
| `QDRANT_HOST` / `QDRANT_PORT` | `localhost:6333` | Qdrant |
| `WEAVIATE_HOST` / `WEAVIATE_PORT` | `localhost:6444` | Weaviate HTTP |
| `WEAVIATE_PORT_GRPC` | `50051` | Weaviate gRPC |
| `SERVER_HOST` / `SERVER_PORT` | `localhost:8080` | FastAPI backend |

In Docker Compose the service names (`vllm`, `qdrant`, `weaviate`, `server`) are used as hostnames.
