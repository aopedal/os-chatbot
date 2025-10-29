import os
from openai import OpenAI

# Initialize client to your local LLM server
client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

# Directory containing your processed knowledge files
knowledge_dir = "./ingestion/knowledge_processed/test"

# Recursively collect all .txt files under knowledge_dir
knowledge_texts = []
for root, _, files in os.walk(knowledge_dir):
    for file in files:
        if file.endswith(".txt"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                knowledge_texts.append(f.read())

# Combine all knowledge into one big system prompt
# (You may want to truncate or summarize if very large)
knowledge_context = "\n\n".join(knowledge_texts)

# Compose the message list
messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. "
            "Use the following background knowledge to assist your reasoning:\n\n"
            f"{knowledge_context}"
        ),
    },
    {"role": "user", "content": "Summarize the plot of Dune."},
]

# Send the request
response = client.chat.completions.create(
    model="/app/models/gpt-oss-20b",
    messages=messages,
)

# Print response and token usage
print(response.choices[0].message.content)
print(response.usage)
