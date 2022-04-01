# Reddit Frame

## Run
run 'main.py' on windows (with working directory of RedditFrame)
run 'run.sh' on linux (in any directory, or from cronjob via 'bash run.sh')

automatically configures based on whether testing on windows or running build on raspberrypi

## Setup
install -> $ pip3 install { library }
external libraries: pillow, python-weather, spidev, RPi.GPIO
note: spidev and RPi.GPIO can only be intstalled (and only need to be installed) on the raspberrypi
python-weather must be installed with the -H tag and/or sudo preface in addition to like above ($ pip3 install -H python-weather, $ sudo pip3 install python-weather).
I say and/or because I installed it both ways just in case and it worked.

## Additional
waveshare e-paper display tutorial: https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT