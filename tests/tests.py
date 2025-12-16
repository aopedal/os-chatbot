import requests
import json
import argparse
import time
from datetime import datetime
import os

# Config
default_inference_model = "gpt-4o" # Feil 

# Function to send a POST request
def send_request(user_id, message, inference_model, embedding_model, vector_db, endpoint):
    payload = {
        "user_id": user_id,
        "message": message,
        "inference_model": inference_model,
        "embedding_model": embedding_model,
        "vector_db": vector_db,
    }

    response = requests.post(endpoint, json=payload)
    return response.json()

# Main function
def main():
    # Argument parser for command line arguments
    parser = argparse.ArgumentParser(description='Test locally run LLM')
    parser.add_argument('--message_file', type=str, required=True, help='Path to the message text file')
    parser.add_argument('--inference_model', type=str, default=default_inference_model, help='Inference model name')
    parser.add_argument('--embedding_model', type=str, required=True, help='Embedding model name')
    parser.add_argument('--vector_db', type=str, required=True, help='Vector database name')
    parser.add_argument('--num_requests', type=int, default=1, help='Number of requests to send (default: 1)')
    parser.add_argument('--delay', type=float, default=0, help='Delay between tests in seconds (default: 0)')
    parser.add_argument('--endpoint', type=str, required=True, help='API endpoint URL')

    args = parser.parse_args()

    # Read message from file
    with open(args.message_file, 'r') as file:
        message = file.read().strip()

    # User ID placeholder (you can assign it dynamically)
    user_id = "sample_user_id"  # Replace with appropriate user ID from session state

    results = []

    # Send requests
    start_time = time.time()
    for i in range(args.num_requests):
        response = send_request(user_id, message, args.inference_model, args.embedding_model, args.vector_db, args.endpoint)
        results.append(response)

        # Delay between requests
        if i < args.num_requests - 1:
            time.sleep(args.delay)

    total_duration = time.time() - start_time

    # Prepare the output file name
    time_stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_filename = f'test_{args.embedding_model}_{args.embedding_model}_{args.inference_model}_{time_stamp}.txt'
    
    # Write results to output file
    with open(output_filename, 'w') as output_file:
        output_file.write(f"Message Prompt: {message}\n")
        output_file.write(f"Responses: {json.dumps(results, indent=2)}\n")
        output_file.write(f"Number of Requests: {args.num_requests}\n")
        output_file.write(f"Delay: {args.delay} seconds\n")
        output_file.write(f"Total Time: {total_duration:.2f} seconds\n")
    
    print(f"Results written to {output_filename}")

if __name__ == "__main__":
    main()
