"""Transcribe package for video-to-text processing and chunking.

This package provides a unified interface for:
- Transcribing video files to text using ASR
- Processing raw transcripts into tokenized chunks
- Running the complete end-to-end pipeline
"""

from .transcribe_nb_whisper import (
    ensure_dir,
    transcribe_video,
    save_transcription,
    get_video_files,
    transcribe_videos,
)

__all__ = [
    "ensure_dir",
    "transcribe_video",
    "save_transcription",
    "get_video_files",
    "transcribe_videos",
]
