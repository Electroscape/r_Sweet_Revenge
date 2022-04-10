## Copy this script to the home directory and make it autostart on boot
# crontab -e
## at the end of the file paste the following line
# @reboot sleep 15 && bash ~/POISON_SCANNER/restart.sh

sudo pkill python
export DISPLAY=:0.0
xhost +
bash ~/POISON_SCANNER/start.sh

