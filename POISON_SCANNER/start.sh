# For clean start
# Kill all relevant programs
sudo pkill fbi
sudo pkill vlc
sudo pkill python

cd ~/POISON_SCANNER

# for smooth transition instead of the terminal appearance
sudo fbi -a -T 1 --noverbose img/black_screen.jpg &

# python script 
python3 src/poison_scanner.py

