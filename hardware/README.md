https://www.meccanismocomplesso.org/en/controlling-arduino-raspberry-pi/




sudo apt-get update
sudo apt-get install arduino-core arduino-mk
sudo apt-get purge openjdk-8-jre-headless
sudo apt-get install openjdk-8-jre-headless

    After installing, I proceed the following :

    --> Go to the location (copy past in the finder the following location) : /usr/lib/jvm/java-8-openjdk-armhf/jre/lib/arm
    --> Click right on arm directory and select Open directory with the terminal
    --> In LXterminal: copy client directory to a new directory server, by the follow terminal command : cp -r client server
    --> Reboot your system : sudo reboot
    It will now work !

sudo apt-get install openjdk-8-jre
sudo apt-get install arduino



https://pblog.ebaker.me.uk/2014/01/uploading-arduino-sketch-from-raspberry.html




sudo apt-get purge openjdk-8-jre-headless
sudo apt-get install openjdk-8-jre-headless
sudo apt-get install openjdk-8-jre



Install from here:
https://github.com/arduino/arduino-cli


arduino-cli board list
arduino-cli core install arduino:avr
arduino-cli core list
arduino-cli board list


arduino-cli compile --fqbn arduino:avr:leonardo ./random_number
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:leonardo ./random_number