import argparse
import glob
import json
import os
from transformers import pipeline

SUPPORTED_VIDEO_EXTS = [".mp4", ".mov", ".mkv", ".avi", ".webm"]


def ensure_dir(path: str):
    if path:
        os.makedirs(path, exist_ok=True)


def transcribe_video(video_path: str, asr, language: str = "no"):
    return asr(
        video_path,
        return_timestamps=True,
        generate_kwargs={
            "num_beams": 5,
            "task": "transcribe",
            "language": language,
        },
    )


def save_transcription(transcription, output_path: str):
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcription, f, ensure_ascii=False)


def get_video_files(input_folder: str):
    return [
        path
        for path in sorted(glob.glob(os.path.join(input_folder, "*")))
        if os.path.splitext(path)[1].lower() in SUPPORTED_VIDEO_EXTS
    ]


def transcribe_videos(
    input_folder: str,
    transcript_folder: str,
    asr,
    overwrite: bool = False,
    language: str = "no",
):
    ensure_dir(transcript_folder)

    video_files = get_video_files(input_folder)
    if not video_files:
        print(f"No supported video files found in {input_folder}.")
        return

    for video_file in video_files:
        base_filename = os.path.splitext(os.path.basename(video_file))[0]
        transcript_file = os.path.join(transcript_folder, f"{base_filename}.txt")

        if os.path.exists(transcript_file) and not overwrite:
            print(f"Skipping {video_file}, transcription already exists at {transcript_file}.")
            continue

        print(f"Transcribing {video_file}")
        transcription = transcribe_video(video_file, asr, language=language)
        save_transcription(transcription, transcript_file)
        print(f"Transcription saved to: {transcript_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe video files using ASR model.")
    parser.add_argument("input_folder", help="Path to the input directory containing video files")
    parser.add_argument(
        "--output-folder",
        default="./local_output",
        help="Directory where transcript text files should be saved",
    )
    parser.add_argument(
        "--model",
        default="NbAiLab/nb-whisper-large",
        help="Hugging Face ASR model name",
    )
    parser.add_argument(
        "--language",
        default="no",
        help="Language code for transcription",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-transcribe existing files",
    )
    args = parser.parse_args()

    asr = pipeline("automatic-speech-recognition", args.model)
    transcribe_videos(args.input_folder, args.output_folder, asr, overwrite=args.overwrite, language=args.language)

