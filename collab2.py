from pynput import keyboard
import serial
import re
import sys
from helpers_serial import position, make_checksum
from datetime import datetime
from time import time

SOG = 0
HDG = 0

try:
    ser = serial.Serial('COM5', 38400, timeout=.1, parity='N')
except:
    ser = None
    print('COM5 not found')

def utcTime():
    # UTC Timestamp in hhmmss.ss format
    timestamp = datetime.utcnow().strftime("%H%M%S.%f")[:-5]
    return timestamp


def convertFromDD(dd):
    
    min = (dd % 1) * 60
    print(min)
    ddmm = int(dd) * 100 + min
    return ddmm
    print(ddmm)

def on_press(key):
    global HDG
    global SOG
    try:
        match key:
            case keyboard.Key.right:
                HDG += 1
                if HDG >= 360: HDG -= 360
            case keyboard.Key.left:
                HDG -= 1
                if HDG < 0: HDG += 360
            case keyboard.Key.up:
                if SOG < 20:
                    SOG +=1
            case keyboard.Key.down:
                if SOG > 0:
                    SOG -=1
    except:
        sys.exit() 

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False


is_gga = True
is_hdt = True

input("Press enter to spawn mothership.")

# TODO Get Ownship GGA from ser
# TODO Define Mothership Dict with ownship position, and 0 COG, HDT, SOG
# TODO Send Mothership GGA, HDT, VTG messages every .2 sec
# TODO Update HDT, COG, and VTG on user input 

if ser:
    while not is_hdt or not is_gga: 
        line = ser.readline().decode('utf-8', errors='ignore')
        gga = re.search('GGA', line)
        hdt = re.search('HDT', line)
        hdg = re.search('HDG', line)
        vhw = re.search('VHW', line)

        if gga:
            list = line.split(',')
            lat = float(list[2])
            print(lat)
            deg = int(lat / 100)
            min = lat % deg
            lat = round(deg + (min / 60), 4)
            print(lat)
            
            
            lon = float(list[4])
            deg = int(lon / 100)
            min = lon % deg
            lon = round(deg + (min / 60), 4)
            if list[5] == "W":
                lon *= -1

            is_gga = True  

        if hdt:
            list = line.split(',')  
            heading = float(list[1])
            is_hdt = True

        if hdg:
            list = line.split(',')  
            heading = float(list[1])
            is_hdt = True

        if vhw:
            list = line.split(',')
            heading = float(list[1])
            is_hdt = True

    mothership = {
        'lat': lat,
        'lon': lon,
        'hdg': int(heading),
        'cog': 'hdg',
        'sog': 0,
        'distance': 100  
    }

'''print(mothership)
print(convertFromDD(mothership['lat']))

mothership = position(mothership)
print(mothership)'''

mothership = {
        'lat': 4221.7866,
        'lon': 07101.8926,
        'hdg': 1,
        'cog': 'hdg',
        'sog': 0,
        'distance': 100  
    }
def getGGA():
    lat = convertFromDD(mothership['lat'])
    lon = convertFromDD(mothership['lon'])
    msg = f'$GPGGA,184854.3,4221.7866,N,07101.8926,W,2,28,0.61,-24.72,M,-33.13,M,,*'
    #msg = f'$GPGGA,{utcTime()},{lat},N,{lon},W,2,28,0.61,-24.53,M,-33.13,M,,*'
    return msg + f'{make_checksum(msg):02x}'

print(getGGA())

# Start non-blocking keyboard listener to update heading and speed
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

listener.start()
timeOfLastMsg = time()
while listener.running:
    if timeOfLastMsg + .2 <= time():
        sys.stdout.write(f'\rHEADING: {HDG:0=3d}°\tSPEED(kn): {SOG:<2d}\tTIME: {utcTime()}')  
        timeOfLastMsg = time()