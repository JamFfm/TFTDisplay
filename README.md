# TFTDisplay
CraftbeerPi3 addon for a 2.2" or 2.8" TFT Display 320x240 with ILI9341 driver

With this add-on you can display something on a 240 x 320 TFT SPI Display.
It is based on the ILI9341 controller.

![](https://github.com/JamFfm/TFTDisplay/blob/master/TFT%20Graph.jpg "TFTDisplax 320x240")

(1)--I followed this how to wiring
http://blog.riyas.org/2014/07/
I put a 48 Ohm resistor inbetween LCD and the Raspi Pin.
(/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/gpio_connectio_to_tft_il9341.png)
BUT I DID NOT USE THE COMMANDS ON THIS PAGE!

(2)-- I followed this page how to install and run it:
https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/usage
Please do not update your Firmware. I will distroy thr Raspi configuration (not the hardware).
I noticed that you need first initialise with DC 18 and RST 23. This causes a white screen. After that change to DC 24 and RST 25. The latter is the GPIO I connected.

The modul can display a temperatur graph by the help of rrdtool.

# Installation
is a bit tricky:
You have to install the dafruit_Pyton_ILI9341 and some other packages.
Most of them are already insatlled but they all have to be present.
At the end the rrdtool has to be installed wit the Raspi software-installer.
In the end you have to install the addon.
Dont forget the reboot.

## Install Adafruit_Pyton_ILI9341 for TFTDisplay_240x320:

(1)-- cd craftbeerpi3

(2)-- sudo apt-get install build-essential python-dev python-smbus python-pip python-imaging python-numpy git

(3)-- sudo pip install pathlib

(4)-- sudo pip install RPi.GPIO

(5)-- sudo git clone https://github.com/adafruit/Adafruit_Python_ILI9341.git

(6)-- cd Adafruit_Python_ILI9341

(7)-- sudo python setup.py install

        
Install rrdtool for python:

## You can install it with the Raspi software installer:

(1)-- Goto options/Einstellungen

(2)-- Add / Remove Software

(3)-- Key in "rrdtools" and hit enter

(4)-- choose "time-series data storage and display system (Phyton Interface)"->python-rrdtool-1.6.0-1+b1

(5)-- hit apply

rrdtool should be installed.

## You have to clon the Addon (as long as ist is not offical)

git clone https://github.com/JamFfm/TFTDisplay.git -b master --single-branch /home/pi/craftbeerpi3/modules/plugins

# Usage

Shows the temp sensor of the Kettle (ID) in TFT_Display_Kettle_ID in parameters.

# Known Problems

TFT_Display_hight and TFT_Display_with in parameters is currently not used 
