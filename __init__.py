#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ILI9341 lib:
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
#
# TFTDisplay Version 1.3.5.6
# Assembled by JamFfm
#
# 14.03.2018 changed DC and RST for init display, change default font size, add title
# 16.03.2018 added alternative autoscale of graph, show XX.x numbers on Y-axis
# 18.03.2018 optimized code in function updateRRDdatabase(kid) (2 times path)
# 18.03.2018 add parameter TFT_Duration in parameters so you can choose which period to show
# 20.03.2018 change init values of createRRDdatabase(), to support long time graphs
# 20.03.2018 build in first steps for ferment support
# 21.03.2018 duration is displayed at Title
# 21.03.2018 change if loop to detect ferm mode, femTemp(femid), set fermentationOn(), etc added
# 09.04.2018 Ferm or Brew mode displayed in Title, finished fermentation support
# 11.04.2018 Added Target Temp-Graph in Ferm mode
# 04.05.2018 delete some code-lines not needed
# 09.06.2018 changed File path name because folder changed from TFTDisplay240x320 to TFTDisplay
# 09.06-2018 finished assembly in the brewcase, fixed a missing installation step in readme
# 27.07.2018 added digit mode
# 28.07.2018 added kettle no in digit display
# 29.07.2018 added Fahrenheit support
# 29.07.2018 added fermentation support for digit modus
# 29.07.2018 fixed a mistake concerning colour in digit fermentatin mode
# 10.08.2018 changed interval in backgroundtask from 5 to 2
# 03.09.2018 added sleep(3) at init to avoid peaks at start or restart of CBPi3
# 13.04.2019 added TFTredrawtime to redraw after set time (reactivates display when wiring is toggling)
# 20.08.2019 Python 3 migration ready fix, maybe some import have to be changed



from modules import cbpi, app
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pathlib import Path
import os, re, threading, time
import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import rrdtool
import modules
import time

global used
used = 0
global Keepstandby
Keepstandby = 0
global femid
femid = 0
global curfemtargTemp
curfemtargTemp = 0
global TFTredrawtime
TFTredrawtime = 0

def TFT240x320(imagefile):
    global used
    global DC
    global RST
    global TFTredrawtime
    
    if used == 0:
        DC = 18
        RST = 25
        used = 1

    elif used == 1:
        DC = 24
        RST = 25
        used = 2

    else:        
        used = used + 1
    pass

    SPI_PORT = 0
    SPI_DEVICE = 0

    # create spi connection
    spidevice = SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000)
    # Create TFT LCD display class
    disp = TFT.ILI9341(DC, rst=RST, spi=spidevice)   
    
    # Initialize display only twice
    if used < 3:
        disp.begin()        
    elif used > (TFTredrawtime):  
        used = 1
    pass
        
    # Load an image
    image = Image.open(imagefile)
    # cbpi.app.logger.info('Loading image %s' % (imagefile))
    
    # Resize the image and rotate it so it's 240x320 pixels.
    image = image.rotate(90).resize((240, 320))
    # Draw the image on the display hardware.
    disp.display(image)

    # Close SPI Connection to avoid "too many files open error"
    spidevice.close()


