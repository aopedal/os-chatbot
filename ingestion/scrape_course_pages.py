import requests
import os
from urllib.parse import urlparse

BASE_URL = 'https://os.cs.oslomet.no/ose/Forelesning'
CATEGORIES = ['os', 'linux']
START_NODE = 2
KNOWLEDGE_DIR = "knowledge"

def download_series(category: str):
    i = START_NODE

    while True:
        url = f"{BASE_URL}/{category}/node{i}.html"
        print(f"Trying {url} …")

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            break

        if response.status_code != 200:
            print(f"Got HTTP {response.status_code}. Stopping.")
            break
        
        save_path = os.path.join(KNOWLEDGE_DIR, category, f"node{i}.html")

        # Make sure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the file
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"Saved {save_path}")
        i += 1

    print(f"Done. Downloaded {i - START_NODE} files from {BASE_URL}/{category}")


if __name__ == "__main__":
    for category in CATEGORIES:
        download_series(category)