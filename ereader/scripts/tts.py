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
        self.volume: int = None
        self.init_volume()

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
        self.audio_proc = subprocess.Popen(['aplay', '-i', f'{self.tts_dir}/{dirname}/sent{num}.wav'], stdin=subprocess.PIPE,
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
        
    def init_volume(self) -> None:
        try:
            process = subprocess.Popen(["amixer", "sget", "Master"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()

            if process.returncode != 0:
                print(f"Error exectuting amixer: {error.strip()}")
                self.volume = 0
                return
            
            for line in output.splitlines():
                if "%" in line:
                    volume_str = line.split("[")[2].split("%")[0]
                    self.volume = int(volume_str)
                    return
        except (IndexError, ValueError) as e:
            print(f"Error retrieving volume: {e}")
        finally:
            self.volume = 0
            return

    def volume_up(self):
        self.volume = min(100, self.volume + 5)
        try:
            command = ["amixer", "sset", "Master", f"{self.volume}%"]
            subprocess.run(command)
        except Exception as e:
            print(f"Error increasing volume: {e}")

    def volume_down(self):
        self.volume = max(0, self.volume - 5)
        try:
            command = ["amixer", "sset", "Master", f"{self.volume}%"]
            subprocess.run(command)
        except Exception as e:
            print(f"Error increasing volume: {e}")

            
sample_text = """It is now three years after the events of A New Hope. The Rebel Alliance has been forced to flee its base on Yavin 4 and establish a new one on the ice planet of Hoth.
An Imperial Star Destroyer, dispatched by the Sith Lord Darth Vader, continuing his quest for Luke Skywalker, launches thousands of probe droids across the galaxy, one of which lands on Hoth and begins its survey of the planet. Luke Skywalker, on patrol astride his tauntaun, discovers the probe, which he mistakes for a meteorite. After reporting to comrade Han Solo that he'll investigate the site, Luke is knocked unconscious by a deadly wampa.
When Luke fails to report in at Echo Base, Han Solo goes out on his tauntaun to search for him in an encroaching storm. Upon waking up, Luke finds himself hanging upside down in a cave; his eyes opening to the sight of a wampa eating his tauntaun. Using the power of the Force, Luke is able to pull his lightsaber out of the snow and to himself. After he ignites it, he cuts himself free and cuts off the attacking wampa's arm just in time, running out of the cave and escaping into the cold night of Hoth.
Luke tries to make his way to Echo Base on foot, but he finds himself lost in the blizzard and collapses in the snow. Suddenly, he sees the Force spirit of Obi-Wan Kenobi appear before him. Kenobi's spirit ghost instructs Luke to go to Dagobah to undergo training under Yoda, a Jedi Grand Master. After the spirit ghost disappears, Han arrives to find an almost unconscious Luke, who is mumbling indistinctly about Obi-Wan, Yoda, and Dagobah. Turning to his tauntaun, Han watches it collapse in the extreme cold. To keep Luke from freezing to death, Han uses Luke's lightsaber to cut open the dead tauntaun and places Luke in it. Han then sets about erecting a shelter for them both. They are forced to stay out during the night as the aircraft (snowspeeders) that the Rebels use for atmospheric flight had not yet been adapted for the extremely low temperatures of the planet and are therefore unable to mount a rescue operation.
The next morning, Rebel Pilots flying the snowspeeders set out from Echo Base to search for the missing men. Zev Senesca, one of the pilots in Rogue Group, makes contact with Han over comlink and the pair are rescued. When they are taken back to base, Luke is put in a bacta tank for healing under the care of medical droid, 2-1B.
Princess Leia Organa urges Han to stay with the Rebels. When Han assumes it is because she has feelings for him, Leia loses her temper and calls him a "stuck-up, half-witted, scruffy-looking nerf herder."
Meanwhile, the probe droid has spotted signs that indicate Hoth is occupied and sends a signal to the Imperial fleet, shortly before being shot at by Han Solo and Chewbacca and triggering its self-destruct mechanism. Aboard the Executor, Admiral Kendal Ozzel dismisses the information as evidence of smugglers, nothing more. However, Darth Vader knows better and orders the fleet to Hoth. Han warns General Rieekan that the Empire is probably aware of their location, and Rieekan orders the evacuation of Echo Base to begin.
Darth Vader and the Imperial forces set course for the Hoth system to set up the attack. The rebels load whatever equipment they can onto transports and plan a rear-guard action to secure their escape. Luke, now fully recovered from the Wampa attack and subsequent exposure, says farewell to Chewbacca and Solo, who have decided to leave the Alliance to resolve their debt to Jabba the Hutt. As the Imperial forces enter the Hoth system, General Rieekan orders full power to the energy shield that is protecting the base from orbital bombardment.
Aboard the Executor, General Maximilian Veers notifies Vader that Admiral Ozzel has emerged from lightspeed too close to Hoth. Ozzel intended to catch the Rebels unaware before they could set up their defenses. However, Vader realizes that the Rebels have been alerted to the fleet's arrival. Via video communication, Vader Force chokes Ozzel to death for his incompetence, then appoints Captain Firmus Piett the new Admiral on the spot. As Vader previously ordered, the Imperial ground forces, commanded by General Veers, land outside the Rebels' shield and march overland to destroy the power generator.
Princess Leia gives the Rebel fighters instructions on the evacuation to leave Hoth two to three ships at a time past the energy shield to a rendezvous point, which is beyond the outer rim. Rieekan lowers the shields to fire the Ion cannon at one of the Imperial Star Destroyers allowing the first transports to escape. The Rebel pilots assigned to hold off the Imperial ground assault depart the Hoth base for the oncoming battle against heavily equipped Imperial forces, who are armed with agile AT-STs (All Terrain Scout Transports) and monstrous AT-AT (All Terrain Armored Transport) walkers, led by General Veers."""


if __name__ == '__main__':
    sentences = sample_text.replace("\n", "").split(".")
    if not sentences[-1]:
        sentences = sentences[:-1]
    sentences = [sentence.strip() + "." for sentence in sentences]
    tts_player = TTSPlayer('../tts')
    tts_player.add_sentences('test', sentences)
    while True:
        if not tts_player.is_playing():
            tts_player.play_next('test')
