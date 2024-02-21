#!/bin/bash
cd "$(dirname "$0")" || exit

pkill python
export DISPLAY=:0.0
xhost +
source venv/bin/activate

# python script 
sudo fbi -T 1 -noverbose -a /home/2cp/POISON_SCANNER/img/hh/black_screen.jpg &
python3 src/poison_scanner.py -c st

