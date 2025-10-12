import requests
import os

def download_series(base_url: str, start: int = 1, output_dir: str = "downloads"):
    """Download sequentially numbered HTML files until one is not found."""
    os.makedirs(output_dir, exist_ok=True)
    i = start

    while True:
        url = f"{base_url}{i}.html"
        filename = os.path.join(output_dir, f"node{i}.html")

        print(f"Trying {url} …")

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as e:
            print(f"⚠️  Request failed: {e}")
            break

        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ Saved {filename}")
            i += 1
        else:
            print(f"❌ Got HTTP {response.status_code} — stopping.")
            break

    print(f"Done. Downloaded {i - start} files from {base_url}")


if __name__ == "__main__":
    # Series 1: Operating Systems lectures
    download_series("https://os.cs.oslomet.no/os/Forelesning/os/node", start=2, output_dir="knowledge/os")

    # Series 2: Linux lectures
    download_series("https://os.cs.oslomet.no/os/Forelesning/linux/node", start=2, output_dir="knowledge/linux")
