
from math import pi
from time import time
from canlib import canlib
from helpers_serial import open_channel, starting_range, spawn, position, ttm, nmea0183, nmea2k
import serial # must install PySerial module to transmit serial data
import socket


try:
    ch0 = open_channel(0) # Initialize CAN channel to receive position data
except:
    print("Unable to initialize CAN channel.  Opening serial port.")
    ch0 = None
    
   
# Configure UDP port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    ser = serial.Serial('COM7', 38400, timeout=1, parity='N') # Open serial port to transmit TTMs
    print(f'TTM serial output: {ser.name}')
except:
    ser = None

ownship = {} # Dict to store ownship position data
approach_angle = float(input("approach angle: ")) # this will determine target's starting range and bearing 
if approach_angle > 360 or approach_angle < -180:
    print('please enter valid approach angle')
    approach_angle = float(input("approach angle: "))
if approach_angle > 180:
    approach_angle -= 360
speed = float(input("speed(kn): ")) / 1.944
distance = int(input("CA distance(m): "))
interval = float(input("Target refresh rate (s): "))

is_target = False
is_hdg = False
start_time = time()
while True:
    try:
        if ch0:
            ownship = nmea2k(ch0)
            is_hdg = True
        
        elif ch0 == None:
            ownship = nmea0183()
            is_hdg = True

        # Create target once ownship position and heading have been determined
        if is_target == False and is_hdg == True:
            bearing = round(approach_angle / 2, 2)
            range = starting_range(distance, approach_angle)
            target = spawn(ownship, bearing, range)
            target['cog'] = approach_angle + ownship['hdg'] + 180
            if target['cog'] > 360:
                target['cog'] -= 360   
            print(f'Target spawned at: {range} meters, Bearing: {bearing}°')
            is_target = True        
        
        if time() >= start_time + interval and is_target == True:
            target['distance'] = speed * (time() - start_time)
            target['sog'] = round(speed * 1.944, 2)
            target = position(target)
            TTM = ttm(ownship, target)

            if ser:
                # send serial ttm message
                ser.write(TTM.encode('utf-8', errors='ignore'))
                ser.flushInput()
            else:
                # send UDP packet
                try:
                    sock.sendto(TTM.encode(), ('172.31.252.100', 10051))
                except OSError:
                    print('Error sending UDP packet')

            # reset timer
            start_time = time()
    except KeyboardInterrupt:
        print('Thanks for using Target Generator v1.0 by Ben Galdo') 
        break

                
      
        

    
        
    










