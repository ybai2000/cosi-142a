from enum import Enum
import serial
import threading
import queue

class Button(Enum):
    SELECT = 1
    BACK = 2
    UP = 3
    DOWN = 4

class PicoListener:
    def __init__(self) -> None:
        self.PORT = "/dev/ttyACM0"
        self.BAUDRATE = 115200
        self.DICT = ("select", "back", "up", "down")
        self.ser = serial.Serial(self.PORT, self.BAUDRATE, timeout=1)
        self.queue = queue.Queue()
        self.stop_event = threading.Event()  # Event to stop the thread

    def read_signal(self) -> None:
        while not self.stop_event.is_set():  # Check if the thread should stop
            if self.ser.in_waiting > 0:
                try:
                    message = int(self.ser.readline().decode('utf-8').strip())
                    self.queue.put(Button(message))
                except Exception as e:
                    print(f"Error reading signal: {e}")

    def listening(self) -> None:
        listener_thread = threading.Thread(target=self.read_signal)
        listener_thread.daemon = True
        listener_thread.start()

    def get_signal_queue(self) -> queue.Queue:
        return self.queue

    def check_interrupt(self) -> Button | None:
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None

    def get_interrupt(self) -> Button:
        return self.queue.get()

    def stop_listening(self) -> None:
        self.stop_event.set()  # Signal the thread to stop
        self.ser.close()  # Close the serial connection


if __name__ == "__main__":
    listener = PicoListener()
    listener.listening()
    print("Start Listening")
    try:
        while True:
            signal = listener.check_interrupt()  # Check for signals in the queue
            if signal:
                print(f"Received signal: {signal.name}")  # Print the signal to the terminal
    except KeyboardInterrupt:
        print("Stopping listener...")
        listener.stop_listening()  # Stop the listener gracefully
