from enum import Enum
import serial
import json
import threading
import queue

class Button(Enum):
    SELECT = 1
    BACK = 2
    UP = 3
    DOWN = 4

class PicoListener:
    def __init__(self):
        self.PORT = "/dev/ttyACM0"
        self.BAUDRATE = 115200
        self.DICT = ("select", "back", "up", "down")
        self.ser = serial.Serial(self.PORT, self.BAUDRATE, timeout=1)
        self.queue = queue.Queue()
        self.stop_event = threading.Event()  # Event to stop the thread

    def read_signal(self):
        while not self.stop_event.is_set():  # Check if the thread should stop
            if self.ser.in_waiting > 0:
                try:
                    message = int(self.ser.readline().decode('utf-8').strip())
                    self.queue.put(Button(message))
                except Exception as e:
                    print(f"Error reading signal: {e}")

    def listening(self):
        listener_thread = threading.Thread(target=self.read_signal)
        listener_thread.daemon = True
        listener_thread.start()

    def get_signal_queue(self):
        return self.queue

    def check_interrupt(self):
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None

    def stop_listening(self):
        self.stop_event.set()  # Signal the thread to stop
        self.ser.close()  # Close the serial connection