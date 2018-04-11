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
# TFTDisplay Version 1.2.1.6
# Assembled by JamFfm
#
# 14.03.2018 changed DC and RST for init display, change default font size, add title
# 16.03.2018 added alternative autocale of graph, show XX.x numbers on Y-axis
# 18.03.2018 optimized code in function updateRRDdatabase(kid) (2 times path)
# 18.03.2018 add parameter TFT_Duration in parameters so you can choose which period to show
# 20.03.2018 change init values of createRRDdatabase(), to support long time graphs
# 20.03.2018 build in first steps for ferment support
# 21.03.2018 duration is displayed at Title
# 21.03.2018 change if loop to detect ferm mode, femTemp(femid), set fermentationOn(), etc added
# 09.04.2018 Ferm or Brew modus displayed in Title, finished fermentation support
# 11.04.2018 Added Target Temp in Ferm mode


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
import modules

global used
used = 0
global Keepstandby
Keepstandby = 0
global femid
femid = 0
global curfemtargTemp
curfemtargTemp = 0

def TFT240x320(imagefile):
    global used
    global DC
    global RST
    
    if used == 0:
        DC = 18
        RST = 25
        used = 1

    elif used == 1:
        DC = 24
        RST = 25
        used = 2

    else:
        used = 3

    SPI_PORT = 0
    SPI_DEVICE = 0

    #create spi connection
    spidevice = SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000)
    # Create TFT LCD display class
    disp = TFT.ILI9341(DC, rst=RST, spi=spidevice)   
    
    # Initialize display only twice
    global used
    if used < 3:
        disp.begin()        
    else:
        pass
        
    # Load an image
    image = Image.open(imagefile)
    #cbpi.app.logger.info('Loading image %s' % (imagefile))
    
    # Resize the image and rotate it so it's 240x320 pixels.
    image = image.rotate(90).resize((240, 320))

    # Draw the image on the display hardware.
    disp.display(image)

    # Close SPI Connection to avoid "too many Ffiles open error"
    spidevice.close()
    
