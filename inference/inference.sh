#!/bin/bash
# Use this script to install and run the inference model if you don't want to use the Docker container.

# If you don't have micromamba, set it up first:
# curl -Ls https://micro.mamba.pm/install.sh | bash
# source ~/.bashrc

micromamba create -n vllm python=3.12
micromamba activate vllm
pip install -r requirements.txt
hf download openai/gpt-oss-20b --local-dir models/gpt-oss-20b
python3 -m vllm.entrypoints.openai.api_server \
      --host 0.0.0.0 \
      --port 8000 \
      --model models/gpt-oss-20b \
      --served-model-name gpt-oss-20b \
      --max_model_len 131072 \
      --gpu-memory-utilization 0.75