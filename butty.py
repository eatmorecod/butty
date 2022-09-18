import serial
import re
import sys

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
    line = ser.readline().decode('utf-8', errors='ignore')
    aivdm = re.search('AIVDM', line)
    apb = re.search('APB', line)
    gga = re.search('GGA', line)
    hdt = re.search('HDT', line)
    hdg = re.search('HDG', line)
    vhw = re.search('VHW', line)
    vtg = re.search('VTG', line)
    ttm = re.search('TTM', line)
    
    if ttm:
        list = line.split(',')
        target = list[1]
        distance = list[2]
        bearing = list[3]
        bearing_units = list[4]
        speed = list[5]
        course = list[6]
        course_units = list[7]
        cpa = list[8]
        tcpa = list[9]
        distance_units = list[10]
        
        timestamp = list[14]

        '''print(f'{line}\nTarget: {target}   |  Range: {distance}   |  Bearing: {bearing}{bearing_units}\n\
Speed: {speed}  | Course: {course}{course_units}  |  CPA: {cpa}{distance_units}\nTCPA: {tcpa}   | Timestamp: {timestamp}\n')
        '''
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
     
    if aivdm: 
        print(line, len(line))
        
        
        

    
''' if hdt:
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


    if vtg:
        list = line.split(',')    
        sog = float(list[5])
        cog = float(list[1])
        


    #if is_gga and is_hdt:
    #    sys.stderr.write(f'LAT: {lat}  LON: {lon}  HDG: {round(heading, 1)}\r')'''
      