def createRRDdatabase():
    rrdtool.create(
    "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd",
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
    "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/fermtemp.rrd",
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
    #kid is the TFT_Kettle_ID from parameters
    pfad = ("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd")
    
    rrdtool.update(pfad, "N:%s" % (Temp(kid)));
    #cbpi.app.logger.info('TFTDisplay  - rrd update')

def updateRRDdatabaseFerment(fid):
    #fid is the TFT_Fermenter_ID from parameters
    pfad = ("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/fermtemp.rrd")
    
    #rrdtool.update(pfad, "N:%s" % (femTemp(fid)));
    rrdtool.update(pfad, "N:%s:%s" % (femTemp(fid),femTargTemp(fid)));
    #cbpi.app.logger.info('TFTDisplay  - rrdferm update')
    
def graphAsFile():
    path = "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.png"
    rrdtool.graph (path,
    "--imgformat", "PNG",
        #"--start", "-40m",
        "--start", "%s" % str((TFTduration)),
        "--font", "DEFAULT:%s" % str((TFTfontsize)),
        "--title", "CBPi3 Brew time=%s,Temp [°C]" % str((TFTduration))[1:],
        "--grid-dash", "0:10",
        "-w %s" % (str(TFTwith)), "-h %s" % (str(TFThight)),
        #"-w 290", "-h 310",                   
        #"--full-size-mode",
        #"--no-gridfit",
        #"--vertical-label", "Degree Celsius °C",
        #"--alt-y-grid",
        #"--color", "CANVAS#000000",
        "--left-axis-format", "%.1lf",
        "--alt-autoscale",  #command this line to change the x-axis scale behavior
        "--no-legend",
        "--slope-mode",     #smoother line
        "--use-nan-for-all-missing-data",
        "DEF:temp=/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd:tempsensor:AVERAGE",
        "LINE3:temp#ff0000:tempsensor")
    #cbpi.app.logger.info('TFTDisplay  - graph created')
    #https://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html here all options are listed

def graphAsFileFerm():
    path = "/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/fermtemp.png"
    rrdtool.graph (path,
    "--imgformat", "PNG",
        "--start", "%s" % str((TFTduration)),
        "--font", "DEFAULT:%s" % str((TFTfontsize)),
        "--title", "CBPi3 Ferm time=%s,Temp [°C]" % str((TFTduration))[1:],
        "--grid-dash", "0:10",
        "-w %s" % (str(TFTwith)), "-h %s" % (str(TFThight)),
        "--left-axis-format", "%.1lf",
        "--alt-autoscale",  #command this line to change the x-axis scale behavior
        "--no-legend",
        "--slope-mode",     #smoother line
        "--use-nan-for-all-missing-data",
        "DEF:temp=/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/fermtemp.rrd:tempsensor:AVERAGE",
        "DEF:targtemp=/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/fermtemp.rrd:targettemp:AVERAGE",
        "LINE3:temp#ff0000:tempsensor",
        "LINE3:targtemp#0000ff:targettemp")
    #cbpi.app.logger.info('TFTDisplay  - fermgraph created')
    #https://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html here all options are listed

def rrdDateiVorhanden():
    my_file = Path("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.rrd")
    my_fermfile = Path("/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/fermtemp.rrd")
    cbpi.app.logger.info('TFTDisplay  - check if file brewtemp.rrd exists?')

    if my_file.exists():
        cbpi.app.logger.info('TFTDisplay  - File brewtemp.rrd exists')
    else:
        createRRDdatabase()
        cbpi.app.logger.info('TFTDisplay  - File brewtemp.rrd created')
    pass

    if my_fermfile.exists():
        cbpi.app.logger.info('TFTDisplay  - File fermtemp.rrd exists')
    else:
        createRRDdatabaseFerment()
        cbpi.app.logger.info('TFTDisplay  - File fermtemp.rrd created')
    pass

def Temp(kkid):
    #cbpi.app.logger.info("TFTDisplay  - Temp ermitteln")
    current_sensor_value_id3 = (cbpi.get_sensor_value(int(cbpi.cache.get("kettle").get(int(kkid)).sensor)))
    curTemp = ("%6.2f" % (float(current_sensor_value_id3)))
    #cbpi.app.logger.info("TFTDisplay  - Temp: %s" % (curTemp))
    return curTemp

def femTemp(femid):
    #cbpi.app.logger.info("TFTDisplay  - ferm Temp ermitteln")
    current_sensor_value_femid = (cbpi.get_sensor_value(int(cbpi.cache.get("fermenter").get(int(femid)).sensor)))
    curfemTemp = ("%6.2f" % (float(current_sensor_value_femid)))
    #cbpi.app.logger.info("TFTDisplay  - Temp: %s" % (curfemTemp))
    return curfemTemp

def femTargTemp(femtargid):
    #cbpi.app.logger.info("TFTDisplay  - ferm Temp ermitteln")
    current_sensor_value_femtarid = (cbpi.cache.get("fermenter")[(int(femtargid))].target_temp)
    curfemtargTemp = ("%6.2f" % (float(current_sensor_value_femtarid)))
    cbpi.app.logger.info("TFTDisplay  - FermTargTemp: %s" % (curfemtargTemp))
    return curfemtargTemp


def is_fermenter_step_running():
    for key, value2 in cbpi.cache["fermenter_task"].iteritems():
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
        cbpi.add_config_parameter("TFT_Width", 384, "number", "Choose TFTDisplay width [pixel], default 384, NO! CBPi reboot required")
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
    except:
        pass
    
#end of init    
    
    @cbpi.backgroundtask(key="TFT240x320job", interval=5)
    def TFT240x320job(api):
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

        global TFTduration
        TFTduration = set_duration()

        global TFTfermenterID
        TFTfermenterID = set_FermentationOn()
        
        s = cbpi.cache.get("active_step")
        
        if s is not None or StartscreenOn == "off" or is_fermenter_step_running() == "active":
            #Brewing Starts and so Chart starts or startscreen is off
            # before we check if fermentation mode is runnning
            if is_fermenter_step_running() == "active":

                #femTemp(TFTfermenterID)
                cbpi.app.logger.info("TFTDisplay  - Fermentation is running")
                updateRRDdatabaseFerment(TFTfermenterID)
                femTargTemp(TFTfermenterID)#test
                graphAsFileFerm()
                imagefile = ('/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/fermtemp.png')
                TFT240x320(imagefile)
                #thread.start_new_thread(TFT240x320,(imagefile,))
                
            else:
                updateRRDdatabase(id3)
                imagefile = ('/home/pi/craftbeerpi3/modules/plugins/TFTDisplay_240x320/brewtemp.png')
                graphAsFile()

                TFT240x320(imagefile)
                #thread.start_new_thread(TFT240x320,(imagefile,))

            global Keepstandby
            Keepstandby = 0
            
        elif StartscreenOn == "on":
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
        else:
            pass
        

            
