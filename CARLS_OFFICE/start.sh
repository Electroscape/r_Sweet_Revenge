#!/bin/bash
cd "$(dirname "$0")" || exit
export DISPLAY=:0.0
python3 carls_office.py -c hh