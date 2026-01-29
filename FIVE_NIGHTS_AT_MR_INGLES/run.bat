@echo off
REM Five Nights at Mr Ingles's - Python Launcher
REM This script sets up and runs the game on Windows.
REM What this does:
REM  - Checks for Python on PATH
REM  - Ensures Pygame is installed (installs via pip using requirements.txt)
REM  - Runs `python main.py`

echo ========================================
echo Five Nights at Mr Ingles's (Python)
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Pygame...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting game...
python main.py
REM Pause at the end so any error messages remain visible
pause
