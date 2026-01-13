#!/bin/bash

python3 tests.py --message_file test_prompt.txt --embedding_model "Alibaba-NLP/gte-multilingual-base" --vector_db qdrant --endpoint "/chat/stream" --num_requests 24 --parallel
python3 tests.py --message_file test_prompt.txt --embedding_model "intfloat/multilingual-e5-large" --vector_db qdrant --endpoint "/chat/stream" --num_requests 24 --parallel
python3 tests.py --message_file test_prompt.txt --embedding_model "BAAI/bge-m3" --vector_db qdrant --endpoint "/chat/stream" --num_requests 24 --parallel