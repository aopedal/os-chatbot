"""Batch convert video files to MP3 audio for efficient transcription.

This script takes all video files from an input folder and converts them to MP3,
storing the audio files in a temporary subfolder. This pre-processing step reduces
file size and ensures consistent audio format for the ASR pipeline.
"""

import argparse
import os
import subprocess
import glob

SUPPORTED_VIDEO_EXTS = [".mp4", ".mov", ".mkv", ".avi", ".webm", ".flv", ".wmv"]
DEFAULT_AUDIO_BITRATE = "128k"


def convert_video_to_mp3(video_path: str, output_path: str, bitrate: str = DEFAULT_AUDIO_BITRATE):
    """Convert a video file to MP3 audio.
    
    Args:
        video_path: Path to input video file.
        output_path: Path where MP3 file will be written.
        bitrate: Audio bitrate (default: "128k").
        
    Raises:
        subprocess.CalledProcessError: If ffmpeg conversion fails.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vn",  # no video
        "-acodec", "libmp3lame",
        "-ab", bitrate,
        "-ar", "16000",  # resample to 16kHz for ASR
        output_path,
    ]
    
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def get_video_files(input_folder: str):
    """Get all video files from a folder.
    
    Args:
        input_folder: Path to folder containing video files.
        
    Returns:
        list: Sorted absolute paths to video files.
    """
    return [
        path
        for path in sorted(glob.glob(os.path.join(input_folder, "*")))
        if os.path.splitext(path)[1].lower() in SUPPORTED_VIDEO_EXTS
    ]


def convert_folder(input_folder: str, output_folder: str, bitrate: str = DEFAULT_AUDIO_BITRATE):
    """Batch convert all videos in a folder to MP3.
    
    Args:
        input_folder: Path to folder containing video files.
        output_folder: Path where MP3 files will be stored.
        bitrate: Audio bitrate for MP3 (default: "128k").
    """
    video_files = get_video_files(input_folder)
    
    if not video_files:
        print(f"No supported video files found in {input_folder}.")
        return
    
    print(f"Converting {len(video_files)} video(s) to MP3...")
    
    for i, video_file in enumerate(video_files, 1):
        base_filename = os.path.splitext(os.path.basename(video_file))[0]
        output_file = os.path.join(output_folder, f"{base_filename}.mp3")
        
        print(f"[{i}/{len(video_files)}] Converting {os.path.basename(video_file)} -> {base_filename}.mp3")
        
        try:
            convert_video_to_mp3(video_file, output_file, bitrate=bitrate)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to convert {video_file}: {e}")
            continue
    
    print(f"✅ Conversion complete. MP3 files stored in {output_folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert video files to MP3 audio for transcription.")
    parser.add_argument(
        "input_folder",
        help="Path to folder containing video files",
    )
    parser.add_argument(
        "--output-folder",
        default=None,
        help="Path where MP3 files will be stored (default: input_folder/audio_temp)",
    )
    parser.add_argument(
        "--bitrate",
        default=DEFAULT_AUDIO_BITRATE,
        help=f"MP3 bitrate (default: {DEFAULT_AUDIO_BITRATE})",
    )
    args = parser.parse_args()
    
    output_folder = args.output_folder or os.path.join(args.input_folder, "audio_temp")
    convert_folder(args.input_folder, output_folder, bitrate=args.bitrate)
