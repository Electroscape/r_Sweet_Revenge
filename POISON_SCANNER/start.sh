## Copy this script to the home directory and make it autostart on boot
# crontab -e
## at the end of the file paste the following line
# @reboot sleep 15 && bash ~/run.sh

cd TE/Rooms/Sweet_Revenge/poison_scanner

# for smooth transition instead of terminal appearance
sudo fbi -a -T 1 --noverbose blackscreen.jpg &

# python script 
python3 poison_scanner.py

