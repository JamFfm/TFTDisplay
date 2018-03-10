#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# Version 1.1.0.0
# Assembled by JamFfm

from modules import cbpi, app
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pathlib import Path
import os, re, thread, time
import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import rrdtool




global used
used = 0
global Keepstandby
Keepstandby = 0
global disp
disp = None

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

def TFT240x320(imagefile):
    global used
    if used == 0:
        DC = 18
        RST = 23
        used = 1
    else:
        DC = 24
        RST = 25
        used = used + 1

    SPI_PORT = 0
    SPI_DEVICE = 0

    #create spi connection
    spidevice=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000)
    # Create TFT LCD display class
    disp = TFT.ILI9341(DC, rst=RST, spi=spidevice)   
    #disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))    

    # Initialize display only twice
    global used
    if used == 1:
        disp.begin()
        
    elif used == 2:
        disp.begin()
    else:
        pass
        cbpi.app.logger.info('TFTDisplay  - no beginn display %s' % (used))

    # Load default font.
    #font = ImageFont.load_default()
        
    # Load an image
    #imagefile = ('/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.png')
    image = Image.open(imagefile)
    #cbpi.app.logger.info('Loading image %s' % (imagefile))
    
    # Resize the image and rotate it so it's 240x320 pixels.
    image = image.rotate(90).resize((240, 320))
    #cbpi.app.logger.info('image rotate')

    # Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
    #draw_rotated_text(image, 'Craftbeerpi 3.0.2', (150, 120), 90, font, fill=(255,255,255))
    #cbpi.app.logger.info('TFTDisplay  - write text')

    # Draw the image on the display hardware.
    disp.display(image)
    #cbpi.app.logger.info('TFTDisplay  - image display')
    spidevice.close()
    

def createRRDdatabase():
    rrdtool.create(
    "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd",
    "--start", "now",
    "--step", "5",
    "RRA:AVERAGE:0.5:1:1200",
    "DS:sensor1:GAUGE:15:10:100" )
    cbpi.app.logger.info('TFTDisplay  - createRRDdatabase')

def updateRRDdatabase(kid):
    pfad = ("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd")
    #cbpi.app.logger.info("TFTDisplay  - %s" % (pfad))
    rrdtool.update("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd", "N:%s" % (Temp(kid)));
    #cbpi.app.logger.info('TFTDisplay  - rrd update')
    
def graphAsFile():
    path = "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.png"
    rrdtool.graph (path,
    "--imgformat", "PNG",
        "--start", "-40m",
        "--font", "DEFAULT:%s" % str((TFTfontsize)),        
        "--grid-dash", "0:10",
        "-w %s" % (str(TFTwith)), "-h %s" % (str(TFThight)),
        #"-w 290", "-h 310",                   
        #"--full-size-mode",
        "--no-gridfit",
        #"--vertical-label", " Degree Celsius",
        "--slope-mode", #smoother line
        "--use-nan-for-all-missing-data",
        "DEF:temp=/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd:sensor1:AVERAGE",
        "LINE3:temp#ff0000:sensor1")
    #cbpi.app.logger.info('TFTDisplay  - graph created')
    #https://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html here all options are listed

def rrdDateiVorhanden():
    my_file = Path("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd")
    cbpi.app.logger.info('TFTDisplay  - check if file brewtemp.rrd exists?')
    if my_file.exists():
        cbpi.app.logger.info('TFTDisplay  - File brewtemp.rrd exists')
    else:
        createRRDdatabase()
        cbpi.app.logger.info('TFTDisplay  - File brewtemp.rrd created')
    pass

def Temp(kkid):
    #cbpi.app.logger.info("TFTDisplay  - Temp ermitteln")
    current_sensor_value_id3 = (cbpi.get_sensor_value(int(cbpi.cache.get("kettle").get(int(kkid)).sensor)))
    curTemp = ("%6.2f" % (float(current_sensor_value_id3)))
    #cbpi.app.logger.info("TFTDisplay  - Temp: %s" % (curTemp))
    return curTemp

