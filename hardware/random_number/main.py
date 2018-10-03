# Trinket IO demo
# Welcome to CircuitPython 2.0.0 :)

import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogOut, AnalogIn
import touchio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import adafruit_dotstar as dotstar
import time
import neopixel

# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)

# Built in red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Analog input on D0
analog1in = AnalogIn(board.D0)

# Analog output on D1
aout = AnalogOut(board.D1)

# Digital input with pullup on D2
button = DigitalInOut(board.D2)
button.direction = Direction.INPUT
button.pull = Pull.UP


# Used if we do HID output, see below
kbd = Keyboard()

######################### HELPERS ##############################

# Helper to convert analog input to voltage
def getVoltage(pin):
    return (pin.value * 3.3) / 65536

######################### MAIN LOOP ##############################

i = 0
while True:

  # set analog output to 0-3.3V (0-65535 in increments)
  aout.value = i * 256

  # Read analog voltage on D0
#  print("D0: %0.2f" % getVoltage(analog1in))

  print('{"guid": "0x123", "value": %0.2f}' % getVoltage(analog1in))

  time.sleep(0.5)
