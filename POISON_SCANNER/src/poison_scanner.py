from time import sleep
import os
from subprocess import Popen, PIPE, DEVNULL

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import board
import busio
from digitalio import DigitalInOut

from adafruit_pn532.i2c import PN532_I2C

# I2C connection:
i2c = busio.I2C(board.SCL, board.SDA)


# keep trying to initialise the sensor
while True:
    try:
        # Non-hardware reset/request with I2C
        pn532 = PN532_I2C(i2c, debug=False)
        ic, ver, rev, support = pn532.firmware_version
        print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
        break
    except:
        print("failed to start RFID")
        sleep(1)

# this delay avoids some problems after wakeup
sleep(0.5)

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

non_poisoned_cards = ['PSB', 'PDT', 'PZK', 'PTB']
poisoned_cards = ['PVM', 'PSV']
read_block = 4
UV_light_pin = 4

vid_command = 'cvlc {0} -f --no-osd --loop &'

UV_LIGHT_ON = GPIO.HIGH
UV_LIGHT_OFF = GPIO.LOW

GPIO.setup(UV_light_pin, GPIO.OUT)
GPIO.output(UV_light_pin, UV_LIGHT_OFF) 

def wait_remove_card(uid):
    while uid:
        # print('Same Card Still there')
        # sleep(0.01)
        try:
            uid = pn532.read_passive_target()
        except RuntimeError:
            uid = None


def scan_field():
    while True:
        try:
            uid = pn532.read_passive_target()
        except RuntimeError:
            uid = None
            # sleep(0.01)

        # print('.', end="") if count <= 3 else print("", end="\r")
        # Try again if no card is available.
        if uid:
            print('Found card')
            break

    return uid


def main():

    print('Welcome to Poison Scanner')
    # clean start
    # Kill all relavent applications
    os.system("sudo pkill vlc")
    os.system(vid_command.format("default_dots.MOV"))

    print('Waiting Card')

    while True:
        uid = scan_field()

        if uid:
            GPIO.output(UV_light_pin, UV_LIGHT_ON)
            try:
                data = pn532.ntag2xx_read_block(read_block)
                print('Card found')
            except Exception:
                data = b"XX"

            try:
                read_data = data.decode('utf-8')[:3]
            except Exception as e:
                print(e)
                read_data = "XXX"

            print('data is: {}'.format(read_data))
            
            if read_data in poisoned_cards + non_poisoned_cards:
                pass
            else:
                print('Wrong Card')
                os.system("sudo pkill vlc")
                os.system(vid_command.format("unknown_strips.MOV"))

            if read_data in poisoned_cards: 
                os.system("sudo pkill vlc")
                os.system(vid_command.format('Giftscannervideo_toxic_mit_sound.mp4'))
                # video is 18 seconds
                sleep(18)
                print('Poisoned card')
                os.system("sudo pkill vlc")
                os.system(vid_command.format('toxic.png'))
            elif read_data in non_poisoned_cards:
                os.system("sudo pkill vlc")
                os.system(vid_command.format('Giftscannervideo_nontoxic_mit_sound.mp4'))
                # video is 7 seconds
                sleep(18)
                print('Clean Card')
                os.system("sudo pkill vlc")
                os.system(vid_command.format('nontoxic.png'))

            #os.system("sudo pkill omxplayer")
            wait_remove_card(uid)
            print("Card Removed")
            GPIO.output(UV_light_pin, UV_LIGHT_OFF) 
            os.system("sudo pkill vlc")
            os.system(vid_command.format("default_dots.MOV"))


if __name__ == "__main__":
    main()
