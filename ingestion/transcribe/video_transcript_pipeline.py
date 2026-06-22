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
from convert_videos_to_audio import convert_folder
from process_video_transcripts import process_folder
from transcribe_nb_whisper import transcribe_videos


def main():
    """Execute the end-to-end video transcription and processing pipeline.
    
    Orchestrates three steps:
    1. Convert video files to MP3 audio
    2. Transcribe MP3s to text
    3. Process transcripts into chunked JSONL
    """
    parser = argparse.ArgumentParser(
        description="Convert videos to audio, transcribe, and process into JSONL chunks."
    )
    parser.add_argument(
        "input_folder",
        help="Path to the folder containing video files"
    )
    parser.add_argument(
        "--audio-folder",
        default=None,
        help="Folder where MP3 files will be stored (default: input_folder/audio_temp)",
    )
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
        "--audio-bitrate",
        default="128k",
        help="MP3 bitrate for audio conversion (default: 128k)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-convert, re-transcribe, and re-process even if outputs exist",
    )
    args = parser.parse_args()

    audio_folder = args.audio_folder or os.path.join(args.input_folder, "audio_temp")

    os.makedirs(args.transcript_folder, exist_ok=True)
    os.makedirs(audio_folder, exist_ok=True)

    print(f"\n📹 Step 1: Converting videos to MP3...")
    convert_folder(args.input_folder, audio_folder, bitrate=args.audio_bitrate)

    print(f"\n🎙️ Step 2: Loading ASR model and transcribing...")
    asr = pipeline("automatic-speech-recognition", args.model)

    print(f"Starting transcription for audio files in {audio_folder}")
    transcribe_videos(
        audio_folder,
        args.transcript_folder,
        asr,
        overwrite=args.overwrite,
        language=args.language,
    )

    print(f"\n📊 Step 3: Processing transcripts into chunks...")
    process_folder(args.transcript_folder, args.output_file)
    print(f"\n✅ Pipeline complete. Chunks written to {args.output_file}")


if __name__ == "__main__":
    main()
