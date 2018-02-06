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
# Version 1.0.0.0

from modules import cbpi, app
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os, re, thread, time
import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import rrdtool
from pathlib import Path



global used
used = 0
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

def TFT240x320():
    ## YOUR CODE GOES HERE    
    ## This is the main job
    global used
    if used == 0:
        DC = 18
        RST = 23
        used = 1
    else:
        DC = 24
        RST = 25

    SPI_PORT = 0
    SPI_DEVICE = 0

    # Create TFT LCD display class
    disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))    

    # Initialize display.
    disp.begin()

    # Load default font.
    font = ImageFont.load_default()
        
    # Load an image
    #imagefile = ('/home/pi/craftbeerpi3/modules/ui/static/logo.png')
    imagefile = ('/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.png')
    image = Image.open(imagefile)
    #cbpi.app.logger.info('Loading image %s' % (imagefile))

    # Resize the image and rotate it so it's 240x320 pixels.
    image = image.rotate(90).resize((240, 320))
    #cbpi.app.logger.info('image rotate')

    # Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
    #draw_rotated_text(image, 'Craftbeerpi 3.0.2', (150, 120), 90, font, fill=(255,255,255))
    #cbpi.app.logger.info('write text')

    # Draw the image on the display hardware.
    disp.display(image)
    cbpi.app.logger.info('image display')

def createRRDdatabase():
    rrdtool.create(
    "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd",
    "--start", "now",
    "--step", "5",
    "RRA:AVERAGE:0.5:1:1200",
    "DS:sensor1:GAUGE:15:10:100" )
    cbpi.app.logger.info('createRRDdatabase')

def updateRRDdatabase():
    pfad = ("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd")
    cbpi.app.logger.info(pfad)
    rrdtool.update("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd", "N:%s" % (Temp()));
    cbpi.app.logger.info('rrd update')
	
def graphAsFile():
    path = "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.png"
    rrdtool.graph (path,
	"--imgformat", "PNG",
    	"--start", "-40m",
        #"-w %s" % (TFTh()),
        #"-h %s" % (TFTw()),
        #"%s" % TFTh(),
        #"%s" % TFTw(),
        "-w 290", "-h 310",
    	"DEF:temp=/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd:sensor1:AVERAGE",
    	"LINE3:temp#ff0000:sensor1")
    cbpi.app.logger.info('graph created')

def rrdDateiVorhanden():
    my_file = Path("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd")
    cbpi.app.logger.info('dateivorhanden?')
    if my_file.exists():
        cbpi.app.logger.info('File brewtemp.rrd exists')
    else:
        createRRDdatabase()
        cbpi.app.logger.info('File brewtemp.rrd created')
    pass

def Temp():
    #read the current temperature of kettle with id2 from parameters  
    current_sensor_value_id2 = (cbpi.get_sensor_value(int(cbpi.cache.get("kettle").get(id2).sensor)))                            
    curTemp = ("%6.2f" % (float(current_sensor_value_id2)))
    cbpi.app.logger.info("%s" % (curTemp))
    return curTemp

def set_parameter_id2():  
    TFTid = cbpi.get_config_parameter("TFTDisplay_Kettle_ID",None)
    if TFTid is None:
        cbpi.add_config_parameter("TFTDisplay_Kettle_ID", 1, "number", "Choose Kettle (Number), CBPi reboot required")
        TFTid = cbpi.get_config_parameter("TFTDisplay_Kettle_ID",None)
        cbpi.app.logger.info("TFTid%s" % (TFTid))
    return TFTid

def TFTh():  
    TFThoehe = cbpi.get_config_parameter("TFTDisplay_hight",None)
    if TFThoehe is None:
        cbpi.add_config_parameter("TFTDisplay_hight", 290, "number", "Choose TFTDisplay hight, CBPi reboot required")
        TFThoehe = str(cbpi.get_config_parameter("TFTDisplay_hight",None))
        cbpi.app.logger.info("TFThoehe: %s" % (TFThoehe))
    return ("-w %s" % TFThoehe)

def TFTw():  
    TFTbr = cbpi.get_config_parameter("TFTDisplay_width",None)
    if TFTbr is None:
        cbpi.add_config_parameter("TFTDisplay_width", 310, "number", "Choose TFTDisplay_width, CBPi reboot required")
        TFTbr = str(cbpi.get_config_parameter("TFTDisplay_width",None))
        cbpi.app.logger.info("TFTbr: %s" % (TFTbr))
    return ("-h %s" % TFTbr)

@cbpi.initalizer(order=3010)
def initTFT(app):
    ##Background Task to load the data    
    global id2
    id2 = int(set_parameter_id2())
    rrdDateiVorhanden()
    
    @cbpi.backgroundtask(key="TFT240x320job", interval=5)
    def TFT240x320job(api):
        ## YOUR CODE GOES HERE    
        ## This is the main job
        updateRRDdatabase()
        cbpi.app.logger.info("TFTh: %s" % (TFTh()))
        cbpi.app.logger.info("TFTw: %s" % (TFTw()))
        graphAsFile()
        thread.start_new_thread(TFT240x320,())
#End of init
