![](https://img.shields.io/badge/CBPi%20addin-functionable_for_V3-green.svg)  ![](https://img.shields.io/github/license/JamFfm/TFTDisplay.svg?style=flat) ![](https://img.shields.io/github/last-commit/JamFfm/TFTDisplay.svg?style=flat) ![](https://img.shields.io/github/release-pre/JamFfm/TFTDisplay.svg?style=flat)



# TFTDisplay add-on for CraftBeerPi 3


CraftBeerPi 3 addon for a 2.2" or 2.8" TFT Display 240 x 320 with ILI9341 driver

With this add-on you can display a temperature graph of a **kettle** (its sensor) or of a **fermenter** on a 240 x 320 TFT SPI Display.
It is based on the ILI9341 controller.

The modul can display a temperatur graph by the help of rrdtool or show just numbers so you can watch temperature from a bit more distance.

The add-on assumes that craftberrpi3 is installed in the following path according the installation instruction (read.me) of craftberrpi3:

/home/pi/craftbeerpi3

![Test Graph](https://github.com/JamFfm/TFTDisplay/blob/master/TFTDisplay_Brew.jpg "BrewTFTDisplay 320x240")

![Test Graph](https://github.com/JamFfm/TFTDisplay/blob/master/Ferment.jpg "FermTFTDisplay 320x240")

![Test Graph](https://github.com/JamFfm/TFTDisplay/blob/master/Startscreen1.JPG  "Startcsceen")

![Test Graph](https://github.com/JamFfm/TFTDisplay/blob/master/Graphmode.JPG  "Graphikmode")

![Test Graph](https://github.com/JamFfm/TFTDisplay/blob/master/DigitMode.JPG  "Digitmode")

## Wiring 


> *Put a 48 Ohm resistor inbetween LED-Pin of TFT and the Raspi Pin.

> update: for me it also worked without the resistor, but I recommend to use one

![Wiring](https://github.com/JamFfm/TFTDisplay/blob/master/50%20Ohm%20at%20lsd%20pin.png "Wiring")

| PowerSuppy | TFT Display  | Level Shifter  | RASPI          | Pin 
| ---------- | ------------ | -------------- | -------------- | -----
| -          | SDK (MISO)   | 1HV       1LV  | GPIO  9 (MISO) | 21  
| -          | LED          | 2HV       2LV  | GPIO 18        | 12  
| -          | SCK          | 3HV       3LV  | GPIO 11 (SCLK) | 23  
| -          | SDI (MOSI)   | 4HV       4LV  | GPIO 10 (MOSI) | 19  
| 5v         | VCC          |  HV        LV  | 3v3            | 1  
| -          | GND          | GND       GND  | GND            | -   
| -          | DC           | 5HV       5LV  | GPIO 24        | 18  
| -          | RESET        | 6HV       6LV  | GPIO 25        | 22  
| -          | CS           | 7HV       7LV  | GPIO  8 (CE0)  | 24  
| -          | -            | 8HV       8LV  | -              | -   


# Installation

is a bit tricky:
You have to install the Adafruit_Python_ILI9341 and some other packages.

Most of them are already installed but they all have to be present.
After that the rrdtool has to be installed with the Raspi software-installer.
In the end you have to install the TFTDisplay addon in CraftBerrPi3 section addon.
Dont forget the reboot.

## 1. Install Adafruit_Python_ILI9341 for TFTDisplay_240x320:
Copy and paste all lines  (1) to (8) one after the other into the Raspi-commandline and hit enter to install.

```python
cd /home/pi/craftbeerpi3
sudo apt-get install build-essential python-dev python-smbus python-pip python-imaging python-numpy git
sudo pip install pathlib
sudo pip install RPi.GPIO
sudo git clone https://github.com/adafruit/Adafruit_Python_ILI9341.git
cd /home/pi/craftbeerpi3/Adafruit_Python_ILI9341
sudo python setup.py install
sudo chown -R pi /home/pi/craftbeerpi3/Adafruit_Python_ILI9341/Adafruit_ILI9341/ILI9341.py
```
        
## 2. Install rrdtool for python:

You can install it with the Raspi software installer:

(1) -- Goto options      (in German Einstellungen)

(2)-- Add / Remove Software

(3)-- Key in "rrd" and hit enter

(4)-- choose "time-series data storage and display system (runtime library)"->librrd8-1.6.0-1+b1

(5)-- choose "time-series data storage and display system (Phyton Interface)"->python-rrdtool-1.6.0-1+b1

(6)-- hit apply

you will be asked for the password and after that rrdtool should be installed.

## 3. You have to install the CBPI3 Addon

(1)-- just install from the add-on screen in Craftbeerpi3

(2)-- reboot the raspi

# Usage

Shows the temperature-sensor of the Kettle (ID) in TFT_Kettle_ID in parameters as a graph over 40 min (adjustible).
You can change width, hight and fontsize. I recomment 384, 400, 16.
Changing these parameters do not need a reboot and are used at once.
To change a temp sensor you can add it to the kettle- or fermenter in CBPI3 and/or you change the kettle- or fermenter ID in parameters. Once you start fermentation steps the fermentation graph is shown (red) with the coresponding target temperature (blue). If you only like to display a graph during Brewing steps or fermentaion steps then turn on the startscreen which will display the CraftbeerPi logo in standby mode

In the digit mode you can watch the current temperature and target temperature of the choosen kettle (ID) from the distance (look at: TFT_Kettle_ID in parameters). When the current-temperature is close to the target-temperature (<2°C or °F) then the digits turn red. So you can change the target-temperature and the coulour changes. Is the target-temperature = 0.00°C or °F the current-temperature stays white. Made that because white is better readable from distance and sometimes no target-temperature is choosen or needed. 

## Parameter

There are several parameter to change the display behavior

- TFT_Duaration: defines the amount of time to draw as graph. It is allowed to use units like m=minutes, d=days, w=weeks, M=months. However the x-axis is not shown properly in every cases. The following values do funktion well: 10m, 20m, 40m, 80m, 100m, 200m, 300m, 400m, 1M, 2M, 4M. Default is 40m

> do not input values below 6m!

- TFT_Fontsize: choose a fontsize, like 12, 14, 16, 18.
Default is 16

- TFT_Hight: Hight of the image displayed in pixel.
Default is 400

- TFT_Kettle_ID: The id of the kettle whose tempsensor is shown in the graph. The kettle id is in the sequence the kettles are listed in "Hardware Settings" beginning with 1. This has affect in Graph- or Digit- mode.

- TFT_StartscreenOn: whether the CraftBerrPi Logo is shown at the beginning and graph begins at start Steps ("on"), or showing graph at start ("off"). This works regardless if Graph- or Digit- mode. Default  is "on".

- TFT_Width: width of the image displayed in pixel.
Default is 384. This shows the x-axis, if you use 380 x-axis is not shown.

- TFT_Fermenter_ID: The id of the fermenter whose tempsensor is shown in the graph. The kettle id is in the sequence the fermenters are listed in "Hardware Settings" beginning with 1. Here also the Target Temp is shown.

- TFT_digitOn: whether the plain numbers are shown. You can watch current- and target temperature. The kettle ID is shown too. You can change it in TFT_Kettle_ID. If this parameter is "off" the Graph mode is on. Default is "off".

- TFT_RedrawTime:sometimes the display turns into white. I assume bad physical connections like wireing. Once that occurs only a reboot of CBPi3 can cure that. During brewing process this is no option. I introduced a redraw of the display at adjustable time. This parameter is the time between the redraws. A redraw is like a two times flash of the Display. It is not exactly sec. So if you have no prolems with white display give this a high number. If you have some troubles with white display then use a small number. Default is 300

# Known Problems


- X-axis is not shown properly at some TFT_Duration values
- I noticed that you need first initialise with DC 18 and RST 25 (with RST 23 there will be a false-color image for a short period). This causes a white (or false-color) screen. After that, change to DC 24 and RST 25. The latter are the GPIO I physically connected. The change is done automatically by the code. So this is only a information to the ones who know to read the code.
- if LED pin of TFT connected to Raspi GPIO 18 (RPM) brightness is low. This is a problem when using the display outside. It becomes hard to read the display at sunshine. Running the LED pin with plain 3.3V/5V is much better. The display can stand 5V but I am afrait that the Raspi can not. Therefore I used a 8 channel levelshifter and put the LED Pin of the display to 5V.This results in a much brighter display!.  Have to do a test brewing outside.
- ugly code style of a beginner :-)
- spelling mistakes
- using a different path for craftbeerpi3 than /home/pi/craftbeerpi3 will cause malfunction. So stick to the installation instruction of craftbeerpi3. This behavior is caused by my bad coding stile and may be fixed in a new version.

**Help is welcome**

# Fixed Problems

- fixed problem with too many files.
- fixed: Graph mode only for brewing-kettles not for fermentation
- fixed: wrong filepathes due to a different folder name TFTDisplay240x320-->TFTDisplay
- fixed: Digit Mode is not ready for fermentation and °F
- fixed: Display stayes white after a temporary connection problem (mostly wireing) but after reconnect the display stayes white


# Support

Report issues either in this Git section or at Facebook at the [Craftbeerpi group](https://www.facebook.com/groups/craftbeerpi/)

# Credit
Got the wiring information from this page:

http://blog.riyas.org/2014/07/

>BUT I DID NOT USE THE COMMANDS OF THIS PAGE!

I followed this page how to install and run the modules:

https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/usage

> Please do not update your firmware. It will distroy the Raspi configuration (hopefully not the hardware).

> Have a look at the installation section of this readme. You only have to follow that one.

