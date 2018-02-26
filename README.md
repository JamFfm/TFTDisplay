# TFTDisplay
CraftbeerPi3 addon for a 2.2" or 2.8" TFT Display 240 x 320 with ILI9341 driver

With this add-on you can display a Temperature Graph of a Kettle (its sensor) on a 240 x 320 TFT SPI Display.
It is based on the ILI9341 controller.

![](https://github.com/JamFfm/TFTDisplay/blob/master/Graph.JPG "TFTDisplax 320x240")

# I followed this only for wiring

>http://blog.riyas.org/2014/07/
>
>BUT I DID NOT USE THE COMMANDS OF THIS PAGE!
>
>*I put a 48 Ohm resistor inbetween LCD-Pin of TFT and the Raspi Pin.

![](https://github.com/JamFfm/TFTDisplay/blob/master/50%20Ohm%20at%20lsd%20pin.png "Wiring")

# I followed this page how to install and run the modules:

>https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/usage
>Please do not update your firmware. It will distroy the Raspi configuration (hopefully not the hardware).
>I noticed that you need first initialise with DC 18 and RST 23. This causes a white / or false-colour screen. After that change to DC 24 and RST 25. The latter are the GPIO I physically connected. The change is done automatically by the code.
>
>The modul can display a temperatur graph by the help of rrdtool.

# Installation
>is a bit tricky:
>You have to install the Adafruit_Pyton_ILI9341 and some other packages.
>Most of them are already installed but they all have to be present.
>After that the rrdtool has to be installed with the Raspi software-installer.
>In the end you have to install the addon.
>Dont forget the reboot.

## Install Adafruit_Pyton_ILI9341 for TFTDisplay_240x320:
Copy and paste all lines with (1) to (7) one after the other into the Raspi-commandline and hit enter to install.

>(1)-- cd craftbeerpi3
>
>(2)-- sudo apt-get install build-essential python-dev python-smbus python-pip python-imaging python-numpy git
>
>(3)-- sudo pip install pathlib
>
>(4)-- sudo pip install RPi.GPIO
>
>(5)-- sudo git clone https://github.com/adafruit/Adafruit_Python_ILI9341.git
>
>(6)-- cd Adafruit_Python_ILI9341
>
>(7)-- sudo python setup.py install

        
## Install rrdtool for python:

#You can install it with the Raspi software installer:

>(1)-- Goto options      in German Einstellungen
>
>(2)-- Add / Remove Software
>
>(3)-- Key in "rrdtools" and hit enter
>
>(4)-- choose "time-series data storage and display system (Phyton Interface)"->python-rrdtool-1.6.0-1+b1
>
>(5)-- hit apply
>
>rrdtool should be installed.

## You have to clone the CBPI3 Addon (as long as it is not offical)

>git clone https://github.com/JamFfm/TFTDisplay.git -b master --single-branch /home/pi/craftbeerpi3/modules/plugins

# Usage

>Shows the temp sensor of the Kettle (ID) in TFT_Kettle_ID in parameters.
>You can change with, hight and fontsize. I recomment 290/310 14 or 380/400 16.
>Changing these parameters do not need a reboot and are taken at once.
>To change a temp sensor you can add it to the kettle in CBPI3 or you change the Kettle ID

# Known Problems

>only for brewing-kettles not for fermentation until now
>there is an error after a while when painting the graph witch stops CBPI3: Error: too many open files

