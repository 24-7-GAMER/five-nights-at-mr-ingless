#!/bin/bash
# Five Nights at Mr Ingles's - Python Launcher (Unix/Linux/Mac)
# This script sets up and runs the game on Unix-like systems.
# What this does:
#  - checks for Python 3 on PATH
#  - ensures Pygame is installed (installs via pip using requirements.txt)
#  - runs `python3 main.py`

echo "========================================"
echo "Five Nights at Mr Ingles's (Python)"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

echo "Checking dependencies..."
python3 -c "import pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Pygame..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "Starting game..."
python3 main.py
