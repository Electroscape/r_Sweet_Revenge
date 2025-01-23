import RPi.GPIO as GPIO
from time import sleep
import vlc
import json
import argparse


argparser = argparse.ArgumentParser(
    description='Taxi')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]',
    default="st"
)

city = argparser.parse_args().city
print(f"setting up for a {city} config")

try:
    with open('config.json') as json_file:
        cfg = json.loads(json_file.read())
        cfg = cfg[city]
        sensor_pin = cfg["sensor"]
        relay_pin = cfg["relay"]
        video_length = cfg["video_length"]
except ValueError as e:
    print('failure to read config.json')
    exit(e)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, GPIO.HIGH)


def set_video(_player, filename):
    media = instance.media_new(filename)  # Create a new media
    _player.set_media(media)
    _player.play()

instance = vlc.Instance('--quiet')
player = instance.media_player_new()
set_video(player, "taxi_start.mp4")
player.toggle_fullscreen()
sleep(0.5)
player.pause()

sleep(1)

def is_door_open():
    return GPIO.input(sensor_pin)


def door_triggered():
    if is_door_open():
        sleep(0.5)
        return is_door_open()
    sleep(0.5)
    return False

def main():
    while is_door_open():
        print("waiting to close door to arm")
        sleep(1)

    print("door closed the first time, armed now")

    while True:
        if door_triggered():
            print("entering video loop")
            while True:
                if not is_door_open():
                    if door_triggered():
                        continue
                    print("Tuer wieder geschlossen")
                    set_video(player, 'SuesseRache_S_Taxifahrt.mp4')
                    sleep(video_length)
                    GPIO.output(relay_pin, GPIO.LOW)
                    set_video(player, 'arrow.mp4')
                    sleep(0.5)
                    player.pause()
                    sleep(5400)


if __name__ == "__main__":
    main()

