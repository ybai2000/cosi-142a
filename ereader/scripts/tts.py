import subprocess
import shutil
import os
from collections import defaultdict


class TTSPlayer:
    def __init__(self, tts_dir: str) -> None:
        self.tts_dir = tts_dir
        self.tts_procs: defaultdict[str, list[subprocess.Popen]] = defaultdict(list)
        self.playing_sent: dict[str, int] = {}
        self.audio_proc: subprocess.Popen = None

    def add_sentences(self, dirname: str, sentences: list[str]) -> None:
        os.makedirs(os.path.join(self.tts_dir, dirname), exist_ok=True)
        for i, sent in enumerate(sentences, 1):
            self.tts_procs[dirname].append(
                subprocess.Popen(['pico2wave', f'-w={self.tts_dir}/{dirname}/sent{i}.wav', sent]))
        self.playing_sent[dirname] = 0

    def play_sentence(self, dirname: str, num: int) -> bool:
        if num < 1 or num > len(self.tts_procs[dirname]):
            return False
        if self.audio_proc is not None:
            self.audio_proc.terminate()
            self.audio_proc.stdin.close()
        self.tts_procs[dirname][num - 1].wait()
        self.playing_sent[dirname] = num
        self.audio_proc = subprocess.Popen(['aplay', '-i', f'{self.tts_dir}/sent{num}.wav'], stdin=subprocess.PIPE,
                                           text=True)

    def play_next(self, dirname: str) -> bool:
        if self.playing_sent[dirname] == len(self.tts_procs[dirname]):
            return False
        self.playing_sent[dirname] += 1
        return self.play_sentence(dirname, self.playing_sent[dirname])

    # todo make play_next and play_prev similar? in that instead of going to beginning of sent if first in page
    # it goes to previous page (aka returns false)
    def play_prev(self, dirname: str) -> bool:
        self.playing_sent[dirname] = self.playing_sent[dirname] - 1 if self.playing_sent[dirname] > 1 else 1
        return self.play_sentence(dirname, self.playing_sent[dirname])

    def pause_resume(self) -> None:
        if self.audio_proc is not None:
            self.audio_proc.stdin.write('\n')
            self.audio_proc.stdin.flush()

    def is_playing(self) -> bool:
        return self.audio_proc is not None and self.audio_proc.poll() is None

    def remove(self, dirname: str) -> None:
        path = os.path.join(self.tts_dir, dirname)
        if os.path.exists(path):
            shutil.rmtree(path)
        self.tts_procs.pop(dirname)
        self.playing_sent.pop(dirname)

    def clean(self) -> None:
        shutil.rmtree(self.tts_dir)
        self.tts_procs = defaultdict(list)
        self.playing_sent = {}
        self.audio_proc = None
