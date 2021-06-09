# BSat Data Logger

Data gathering code for the West Point Ballonsat. Forked new in 2021. 

Requires:
1. High-altitude GPS via serial
3. Barometer / Altimeter via MPL3115A2 (i2c)
4. nRF24L01 radio bluetooth module
5. Raspberry Pi Zero
6. 3.7V to 5V boost converter with extra microUSB connection (https://thepihut.com/blogs/raspberry-pi-tutorials/running-a-raspberry-pi-zero-from-an-aa-battery-pack)
7. Custom PCB (in the works)

Simple script with the following steps:
1. Captures GPS data, temperature, and pressure
2. Saves timestamped raw data into csv
3. Takes PiCam picture
4. Timestamps PiCam picture with GPS data
4. Saves timestamped picture
5. Transmits telemetry via nRF24L01 module

Takes from these links:
1. https://www.hackster.io/wirekraken/connecting-an-nrf24l01-to-raspberry-pi-9c0a57
2. https://picamera.readthedocs.io/en/release-1.13/quickstart.html
3. https://developer.here.com/blog/read-gps-data-with-a-raspberry-pi-zero-w-and-node.js?cid=Developer-Facebook_Comms-CM--Devblog-
4. https://www.raspberrypi-spy.co.uk/2012/08/reading-analogue-sensors-with-one-gpio-pin/ (optional)
5. http://thezanshow.com/electronics-tutorials/raspberry-pi/tutorial-14

Requires the following additional python modules
wifi
pynmea
pyserial
logging
os
sqlite3


Wiring Guide:
1. Connect PiCamera to HDMI port (requires ribbon changer)
2. Connect nRF24L01 using SPI
3. Connect GPS to Serial
4. Connect MPL3115A2 to I2C

**Note:** There are quite a few steps the raspberry pi zero has to go through before the code can be run. Comb through each of the links and perform the steps (usually install modules, turn on SPI/UART/Serial/I2C, then test example code.
