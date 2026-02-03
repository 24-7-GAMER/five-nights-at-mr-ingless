#!/usr/bin/env python3
"""
Build executable for Five Nights at Mr Ingles's
Creates a standalone .exe with PyInstaller
"""

import sys
import os
import shutil
import subprocess
import time

def print_progress(message, progress=None):
    """Print a progress message with optional progress bar"""
    if progress is not None:
        bar_length = 40
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        percentage = int(progress * 100)
        print(f"\r{message} [{bar}] {percentage}%", end='', flush=True)
    else:
        print(f"► {message}")

def main():
    """Build the executable with error handling"""
    try:
        # Change to script directory to ensure we're in the right place
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        print("=" * 70)
        print(" " * 15 + "Five Nights at Mr Ingles's - Build Tool")
        print("=" * 70)
        print(f"Working directory: {os.getcwd()}")
        print()
        
        # Step 1: Check PyInstaller
        print_progress("Step 1/5: Checking PyInstaller installation")
        try:
            import PyInstaller
            print(f" ✓ Found version {PyInstaller.__version__}")
        except ImportError:
            print(" ✗ Not found, installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                                stdout=subprocess.DEVNULL)
            print_progress("Step 1/5: PyInstaller installed successfully")
        
        time.sleep(0.3)
        print()
        
        # Step 2: Clean previous builds
        print_progress("Step 2/5: Cleaning previous builds")
        for i, folder in enumerate(['build', 'dist'], 1):
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    print(f"\r► Step 2/5: Cleaning previous builds - Removed {folder}/", flush=True)
                except Exception as e:
                    print(f"\r► Step 2/5: Cleaning previous builds - Warning: {e}", flush=True)
            time.sleep(0.2)
        
        # Remove old spec file
        spec_file = "Five Nights At Mr Ingles's.spec"
        if os.path.exists(spec_file):
            os.remove(spec_file)
        spec_file = "main.spec"
        if os.path.exists(spec_file):
            os.remove(spec_file)
        print_progress("Step 2/5: Cleanup complete", 1.0)
        print()
        time.sleep(0.3)
        
        # Step 3: Verify assets
        print_progress("Step 3/5: Verifying assets")
        icon_path = "assets/img/title.png"
        if os.path.exists(icon_path):
            print(f" ✓ Icon found: {icon_path}")
        else:
            print(f" ⚠ Icon not found: {icon_path}, will use default")
            icon_path = "NONE"
        
        if os.path.exists("assets"):
            asset_count = sum([len(files) for _, _, files in os.walk("assets")])
            print(f" ✓ Assets folder found ({asset_count} files)")
        else:
            print(" ⚠ Warning: assets folder not found!")
        
        time.sleep(0.3)
        print()
        
        # Step 4: Build executable
        print_progress("Step 4/5: Building executable with PyInstaller")
        print()
        print("-" * 70)
        
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--onefile",                    # Single executable file
            "--windowed",                   # No console window (GUI app)
            "--name", "Five Nights At Mr Ingles's",  # Output name with proper spacing
            "--add-data", "assets;assets",  # Include assets folder
            "--icon", icon_path,            # Use title.png as icon
            "--clean",                      # Clean PyInstaller cache
            "main.py"
        ]
        
        print("PyInstaller command:")
        print("  " + " ".join(cmd))
        print("-" * 70)
        print()
        
        # Run PyInstaller with live output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(f"  {line.rstrip()}")
        
        process.wait()
        result_code = process.returncode
        
        print()
        print("-" * 70)
        
        if result_code != 0:
            print()
            print("=" * 70)
            print("  ✗ BUILD FAILED")
            print("=" * 70)
            print(f"  PyInstaller exited with code {result_code}")
            print()
            print("  Common issues:")
            print("    1. Missing dependencies - run: pip install -r requirements.txt")
            print("    2. Antivirus blocking PyInstaller")
            print("    3. File permissions in build/dist folders")
            print("=" * 70)
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        print()
        
        # Step 5: Verify output
        print_progress("Step 5/5: Verifying build output")
        time.sleep(0.5)
        
        exe_path = os.path.join("dist", "Five Nights At Mr Ingles's.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f" ✓ Executable created successfully!")
            print()
            print("=" * 70)
            print("  ✓ BUILD SUCCESSFUL!")
            print("=" * 70)
            print(f"  Output: {exe_path}")
            print(f"  Size: {size_mb:.2f} MB")
            print()
            print("  The game is ready to distribute!")
            print("  Anyone with Windows can run it - no Python needed.")
            print("=" * 70)
        else:
            print(f" ⚠ Warning: Expected executable not found")
            print(f"   Looking for: {exe_path}")
            print("   Check the dist/ folder manually")
            print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("  ✗ Build cancelled by user")
        print("=" * 70)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 70)
        print("  ✗ UNEXPECTED ERROR")
        print("=" * 70)
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 70)
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Keep window open
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