def Digit(kettleID):
    global used
    global DC
    global RST
    global TFTredrawtime
    
    if used == 0:
        DC = 18
        RST = 25
        used = 1

    elif used == 1:
        DC = 24
        RST = 25
        used = 2

    else:
        used = used + 1
    pass

    SPI_PORT = 0
    SPI_DEVICE = 0

    #create spi connection
    spidevice = SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000)
    # Create TFT LCD display class
    disp = TFT.ILI9341(DC, rst=RST, spi=spidevice)   
    
    # Initialize display only twice
    if used < 3:
        disp.begin()        
    elif used > (TFTredrawtime):
        used = 1
    pass

    # Clear the display to a black background.
    # Can pass any tuple of red, green, blue values (from 0 to 255 each).
    disp.clear((0, 0, 0))

    # Get a PIL Draw object to start drawing on the display buffer.
    draw = disp.draw()
    
    font = ImageFont.truetype('/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fonts/Share-TechMono.ttf', 80)
    fontmin = ImageFont.truetype('/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fonts/Share-TechMono.ttf', 20)

    def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
        # Get rendered font width and height.
        draw = ImageDraw.Draw(image)
        width, height = draw.textsize(text, font=font)
        # Create a new image with transparent background to store the text.
        textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        # Render the text.
        textdraw = ImageDraw.Draw(textimage)
        textdraw.text((0, 0), text, font=font, fill=fill)
        # Rotate the text image.
        rotated = textimage.rotate(angle, expand=1)
        # Paste the text into the image, using it as a mask for transparency.
        image.paste(rotated, position, rotated)

    # Write lines of text on the buffer, rotated 90 degrees counter clockwise.
    # different text for fermentation mode and brew mode

    if is_fermenter_step_running() == "active":
        
        TextDigit = (u"%6.2f%s" % (float(femTemp(kettleID)),(tftunit())))
    
        TextDigitSetTemp = (u"%6.2f%s" % (float(femTargTemp(kettleID)),(tftunit())))

        # change colour when temp is 2 C/F away from targettemp
        Diff = (float(femTargTemp(kettleID))-float(femTemp(kettleID)))
        # cbpi.app.logger.info("TFTDisplay  - Diff fermTarget to fermTemp %6.2f" % (Diff))

        if Diff > 2 or Diff < -2 and (float(femTargTemp(kettleID))) != 0:
            fill1 = (255, 0, 0)
        else:
            fill1 = (255,255,255)
        
        draw_rotated_text(disp.buffer, u"Curr. temperature of fermeter", (0, 0), 90, fontmin, fill=(255,255,255))
        draw_rotated_text(disp.buffer, TextDigit, (20, 10), 90, font, fill1)
        draw.line((105, 0, 105, 320), fill=(0,255,0), width=3)
        draw_rotated_text(disp.buffer, (u"Temperat. of fermeter no %s " % (kettleID)), (110, 0), 90, fontmin, fill=(0,255,0))
        draw.line((135, 0, 135, 320), fill=(0,255,0), width=3)
        draw_rotated_text(disp.buffer, TextDigitSetTemp, (135, 10), 90, font, fill=(255,255,0))
        draw_rotated_text(disp.buffer, u"Target temperat. of fermenter", (215, 0), 90, fontmin, fill=(255,255,0))

    else:

        TextDigit = (u"%6.2f%s" % (float(Temp(kettleID)), (tftunit())))
    
        TextDigitSetTemp = (u"%6.2f%s" % (float(TempTargTemp(kettleID)), (tftunit())))

        # change colour when temp is 2 C/F close to targettemp
        Diff = (float(TempTargTemp(kettleID))-float(Temp(kettleID)))
        # cbpi.app.logger.info("TFTDisplay  - Diff Target to Temp %6.2f" % (Diff))

        if Diff < 2 and (float(TempTargTemp(kettleID))) != 0:
            fill1 = (255, 0, 0)
        else:
            fill1 = (255,255,255)

        draw_rotated_text(disp.buffer, u"Current temperature of kettle", (0, 0), 90, fontmin, fill=(255,255,255))
        draw_rotated_text(disp.buffer, TextDigit, (20, 10), 90, font, fill1)
        draw.line((105, 0, 105, 320), fill=(0,255,0), width=3)
        draw_rotated_text(disp.buffer, (u"Temperatures of kettle no %s " % (kettleID)), (110, 0), 90, fontmin, fill=(0,255,0))
        draw.line((135, 0, 135, 320), fill=(0,255,0), width=3)
        draw_rotated_text(disp.buffer, TextDigitSetTemp, (135, 10), 90, font, fill=(255,255,0))
        draw_rotated_text(disp.buffer, u"Target temperature of kettle", (215, 0), 90, fontmin, fill=(255,255,0))

    # Write buffer to display hardware, must be called to make things visible on the display!
    disp.display()
    
    # Close SPI Connection to avoid "too many files open error"
    spidevice.close()
    
    
