import argparse
import board
import busio
import gc
import json
import RPi.GPIO as GPIO
import vlc

from adafruit_pn532.i2c import PN532_I2C
from digitalio import DigitalInOut
from subprocess import Popen, PIPE, DEVNULL
from time import sleep
import logging
import subprocess
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

'''
=========================================================================================================
Argument parser
=========================================================================================================
'''

argparser = argparse.ArgumentParser(
    description='Poison-Scanner')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]')

city = argparser.parse_args().city


'''
=========================================================================================================
Load config
=========================================================================================================
'''
with open('src/config.json', 'r') as config_file:
    config = json.load(config_file)

'''
=========================================================================================================
Global VLC variables
=========================================================================================================
'''
vlc_instance = vlc.Instance() # creating Instance class object
player = vlc_instance.media_player_new() # creating a new media object

'''
=========================================================================================================
set UV LIGHT variables
=========================================================================================================
'''

GPIO.setmode(GPIO.BCM)
GPIO.setup(config["PIN"][city]["UV_light_pin"], GPIO.OUT)
GPIO.output(config["PIN"][city]["UV_light_pin"], config["PIN"][city]["UV_LIGHT_OFF"]) 

'''
=========================================================================================================
PN532 init
=========================================================================================================
'''
# I2C connection:
i2c = busio.I2C(board.SCL, board.SDA)

while True:
    attempts = 0
    try:
        # Non-hardware reset/request with I2C
        pn532 = PN532_I2C(i2c, debug=False)
        ic, ver, rev, support = pn532.firmware_version
        print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
        break
    except Exception as exp:
        attempts += 1
        if attempts > 10:
            logging.warning(f"RFID startup failure: {exp}")
        print("failed to start RFID")
        sleep(1)
        
pn532.SAM_configuration() # Configure PN532 to communicate with MiFare cards

'''
=========================================================================================================
VLC init
=========================================================================================================
'''

def play_video(path):
    try:
        player.set_fullscreen(True) # set full screen
        player.set_mrl(path)    #setting the media in the mediaplayer object created
        player.play()           # play the video
    except Exception as exp:
        logging.error(f"error within play_video {exp}")
'''
=========================================================================================================
RFID functions
=========================================================================================================
'''

def rfid_read(read_block):
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
    return read_data


def rfid_present():
    '''
    checks if the card is present inside the box
    '''
    try:
        uid = pn532.read_passive_target(timeout=0.5) #read the card
    except RuntimeError:
        uid = None
    except Exception as exp:
        logging.warning(f"unexpected rfid error: {exp}")

    return uid


'''
=========================================================================================================
"MAIN"
=========================================================================================================
'''
def main():

    print('Welcome to Poison Scanner')

    play_default_video = True #play default video

    while True:

        gc.collect()

        if player.get_state() == vlc.State.Ended or play_default_video:
            play_video(config['PATH']['video'] + "/default.mov")
            play_default_video = False

        if rfid_present():

            # uid = rfid_present()
            GPIO.output(config["PIN"][city]["UV_light_pin"], config["PIN"][city]["UV_LIGHT_ON"])
            read_data = rfid_read(config["BLOCK"]["read_block"])
            
            if read_data in config["CARDS"]["poisoned_cards"] + config["CARDS"]["non_poisoned_cards"]:
                pass
            else:
                print('Wrong Card')
                play_video(config['PATH']['video'] + "/try_again.mov")

            if read_data in config["CARDS"]["poisoned_cards"]:
                play_video(config['PATH']['video'] + "/scanner_toxic_sound.mp4")
                print('Poisoned card')
            elif read_data in config["CARDS"]["non_poisoned_cards"]:
                play_video(config['PATH']['video'] + "/scanner_nontoxic_sound.mp4")
                print('Non poisoned card')

  
            while rfid_present():
                 continue

            print("Card Removed")

            GPIO.output(config["PIN"][city]["UV_light_pin"], config["PIN"][city]["UV_LIGHT_OFF"]) 
            play_default_video = True


if __name__ == "__main__":
    try:
        main()
    except Exception as exp:
        logging.error(f"fatal Error: {exp}")
    finally:
        subprocess.call(['sh', './start.sh'])

