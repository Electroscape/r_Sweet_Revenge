import argparse
import time
import datetime
import json
import os
from tokenize import String
import vlc
import RPi.GPIO as GPIO

video_length = 26

argparser = argparse.ArgumentParser(
    description='Taxi')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]')


city = argparser.parse_args().city


# adjusted the path in start.sh, so no foldername needed here
with open('src/config.json', 'r') as config_file:
    config = json.load(config_file)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# no extra variable needed
GPIO.setup(config["PIN"][city]["sensor"], GPIO.IN)
# no extra variable needed
GPIO.setup(config["PIN"][city]["relay"], GPIO.OUT)
# no extra variable needed, True = GPIO.HIGH
GPIO.output(config["PIN"][city]["relay"], True)


# creating Instance class object
vlc_instance = vlc.Instance( ) # creating Instance class object
player = vlc_instance.media_player_new() # creating a new media object
player.set_fullscreen(True) # set full screen
player.set_mrl(config["PATH"]["image"] + city + "/TaxiLogo.png")
player.play()


# Motion Detection boolean check
# No camelCase in Python, always use snake_case
def get_motion_detected(sensor_input):
    '''
    Description
    -----------
    Checking the output of the connected sensor.\n
    Is motion detected?

    Parameters
    ----------
    sensor_input : *int*
        - 0 = no motion
        - 1 = motion
    '''
    if sensor_input == 1:
        return True
    return False


def get_door_closed(sensor_input):
    '''
    Description
    -----------
    Checking the output of the connected sensor.\n
    Is door closed?

    Parameters
    ----------
    sensor_input : *int*
        - 0 = door open
        - 1 = door closed
    '''
    if sensor_input == 1:
        return True
    return False


def play_video(path):

    '''
    Description
    -----------
    Displaying the video once sensor is high
    set the mrl of the video to the mediaplayer
    play the video and

    Check if its the taxi video or arrow ?
    "mp4" = Taxi video
    "png" = ArrowLogo
    '''
    

    player.set_mrl(path)    #setting the media in the mediaplayer object created
    player.play()           # play the video
    if path[-3:] == "mp4":  #check if its the taxi video, if not its the arrow video 
        while player.get_state() != vlc.State.Ended : # loop until the video is finished
            continue
        return True
    else :  # the taxi video is finished, display the arrow
        while True:
            continue
    

def end_of_video():
    '''
    Description
    -----------
    Sequence after playing the video.\n
    Opens the door and shows the arrow.

    Parameters
    ----------
    None
    '''
    set_exit_door(config["PIN"][city]["door_open"])
    play_video(config["PATH"]["image"] + city + "/ArrowLogo.png")



def set_exit_door(value):
    '''
    Description
    -----------
    Controls the relay of the exit door.\n
    Configuration of door open/closed in config.json

    Parameters
    ----------
    value : *bool*
        - True: GPIO.HIGH
        - False: GPIO.LOW
    '''
    GPIO.output(config["PIN"][city]["relay"], value)
    


def start_conditions_hh():
    '''
    Description
    -----------
    Conditions to start the taxi sequence in Hamburg.\n

    Parameters
    ----------
    None

    Return
    ----------
    True: motion detected
    False: no motion detected
    '''
    if get_motion_detected(GPIO.input(config["PIN"][city]["sensor"])):
        return True
    return False


def start_conditions_st():
    '''
    Description
    -----------
    Conditions to start the taxi sequence in Stuttgart.\n
    Sequence:\n
    - players open door
    - players get in
    - players close door

    Parameters
    ----------
    None

    Return
    ----------
    True: sequence complete
    False: door not opened yet
    '''
    if not get_door_closed(GPIO.input(config["PIN"][city]["sensor"])):
        while not get_door_closed(GPIO.input(config["PIN"][city]["sensor"])):
            pass
        return True
    return False


def main():

    if city == "hh":
        while not start_conditions_hh():
            pass
    elif city == "st":
        while not start_conditions_st():
            pass

    # if play_video finished it returns True -> end_of_video starts
    if play_video(config["PATH"]["video"] + city + "/TE_SR_Taxi.mp4"):
        end_of_video()


if __name__ == "__main__":
    main()
