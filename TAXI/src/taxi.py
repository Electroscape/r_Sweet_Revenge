# coding=utf-8
import argparse
import time
import datetime
import os
import subprocess
import RPi.GPIO as GPIO
from subprocess import Popen



argparser = argparse.ArgumentParser(
    description='Taxi')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / s]')

args = argparser.parse_args()

city = args.city


Path_To_TaxiLogo = "sudo fbi -T 1 -noverbose -a /home/pi/TAXI/img/TaxiLogo.png &"
Path_To_TaxiVideo = "/home/pi/TAXI/vid/" + city + "/TE_SR_Taxi.mp4"
Path_To_ArrowLogo = "sudo fbi -T 1 -noverbose -a /home/pi/TAXI/img/ArrowLogo.png &"

SENSOR_PIN = 23
RELAY_PIN = 22



GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)

os.system(Path_To_TaxiLogo)
time.sleep(15)
i= 0

while True:
    i=GPIO.input(SENSOR_PIN)
    if i==0:
        time.sleep(2)
        print("No Movement")

    elif i==1:
        print("Movement Detected")
        os.system("sudo killall -9 fbi")
        Popen(['omxplayer', '-b', Path_To_TaxiVideo])
        time.sleep(25)

        # Logging: door was opened
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("Door Open")
        
        os.system(Path_To_ArrowLogo)
        break
