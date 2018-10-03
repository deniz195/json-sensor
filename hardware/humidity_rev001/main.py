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

from busio import I2C
from board import SCL, SDA
import adafruit_sht31d

i2c = I2C(SCL, SDA)

sensor = adafruit_sht31d.SHT31D(i2c)


# # Built in red LED
# led = DigitalInOut(board.D13)
# led.direction = Direction.OUTPUT

# # Analog input on D0
# analog1in = AnalogIn(board.D0)

# # Analog output on D1
# aout = AnalogOut(board.D1)

# # Digital input with pullup on D2
# button = DigitalInOut(board.D2)
# button.direction = Direction.INPUT
# button.pull = Pull.UP


# # Used if we do HID output, see below
# kbd = Keyboard()

######################### HELPERS ##############################

# # Helper to convert analog input to voltage
# def getVoltage(pin):
#     return (pin.value * 3.3) / 65536

######################### MAIN LOOP ##############################

averages = 1
# report_time = 0.0
# loop_time = report_time/averages

i = 0

temperature = 0
relative_humidity = 0

while True:

  temperature += sensor.temperature
  relative_humidity += sensor.relative_humidity  

  if i == averages - 1:
    temperature /= averages
    relative_humidity /= averages

    output = ""
    output += '{'
    output += ' "guid": "btrn-tmp-sensor-0001",'
    output += ' "temperature":  %0.2f,' % sensor.temperature
    output += ' "relative_humidity":  %0.2f,' % sensor.relative_humidity
    output += '}'

    print(output)

    temperature = 0
    relative_humidity = 0


  i = (i + 1) %  averages

  # time.sleep(loop_time)
