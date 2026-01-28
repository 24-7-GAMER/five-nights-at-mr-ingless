#!/bin/bash
# Five Nights at Mr Ingles's - Python Launcher (Unix/Linux/Mac)

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
