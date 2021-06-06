# BSat Data Logger

Data gathering code for the West Point Ballonsat. Forked new in 2021. 

Requires:
1. High-altitude GPS
2. TMP36 Temperature Sensor
3. Altimeter
4. (XBee Bluetooth Module)[https://artifexanima.wordpress.com/2015/04/28/connecting-xbee-to-raspberry-pi/]

Simple script with the following steps:
1. Captures GPS data, temperature, and pressure
2. Saves timestamped raw data into csv
3. Takes PiCam picture
4. Timestamps PiCam picture with GPS data
4. Saves timestamped picture
5. Transmits telemetry via Xbee Module

Takes from these links:
1. 

Requires the following additional python modules
wifi
pynmea
pyserial
logging
os
sqlite3
