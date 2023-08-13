import whisper

model = whisper.load_model("tiny")

result_1 = model.transcribe("audio_files/audio_1.mp3")
print(result_1["text"])

result_2 = model.transcribe("audio_files/audio_2.mp3")
print(result_2["text"])

result_3 = model.transcribe("audio_files/audio_3.mp3")
print(result_3["text"])