def createRRDdatabase():
    rrdtool.create(
        "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/brewtemp.rrd",
        "--start", "now",
        "--step", "5",
        "DS:tempsensor:GAUGE:30:-10:110",
        "RRA:AVERAGE:0.5:1:10d",
        "RRA:AVERAGE:0.5:60:90d",
        "RRA:AVERAGE:0.5:3600:540d",
        "RRA:AVERAGE:0.5:86400:3600d",
    )
    cbpi.app.logger.info('TFTDisplay  - RRDdatabase brewtemp.rrd created')

def createRRDdatabaseFerment():
    rrdtool.create(
        "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fermtemp.rrd",
        "--start", "now",
        "--step", "5",
        "DS:tempsensor:GAUGE:30:-10:110",
        "DS:targettemp:GAUGE:30:-10:110",
        "RRA:AVERAGE:0.5:1:10d",
        "RRA:AVERAGE:0.5:60:90d",
        "RRA:AVERAGE:0.5:3600:540d",
        "RRA:AVERAGE:0.5:86400:3600d",
    )  
    cbpi.app.logger.info('TFTDisplay  - RRDdatabase fermtemp.rrd created')


def updateRRDdatabase(kid):
    # kid is the TFT_Kettle_ID from parameters
    pfad = ("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/brewtemp.rrd")    
    rrdtool.update(pfad, "N:%s" % (Temp(kid)));
    # cbpi.app.logger.info('TFTDisplay  - rrd update')

def updateRRDdatabaseFerment(fid):
    # fid is the TFT_Fermenter_ID from parameters
    pfad = ("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fermtemp.rrd")
    rrdtool.update(pfad, "N:%s:%s" % (femTemp(fid), femTargTemp(fid)));
    # cbpi.app.logger.info('TFTDisplay  - rrdferm update')
    
def graphAsFile(path_of_image):
    # path = "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/brewtemp.png"
    path = path_of_image
    rrdtool.graph(
        path,
        "--imgformat", "PNG",
        # "--start", "-40m",
        "--start", "%s" % str((TFTduration)),
        "--font", "DEFAULT:%s" % str((TFTfontsize)),
        "--title", "CBPi3 Brew time=%s,Temp [°%s]" % ((str((TFTduration))[1:]), str(tftunit()[1:])),
        "--grid-dash", "0:10",
        "-w %s" % (str(TFTwith)), "-h %s" % (str(TFThight)),
        # "-w 290", "-h 310",
        # "--full-size-mode",
        # "--no-gridfit",
        # "--vertical-label", "Degree Celsius °C",
        # "--alt-y-grid",
        # "--color", "CANVAS#000000",
        "--left-axis-format", "%.1lf",
        "--alt-autoscale",  # command this line to change the x-axis scale behavior
        "--no-legend",
        "--slope-mode",     # smoother line
        "--use-nan-for-all-missing-data",
        "DEF:temp=/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/brewtemp.rrd:tempsensor:AVERAGE",
        "LINE3:temp#ff0000:tempsensor")
    # cbpi.app.logger.info('TFTDisplay  - graph created')
    # https://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html here all options are listed

