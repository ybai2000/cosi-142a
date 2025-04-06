import sys
import utime
import machine
import ujson

led = machine.Pin("LED", machine.Pin.OUT)
select = machine.PIN()
back = machine.PIN()
up = machine.PIN()
down = machine.PIN()

while True:
    with open("signal.json") as f:
        signal = ujson.load(f)
        
    sys.stdout.buffer.write(b"Data from Pico\n")
    led.value(0)
    utime.sleep(1)
