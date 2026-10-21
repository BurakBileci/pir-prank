import subprocess


class PirSensor:
    def __init__(self, chip, line):
        self.command = [
            "/usr/bin/gpiomon",
            "--rising-edge",
            chip,
            str(line),
        ]
        self.process = None

    def events(self):
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        try:
            for output in self.process.stdout:
                if "RISING EDGE" in output:
                    yield output.strip()
        finally:
            self.close()

    def close(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=3)
