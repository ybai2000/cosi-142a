import sys
import utime
import machine
import ujson

led = machine.Pin("LED", machine.Pin.OUT)

# Define pin constants
SELECT_PIN = 0
BACK_PIN = 4
UP_PIN = 8
DOWN_PIN = 16

# Define pins with pull-up resistors
select = machine.Pin(SELECT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
back = machine.Pin(BACK_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
up = machine.Pin(UP_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
down = machine.Pin(DOWN_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

# Global variable for debouncing
last_triggered = 0

# Function to handle pin interrupts
def closure(value):
    def pin_triggered(pin):
        try:
            global last_triggered
            current_time = utime.ticks_ms()
            if utime.ticks_diff(current_time, last_triggered) < 50:  # Debounce for 50ms
                return
            last_triggered = current_time
            sys.stdout.buffer.write(str(value).encode('utf-8') + b'\n')
            led.toggle()
        except Exception as e:
            sys.stderr.write(f"Error in interrupt handler: {e}\n")
    return pin_triggered

# Attach interrupts to pins
select.irq(trigger=machine.Pin.IRQ_RISING, handler=closure(0))
back.irq(trigger=machine.Pin.IRQ_RISING, handler=closure(1))
up.irq(trigger=machine.Pin.IRQ_RISING, handler=closure(2))
down.irq(trigger=machine.Pin.IRQ_RISING, handler=closure(3))

# Keep the program running
try:
    while True:
        utime.sleep(1)
except KeyboardInterrupt:
    print("Program terminated.")
