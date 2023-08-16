#!/home/magic/Projects/magic-mirror-frontend/porcupine/.venv/bin/python

import pvporcupine       # Porcupine wake word detection
import pyaudio           # Audio recording and stream management
import wave              # WAV file reading and writing
import numpy as np       # Audio data array manipulation
import time              # Silence duration calculation
import whisper           # Whisper ASR model for transcription
from pydub import AudioSegment   # Audio file format conversion (WAV to MP3)
import requests          # Making an HTTP request to the LLM API
import subprocess       # mimic3 for text-to-speech conversion and playing the audio response



# Constants
SILENCE_THRESHOLD = 1000 # You may need to adjust this threshold
SILENCE_DURATION = 4 # Seconds of silence to stop recording


def initialize():
    """
    Initialize default values for recording status, silence start time, and audio frames list.
    """
    return False, None, []


def create_porcupine():
    """
    Create and return a Porcupine wake word detection object
    """
    return pvporcupine.create(
        access_key='2/2V5+k37vGePDtulTsGJYDQTgk8F/oUx5dLDNlfju+NOcRsIHCGqw==',
        keyword_paths=['/Users/larsnet/magic-mirror-frontend/porcupine/Keywords/mac/porcupine_mac.ppn']
    )


def setup_pyaudio(porcupine):
    """
    Setup the PyAudio stream for audio recording.
    
    Args:
        porcupine (object): Initialized Porcupine object.
        
    Returns:
        tuple: Contains the initialized PyAudio engine and its audio stream.
    """
    sample_rate = 16000  # Sample rate for audio stream.
    frame_length = 512  # Frame length for audio stream.
    
    audio_engine = pyaudio.PyAudio()
    stream = audio_engine.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length # This sets the frames_per_buffer to 512, matching Porcupine's expectation
    )
    return audio_engine, stream


def load_whisper_model():
    """
    Load the Whisper ASR model for transcription.
    """
    return whisper.load_model("tiny")


def get_next_audio_frame(stream, porcupine):
    """
    Capture the next audio frame from the PyAudio stream.
    
    Args:
        stream (object): Active PyAudio stream.
        porcupine (object): Initialized Porcupine object.
        
    Returns:
        ndarray: Array containing audio data.
    """
    audio_buffer = stream.read(porcupine.frame_length, exception_on_overflow=False)
    return np.frombuffer(audio_buffer, dtype=np.int16)


def save_recording_as_wav(audio_frames, audio_engine, sample_rate=16000):
    """
    Save recorded audio frames as a WAV file.
    
    Args:
        audio_frames (list): List of recorded audio frames.
        audio_engine (object): PyAudio engine.
        sample_rate (int): Sample rate for the recording. Default is 16000.
    """
    wav_path = 'recording.wav'
    with wave.open(wav_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio_engine.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(audio_frames))
    return wav_path


def convert_wav_to_mp3(wav_path):
    """
    Convert a WAV file to MP3 format using pydub.
    """
    audio = AudioSegment.from_wav(wav_path)
    mp3_path = 'YOUR_MP3_PATH'
    audio.export(mp3_path, format='mp3')
    return mp3_path


def transcribe_with_whisper(mp3_path, whisper_model):
    """
    Transcribe an MP3 file using the Whisper ASR model.
    
    Args:
        mp3_path (str): Path to the MP3 file to be transcribed.
        whisper_model (object): Initialized Whisper model.
        
    Returns:
        str: Transcribed text.
    """
    result = whisper_model.transcribe(mp3_path)
    transcription = result["text"]
    with open('YOUR_TRANSCRIPT_PATH', 'w') as file:
        file.write(transcription)
    return transcription


def get_response_from_api(transcription):
    """
    Get a response from the LLM API using the provided transcription.
    
    Args:
        transcription (str): Transcribed text.
        
    Returns:
        str: Response text from the API.
    """
    HOST_IP = "127.0.0.1"
    PORT = 8000
    payload = {'user_input': transcription}
    r = requests.get(f'http://{HOST_IP}:{PORT}/chatbot', params=payload)
    data = r.json()
    return data['chatbot_response']['text']


def text_to_speech_mimic(text):
    """
    Convert text to speech using the mimic3 tool and play the generated audio response.
    """
    cmd = ["mimic", "-t", text, "-o", "response.wav"]
    subprocess.run(cmd)
    subprocess.run(["aplay", "response.wav"])


def main_loop(porcupine, audio_engine, stream, whisper_model):
    """
    Main loop to listen for the wake word, record audio, and process user input.
    
    Args:
        porcupine (object): Initialized Porcupine object for wake word detection.
        audio_engine (object): PyAudio engine.
        stream (object): Active PyAudio stream.
        whisper_model (object): Initialized Whisper ASR model.
    """
    recording, silence_start_time, audio_frames = initialize()

    while True:
        audio_frame = get_next_audio_frame(stream, porcupine)
        keyword_index = porcupine.process(audio_frame)
  
        if keyword_index == 0:
            print("Wake word detected!")
            recording = True
            audio_frames = []  # Reset audio frames

        if recording:
            audio_frames.append(audio_frame)
            audio_data = np.frombuffer(audio_frame, dtype=np.int16)
      
            # Check for silence
            if np.abs(audio_data).mean() < SILENCE_THRESHOLD:
                if silence_start_time is None:
                    silence_start_time = time.time()
                elif time.time() - silence_start_time > SILENCE_DURATION:
                    print("Silence detected, stopping recording...")
                    recording = False
              
                    wav_path = save_recording_as_wav(audio_frames, audio_engine)
                    mp3_path = convert_wav_to_mp3(wav_path)
                    print(f"Saved recording as {mp3_path}")

                    transcription = transcribe_with_whisper(mp3_path, whisper_model)
                    response_string = get_response_from_api(transcription)
                    print(response_string)

                    text_to_speech_mimic(response_string)
            else:
                silence_start_time = None
        
        if not recording:
            print("Ready for the next command...")  
            continue 

def cleanup(porcupine, stream, audio_engine):
    """
    Clean up resources and close streams.
    
    Args:
        porcupine (object): Initialized Porcupine object.
        stream (object): Active PyAudio stream.
        audio_engine (object): PyAudio engine.
    """
    porcupine.delete()
    stream.stop_stream()
    stream.close()
    audio_engine.terminate()


if __name__ == '__main__':
    porcupine = create_porcupine()
    audio_engine, stream = setup_pyaudio(porcupine)
    whisper_model = load_whisper_model()
    
    try:
        main_loop(porcupine, audio_engine, stream, whisper_model)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up...")
    finally:
        cleanup(porcupine, stream, audio_engine)
