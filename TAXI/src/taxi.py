# coding=utf-8
import argparse
import time
import datetime
import json
import os
import vlc
import RPi.GPIO as GPIO



argparser = argparse.ArgumentParser(
    description='Taxi')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]')

args = argparser.parse_args()

city = args.city


with open('src/config.json', 'r') as config_file:
    config = json.load(config_file)

SENSOR_PIN = config["pins"]["SENSOR_PIN"]
RELAY_PIN = config["pins"]["RELAY_PIN"]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)

vid_path = config["paths"]["video"]
Taxi_Logo_path = config["paths"]["TaxiLogo"]
Arrow_Logo_path = config["paths"]["ArrowLogo"]

cmnd = 'cvlc {0} -f --no-osd --loop &'
vid_command = cmnd.format( vid_path + "TE_SR_Taxi.mp4" )
pic_command = cmnd.format(Taxi_Logo_path + "TaxiLogo.png")
pic2_command = cmnd.format(Arrow_Logo_path + "ArrowLogo.png")


os.system(pic_command)
time.sleep(15)

#Motion Detection boolean check 
def checkMotion(motion):
    if motion == 1:
        return True
        
    else:
        return False

#play video if sensor is detected
def playVideo():
    
    os.system("sudo pkill vlc")
    os.system(vid_command)
  
    time.sleep(26)
    os.system("sudo pkill vlc")

    # Logging: door was opened
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Door Open")


def main():

    while True:

        detected = checkMotion(GPIO.input(SENSOR_PIN))
        if not detected:
            time.sleep(2)
            print ("Motion is not Detected")

        else:
            print("Motion is Detected")
            playVideo()
            os.system(pic2_command)
            break


if __name__ == "__main__":
    main()