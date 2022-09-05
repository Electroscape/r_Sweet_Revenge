# For clean start
# Kill all relevant programs
sudo pkill fbi
sudo pkill vlc
sudo pkill python

cd ~/POISON_SCANNER/

# python script 
sudo fbi -T 1 -noverbose -a /home/2cp/POISON_SCANNER/img/hh/black_screen.jpg &
python3 src/poison_scanner.py -c hh

