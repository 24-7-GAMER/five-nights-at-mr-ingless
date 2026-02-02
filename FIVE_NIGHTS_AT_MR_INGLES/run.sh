#!/bin/bash
# Five Nights at Mr Ingles's - Cross-Platform Launcher
# Works on Mac, Linux, and Unix systems
# Simply run: bash run.sh (no chmod +x needed!)

cd "$(dirname "$0")" || exit 1

# Try to find python3, then python
if command -v python3 &> /dev/null; then
    python3 launch.py
elif command -v python &> /dev/null; then
    python launch.py
else
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi
