import logging
import queue
import random
import signal
import subprocess
import threading
import time

from config import (
    GPIO_CHIP,
    GPIO_LINE,
    LOGS_DIR,
    SOUNDS_DIR,
    MIN_DELAY_SECONDS,
    MAX_DELAY_SECONDS,
    MAX_PENDING_EVENTS,
)
from pir_sensor import PirSensor
from sound_player import SoundPlayer


def main():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOGS_DIR / "pir-prank.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    events = queue.Queue(maxsize=MAX_PENDING_EVENTS)
    stop_event = threading.Event()
    sensor = PirSensor(GPIO_CHIP, GPIO_LINE)
    player = SoundPlayer(SOUNDS_DIR)

    def read_sensor():
        while not stop_event.is_set():
            try:
                for event in sensor.events():
                    if stop_event.is_set():
                        break

                    try:
                        events.put_nowait(event)
                        logging.info("PIR event received")
                        print("Hareket algilandi.")
                    except queue.Full:
                        logging.warning("Event queue full; event dropped")
                        print("Kuyruk dolu; yeni olay atlandi.")

                if not stop_event.is_set():
                    logging.warning("GPIO monitor ended; retrying")
                    time.sleep(2)

            except (OSError, subprocess.SubprocessError) as exc:
                logging.exception("GPIO monitor error: %s", exc)
                time.sleep(2)

    def shutdown(_signum, _frame):
        stop_event.set()
        sensor.close()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)


    reader = threading.Thread(target=read_sensor, daemon=True)
    reader.start()

    print("PIR Prank calisiyor. Durdurmak icin Ctrl+C.")
    logging.info("Application started")

    try:
        while not stop_event.is_set():
            try:
                event = events.get(timeout=0.5)
            except queue.Empty:
                continue

            delay = random.uniform(
                MIN_DELAY_SECONDS, MAX_DELAY_SECONDS
            )
            print(f"Tepki gecikmesi: {delay:.2f} saniye")
            stop_event.wait(delay)

            if stop_event.is_set():
                break

            logging.info("Playing sound after random delay")
            player.play_random()
            events.task_done()

    finally:
        stop_event.set()
        sensor.close()
        logging.info("Application stopped")
        print("Program durduruldu.")


if __name__ == "__main__":
    main()
