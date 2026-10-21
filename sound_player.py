import random
import subprocess
import time
from pathlib import Path

from config import (
    MIN_VOLUME,
    MAX_VOLUME,
    MIN_PLAY_SECONDS,
    MAX_PLAY_SECONDS,
)


class SoundPlayer:
    def __init__(self, sounds_dir):
        self.sounds_dir = Path(sounds_dir)

    def available_sounds(self):
        return sorted(
            path for path in self.sounds_dir.glob("*.wav")
            if path.is_file()
        )

    def play_random(self):
        sounds = self.available_sounds()

        if not sounds:
            print("Ses dosyasi bulunamadi; sounds/ klasorune WAV ekle.")
            return

        sound = random.choice(sounds)
        volume = random.uniform(MIN_VOLUME, MAX_VOLUME)
        duration = random.uniform(
            MIN_PLAY_SECONDS, MAX_PLAY_SECONDS
        )

        print(
            f"Ses: {sound.name} | "
            f"Ses seviyesi: %{volume * 100:.0f} | "
            f"Sure: {duration:.1f} saniye"
        )

        process = subprocess.Popen([
            "/usr/bin/pw-play",
            "--volume", f"{volume:.2f}",
            str(sound),
        ])

        try:
            process.wait(timeout=duration)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        print("Ses oynatma tamamlandi.")
