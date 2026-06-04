import argparse
import os
import glob
from transformers import pipeline

def transcribe_audio(audio_path):
    # Transcribe the given audio file
    transcription = asr(
        audio_path,
        return_timestamps=True,
        generate_kwargs={
            'num_beams': 5,
            'task': 'transcribe',
            'language': 'no'
        }
    )
    return transcription

def process_audios(input_folder):
    # Iterate over all .wav files in the input folder
    for audio_file in glob.glob(os.path.join(input_folder, "*.wav")):
        # Get the base filename without extension
        base_filename = os.path.splitext(os.path.basename(audio_file))[0]

        # Call the transcription function
        transcription = transcribe_audio(audio_file)

        # Define the output .txt file path
        output_file = os.path.join('./local_output', f"{base_filename}.txt")

	# Check if the transcription file already exists
        if os.path.exists(output_file):
            print(f"Skipping {audio_file}, transcription already exists at {output_file}.")
            continue

        # Save the transcription to the .txt file
        with open(output_file, 'w') as f:
            f.write(str(transcription))  # Adjust depending on your transcription format

        print(f"Transcription saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio files using ASR model.')
    parser.add_argument('input_folder', help='Path to the input directory containing audio files')
    args = parser.parse_args()

    # Load the model for automatic speech recognition
    asr = pipeline("automatic-speech-recognition", "NbAiLab/nb-whisper-large")

    process_audios(args.input_folder)

