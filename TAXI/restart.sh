export DISPLAY=:0
xhost +

echo "restarting"
sudo pkill omxplayer
sudo pkill python
sudo python ~/taxi/video_5.py
