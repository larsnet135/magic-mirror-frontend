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

# Variables
recording = False
silence_start_time = None
audio_frames = []

# Create porcupine object
porcupine = pvporcupine.create(
  access_key='2/2V5+k37vGePDtulTsGJYDQTgk8F/oUx5dLDNlfju+NOcRsIHCGqw==', # --> change
  keyword_paths=['/Users/larsnet/magic-mirror-frontend/porcupine/Keywords/mac/porcupine_mac.ppn'] # --> change
)

# Create a PyAudio object
audio_engine = pyaudio.PyAudio()
sample_rate = 16000
frame_length = 512

stream = audio_engine.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length)  # This sets the frames_per_buffer to 512, matching Porcupine's expectation

# Create a Whisper model
whisper_model = whisper.load_model("tiny")

# Main Function
def get_next_audio_frame():
    audio_buffer = stream.read(porcupine.frame_length, exception_on_overflow=False)
    audio_data = np.frombuffer(audio_buffer, dtype=np.int16)
    return audio_data


def write_response_file(response: str) -> None:
    with open("chatbot_responses/response.txt", "w") as outputfile:
        outputfile.write(response)


while True:
  audio_frame = get_next_audio_frame()
  keyword_index = porcupine.process(audio_frame)
  
  if keyword_index == 0:
      print("Wake word detected!")
      recording = True
      audio_frames = [] # Reset audio frames

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
              
              # Save recording as WAV
              wav_path = 'recording.wav'
              with wave.open(wav_path, 'wb') as wf:
                  wf.setnchannels(1)
                  wf.setsampwidth(audio_engine.get_sample_size(pyaudio.paInt16))
                  wf.setframerate(sample_rate)
                  wf.writeframes(b''.join(audio_frames))

              # Convert to MP3
              audio = AudioSegment.from_wav(wav_path)
              mp3_path = '/Users/larsnet/magic-mirror-frontend/porcupine/mp3_files/audio.mp3' # --> change
              audio.export(mp3_path, format='mp3')
              print(f"Saved recording as {mp3_path}")

              # Transcribe the recording using Whisper
              result = whisper_model.transcribe(mp3_path)
              transcription = result["text"]
              file_path_transcript = '/Users/larsnet/magic-mirror-frontend/porcupine/transcripts/transcript.txt' # --> change
              with open(file_path_transcript, 'w') as file:
                  file.write(transcription)
            
              # Call of LLM API
              HOST_IP = "127.0.0.1"
              PORT = 8000
              USER_INPUT = transcription # Using the transcription as user input
              payload = {'user_input': f'{USER_INPUT}'}
              r = requests.get(f'http://{HOST_IP}:{PORT}/chatbot', params=payload)
              data = r.json()
              response_string = data['chatbot_response']['text']
              print(response_string)
              write_response_file(response_string) # Writing the response to a file

              # Use of mimic3 for text-to-speech
              def text_to_speech_mimic(text):
                cmd = ["mimic", "-t", text, "-o", "response.wav"]
                subprocess.run(cmd)

              text_to_speech_mimic(response_string_chatbot)
              subprocess.run(["aplay", "response.wav"])

      else:
          silence_start_time = None



# Clean up
porcupine.delete()
stream.stop_stream()
stream.close()
audio_engine.terminate()