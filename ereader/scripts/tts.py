import subprocess
import shutil
import os


class PageToSpeech:

    def __init__(self, sentences: list[str], wav_path: str):
        self.path = wav_path
        os.makedirs(os.path.dirname(wav_path), exist_ok=True)
        self.tts_procs: list[subprocess.Popen] = []
        # If this loop generates first sentence(s) too slowly, will change to do one at a time in thread
        for i, sent in enumerate(sentences):
            self.tts_procs.append(subprocess.Popen(['pico2wave', f'-w={wav_path}/sent{i}.wav', sent]))
        self.audio_proc: subprocess.Popen = None
        self.num_sentences = len(sentences)
        self.playing_sent = 0

    def play_sentence(self, num: int):
        if not isinstance(num, int):
            return
        if num < 1 or num > self.num_sentences:
            return
        if self.audio_proc is not None:
            self.audio_proc.terminate()
            self.audio_proc.stdin.close()
        self.tts_procs[num].wait()
        self.playing_sent = num
        self.audio_proc = subprocess.Popen(['aplay', '-i', f'{self.path}/sent{num}.wav'], stdin=subprocess.PIPE)

    def play_next_sentence(self):
        self.play_sentence(++self.playing_sent)

    def pause_resume(self):
        self.audio_proc.stdin.write('\n')
        self.audio_proc.stdin.flush()

    def cleanup(self):
        if self.audio_proc is not None:
            self.audio_proc.terminate()
            self.audio_proc.stdin.close()
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
