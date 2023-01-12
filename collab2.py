import sys
from pynput import keyboard
import serial
import re
from helpers_serial import position, make_checksum, open_channel, close_channel
from math import radians, degrees
from datetime import datetime
from time import time, sleep
from canlib import canlib
from canlib.canlib import ChannelData


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

def nmea2k(ch):
    ownship = {}
    var = False
    position = False
    hdg = False
    cog = True
    while True:
        try:
            frame = ch.read(timeout=500)
        except(canlib.canNoMsg) as ex:
            pass
        except(canlib.canError) as ex:
            print(ex)
        
        pgn = (frame.id & 33554176)>>8 # Decode pgn from message identifier
        data = []
            
         # Variation
        if pgn == 0x1F11A:
            for byte in frame.data:
                data.append(byte)
            var = f'{data[5]:02x}{data[4]:02x}'
            if int(var, 16) > 0x0fff:
                var = (int(var, 16) - 0xffff) * .0057
        
        # HEADING
        if pgn == 0x1F112:
            for byte in frame.data:
                data.append(byte)
            hdg = f'{data[2]:02x}{data[1]:02x}'
            if data[7] == 253:
                if var: 
                    ownship['hdg'] = round((int(hdg, 16) * .0057) + var, 1)
                    hdg = True
            
            else:
                ownship['hdg'] = round((int(hdg, 16) * .0057), 1)
                hdg = True
                
        # POSITION
        if pgn == 0x1F801:
            for byte in frame.data:
                data.append(byte)
            lat = f'{data[3]:02x}{data[2]:02x}{data[1]:02x}{data[0]:02x}'
            lon = f'{data[7]:02x}{data[6]:02x}{data[5]:02x}{data[4]:02x}'
            ownship["lat"] = radians(round(int(lat, 16) * 1 * 10** -7, 6))
            if int(lon, 16) > int(0x0fffffff):
                ownship['lon'] = radians(round((int(lon, 16) - int(0xffffffff)) * 1 * 10** -7, 6))
            else:
                ownship['lon'] = radians(round(int(lon, 16) * 1 * 10** -7, 6))             
            position = True
        if position == True and hdg == True and cog == True:
            return ownship    

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

input('Press enter to spawn mothership:')

try:
    ch0 = open_channel(0) # Initialize CAN channel to receive position data
    mothership = nmea2k(ch0)
    mothership['sog'] = 0.0
    mothership['cog'] = mothership['hdg']
    mothership['distance'] = 50
    close_channel(ch0)

except:
    print("Unable to initialize CAN channel.  Opening serial port.")
    ch0 = None

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
        mothership = position(mothership)
        serTx.write(f'{getGGA()}{getHDG()}{getVTG()}{getZDA()}\r'.encode('utf-8', errors='ignore'))
        serTx.flush()
        mothership['distance'] = (mothership['sog'] / 1.944) * .2 #(time() - timeOfLastMsg)
        mothership['cog'] = mothership['hdg']       
        sys.stdout.write(f'\rHEADING: {int(mothership["hdg"]):0=3d}°\tSPEED(kn): {int(mothership["sog"]):<2d}\tTIME: {utcTime()}')  
        timeOfLastMsg = time()
        
serTx.close()
