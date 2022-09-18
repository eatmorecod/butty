import serial
import re
import sys

ser = serial.Serial('COM6', 38400, timeout=.1, parity='N')
is_ttm = False
is_hdg = False
is_tracker = False 

while True:
    line = ser.readline().decode('utf-8', errors='ignore')
    zda = re.search('ZDA', line)
    vhw = re.search('VHW', line)
    apb = re.search('APB', line)
    gga = re.search('GGA', line)
    hdt = re.search('HDT', line)
    vtg = re.search('VTG', line)
    ttm = re.search('TTM', line)
    
    if hdt:
        list = line.split(',')  
        hdg = float(list[1])
        is_hdg = True

    if zda:
        list = line.split(',')
        time = float(list[1])
    
    if vhw:
        list = line.split(',')
        hdg = float(list[1])
        is_hdg = True    

    if ttm:   
        list = line.split(',')
        target = list[1]
        distance = float(list[2])
        bearing = float(list[3])
        bearing_units = list[4]
        speed = float(list[5])
        course = float(list[6])
        course_units = list[7]
        cpa = list[8]
        tcpa = list[9]
        distance_units = list[10]
        timestamp = float(list[14])
        is_ttm = True
        if is_hdg == True:
            bearing = bearing + hdg
            if bearing > 360:
                bearing -= 360
        
        
        if is_ttm == True and is_hdg == True:
            
            if is_tracker == False:
                tracker_id = input(f'Target {target} acquired.  Tracker ID: ')
                is_tracker = True
                

            sys.stdout.write(f'ID: {tracker_id}  |  RANGE: {round(distance * 1852, 2)}  |  BEARING: {round(bearing, 2)}  |  Time: {timestamp}     \r')   
            sys.stdout.flush()   
            