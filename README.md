# TFTDisplay
CraftbeerPi3 addon for a 2.2" or 2.8" TFT Display 320x240 with ILI9341 driver

With this add-on you can display something on a 240 x 320 TFT SPI Display.
It is based on the ILI9341 controller.

(1)--I followed this how to wiring
http://blog.riyas.org/2014/07/
I put a 48 Ohm resistor inbetween LCD and the Raspi Pin.
![GitHub Logo](/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/gpio_connectio_to_tft_il9341.png)

(2)-- I followed how to install and run it:
https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/usage
Please do not update your Firmware. I will distroy thr Raspi configuration (not the hardware).
I noticed that you need first initialise with DC 18 and RST 23. This causes a white screen. After that change to DC 24 and RST 25. The latter is the GPIO I connected.

The modul can display a temperatur graph by the help of rrdtool.

# Installation
is a bit tricky:

Install Adafruit_Pyton_ILI9341 for TFTDisplay_240x320:

(1)-- sudo apt-get install build-essential python-dev python-smbus python-pip python-imaging python-numpy git
(2)-- sudo pip install pathlib
(3)-- sudo pip install RPi.GPIO
(4)-- sudo git clone https://github.com/adafruit/Adafruit_Python_ILI9341.git
(5)-- cd Adafruit_Python_ILI9341
(6)-- sudo python setup.py install
        
Install rrdtool for python:

You can install it with the Raspi software insataller:
(1)--Goto options/Einstellungen
(2)--Add / Remove Software
(3)--Key in "rrdtools" and hit enter
(4)--choose "time-series data storage and display system (Phyton Interface)"->python-rrdtool-1.6.0-1+b1
(5)--hit apply

rrdtool should be installed.

