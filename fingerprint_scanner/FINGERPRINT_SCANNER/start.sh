#!/bin/bash
cd "$(dirname "$0")"

sudo pkill python
export DISPLAY=:0.0

# cd ~/Tatort_test/r_Sweet_Revenge/fingerprint_scanner/FINGERPRINT_SCANNER/src/
python3 fingerprint_scanner.py -c hh
