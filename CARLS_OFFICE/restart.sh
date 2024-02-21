#!/bin/bash
cd "$(dirname "$0")" || exit

sudo pkill python
bash start.sh
