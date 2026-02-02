@echo off
REM Five Nights at Mr Ingles's - Windows Launcher
REM Simply double-click this file to play!

cd /d "%~dp0" || exit /b 1

REM Try to find python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Starting Five Nights at Mr Ingles's...
python launch.py
pause
