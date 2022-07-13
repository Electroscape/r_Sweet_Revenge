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

'''
=========================================================================================================
Argument parser
=========================================================================================================
'''

argparser = argparse.ArgumentParser(
    description='Microscope')

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
    try:
        # Non-hardware reset/request with I2C
        pn532 = PN532_I2C(i2c, debug=False)
        ic, ver, rev, support = pn532.firmware_version
        print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
        break
    except:
        print("failed to start RFID")
        sleep(1)
        
pn532.SAM_configuration() # Configure PN532 to communicate with MiFare cards

'''
=========================================================================================================
VLC init
=========================================================================================================
'''

def play_video(path):

    '''
    Description
    -----------
    Displaying the video once sensor is high
    set the mrl of the video to the mediaplayer
    play the video and

    '''
    player.set_fullscreen(True) # set full screen
    player.set_mrl(path)    #setting the media in the mediaplayer object created
    player.play()           # play the video
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

    return uid


'''
=========================================================================================================
"MAIN"
=========================================================================================================
'''
def main():

    print('Welcome to Poison Scanner')

    pdv = True #play default video

    print('Waiting Card')

    while True:
        gc.collect()
        if player.get_state() == vlc.State.Ended or pdv==True:

            play_video(config['PATH']['video'] + "/default.mov")
            pdv = False

        if rfid_present():

            uid = rfid_present()

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
            pdv = True


if __name__ == "__main__":
    main()
