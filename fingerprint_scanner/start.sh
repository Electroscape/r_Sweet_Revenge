#!/bin/bash
cd "$(dirname "$0")" || exit

pkill python
export DISPLAY=:0.0
xhost +
source venv/bin/activate
python fingerprint_scanner.py -c hh
