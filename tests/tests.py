import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
import httpx
import utils.config as app_config
import json
import argparse
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Config
default_inference_model = "gpt-oss-20b" 

# Function to send a POST request
def send_request(user_id, message, inference_model, embedding_model, vector_db, endpoint):
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

    return response_string

# Main function
def main():
    # Argument parser for command line arguments
    parser = argparse.ArgumentParser(description='Test locally run LLM')
    parser.add_argument('--message_file', type=str, required=True, help='Path to the message text file')
    parser.add_argument('--inference_model', type=str, default=default_inference_model, help='Inference model name')
    parser.add_argument('--embedding_model', type=str, required=True, help='Embedding model name')
    parser.add_argument('--vector_db', type=str, required=True, help='Vector database name')
    parser.add_argument('--num_requests', type=int, default=1, help='Number of requests to send (default: 1)')
    parser.add_argument('--delay', type=float, default=0, help='Delay between requests in seconds (default: 0)')
    parser.add_argument('--endpoint', type=str, required=True, help='API endpoint URL')
    parser.add_argument('--parallel', action='store_true', help='Send requests in parallel')

    args = parser.parse_args()

    # Read message from file
    with open(args.message_file, 'r') as file:
        message = file.read().strip()

    # User ID placeholder (you can assign it dynamically)
    user_id = "sample_user_id"  # Replace with appropriate user ID from session state

    results = []

    # Send requests
    start_time = time.time()

    if args.parallel:
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(send_request, i, message, args.inference_model, args.embedding_model, args.vector_db, args.endpoint): i for i in range(args.num_requests)
            }

            # Print statement for each request submitted
            print(f"Sent {args.num_requests} requests in parallel.")

            for future in as_completed(futures):
                response = future.result()
                results.append(response)

                # Print statement for each response received
                print(f"Response received for request ID: {futures[future]}")

    else:
        for i in range(args.num_requests):
            response = send_request(i, message, args.inference_model, args.embedding_model, args.vector_db, args.endpoint)
            results.append(response)

            # Delay between requests
            if i < args.num_requests - 1:
                time.sleep(args.delay)

    total_duration = time.time() - start_time

    # Prepare the output file name
    time_stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    os.makedirs('test_results', exist_ok=True)
    output_filename = f'test_{args.embedding_model}_{args.inference_model}_{time_stamp}.txt'
    output_filename = output_filename.replace('/', '-')
    output_filename = os.path.join('test_results', output_filename)
    
    # Write results to output file
    with open(output_filename, 'w') as output_file:
        output_file.write(f"Message Prompt: {message}\n")
        output_file.write(f"Number of Requests: {args.num_requests}\n")
        output_file.write(f"Delay: {args.delay} seconds\n")
        output_file.write(f"Total Time: {total_duration:.2f} seconds\n")
        output_file.write(f"Responses: \n\n{'\n\n--------------------\n\n'.join(results)}\n")
        
    print(f"Results written to {output_filename}")

if __name__ == "__main__":
    main()
