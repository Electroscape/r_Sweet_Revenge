#!/bin/bash
sudo pkill python
cd "${0%/*}" || exit

source venv/bin/activate

echo "$VIRTUAL_ENV"

# Check if the venv is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Virtual environment not activated!"
    exit 1
fi

export DISPLAY=:0.0
python video_5.py -c "st"