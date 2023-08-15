## Magic Mirror with Smart Chat Capabilities

This guide will walk you through setting up a smart mirror interface that listens for a wake word, records your speech, transcribes it, and then uses an API to get a chatbot's response, which is finally converted to speech using the Mimic TTS system.

### Overview:

1. **Wake Word Detection**: The system continually listens for a specific wake word using Porcupine. Upon hearing the wake word, it begins recording audio.
2. **Audio Recording**: Audio is recorded until a set duration of silence is detected.
3. **Audio Transcription**: The recorded audio is transcribed into text using the Whisper model.
4. **Chatbot Interaction**: The transcribed text is sent to an LLM API, which returns a chatbot's response.
5. **Text-to-Speech Conversion**: The chatbot's response is converted into speech using the Mimic TTS system.

### Step-by-Step Guide:

1. **Setup**:
    - Choose a device (e.g., Raspberry Pi) and set up a lightweight window manager.
    - Install MagicMirror and configure it.
    - Test the audio and microphone setup.
    - Add the `MMM-WhisperGPT` module for chat capabilities.

2. **Wake Word Detection**:
    - Using Porcupine, the script continuously listens for a wake word.
    - Once the wake word is detected, the script starts recording audio.

3. **Recording Audio with Silence Detection**:
    - The audio is recorded in frames.
    - The script checks the loudness of each frame and waits for a set period of silence (defined by `SILENCE_DURATION` and `SILENCE_THRESHOLD`) to stop recording.
    - The recorded audio is then saved as a WAV file and converted to MP3 format.

4. **Audio Transcription**:
    - The MP3 audio file is transcribed into text using the Whisper model.
    - The transcription is saved to a text file.

5. **Chatbot Interaction**:
    - The transcribed text is sent to the LLM API.
    - The API returns a chatbot response in text form.

6. **Text-to-Speech Conversion with Mimic**:
    - The text response from the chatbot is converted to speech using the Mimic TTS system.
    - This is achieved by invoking Mimic via a subprocess in Python.
    - The spoken version of the chatbot's response is saved as an audio file (`response.wav`).

### NOTES:
- Note: This code uses the pydub library to convert the WAV recording to MP3. 
You'll need to install it and have FFmpeg available in your system. 
You can install pydub using `pip install pydub`, and you can usually 
install FFmpeg through your system's package manager -> brew install ffmpeg
Make sure to adjust the SILENCE_THRESHOLD to match the level that 
you consider to be silence for your environment and microphone.