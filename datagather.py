import os.path
import socket
import sys
import os
import sqlite3
from subprocess import call
from wifi import Cell
import pynmea2
import time
import serial
import logging
import picamera
import fractions
import pdb
#from gps3 import gps3
from gps3.agps3threaded import AGPS3mechanism

def getlocation(agps_thread): #Pass in gps interface
    #Get current location and return it as a key pair
    #ser = serial.Serial()
    #ser.port = gpsdevice
    #ser.baudrate = 4800
    print("In GPS Getlocation")
    try:
        print('Lat{}'.format(agps_thread.data_stream.lat))
        gpsdata = {'latitude': agps_thread.data_stream.lat, 'longitude': agps_thread.data_stream.lon, 'timestamp' : agps_thread.data_stream.time, 'altitude' : agps_thread.data_stream.alt}
        if gpsdata['latitude'] == 'n\a' or gpsdata['longitude'] == 'n/a' or gpsdata['altitude'] == 'n/a' or gpsdata['timestamp'] == 'n/a':
            gpsdata = {'latitude': '0', 'longitude': '0', 'timestamp': '0', 'altitude': '0'}
        #pdb.set_trace()
        #new_data = gps_socket[1]
        #if new_data:
        #    data_stream.unpack(new_data)
        #    pdb.set_trace()
        #    print("latitude= ", data_stream.TPV['lat'])
        #    print(data_stream)
        #ser.open()
        #logging.debug("Getting GPS Location")
        #gotlocation = False
        #while (gotlocation == False):
            #gpstext = str(ser.readline())
            #if (gpstext[3:8] == 'GPGGA'):
                #Found the proper string, now get the lat long
                #Probably needs a check for GPS lock.
                #print("Got GPGGA")
                #gotlocation = True
                #g = nmea.GPGGA()
                #print(gpstext)
                #g.parse(gpstext)
                #We need to truncate the string.  Remove the first two and last 5 of it
                #g = pynmea2.parse(gpstext[2:-5])
                #print("Parsed data is : " + g)
                #gpsdata = {'latitude':g.latitude, 'longitude': g.longitude, 'timestamp':g.timestamp, 'altitude':g.altitude}
                #return g
            #else:
                #print("bad string")
                #print("GPS Text was: " + gpstext[3:8])
                #print("Fulltext as: " + gpstext)
	        #if gpsdata['latitude'] == '' or gpsdata['longitude'] == '' or gpsdata['altitude'] == '' or gpsdata['timestamp'] == '':
                #gpsdata = {'latitude':'0', 'longitude': '0', 'timestamp':'0', 'altitude':'0'}

    except Exception as e:
        print(e)
        print("GPS Not found or GPS failed")
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
            power int, channel int, enc_type varchar(100), mode varchar(100), pic_filename varchar(100), latitude float, longitude float, altitude float, temperature int, created_at float)''')
        conn.commit()
        print ("Database Created")
        return conn


def saveData(wifitree, gpsdata, picnum, conn, temp):
        for ap in wifitree:
                encryption = ap.encryption_type
                print("bssid: " + ap.ssid)
                pdb.set_trace()
                picfilename = ("cap" + str(picnum) +".jpg")
                #TODO: Take picture with superimposed GPS coordinates
                #Save to database
                c = conn.cursor()
                c.execute("INSERT INTO datasamples(bssid, essid, power, channel, enc_type, mode, pic_filename, latitude, longitude, altitude, temperature, created_at) VALUES('" + ap.address + "','" + ap.ssid + "','" + str(ap.signal) + "','" + str(ap.channel) + "','" + encryption + "','" + ap.mode + "', '" + picfilename + "','" + str(float(gpsdata['latitude'])) + "','" + str(float(gpsdata['longitude'])) + "', '" + str(float(gpsdata['altitude'])) + "', '" + str(temp) + "', '" + str(float(gpsdata['timestamp'])) + "')")
                conn.commit()

def scan(interface):
    print("Begin scan")
    wifitree = Cell.all(interface)
    #print(wifitree)
    return wifitree

def main(argv):
    #get wifi device from argv
    print ("Arg: " )
    print (argv)
    if (len(argv) == 3):
        interface = argv[1]
        gpsdevice = argv[2]
    else:
        interface = 'wlan1'
        #gpsdevice = '/dev/ttyS0' #depricated
    camera = picamera.PiCamera()
    camera.resolution = (3280, 2464) #this is assuming v1, will change to 3280 × 2464 if v2
    #Main Loop
    picnum = 0
    while (os.path.isfile("cap" +str(picnum)+".jpg") == True):
        picnum += 1
    conn = initdb("balloonsat")
    #gps_socket = gps3.GPSDSocket()
    #data_stream = gps3.DataStream()
    #gps_socket.connect()
    #gps_socket.watch()
    agps_thread = AGPS3mechanism()
    agps_thread.stream_data()
    agps_thread.run_thread()
    gpsdata = {}
    while (1):
        gpsdata = getlocation(agps_thread)
        imagefile = ("cap" + str(picnum) + ".jpg")
        #print("The GPS data is:" + str(gpsdata))
        lat = ''
        lon = ''
        alt = ''
        timestamp = ''
        try:
            print("lat " +str(gpsdata['latitude']) + "lon "+str(gpsdata['longitude']) + " alt " + str(gpsdata['altitude']))
            lat = gpsdata['latitude']
            lon = gpsdata['longitude']
            alt = gpsdata['altitude']
        except:
            print("Gps Data could not be printed/converted")
        try:
            tempfile = open("/sys/class/thermal/thermal_zone0/temp")
            tempInt = int(tempfile.read(6))
        except:
            tempInt = 0
            print("Temp data could not be retrieved")
        try:
            wifitree = scan(interface)
            print (wifitree)
        except:
            print("No wifi data recieved")
        try:
            #pdb.set_trace()
            #print("Going to send: " + str(lat) + " Lat and " + str(lon) + " Long")
            #camera.exif_tags['GPS.GPSAltitude'] = gpsdata.altitude
            #camera.exif_tags['GPS.GPSAltitudeRef'] = '0'
            #camera.exif_tags['GPS.GPSLatitude'] = lat
            #camera.exif_tags['GPS.GPSLatitudeRef'] = 'N'
            #camera.exif_tags['GPS.GPSLongitude'] = long
            #camera.exif_tags['GPS.GPSLongitudeRef'] = 'W'
            #camera.exif_tags[0x9400] = str(tempInt) + '/1000'
            camera.capture(imagefile)
        except:
            print("No camera currently detected")
        try:
            saveData(wifitree, gpsdata, picnum, conn, tempInt)
        except:
            print("unable to save data")
        picnum = picnum + 1
        time.sleep(5) #wait 10 seconds, then rescan


if __name__ == "__main__":
    main(sys.argv)
