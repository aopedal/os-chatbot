import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
import httpx
import utils.config as app_config
import json
import argparse
import time
from datetime import datetime

# Config
default_inference_model = "gpt-oss-20b"

# Function to send a POST request
def send_request(user_id, message, inference_model, embedding_model, vector_db, endpoint):

    start_request_time = time.time()

    print(f"Sending request for user_id: {user_id}")
    response_string = ""

    with httpx.stream(
            "POST",
            f"{app_config.RETRIEVAL_URL}{endpoint}",
            json={
                "user_id": str(user_id),
                "message": message,
                "inference_model": inference_model,
                "embedding_model": embedding_model,
                "vector_db": vector_db,
            },
            timeout=None,
        ) as response:
            for line in response.iter_lines():
                if not line:
                    continue

                chunk = json.loads(line)

                if chunk["type"] == "delta":
                    response_string += chunk["text"]

                elif chunk["type"] == "done":
                    break

    end_request_time = time.time()
    response_time = end_request_time - start_request_time

    return response_string, response_time

# Main function
def main():
    parser = argparse.ArgumentParser(description='Test locally run LLM - Sequential')
    parser.add_argument('--message_file', type=str, required=True, help='Path to the message text file (one prompt per line)')
    parser.add_argument('--inference_model', type=str, default=default_inference_model, help='Inference model name')
    parser.add_argument('--embedding_model', type=str, required=True, help='Embedding model name')
    parser.add_argument('--vector_db', type=str, required=True, help='Vector database name')
    parser.add_argument('--endpoint', type=str, required=True, help='API endpoint URL')

    args = parser.parse_args()

    # Read prompts from file — each line is a separate prompt
    with open(args.message_file, 'r') as file:
        prompts = [line.strip() for line in file.readlines() if line.strip()]

    num_prompts = len(prompts)
    print(f"Loaded {num_prompts} prompts from {args.message_file}")

    user_id = "sample_user_id"

    results = []
    response_times = []

    # Send all prompts sequentially — one at a time
    start_time = time.time()

    for i, prompt in enumerate(prompts):
        print(f"\n[{i+1}/{num_prompts}] Sending: \"{prompt[:50]}...\"")
        response, response_time = send_request(user_id, prompt, args.inference_model, args.embedding_model, args.vector_db, args.endpoint)
        results.append(response)
        response_times.append(response_time)
        print(f"[{i+1}/{num_prompts}] Done in {response_time:.2f}s")

    total_duration = time.time() - start_time

    # Write results to output file
    time_stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    os.makedirs('test_results', exist_ok=True)
    output_filename = os.path.join('test_results', f'test_sequential_{time_stamp}.txt')

    with open(output_filename, 'w') as output_file:
        output_file.write(f"Mode: Sequential\n")
        output_file.write(f"Inference Model: {args.inference_model}\n")
        output_file.write(f"Embedding Model: {args.embedding_model}\n")
        output_file.write(f"Vector DB: {args.vector_db}\n")
        output_file.write(f"Number of Prompts: {num_prompts}\n")
        output_file.write(f"Total Time: {total_duration:.2f} seconds\n")
        output_file.write(f"Average Time per Prompt: {total_duration/num_prompts:.2f} seconds\n\n")
        output_file.write("Response Times (in seconds):\n")
        for i, response_time in enumerate(response_times):
            output_file.write(f"Prompt {i}: {response_time:.2f} seconds\n")
        output_file.write("\n")

        for i, (prompt, response) in enumerate(zip(prompts, results)):
            output_file.write(f"\n{'='*60}\n")
            output_file.write(f"Prompt {i}: {prompt}\n")
            output_file.write(f"Response Time: {response_times[i]:.2f} seconds\n")
            output_file.write(f"{'='*60}\n\n")
            output_file.write(f"{response}\n")

    print(f"\nTotal: {total_duration:.2f}s | Avg: {total_duration/num_prompts:.2f}s per prompt")
    print(f"Results written to {output_filename}")

if __name__ == "__main__":
    main()
