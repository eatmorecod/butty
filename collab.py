import keyboard
import serial
import re

ser = serial.Serial('COM5', 38400, timeout=.1, parity='N')
heading = False
speed = False
position = False

input("Press enter to spawn mothership.")

# TODO Get Ownship GGA from ser
# TODO Define Mothership Dict with ownship position, and 0 COG, HDT, SOG
# TODO Send Mothership GGA, HDT, VTG messages every .2 sec
# TODO Update HDT, COG, and VTG on user input 

while not heading or not position or not speed: 
    line = ser.readline().decode('utf-8', errors='ignore')
    gga = re.search('GGA', line)
    hdt = re.search('HDT', line)
    hdg = re.search('HDG', line)
    vhw = re.search('VHW', line)
    vtg = re.search('VTG', line)







