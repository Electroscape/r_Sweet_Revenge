#!/bin/bash
cd "$(dirname "$0")" || exit
sudo pkill python
export DISPLAY=:0.0
python3 office_pc.py -c s
