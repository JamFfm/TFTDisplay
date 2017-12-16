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

from modules import cbpi, app
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os, re, thread, time
import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

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
    imagefile = ('/home/pi/craftbeerpi3/modules/ui/static/logo.png')
    image = Image.open(imagefile)
    cbpi.app.logger.info('Loading image %s' % (imagefile))

    # Resize the image and rotate it so it's 240x320 pixels.
    image = image.rotate(90).resize((240, 320))
    cbpi.app.logger.info('image rotate')

    # Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
    draw_rotated_text(image, 'Craftbeerpi 3.0.2', (150, 120), 90, font, fill=(255,255,255))
    cbpi.app.logger.info('write text')

    # Draw the image on the display hardware.
    disp.display(image)
    cbpi.app.logger.info('image display')

@cbpi.initalizer(order=3010)
def initTFT(app):
    ##Background Task to load the data  
    @cbpi.backgroundtask(key="TFT240x320job", interval=15)
    def TFT240x320job(api):
        ## YOUR CODE GOES HERE    
        ## This is the main job
        thread.start_new_thread (TFT240x320())
#End of init
