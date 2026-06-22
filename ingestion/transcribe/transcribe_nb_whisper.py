"""Video transcription module using Hugging Face Transformers ASR model.

This module provides functionality to transcribe video files directly using the
Norwegian Whisper model (NbAiLab/nb-whisper-large). It supports multiple video
formats and saves transcripts as JSON files with timestamp information.
"""

import argparse
import glob
import json
import os
import shutil
from transformers import pipeline

SUPPORTED_AUDIO_EXTS = [".mp3", ".wav", ".flac"]


def ensure_dir(path: str):
    """Create directory if it doesn't exist.
    
    Args:
        path: Directory path to create. If empty, does nothing.
    """
    if path:
        os.makedirs(path, exist_ok=True)


def transcribe_video(video_path: str, asr, language: str = "no"):
    """Transcribe a single video file.
    
    Args:
        video_path: Path to video file to transcribe.
        asr: Hugging Face ASR pipeline object.
        language: ISO 639-1 language code (default: "no" for Norwegian).
        
    Returns:
        dict: Transcription result with chunks and metadata.
    """
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
    """Save transcription to JSON file.
    
    Args:
        transcription: Transcription dict from ASR model.
        output_path: Path where JSON file will be written.
    """
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcription, f, ensure_ascii=False)


def get_audio_files(input_folder: str):
    """Get sorted list of all supported audio files in a folder.
    
    Supported formats: .mp3, .wav, .flac
    
    Args:
        input_folder: Path to folder containing audio files.
        
    Returns:
        list: Sorted absolute paths to audio files.
    """
    return [
        path
        for path in sorted(glob.glob(os.path.join(input_folder, "*")))
        if os.path.splitext(path)[1].lower() in SUPPORTED_AUDIO_EXTS
    ]


def transcribe_videos(
    input_folder: str,
    transcript_folder: str,
    asr,
    overwrite: bool = False,
    language: str = "no",
):
    """Batch transcribe all audio files in a folder.
    
    Skips videos that already have transcripts unless overwrite=True.
    Saves each transcript as {video_name}.txt in transcript_folder.
    
    Args:
        input_folder: Path to folder containing video files.
        transcript_folder: Where to save transcript .txt files.
        asr: Hugging Face ASR pipeline object.
        overwrite: If True, re-transcribe even if output exists (default: False).
        language: Language code for transcription (default: "no" for Norwegian).
    """

    ensure_dir(transcript_folder)

    audio_files = get_audio_files(input_folder)
    if not audio_files:
        print(f"No supported audio files found in {input_folder}.")
        return

    for audio_file in audio_files:
        base_filename = os.path.splitext(os.path.basename(audio_file))[0]
        transcript_file = os.path.join(transcript_folder, f"{base_filename}.txt")

        if os.path.exists(transcript_file) and not overwrite:
            print(f"Skipping {audio_file}, transcription already exists at {transcript_file}.")
            continue

        print(f"Transcribing {audio_file}")
        transcription = transcribe_video(audio_file, asr, language=language)
        save_transcription(transcription, transcript_file)
        print(f"Transcription saved to: {transcript_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio/video files using ASR model.")
    parser.add_argument("input_folder", help="Path to the input directory containing audio/video files")
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