def set_TFTh():  
    TFThoehe = (cbpi.get_config_parameter("TFT_Hight", None))
    if TFThoehe is None:
        cbpi.add_config_parameter("TFT_Hight", 310, "number", "Choose TFTDisplay hight, default 310/400, NO! CBPi reboot required")
        TFThoehe = (cbpi.get_config_parameter("TFT_Hight", None))
        cbpi.app.logger.info("TFTDisplay  - TFThoehe added: %s" % (TFThoehe))
    #cbpi.app.logger.info("TFTDisplay  - TFThoehe read Database: %s" % (TFThoehe))
    return TFThoehe


def set_TFTw():  
    TFTbr = (cbpi.get_config_parameter("TFT_Width", None))
    if TFTbr is None:
        cbpi.add_config_parameter("TFT_Width", 290, "number", "Choose TFTDisplay width, default 290/380, NO! CBPi reboot required")
        TFTbr = (cbpi.get_config_parameter("TFT_Width", None))
        cbpi.app.logger.info("TFTDisplay  - TFTbr added: %s" % (TFTbr))
    #cbpi.app.logger.info("TFTDisplay  - TFTbr read Database: %s" % (TFTbr))
    return TFTbr

def set_parameter_id3():  
    TFTid3 = cbpi.get_config_parameter("TFT_Kettle_ID", None)
    if TFTid3 is None:
        TFTid3 = 1
        cbpi.add_config_parameter ("TFT_Kettle_ID", 1, "number", "Choose kettle (Number), NO! CBPi reboot required")      
        #cbpi.app.logger.info("TFTDisplay  - TFTid added: %s" % (TFTid3))
    return TFTid3

def set_fontsize():
    fosi = cbpi.get_config_parameter("TFT_Fontsize", None)
    if fosi is None:
        fosi = 14
        cbpi.add_config_parameter ("TFT_Fontsize", 14, "number", "Choose fontsize of grid default is 14, NO! CBPi reboot required")
        #cbpi.app.logger.info("TFTDisplay  - TFT_Fontsize added: %s" % (fosi))
    return fosi

def set_StartscreenOn():
    startsc = cbpi.get_config_parameter("TFT_StartscreenOn", None)
    if startsc is None:
        startsc = "on"
        cbpi.add_config_parameter ("TFT_StartscreenOn", "on", "select", "skip the CBPI Logo and start chart at power on, NO! CBPi reboot required", ["on", "off"])
        cbpi.app.logger.info("TFTDisplay  - TFT_StartscreenOn: %s" % (startsc))
    return startsc

@cbpi.initalizer(order=3100)
def initTFT(app):       

    rrdDateiVorhanden()
    try:
        cbpi.app.logger.info("TFTDisplay  - TFTKetteID:     %s" % (set_parameter_id3()))
        cbpi.app.logger.info("TFTDisplay  - TFThight:       %s" % (set_TFTh()))
        cbpi.app.logger.info("TFTDisplay  - TFTwith:        %s" % (set_TFTw()))
        cbpi.app.logger.info("TFTDisplay  - TFTfontsize:    %s" % (set_fontsize()))
    except:
        pass
    
#end of init    
    
    @cbpi.backgroundtask(key="TFT240x320job", interval=5)
    def TFT240x320job(api):
        ## YOUR CODE GOES HERE    
        ## This is the main job
        
        global id3
        id3 = set_parameter_id3()

        global TFThight
        TFThight = set_TFTh()

        global TFTwith
        TFTwith = set_TFTw()

        global TFTfontsize
        TFTfontsize = set_fontsize()

        global StartscreenOn
        StartscreenOn = set_StartscreenOn()

        s = cbpi.cache.get("active_step")
        
        if s is not None or StartscreenOn == "off":
            #Brewing Starts and so Chart starts or startscreen is off
            
            updateRRDdatabase(id3)
            
            graphAsFile()

            imagefile = ('/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.png')

            TFT240x320(imagefile)
            #thread.start_new_thread(TFT240x320,(imagefile,))

            global Keepstandby
            Keepstandby = 0
            
        else:
            #Standby screen

            global Keepstandby
            
            if Keepstandby < 2:
                StandbyPath = "/home/pi/craftbeerpi3/modules/ui/static/logo.png"
                TFT240x320(StandbyPath)
                #thread.start_new_thread(TFT240x320,(imagefile))
                global Keepstandby
                Keepstandby = Keepstandby + 1
            else:
                #just keep the image on the scrreen without redraw
                pass

