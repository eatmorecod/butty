import serial
import re
import socket

# Configure UDP port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


ser = serial.Serial('COM3', 38400, timeout=1, parity='N')
while True:
    line = ser.readline().decode()

    try:
        sock.sendto(line.encode(), ('172.31.252.100', 10051))
    except OSError:
        print('Error sending UDP packet')
    
    
