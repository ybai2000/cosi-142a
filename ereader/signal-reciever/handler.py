import json
import sys

BAUDRATE = 115200
PORT = "/dev/ttyACM0"

def process_signal():
    for line in sys.stdin:
        try:
            signal = json.loads(line.strip())
        except Exception as e:
            continue
    print(f"received signal: {signal}")
