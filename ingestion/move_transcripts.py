import os
import re
import shutil
from urllib.parse import urlparse

ROOT_DIR = "knowledge"
VIDEO_BASE_DIR = os.path.join("knowledge", "os", "Forelesning", "video")

# Regex to extract href attributes
HREF_REGEX = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


def find_video_urls():
    video_urls = set()

    for root, _, files in os.walk(ROOT_DIR):
        for filename in files:
            if filename.lower().endswith(".html"):
                path = os.path.join(root, filename)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for match in HREF_REGEX.findall(content):
                    if "/Forelesning/video/" in match:
                        video_urls.add(match)

    return video_urls


def extract_video_paths(video_urls):
    """
    Extract paths like: 2021/linux1a.mp4
    """
    video_paths = []

    for url in video_urls:
        parsed = urlparse(url)
        path = parsed.path

        marker = "/Forelesning/video/"
        if marker in path:
            relative = path.split(marker, 1)[1]
            video_paths.append(relative)

    return video_paths


def move_txt_files(video_paths):
    for video_path in video_paths:
        video_dir, video_file = os.path.split(video_path)
        base_name, _ = os.path.splitext(video_file)
        txt_name = base_name + ".txt"

        src_txt = os.path.join(VIDEO_BASE_DIR, txt_name)
        dest_dir = os.path.join(VIDEO_BASE_DIR, video_dir)
        dest_txt = os.path.join(dest_dir, txt_name)

        if not os.path.exists(src_txt):
            continue  # No matching txt file

        # Already in correct location
        if os.path.exists(dest_txt):
            continue

        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(src_txt, dest_txt)
        print(f"Moved {txt_name} -> {dest_dir}")


def main():
    video_urls = find_video_urls()
    video_paths = extract_video_paths(video_urls)
    move_txt_files(video_paths)


if __name__ == "__main__":
    main()
