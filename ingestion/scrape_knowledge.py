import requests
import os
from urllib.parse import urlparse

BASE_URL = 'https://os.cs.oslomet.no/os/Forelesning'
CATEGORIES = ['os', 'linux']
START_NODE = 2
KNOWLEDGE_DIR = "knowledge"

def download_series(base_url: str):
    i = START_NODE

    while True:
        url = f"{base_url}/node{i}.html"
        print(f"Trying {url} …")

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            break

        if response.status_code == 200:
            parsed_url = urlparse(url)
            path = parsed_url.path.lstrip("/")
            save_path = os.path.join("KNOWLEDGE_DIR", path)

            # Make sure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the file
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"Saved {save_path}")
            i += 1
        else:
            print(f"Got HTTP {response.status_code}. Stopping.")
            break

    print(f"Done. Downloaded {i - START_NODE} files from {base_url}")


if __name__ == "__main__":
    for category in CATEGORIES:
        download_series(f"{BASE_URL}/{category}")