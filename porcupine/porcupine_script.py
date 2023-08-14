import pvporcupine
import pyaudio
import wave
import numpy as np
import time
import whisper
from pydub import AudioSegment

"""
Note: This code uses the pydub library to convert the WAV recording to MP3. 
You'll need to install it and have FFmpeg available in your system. 
You can install pydub using `pip install pydub`, and you can usually 
install FFmpeg through your system's package manager -> brew install ffmpeg
Make sure to adjust the SILENCE_THRESHOLD to match the level that 
you consider to be silence for your environment and microphone.
+ Need for pip install whisper
+ brew install portaudio
+ pip3 install pyaudio
+ pip3 install pvporcupine
+ pip3 install pydub
"""

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
      
      else:
          silence_start_time = None

# Clean up
porcupine.delete()
stream.stop_stream()
stream.close()
audio_engine.terminate()