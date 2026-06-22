"""End-to-end pipeline for video transcription and processing.

This module orchestrates a complete pipeline that:
1. Loads a video folder
2. Transcribes all video files using the Norwegian Whisper ASR model
3. Processes transcripts into tokenized chunks
4. Outputs a JSONL file ready for embedding and retrieval
"""

import argparse
import os

from transformers import pipeline
from .process_video_transcripts import process_folder
from .transcribe_nb_whisper import transcribe_videos


def main():
    """Execute the end-to-end video transcription and processing pipeline."""
    parser = argparse.ArgumentParser(
        description="Transcribe videos and process transcripts into a JSONL chunk file."
    )
    parser.add_argument("input_folder", help="Path to the folder containing video files")
    parser.add_argument(
        "--transcript-folder",
        default="./local_output",
        help="Folder for saved transcript text files",
    )
    parser.add_argument(
        "--output-file",
        default="./chunks_video_transcripts.jsonl",
        help="Path where processed transcript chunks will be written",
    )
    parser.add_argument(
        "--model",
        default="NbAiLab/nb-whisper-large",
        help="Hugging Face ASR model to use for transcription",
    )
    parser.add_argument(
        "--language",
        default="no",
        help="Language code for transcription",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-transcribe videos even if transcripts already exist",
    )
    args = parser.parse_args()

    os.makedirs(args.transcript_folder, exist_ok=True)

    print("Loading ASR model. This may take a moment...")
    asr = pipeline("automatic-speech-recognition", args.model)

    print(f"Starting transcription pipeline for videos in {args.input_folder}")
    transcribe_videos(
        args.input_folder,
        args.transcript_folder,
        asr,
        overwrite=args.overwrite,
        language=args.language,
    )

    print(f"Processing transcript files from {args.transcript_folder}")
    process_folder(args.transcript_folder, args.output_file)
    print(f"Pipeline complete. Processed transcripts written to {args.output_file}")


if __name__ == "__main__":
    main()
