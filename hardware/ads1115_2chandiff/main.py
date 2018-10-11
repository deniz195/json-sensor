import time
import board
import busio
from adafruit_ads1x15.differential import ADS1115
import array

import touchio

def calc_mean(this_array):
    return sum(this_array)/len(this_array)


adc_active = True
# adc_active = False

# Capacitive touch on D3
touch = touchio.TouchIn(board.D3)

if adc_active:
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)
    # Create the ADC object using the I2C bus
    adc = ADS1115(i2c)

# adc_gain = 2/3
adc_gain = 1
# ADS1X15_CONFIG_GAIN = {
#     2/3: 0x0000,
#     1:   0x0200,
#     2:   0x0400,
#     4:   0x0600,
#     8:   0x0800,
#     16:  0x0A00
# }

adc_datarate = 128
# # Mapping of data/sample rate to config register values for ADS1115 (slower).
# ADS1115_CONFIG_DR = {
#     8:    0x0000,
#     16:   0x0020,
#     32:   0x0040,
#     64:   0x0060,
#     128:  0x0080,
#     250:  0x00A0,
#     475:  0x00C0,
#     860:  0x00E0
# }

# https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/blob/master/adafruit_ads1x15/adafruit_ads1x15.py

channels = (0, 3)
channel_names = ['adc_ch01', 'adc_ch23']

print_length = 3
print_index = 0

data_length = 20
data_index = 0
data_raw = [array.array('f', [0] * data_length) for p in channels]
data_avg = [0.0 for p in channels]

touch_raw = array.array('f', [0] * data_length)
touch_avg = 0.0

while True:
    touch_raw_value = touch.raw_value

    touch_raw[data_index] = touch.raw_value

    if adc_active:
        for i, ch in enumerate(channels):
            raw = adc.read_volts_difference(ch, adc_gain, adc_datarate)
            data_raw[i][data_index] = raw   
      
    if print_index == 0:        
        output = ""
        output += '{'
        output += ' "guid": "btrn-adc-sensor-0002", '
        
        touch_avg = calc_mean(touch_raw)
        output += ' "touch_raw"'
        output += ':  %0.2f' % touch_avg

        if adc_active:
            for i, p in enumerate(channels):
                data_avg[i] = calc_mean(data_raw[i])

                output += ', '
                output += '"' + channel_names[i] + '"'
                output += ':  %0.6f' % data_avg[i]

        output += '}'

        print(output)

    # # Print results
    # print("{:>5}\t{:>5.3f}".format(raw, volts))

    # Sleep for a bit
 #   time.sleep(0.5)

    data_index = (data_index + 1) % data_length
    print_index = (print_index + 1) % print_length
