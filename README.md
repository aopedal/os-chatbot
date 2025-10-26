# OS chatbot
Shared repository for various components related to a chatbot for the operating systems curriculum.

### Instructions

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

# Set up local image for qdrant vector db
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
# Or run qdrant directly if Docker is not available

# Install dependencies in virtual environment
python3 -m venv .venv
source .venv/bin/activate
for dir in ingestion retrieval frontend; do
    pip install -r "$dir/requirements.txt"
done

# Ingest knowledge to vector db
cd ingestion
python3 ingest_to_qdrant.py
cd ..

# Run retrieval server
cd retrieval
uvicorn server:app --host 0.0.0.0 --port 8080

# Run Streamlit frontend
streamlit run frontend/app.py
```

(The following step is not necessary on Pegasus LLM)
This expects an OpenAI API-compatible LLM to be running locally on port 8000. To tunnel to an external LLM via SSH, do something like this:
```bash
ssh -L 8000:localhost:8000 alope0420@gpu5.cs.oslomet.no
```
Now, local port 8000 forwards to port 8000 on the remote server. The terminal must be kept open.