def graphAsFileFerm(path_of_image):
    path = "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fermtemp.png"
    rrdtool.graph(
        path,
        "--imgformat", "PNG",
        "--start", "%s" % str((TFTduration)),
        "--font", "DEFAULT:%s" % str((TFTfontsize)),
        "--title", "CBPi3 Ferm time=%s,Temp [°%s]" % ((str((TFTduration))[1:]),str(tftunit()[1:])),
        "--grid-dash", "0:10",
        "-w %s" % (str(TFTwith)), "-h %s" % (str(TFThight)),
        "--left-axis-format", "%.1lf",
        "--alt-autoscale",  # command this line to change the x-axis scale behavior
        "--no-legend",
        "--slope-mode",     # smoother line
        "--use-nan-for-all-missing-data",
        "DEF:temp=/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fermtemp.rrd:tempsensor:AVERAGE",
        "DEF:targtemp=/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fermtemp.rrd:targettemp:AVERAGE",
        "LINE3:temp#ff0000:tempsensor",
        "LINE3:targtemp#0000ff:targettemp")
    # cbpi.app.logger.info('TFTDisplay  - fermgraph created')
    # https://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html here all options are listed

def rrdDateiVorhanden():
    my_file = Path("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/brewtemp.rrd")
    my_fermfile = Path("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fermtemp.rrd")
    cbpi.app.logger.info('TFTDisplay  - check if file brewtemp.rrd exists?')

    if my_file.exists():
        cbpi.app.logger.info('TFTDisplay  - File brewtemp.rrd exists')
    else:
        createRRDdatabase()
        # cbpi.app.logger.info('TFTDisplay  - File brewtemp.rrd created')
    pass

    if my_fermfile.exists():
        cbpi.app.logger.info('TFTDisplay  - File fermtemp.rrd exists')
    else:
        createRRDdatabaseFerment()
        # cbpi.app.logger.info('TFTDisplay  - File fermtemp.rrd created')
    pass

def Temp(kkid):
    # cbpi.app.logger.info("TFTDisplay  - Temp ermitteln")
    current_sensor_value_id3 = (cbpi.get_sensor_value(int(cbpi.cache.get("kettle").get(int(kkid)).sensor)))
    curTemp = ("%6.2f" % (float(current_sensor_value_id3)))
    # cbpi.app.logger.info("TFTDisplay  - Temp: %s" % (curTemp))
    return curTemp

def TempTargTemp(temptargid):
    # cbpi.app.logger.info("TFTDisplay  - Target Temp ermitteln")
    current_sensor_value_temptargid = (cbpi.cache.get("kettle")[(int(temptargid))].target_temp)
    targTemp = ("%6.2f" % (float(current_sensor_value_temptargid)))
    # cbpi.app.logger.info("TFTDisplay  - TargTemp: %s" % (targTemp))
    return targTemp

def femTemp(femid):
    # cbpi.app.logger.info("TFTDisplay  - ferm Temp ermitteln")
    current_sensor_value_femid = (cbpi.get_sensor_value(int(cbpi.cache.get("fermenter").get(int(femid)).sensor)))
    curfemTemp = ("%6.2f" % (float(current_sensor_value_femid)))
    # cbpi.app.logger.info("TFTDisplay  - FermTemp: %s" % (curfemTemp))
    return curfemTemp

def femTargTemp(femtargid):
    # cbpi.app.logger.info("TFTDisplay  - ferm Temp ermitteln")
    current_sensor_value_femtarid = (cbpi.cache.get("fermenter")[(int(femtargid))].target_temp)
    curfemtargTemp = ("%6.2f" % (float(current_sensor_value_femtarid)))
    # cbpi.app.logger.info("TFTDisplay  - FermTargTemp: %s" % (curfemtargTemp))
    return curfemtargTemp

def tftunit():
    unit = u"°%s" % (cbpi.get_config_parameter("unit", None))
    # cbpi.app.logger.info("TFTDisplay  - TFTunit: %s" % (unit))
    return unit

def is_fermenter_step_running():
    for key, value2 in cbpi.cache["fermenter_task"].items():
        if value2.state == "A":
            return "active"
        else:
            pass

def set_TFTh():
    TFThoehe = (cbpi.get_config_parameter("TFT_Hight", None))
    if TFThoehe is None:
        cbpi.add_config_parameter("TFT_Hight", 400, "number", "Choose TFTDisplay hight [pixel], default 400, NO! CBPi reboot required")
        TFThoehe = (cbpi.get_config_parameter("TFT_Hight", None))
        cbpi.app.logger.info("TFTDisplay  - TFThoehe added: %s" % (TFThoehe))
    return TFThoehe

