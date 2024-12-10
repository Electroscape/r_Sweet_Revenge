pkill python
export DISPLAY=:0.0

cd "${0%/*}" || exit

source venv/bin/activate
python video_5.py -c "st"