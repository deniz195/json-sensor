import time
import board
import busio

import adafruit_tmp007
import adafruit_sht31d

import machine_guid

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)

sensor_tmp007 = adafruit_tmp007.TMP007(i2c)
sensor_sht31d = adafruit_sht31d.SHT31D(i2c)

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0


######################### HELPERS ##############################

# # Helper to convert analog input to voltage
# def getVoltage(pin):
#     return (pin.value * 3.3) / 65536

######################### MAIN LOOP ##############################


averages = 1
# report_time = 0.0
# loop_time = report_time/averages

i = 0

die_temp = 0
obj_temp = 0
amb_temperature = 0
amb_relative_humidity = 0

last_exception = None

while True:
  try:
    die_temp += sensor_tmp007.die_temperature
    obj_temp += sensor_tmp007.temperature
    amb_temperature += sensor_sht31d.temperature
    amb_relative_humidity += sensor_sht31d.relative_humidity  

    if i == averages - 1:
      die_temp /= averages
      obj_temp /= averages
      amb_temperature /= averages
      amb_relative_humidity /= averages

      output = ""
      output += '{'
      output += ' "guid": "%s",' % machine_guid.guid
      output += ' "object_temp":  %0.2f,' % obj_temp
      output += ' "die_temp":  %0.2f,' % die_temp
      output += ' "amb_temp":  %0.2f,' % amb_temperature
      output += ' "amb_relative_humidity":  %0.2f' % amb_relative_humidity

      if last_exception is not None:
        output += ', "last_exception": "%s"' % last_exception

      output += '}'

      print(output)
      ## check output against https://jsonlint.com/ --> OK

      die_temp = 0
      obj_temp = 0
      amb_temperature = 0
      amb_relative_humidity = 0

    i = (i + 1) %  averages

  except BaseException as e:
    last_exception = str(repr(e))
    last_exception = last_exception.replace('"', '\'').replace('\n', '') ## make JSON string save



  # time.sleep(loop_time)
