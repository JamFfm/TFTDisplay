# TFTDisplay
CraftbeerPi3 addon for a 2.2" or 2.8" TFT Display 240 x 320 with ILI9341 driver

With this add-on you can display a Temperature Graph of a Kettle (its sensor) on a 240 x 320 TFT SPI Display.
It is based on the ILI9341 controller.

The modul can display a temperatur graph by the help of rrdtool.

![Test Graph](https://github.com/JamFfm/TFTDisplay/blob/master/Graph.JPG "TFTDisplax 320x240")

## I followed this link **only** for wiring

http://blog.riyas.org/2014/07/

>BUT I DID NOT USE THE COMMANDS OF THIS PAGE!

> *I put a 48 Ohm resistor inbetween LED-Pin of TFT and the Raspi Pin.

> update: for me it also worked without the resistor, but I recommend to use one

![Wiring](https://github.com/JamFfm/TFTDisplay/blob/master/50%20Ohm%20at%20lsd%20pin.png "Wiring")

## I followed this page how to install and run the modules:

https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/usage

> Please do not update your firmware. It will distroy the Raspi configuration (hopefully not the hardware).

> Have a look at the installation section of this readme. You only have to follow that one.



# Installation

is a bit tricky:
You have to install the Adafruit_Pyton_ILI9341 and some other packages.

Most of them are already installed but they all have to be present.
After that the rrdtool has to be installed with the Raspi software-installer.
In the end you have to install the addon.
Dont forget the reboot.

## 1. Install Adafruit_Pyton_ILI9341 for TFTDisplay_240x320:
Copy and paste all lines  (1) to (7) one after the other into the Raspi-commandline and hit enter to install.

(1)-- cd craftbeerpi3

(2)-- sudo apt-get install build-essential python-dev python-smbus python-pip python-imaging python-numpy git

(3)-- sudo pip install pathlib

(4)-- sudo pip install RPi.GPIO

(5)-- sudo git clone https://github.com/adafruit/Adafruit_Python_ILI9341.git

(6)-- cd Adafruit_Python_ILI9341

(7)-- sudo python setup.py install

        
## 2. Install rrdtool for python:

You can install it with the Raspi software installer:

(1)-- Goto options      in German Einstellungen

(2)-- Add / Remove Software

(3)-- Key in "rrdtools" and hit enter

(4)-- choose "time-series data storage and display system (Phyton Interface)"->python-rrdtool-1.6.0-1+b1

(5)-- hit apply

rrdtool should be installed.

## 3. You have to clone the CBPI3 Addon (as long as it is not offical)

(1)-- git clone https://github.com/JamFfm/TFTDisplay.git -b master --single-branch /home/pi/craftbeerpi3/modules/plugins

**or** when official

(1)-- just install from the add-on screen in Craftbeerpi3

# Usage

Shows the temperature-sensor of the Kettle (ID) in TFT_Kettle_ID in parameters as a graph over 40 min (adjustible).
You can change width, hight and fontsize. I recomment 384, 400, 16.
Changing these parameters do not need a reboot and are used at once.
To change a temp sensor you can add it to the kettle in CBPI3 and/or you change the Kettle ID in parameters.

## Parameter

There are several parameter to change the display behavior

- TFT_Duaration: defines the amount of time to draw as graph. It is allowed to use units like m=minutes, d=days, w=weeks, M=months. However the x-axis is not shown properly in every cases. The following values do funktion well: 10m, 20m, 40m, 80m, 100m, 200m, 300m, 400m, 1M, 2M, 4M.

> do not input values below 6m!

Default is 40m

- TFT_Fontsize: choose a fontsize, like 12, 14, 16, 18.
Default is 16

- TFT_Hight: Hight of the image displayed in pixel.
Default is 400

- TFT_Kettle_ID: The id of the kettle whose tempsensor is shown in the graph. The kettle id is in the sequence the kettles are listed in "Hardware Settings" beginning with 1

- TFT_StartscreenOn: whether the CraftBerrPi Logo is shown at the beginning and graph begins at start Steps ("on"), or showing graph at start ("off")

- TFT_Width: width of the image displayed in pixel.
Default is 384. This shows the x-axis, if you use 380 x-axis is not shown.

# Known Problems

- only for brewing-kettles not for fermentation until now 
- The responce to clicks in the gui may become a little bit delayed
- X-axis is not shown properly at some TFT_Duration values
- I noticed that you need first initialise with DC 18 and RST 25 (with RST 23 there will be a false-color image for a short period). This causes a white (or false-color screen). After that change to DC 24 and RST 25. The latter are the GPIO I physically connected. The change is done automatically by the code.
- cant adjust the brightness and backlight

**Help is welcome.**

# Fixed Problems

Fixed problem with too many files.

# Support

Report issues either in this Git section or at Facebook in the [Craftbeerpi group](https://www.facebook.com/groups/craftbeerpi/)

