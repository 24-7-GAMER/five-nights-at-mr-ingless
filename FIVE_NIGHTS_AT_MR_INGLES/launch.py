#!/usr/bin/env python3
"""
Universal Game Launcher
Works on Windows, Mac, and Linux without requiring chmod +x
Just double-click this file or run 'python launch.py'
"""

import os
import sys
import subprocess

def main():
    """Launch the game"""
    # Get the directory this script is in
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    
    # Change to the script directory so relative paths work
    try:
        os.chdir(script_dir)
        print(f"Working directory: {os.getcwd()}")
    except Exception as e:
        print(f"Warning: Could not change to script directory: {e}")
    
    # Verify main.py exists
    if not os.path.exists(main_script):
        print(f"ERROR: Could not find main.py in {script_dir}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Run the game
    try:
        subprocess.run([sys.executable, main_script], check=True)
    except subprocess.CalledProcessError:
        print("Game exited with an error.")
        input("Press Enter to exit...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
