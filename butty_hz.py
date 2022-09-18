import serial
import re
import sys
from time import time

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

is_gga = False
is_hdt = False
counter = 0

ser = serial.Serial('COM4', 38400, timeout=.1, parity='N')
while True:
    hz = counter
    
    counter = 0
    sys.stdout.write(f'counter: {counter}   hz: {hz}\r')
    start_time = time()
    
    while time() - start_time < 1:
        
        line = ser.readline().decode('utf-8', errors='ignore')
        apb = re.search('APB', line)
        gga = re.search('GGA', line)
        hdt = re.search('HDT', line)
        hdg = re.search('HDG', line)
        vhw = re.search('VHW', line)
        vtg = re.search('VTG', line)
        ttm = re.search('TTM', line)
        
        
        if gga:
            list = line.split(',')
            lat = float(list[2])
            deg = int(lat / 100)
            min = lat % deg
            lat = round(deg + (min / 60), 4)
            
            
            lon = float(list[4])
            deg = int(lon / 100)
            min = lon % deg
            lon = round(deg + (min / 60), 4)
            if list[5] == "W":
                lon *= -1

            counter += 1
            is_gga = True  
            sys.stdout.write(f'counter: {counter}\r')
        
        
        

    
