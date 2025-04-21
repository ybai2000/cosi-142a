import serial
import json

class Pico_listener():
    PORT = "/dev/ttyACM0"
    BAUDRATE = 115200
    DICT = ("select", "back", "up", "down")
    SER =  serial.Serial(PORT, BAUDRATE, timeout=1)

    def read_signal() -> json:
        global ser
        if ser.in_waiting > 0:
            m = ser.readline().decode("utf-8").strip()
            