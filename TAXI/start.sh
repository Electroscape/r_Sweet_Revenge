export DISPLAY=:0
xhost +

sudo pkill python
sudo pkill fbi
sudo pkill vlc

cd ~/TAXI
python3 src/taxi.py -c hh
