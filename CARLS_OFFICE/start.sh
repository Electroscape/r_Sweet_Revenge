#!/bin/bash
cd "$(dirname "$0")" || exit
sudo pkill python
export DISPLAY=:0.0
python3 carls_office.py -c st