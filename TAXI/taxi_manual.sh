echo "running taxi manual"
sudo pkill python
sudo pkill omxplayer
raspi-gpio set 22 op
raspi-gpio set 22 dh
omxplayer ~/taxi/SuesseRache_S_Taxifahrt.mp4 --no-osd &&
raspi-gpio set 22 dl
omxplayer ~/taxi/arrow.mp4 --no-osd --loop &
echo "finished"