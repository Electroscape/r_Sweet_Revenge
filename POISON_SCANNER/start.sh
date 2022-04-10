# For clean start
# Kill all relevant programs
sudo pkill fbi
sudo pkill vlc

cd ~/POISON_SCANNER

# for smooth transition instead of the terminal appearance
sudo fbi -a -T 1 --noverbose img/blackscreen.jpg &

# python script 
python3 src/poison_scanner.py

