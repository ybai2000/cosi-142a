import os
import time
import whisper

start_time = time.time()
model = whisper.load_model('tiny.en')


print('got model in', time.time()-start_time)

audio_path = os.path.join(os.path.dirname(__file__), "trimmed.flac")

start_time = time.time()

result = model.transcribe(
        audio_path, language='en', temperature=0.0, word_timestamps=True
    )
    
print('got result in', time.time()-start_time)

transcription = result["text"].lower()

print(transcription)


