import socket
import sys
import os
import sqlite3
from subprocess import call
from wifi import Cell
from pynmea import nmea
import time
import serial
import logging
import picamera
import fractions

def getlocation(gpsdevice): #Pass in gps interface
    #Get current location and return it as a key pair
    ser = serial.Serial()
    ser.port = gpsdevice
    ser.baudrate = 4800
    try:
        ser.open()
        logging.debug("Getting GPS Location")
        gotlocation = False
        while (gotlocation == False):
            gpstext = str(ser.readline())
            if (gpstext[3:8] == 'GPGGA'):
                #Found the proper string, now get the lat long
                #Probably needs a check for GPS lock.
                gotlocation = True
                g = nmea.GPGGA()
                g.parse(gpstext)
                gpsdata = {'latitude':g.latitude, 'longitude': g.longitude, 'timestamp':g.timestamp, 'altitude':g.antenna_altitude}
            else:
                logging.debug("GPS Text was: " + gpstext[3:8])
    except:
        logging.debug("GPS Not found.  ")
        gpsdata = {'latitude':'0', 'longitude': '0', 'timestamp':'0', 'altitude':'0'}
    return gpsdata


def initdb(dbname):
    #Check if db exists.  Create the db if it does not.
    if os.path.isfile(dbname + ".db"):
        conn = sqlite3.connect(dbname + ".db")
        print ("Connected to " + dbname)
        return conn
    else:
        #Open and create the database and add encoding types
        conn = sqlite3.connect(dbname + ".db")
        c = conn.cursor()
        c.execute('''CREATE TABLE datasamples
            (bssid character(12), essid varchar(255),
            power int, channel int, enc_type varchar(100), mode varchar(100), pic_filename varchar(100), latitude float, longitude float, altitude float, created_at int)''')
        conn.commit()
        print ("Database Created")
        return conn


def saveData(wifitree, gpsdata, picnum, conn):
    for ap in wifitree:
        encryption = ap.encryption_type
        print("bssid: " + ap.ssid)
        print(gpsdata)
        picfilename = ("picture" + str(picnum) +".jpg")
        #TODO: Take picture with superimposed GPS coordinates
        #Save to database

        c = conn.cursor()
        c.execute("INSERT INTO datasamples(bssid, essid, power, channel, enc_type, mode, pic_filename, latitude, longitude, altitude, created_at) VALUES('" + ap.address + "','" + ap.ssid + "','" + str(ap.signal) + "','" + str(ap.channel) + "','" + encryption + "','" + ap.mode + "', '" + picfilename + "','" + str(gpsdata['latitude']) + "','" + str(gpsdata['longitude']) + "', '" + str(gpsdata['altitude']) + "', '" + gpsdata['timestamp'] + "')")
        conn.commit()

def scan(interface):
    print("Begin scan")
    wifitree = Cell.all(interface)
    return wifitree

def converter(num):
        mod1 = num%100
        deg = int((num-mod1)/100)
        mod2 = mod1%1
        min = int(mod1-mod2)
        sec = mod2*100
        return ((deg, 1), (min, 1), fractions.Fraction.from_float(sec).limit_denominator())

def main(argv):
    #get wifi device from argv
    print ("Arg: " )
    print (argv)
    if (len(argv) == 3):
        interface = argv[1]
        gpsdevice = argv[2]
    else:
        interface = 'wlan0'
        gpsdevice = '/dev/ttyUSB0'
    camera = picamera.PiCamera()

    #Main Loop
    picnum = 0
    conn = initdb("balloonsat")
    while (1):
        imagefile = "cap" + str(picnum) + ".jpg"
        #Get GPS Coords
        gpsdata = getlocation(gpsdevice)
        long = converter(gpsdata['longitude'])
        lat = converter(gpsdata['latitude'])
        alt = fractions.Fraction.from_float(gpsdata['altitude']).limit_denominator()
        wifitree = scan(interface)
        print(gpsdata)
        camera.exif_tags['GPS.GPSAltitude'] = alt
        camera.exif_tags['GPS.GPSLatitude'] = lat
        camera.exif_tags['GPS.GPSLongitude'] = long
        camera.capture(imagefile)
        saveData(wifitree, gpsdata, picnum, conn)
        picnum = picnum + 1
        time.sleep(10) #wait 10 seconds, then rescan


if __name__ == "__main__":
    main(sys.argv)