def set_TFTw():
    TFTbr = (cbpi.get_config_parameter("TFT_Width", None))
    if TFTbr is None:
        cbpi.add_config_parameter("TFT_Width", 388, "number", "Choose TFTDisplay width [pixel], default 388, NO! CBPi reboot required")
        TFTbr = (cbpi.get_config_parameter("TFT_Width", None))
        cbpi.app.logger.info("TFTDisplay  - TFTbr added: %s" % (TFTbr))
    return TFTbr

def set_parameter_id3():
    TFTid3 = cbpi.get_config_parameter("TFT_Kettle_ID", None)
    if TFTid3 is None:
        TFTid3 = 1
        cbpi.add_config_parameter ("TFT_Kettle_ID", 1, "number", "Choose kettle (Number), NO! CBPi reboot required")      
        cbpi.app.logger.info("TFTDisplay  - TFTid added: %s" % (TFTid3))
    return TFTid3

def set_fontsize():
    fosi = cbpi.get_config_parameter("TFT_Fontsize", None)
    if fosi is None:
        fosi = 16
        cbpi.add_config_parameter ("TFT_Fontsize", 16, "number", "Choose fontsize of grid default is 16, NO! CBPi reboot required")
        cbpi.app.logger.info("TFTDisplay  - TFT_Fontsize added: %s" % (fosi))
    return fosi

def set_StartscreenOn():
    startsc = cbpi.get_config_parameter("TFT_StartscreenOn", None)
    if startsc is None:
        startsc = "on"
        cbpi.add_config_parameter ("TFT_StartscreenOn", "on", "select", "Skip the CBPI Logo and start chart of kettle at power on, NO! CBPi reboot required", ["on", "off"])
        cbpi.app.logger.info("TFTDisplay  - TFT_StartscreenOn added: %s" % (startsc))
    return startsc

def set_duration():
    dur = cbpi.get_config_parameter("TFT_Duration", None)
    if dur is None:
        dur = "40m"
        cbpi.add_config_parameter ("TFT_Duration", "40m", "string", "Choose time elapsed to be displayed, default is 40m (40 minutes), have a look at readme, NO! CBPi reboot required")        
        cbpi.app.logger.info("TFTDisplay  - TFT_Duration added: %s" % (dur))
    dur = ("-%s" % (dur))
    return dur

def set_FermentationOn():
    fermon = cbpi.get_config_parameter("TFT_Fermenter_ID", None)
    if fermon is None:
        fermon = 1
        cbpi.add_config_parameter ("TFT_Fermenter_ID", 1, "number", "Choose fermenter (Number) NO! CBPi reboot required")
        cbpi.app.logger.info("TFTDisplay  - TFT_Fermenter_ID added: %s" % (fermon))
    return fermon

def set_DigitOn():
    digit = cbpi.get_config_parameter("TFT_digitOn", None)
    if digit is None:
        digit = "off"
        cbpi.add_config_parameter ("TFT_digitOn", "off", "select", "No graph just big digits showing temperature, NO! CBPi reboot required", ["on", "off"])
        cbpi.app.logger.info("TFTDisplay  - TFT_digitOn added:  %s" % (digit))
    return digit

def set_TFT_RedrawTime():
    rt = cbpi.get_config_parameter("TFT_RedrawTime", None)
    if rt is None:
        rt = 120
        cbpi.add_config_parameter ("TFT_RedrawTime", 120, "number", "Choose time [sec] between redraws (flashes), default is 120sec, NO! CBPi reboot required")
        cbpi.app.logger.info("TFTDisplay  - TFT_RedrawTime added: %s" % (rt))
    rt = (int(rt) / 2)  # intervall of backgroundtask is 2sec so if we want sec in the parameter we devide with 2
    return rt    


