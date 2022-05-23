# coding=utf-8
import argparse
import time
import datetime
import os
import subprocess
import vlc
import RPi.GPIO as GPIO

from subprocess import Popen

argparser = argparse.ArgumentParser(
    description='Taxi')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]')

args = argparser.parse_args()

city = args.city


Path_To_TaxiLogo = "cvlc /home/pi/TAXI/img/TaxiLogo.png  -f --no-osd --loop &"
Path_To_ArrowLogo = "cvlc /home/pi/TAXI/img/ArrowLogo.png  -f --no-osd --loop &"

SENSOR_PIN = 23
RELAY_PIN = 22



GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)
#media = vlc.MediaPlayer(Path_To_TaxiVideo)



vid_path = 'TE_SR_Taxi.mp4' 
pic_path = 'TaxiLogo.png'
pic2_path = 'ArrowLogo.png'

cmnd = 'cvlc {0} -f --no-osd &'
vid_command = cmnd.format(f"~/TAXI/vid/hh/{vid_path}")
pic_command = cmnd.format(f"~/TAXI/img/{pic_path}")
pic2_command = cmnd.format(f"~/TAXI/img/{pic2_path}")


os.system(pic_command)
time.sleep(5)

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
  
    #Popen(['omxplayer', '-b', Path_To_TaxiVideo])
    time.sleep(25)
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