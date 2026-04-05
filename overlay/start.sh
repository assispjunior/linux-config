#!/bin/bash
pgrep -f "tray.py"   | xargs kill -9 2>/dev/null
pgrep -f "overlay.py"| xargs kill -9 2>/dev/null
sleep 1
cd "$(dirname "$0")"
python3 tray.py &