@cbpi.initalizer(order=3100)
def initTFT(app):       

    rrdDateiVorhanden()
    try:
        cbpi.app.logger.info("TFTDisplay  - TFTKetteID:         %s" % (set_parameter_id3()))
        cbpi.app.logger.info("TFTDisplay  - TFThight:           %s" % (set_TFTh()))
        cbpi.app.logger.info("TFTDisplay  - TFTwith:            %s" % (set_TFTw()))
        cbpi.app.logger.info("TFTDisplay  - TFTfontsize:        %s" % (set_fontsize()))
        cbpi.app.logger.info("TFTDisplay  - TFTduration:        %s" % (set_duration()))
        cbpi.app.logger.info("TFTDisplay  - TFT_Fermenter_ID:   %s" % (set_FermentationOn()))
        cbpi.app.logger.info("TFTDisplay  - TFT_DigitOn:        %s" % (set_DigitOn()))
        cbpi.app.logger.info("TFTDisplay  - TFT_RedrawTime:     %s" % (set_TFT_RedrawTime()))
    except:
        pass
    # waits until tempprobe shows proper values at start. So no peak at startup
    time.sleep(3)

    # end of init
    
    @cbpi.backgroundtask(key="TFT240x320job", interval=2)
    # if you change interval please change divisor in set_TFT_RedrawTime()
    def TFT240x320job(api):
        # This is the main job
        
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

        global TFTduration
        TFTduration = set_duration()

        global TFTfermenterID
        TFTfermenterID = set_FermentationOn()

        global IsDigitOn
        IsDigitOn = set_DigitOn()

        global TFTredrawtime
        TFTredrawtime = set_TFT_RedrawTime()

        global Keepstandby

        threadnames = threading.enumerate()
        # cbpi.app.logger.info("NextionDisplay  - names current thread %s" % threadnames)
        threadnames = str(threadnames)
        
        s = cbpi.cache.get("active_step")
        
        if s is not None or StartscreenOn == "off" or is_fermenter_step_running() == "active":
            # either brewing starts and so chart/digit starts or startscreen is off
            # before, we check if digit mode is on and in which mode
            # then, we check in which mode to show graph either in fermentation mode or brew mode

            if IsDigitOn == "on":

                # cbpi.app.logger.info("TFTDisplay  - digitOn   is running")
                if is_fermenter_step_running() == "active":
                    Digit(TFTfermenterID)
                else:
                    Digit(id3)

            elif is_fermenter_step_running() == "active":
                cbpi.app.logger.info("TFTDisplay  - Fermentation is running")
                updateRRDdatabaseFerment(TFTfermenterID)
                imagefile = '/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/fermtemp.png'
                graphAsFileFerm(imagefile)
                time.sleep(1)
                TFT240x320(imagefile)
                # if "<Thread(TFTfermenting," in threadnames:
                    # cbpi.app.logger.info("TFTDisplay  - thread TFTfermenting detected")
                    # pass
                # else:
                    # pass
                    # t_fermenting = threading.Thread(target=TFT240x320, name='TFTfermenting', args=(imagefile,))
                    # t_fermenting.start()

            else:
                
                updateRRDdatabase(id3)
                imagefile = '/home/pi/craftbeerpi3/modules/plugins/TFTDisplay/brewtemp.png'
                graphAsFile(imagefile)
                time.sleep(1)
                TFT240x320(imagefile)
                # t_brewing = threading.Thread(target=TFT240x320, name='TFT240x320', args=(imagefile,))
                # t_brewing.start()

            Keepstandby = 0
            
        elif StartscreenOn == "on":
            #  Standby screen
           
            if Keepstandby < 2:
                standbypath = "/home/pi/craftbeerpi3/modules/ui/static/logo.png"
                TFT240x320(standbypath)
                Keepstandby = Keepstandby + 1
            else:
                # just keep the image on the screen without redraw
                pass      
        else:
            pass
