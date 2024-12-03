echo "opening taxi"
sudo pkill python
sudo pkill omxplayer
omxplayer ~/taxi/arrow.mp4 --no-osd --loop &
raspi-gpio set 22 op
raspi-gpio set 22 dl
