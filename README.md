# TFTDisplay
CraftbeerPi3 addon for a 2.2" TFT Display 320x240 with ILI9341 driver

With this add-on you can display something on a 240 x 320 TFT SPI Display.
It is based on the ILI9341 controller.

(1)--I followed this how to wiring
http://blog.riyas.org/2014/07/
I put a 48 Ohm resistor inbetween LCD and the Raspi Pin.
![GitHub Logo](/home/pi/craftbeerpi3/modules/plugins/TFT_Display_240x320/gpio_connectio_to_tft_il9341.png)

(2)-- I followed how to install and run it:
https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/usage
Please do not update your Firmware. I will distroy thr Raspi config.
I noticed that you need first initialise with DC 18 and RST 23. This causes a white screen. After that change to DC 24 and RST 25. The latter is thr GPIO I connected.

Until now only the Craftbeerlogo is displayed with a bit Text.

In the future the display may display a Temp Graph of the Mask or fermentation
