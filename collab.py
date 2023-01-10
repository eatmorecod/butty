import sys
from pynput import keyboard
import serial
import re
from helpers_serial import position, make_checksum
from math import radians, degrees
from datetime import datetime
from time import time, sleep


print('\n\
    *********************************************************************\n\
    *********************************************************************\n\
    ***  |||||||||   |||   |||   |||||||||   |||||||||   |||     |||  ***\n\
    ***  |||    |||  |||   |||      |||         |||       |||   |||   ***\n\
    ***  |||||||||   |||   |||      |||         |||         |||||     ***\n\
    ***  |||    |||  |||   |||      |||         |||          |||      ***\n\
    ***  |||||||||   |||||||||      |||         |||          |||      ***\n\
    *********************************************************************\n\
    *********************************************************************\n')

mothership = {
    'lat': 0.0,
    'lon': 0.0,
    'hdg': 0.0,
    'cog': 0.0,
    'sog': 0.0,
    'distance': 100  
}

try:
    ser = serial.Serial('COM6', 38400, timeout=.1, parity='N')
except:
    ser = None
    print('COM6 not found')

def utcTime():
    # UTC Timestamp in hhmmss.ss format
    timestamp = datetime.utcnow().strftime("%H%M%S.%f")[:-5]
    return timestamp

def convertFromDD(dd):
    
    dd = abs(dd)
    min = (dd % 1) * 60
    ddmm = int(dd) * 100 + min
    return round(ddmm, 4) 

def on_press(key):
    try:
        match key:
            case keyboard.Key.right:
                mothership['hdg'] += 1
                if mothership['hdg'] >= 360: mothership['hdg'] -= 360
            case keyboard.Key.left:
                mothership['hdg'] -= 1
                if mothership['hdg'] < 0: mothership['hdg'] += 360
            case keyboard.Key.up:
                if mothership['sog'] < 20:
                    mothership['sog'] +=1
            case keyboard.Key.down:
                if mothership['sog'] > 0:
                    mothership['sog'] -=1
    except:
        sys.exit() 

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False

is_gga = False
is_hdt = False

input("Press enter to spawn mothership.")

# Get Ownship GGA from ser
if ser:
    while not is_hdt or not is_gga: 
        line = ser.readline().decode('utf-8', errors='ignore')
        gga = re.search('GGA', line)
        hdt = re.search('HDT', line)
        hdg = re.search('HDG', line)
        vhw = re.search('VHW', line)

        if gga:
            list = line.split(',')
            
            # get latitude and convert from ddmm.mm to dd.dddd
            lat = float(list[2])
            deg = int(lat / 100)
            min = lat % deg
            lat = round(deg + (min / 60), 4)
            
            # convert to radians for position calculations
            mothership['lat'] = radians(lat) 
            
            #get longitude and convert from ddmm.mm to dd.dddd
            lon = float(list[4])
            deg = int(lon / 100)
            min = lon % deg
            lon = round(deg + (min / 60), 4)
            if list[5] == "W":
                lon *= -1
            # Convert to radians for position calculations
            mothership['lon'] = radians(lon)
            
            is_gga = True  

        if hdt:
            list = line.split(',')  
            mothership['hdg'] = float(list[1])
            is_hdt = True

        if hdg:
            list = line.split(',')  
            mothership['hdg'] = float(list[1]) - float(list[4])
            is_hdt = True

        '''if vhw:
            list = line.split(',')
            heading = float(list[1])
            is_hdt = True'''

    ser.close()

def getGGA():
    lat = convertFromDD(degrees(mothership['lat']))
    lon = convertFromDD(degrees(mothership['lon']))
    msg = f'$GPGGA,{utcTime()},{lat},N,0{lon},W,2,28,0.61,-24.72,M,-33.13,M,,*'
    return msg + f'{make_checksum(msg):02x}\n'

def getHDG():
    msg = f'$HCHDT,{round(mothership["hdg"])}.0,T*'
    return msg + f'{make_checksum(msg):02x}\n'

def getVTG():
    msg = f'$GPVTG,{round(mothership["cog"])}.0,T,,M,{round(round(mothership["sog"]))}.0,N,{round(mothership["sog"] * 1.852, 2)},K,D*'
    return msg + f'{make_checksum(msg):02x}\n'

def getZDA():
    msg = f'$GPZDA,{utcTime()},{datetime.utcnow().strftime("%d,%m,%Y")},00,01*'
    return msg + f'{make_checksum(msg):02x}\n'


# Open serial port to transmit mothership GPS
try:
    serTx = serial.Serial('COM5', 38400, timeout=.1, parity='N')
except:
    serTx = None
    print('COM5 not found')


# Start non-blocking keyboard listener to update heading and speed
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

listener.start()
timeOfLastMsg = time()

while listener.running:
    # Send Mothership GGA, HDT, VTG messages every .2 sec
    if timeOfLastMsg + .2 <= time():
        mothership['distance'] = (mothership['sog'] / 1.944) * .2 #(time() - timeOfLastMsg)
        mothership['cog'] = mothership['hdg']
        mothership = position(mothership)
        
        serTx.write(f'{getGGA()}{getHDG()}{getVTG()}{getZDA()}\r'.encode('utf-8', errors='ignore'))
        serTx.flush()
        
        sys.stdout.write(f'\rHEADING: {int(mothership["hdg"]):0=3d}°\tSPEED(kn): {int(mothership["sog"]):<2d}\tTIME: {utcTime()}')  
        timeOfLastMsg = time()
        
serTx.close()
