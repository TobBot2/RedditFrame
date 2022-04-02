# Reddit Frame

## Run
run 'main.py' on windows (with working directory of RedditFrame)
run 'run.sh' on raspberrypi (in any directory, or from cronjob via 'bash run.sh')

automatically configures based on whether testing on windows or running build on raspberrypi

## Setup
install: $ pip3 install { library }
libraries to install: pillow, python-weather

Change the /home/pi part in errors.txt to the complete path to the directory for you.

Modify 'filer.py' if you're getting errors about a nonexistent file/directory

### RaspberryPi Setup
Also install the libraries: spidev, RPi.GPIO
note: spidev and RPi.GPIO might be pre-installed (they were for me).

### Cronjob Setup (Automate Display on RaspberryPi)
python-weather must be installed with the -H tag and/or sudo preface in addition to the above-mentioned installation when run on a cronjob.
    $ pip3 install -H python-weather
    $ sudo pip3 install python-weather
I say and/or because I installed it both ways just in case and it worked. You might not actually need both.

Automate the execution of this using a cronjob. Execute:
    $ sudo crontab -e
Add the lines:
    @reboot sleep 15 && cd path/to/directory && bash run.sh
    0 * * * * cd path/to/directory && bash run.sh
The first line will execute the script fifteen seconds after a reboot (the fifteen seconds allows it to connect to the internet)
The second line will execute the script at the start of every hour.

## Customization

If you customize, I recommend using windows for testing. If you're on mac, you should be able to just add 'or sys.platform == 'mac' to wherever it says 'if sys.platform == 'win32'', but I haven't tested it so I'm not adding it in. Change 'subreddits.csv' to change the which subreddits to sample from. If you dig into the code, things are generally pretty dynamic and easy to change.

If you want to change the frequency at which the display changes with the cronjob, go to https://cron.help and replace the '0 * * * *' with the new frequency syntax. I set it to */5 * * * * for testing (once every five minutes). Keep in mind the refresh limits of the display though.

## Waveshare display
Display I used: https://www.waveshare.com/7.5inch-e-paper.htm
Waveshare e-paper display tutorial: https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT
Note that the files epd7in5_V2.py and epdconfig.py were taken from waveshare's official github. I did slightly modify them (I think I just removed some import statements). Here's the repository: https://github.com/waveshare/e-Paper/tree/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd.
Also note that this is made for the 7.5inch two-color V2 (480x800) screen. If you want to modify it for a different screen, change the file 'epd7in5_V2' to the one corresponding to your model. The versions with a letter after the dimensions signifies it is for a multicolor screen (I'm fairly certain, at least. It took *hours* for me to figure that out!).