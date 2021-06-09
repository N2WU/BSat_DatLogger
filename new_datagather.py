from gps import *
import time
import picamera
from subprocess import call
from datetime import datetime
#from time import sleep #fix this
import smbus
import csv
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
#import time
import spidev


"""
Setup Data
1. Create the blank CSV with appropriate Headers
2. Set up the nRF24L01 to transmit telemetry

"""



#Row = [index, gpsData, weatherData]
CSVHeaders = ["Index", "Time", "Latitude", "Longtitude", "Pressure (kPa)", "Altitude (m)", "Temperature (C)"] 
with open('data.csv', 'w') as f: 
    write = csv.writer(f) 
    write.writerow(CSVHeaders) 
    
    
#Now, set up the radio for transmitting
#



pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)

radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x60)
radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MIN)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1, pipes[0])
radio.printDetails()

ackPL = [1]

def getPositionData(gps):
    nx = gpsd.next()
    # For a list of all supported classes and fields refer to:
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    if nx['class'] == 'TPV':
        latitude = getattr(nx,'lat', "Unknown")
        longitude = getattr(nx,'lon', "Unknown")
        print "Your position: lon = " + str(longitude) + ", lat = " + str(latitude)
        latlonString = [latitude, longitude]
        return latlonString

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

def getWeatherData():
    # Distributed with a free-will license.
    # Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
    # MPL3115A2
    # This code is designed to work with the MPL3115A2_I2CS I2C Mini Module
    # Get I2C bus
    bus = smbus.SMBus(1)
    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    # 0xB9(185) Active mode, OSR = 128, Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)
    # MPL3115A2 address, 0x60(96)
    # Select data configuration register, 0x13(19)
    # 0x07(07) Data ready event enabled for altitude, pressure, temperature
    bus.write_byte_data(0x60, 0x13, 0x07)
    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    # 0xB9(185) Active mode, OSR = 128, Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)
    time.sleep(1)
    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 6 bytes
    # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 6)
    # Convert the data to 20-bits
    tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    temp = ((data[4] * 256) + (data[5] & 0xF0)) / 16
    altitude = tHeight / 16.0
    cTemp = temp / 16.0
    fTemp = cTemp * 1.8 + 32
    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    # 0x39(57) Active mode, OSR = 128, Barometer mode
    bus.write_byte_data(0x60, 0x26, 0x39)
    time.sleep(1)
    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 4 bytes
    # status, pres MSB1, pres MSB, pres LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 4)
    # Convert the data to 20-bits
    pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    pressure = (pres / 4.0) / 1000.0
    # Output data to screen
    # print "Pressure : %.2f kPa" %pressure
    # print "Altitude : %.2f m" %altitude
    # print "Temperature in Celsius : %.2f C" %cTemp
    # print "Temperature in Fahrenheit : %.2f F" %fTemp
    presAltTemp = [pressure, altitude, cTemp]
    return presAltTemp

         
def writeCSV(gpsData, weatherData, index)
    timenow = datetime.now()
    # Create file name for our picture
    stringTime = currentTime.strftime("%Y.%m.%d-%H%M%S")
    Row = [index, stringTime, gpsData[0], gpsData[1], weatherData[0], weatherData[1], weatherData[2]]
    with open(r'data.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(Row)

# Next read from the pressure sensor    
# Transmit telemetry every time the pictures are timestamped

# Our file path
filePath = "/home/pi/Desktop/timestamped_pics/"
picTotal = 50
picCount = 0

while picCount < picTotal:

    # Grab the current time
    currentTime = datetime.now()
    # Create file name for our picture
    picTime = currentTime.strftime("%Y.%m.%d-%H%M%S")
    picName = picTime + '.jpg'
    completeFilePath = filePath + picName

    # Take picture using new filepath
    with picamera.PiCamera() as camera:
        camera.resolution = (1280,720)
        camera.capture(completeFilePath)
        print("We have taken a picture.")
    gpsData = getPositionData(gpsd)
    weatherData = getWeatherData()
    # Create our stamp variable
    timestampMessage = currentTime.strftime("%Y.%m.%d - %H:%M:%S")
    newTimestampMessage = timestampMessage + "Lat:" + gpsData[0] + ", Lon:" + gpsData[1] + ", Alt (m):" + weatherData[1]  
    # Create time stamp command to have executed
    # print("Pressure (kPa)" + weatherData[0] + "Altitude (m)" + weatherData[1] + "Temp (C)" + weatherData[2])
    timestampCommand = "/usr/bin/convert " + completeFilePath + " -pointsize 36 \
    -fill white -annotate +100+100 '" + timestampMessage + "' " + completeFilePath
    # Actually execute the command!
    call([timestampCommand], shell=True)
    print("We have timestamped our picture!")
    writeCSV(gpsData, weatherData, picCount)
    print("Written to CSV")
    

    # Radio command: http://thezanshow.com/electronics-tutorials/raspberry-pi/tutorial-32-33
    message = "Index: " + picCount + ", Temp (C):" + weatherData[2] 

    # send a packet to receiver
    radio.write(message)
    print("Sent: {}".format(message))

    # did it return with a payload?
    if radio.isAckPayloadAvailable():
        pl_buffer=&#91;&#93;
        radio.read(pl_buffer, radio.getDynamicPayloadSize())
        print(pl_buffer)
        print("Translating the acknowledgement to unicode characters...")
        string = ""
        for n in pl_buffer:
            # We want to only decode standard symbols/alphabet/numerals
            # Based off unicode standards, our encoding method
            if (n >= 32 and n <= 126):
                string += chr(n)
        print(string)
        # So our command was received and acknowledged. We should
        # setup ourselves to receive what that temperature was.
        receiveData()
    else:
        print("No received acknowledgement.")
    time.sleep(0.5)
    
    picCount += 1
    time.sleep(10) 

         

"""
def receiveData():
    print("Ready to receive data.")
    radio.startListening()
    pipe = [0]
    while not radio.available(pipe):
        time.sleep(1/100)
    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())

    print("Translating the receivedMessage to unicode characters...")
    string = ""
    for n in receivedMessage:
        # We want to only decode standard symbols/alphabet/numerals
        # Based off unicode standards, our encoding method
        if (n >= 32 and n <= 126):
            string += chr(n)
    print("Our sensor sent us: {}".format(string))
    radio.stopListening()
    
"""




