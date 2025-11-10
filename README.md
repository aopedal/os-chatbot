# OS chatbot
The goal of this project is to make a RAG and/or CAG chatbot specialized in answering questions from the curriculum for the DATA2500 Operating Systems subject at Oslo Metropolitan University. An important design criterion is that the chatbot should be able to run locally on university-owned hardware.

At the moment, vLLM + gpt-oss-20b has been chosen as the inference stack for the project. Having tested both vLLM and Ollama on the university's nVidia GPUs, we found the former to be far superior performance-wise. We have not done extensive comparisons of different language model candidates, but we consider gpt-oss-20b a strong enough option to move forward with for now. It could be compared against other alternatives in the future, once the other components have been ironed out more.

The current focus of the project is to make a working RAG chatbot, and in order to pick a suitable vector database and embedding model, we are currently in the process of conducting a small-scale quality comparison of a few candidates.
- Vector databases:
  - Qdrant
  - Weaviate
- Embedding models:
  - ltg/norbert3-base
  - NbAiLab/nb-sbert-base
  - intfloat/multilingual-e5-large
  - BAAI/bge-m3
  - Alibaba-NLP/gte-multilingual-base
During the ingestion step, knowledge is transformed into embeddings for each of the five models and then stored in both Qdrant and Weaviate, for a total of 10 configurations to be compared.

Other items being considered or worked in parallel can be found in TODO.md (some text in Norwegian).

### Architecture
The OS chatbot consists of a few main components:
- `/inference`: Inference model, currently vLLM (for optimal performance on nVidia GPU) with gpt-oss-20b weights.
- `/vectordb`: Docker compose file for setting up the vector databases used.
- `/ingestion`: Scripts for processing and ingesting knowledge into vector databases.
  - `scrape_course_pages.py`: If necessary, can be used to scrape HTML files from the official course site (os.cs.oslomet.no/os).
  - `preprocess_course_pages.py`: Takes HTML and TXT files from the knowledge directory and processes them into plaintext ready for ingestion. The outputs are saved both into a `knowledge_processed` directory for manual verification of results, and a `processed_chunks.jsonl` file for the ingestion step.
  - `ingest.py`: Ingests the preprocessed knowledge into 2 different vector databases using 5 different embedding models, for a total of 10 configurations.
- `/retrieval`: Backend server that receives user prompts, finds the closest embeddings in the chosen vector database and for the chosen embedding model, and passes the found knowledge to the LLM to augment the response generation.
- `/frontend`: Lightweight, but extensible Streamlit-based frontend for the chatbot.
- `/utils`: Config and other files that are used by multiple components (mainly retrieval and frontend).

### Instructions

The entire project is designed to be run from a single `compose.yaml` file, found in the root directory.
```bash
sudo docker compose up -d
```

Before first run, or if knowledge data has changed, the knowledge should be preprocessed and ingested:
```bash
# Ingest knowledge to vector db (only needed when knowledge has changed)
cd ingestion
python3 preprocess.py
python3 ingest.py
cd ..
```

### Alternate instructions (not recommended)

It may be possible to run the individual components manually with or without Docker, but this isn't actively being supported, so YMMV. The below instructions may be outdated and require tweaks to work with the latest version of the project.

Recommend running under Linux or WSL.
```bash
# Set up and run inference model
# Either use the Docker container:
cd inference
sudo docker compose up -d
# Or run outside a container:
cd inference
chmod +x inference.sh
./inference.sh
cd ..

# Set up vector databases
cd vectordb
sudo docker compose up -d
cd ..
# Or download and run Qdrant/Weaviate according to their instructions
# Weaviate should be on port 6444 rather than 8080 to avoid collisions

# Install dependencies in virtual environment
python3 -m venv .venv
source .venv/bin/activate
for dir in ingestion retrieval frontend; do
    pip install -r "$dir/requirements.txt"
done

# Run retrieval server
cd retrieval
uvicorn server:app --host 0.0.0.0 --port 8080
cd ..
# or use start.sh script in retrieval folder

# Run Streamlit frontend
streamlit run frontend/app.py
# or use start.sh script in frontend folder
```

(The following step is not necessary for the Pegasus server)

If running different components on different hosts, SSH tunneling may be necessary. For example, the LLM uses a lot of VRAM and may be run on its own host, or a third-party LLM (with an OpenAI-compatible API) may be substituted. To tunnel to an external LLM via SSH, do something like this:
```bash
ssh -L 8000:localhost:8000 user@example.com
```
Now, local port 8000 forwards to port 8000 on the remote server. The terminal must be kept open, so this is primarily suitable for development/testing.