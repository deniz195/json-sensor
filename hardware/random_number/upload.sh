#!/bin/bash

# arduino --upload random_number.ino --board arduino:avr:leonardo --port /dev/ttyACM0
# arduino --upload random_number.ino --port /dev/ttyACM0

arduino-cli compile --fqbn arduino:avr:leonardo .
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:leonardo ./


