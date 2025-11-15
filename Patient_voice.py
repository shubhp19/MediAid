# if you don't use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

# Step1: Setup Audio recorder (ffmpeg & portaudio)
# Install required libraries if not done already:
# pip install SpeechRecognition pydub portaudio pyaudio

import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("ERROR: GROQ_API_KEY is missing! Check your .env file.")

stt_model = "whisper-large-v3"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Simplified function to record audio from the microphone and save it as an MP3 file.

    Args:
    file_path (str): Path to save the recorded audio file.
    timeout (int): Maximum time to wait for a phrase to start (in seconds).
    phrase_time_limit (int): Maximum time for the phrase to be recorded (in seconds).
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")

            # Record the audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")

            # Convert the recorded audio to an MP3 file
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")

            logging.info(f"Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

audio_filepath = "patient_voice_test_for_patient.mp3"
# Uncomment to test recording
# record_audio(file_path=audio_filepath)

# Step2: Setup Speech to Text (STT) model for transcription
# Install the `groq` library if not done already
# pip install groq

from groq import Groq

# Ensure you have set the environment variable GROQ_API_KEY correctly
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
stt_model = "whisper-large-v3"

def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY):
    """
    Transcribe speech from an audio file using the Groq API.

    Args:
    stt_model (str): Model name to use for transcription.
    audio_filepath (str): Path to the audio file to be transcribed.
    GROQ_API_KEY (str): API key for Groq service.

    Returns:
    str: Transcribed text from the audio file.
    """
    client = Groq(api_key=GROQ_API_KEY)

    try:
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )

        return transcription.text
    except Exception as e:
        logging.error(f"An error occurred during transcription: {e}")
        return None

# Example usage (Uncomment to test):
# transcription = transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY)
# print(transcription)