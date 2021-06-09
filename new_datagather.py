
from gps import *
import time
import picamera
from subprocess import call
from datetime import datetime
from time import sleep

def getPositionData(gps):
    nx = gpsd.next()
    # For a list of all supported classes and fields refer to:
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    if nx['class'] == 'TPV':
        latitude = getattr(nx,'lat', "Unknown")
        longitude = getattr(nx,'lon', "Unknown")
        print "Your position: lon = " + str(longitude) + ", lat = " + str(latitude)

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

        
    
    

# Our file path
filePath = "/home/pi/Desktop/cookie/timestamped_pics/"
picTotal = 5
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
    getPositionData(gpsd)
    # Create our stamp variable
    timestampMessage = currentTime.strftime("%Y.%m.%d - %H:%M:%S")
    newTimestampMessage = timestampMessage + latitude + "," + longitude
    # Create time stamp command to have executed
    timestampCommand = "/usr/bin/convert " + completeFilePath + " -pointsize 36 \
    -fill red -annotate +700+650 '" + timestampMessage + "' " + completeFilePath
    # Actually execute the command!
    call(&#91;timestampCommand&#93;, shell=True)
    print("We have timestamped our picture!")

    # Advance our picture counter
    picCount += 1
    sleep(10)
