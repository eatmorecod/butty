import keyboard
import serial
import re
from helpers_serial import position

ser = serial.Serial('COM5', 38400, timeout=.1, parity='N')

def convertFromDD(dd):
    min = (dd % 1) * 60
    print(min)
    ddmm = dd * 100 + min
    print(ddmm) 

is_gga = False
is_hdt = False

input("Press enter to spawn mothership.")

# TODO Get Ownship GGA from ser
# TODO Define Mothership Dict with ownship position, and 0 COG, HDT, SOG
# TODO Send Mothership GGA, HDT, VTG messages every .2 sec
# TODO Update HDT, COG, and VTG on user input 

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
    'hdg': heading,
    'cog': heading,
    'sog': 0.0,
    'distance': 100  
}


print(mothership)
print(convertFromDD(mothership['lat']))

mothership = position(mothership)
print(mothership)












