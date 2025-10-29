import time
import serial
import sys

port = "COM1" if sys.platform.startswith('win') else "/dev/ttyACM0"

try:
    arduino = serial.Serial(port, 9600)
    time.sleep(2)  # Wait for the connection to establish
    print("Connected to Arduino")
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    arduino = None

def send_command(command):
    if arduino and arduino.is_open:
        arduino.write(command.encode())
        print(f"Sent command: {command}")
    else:
        print("Arduino is not connected.")