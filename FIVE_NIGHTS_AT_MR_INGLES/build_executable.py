#!/usr/bin/env python3
"""
Build executable for Five Nights at Mr Ingles's
Creates a standalone .exe with PyInstaller
"""

import sys
import os
import shutil
import subprocess

def main():
    """Build the executable with error handling"""
    try:
        # Change to script directory to ensure we're in the right place
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        print("=" * 60)
        print("Building Five Nights at Mr Ingles's Executable")
        print("=" * 60)
        print(f"Working directory: {os.getcwd()}")
        print()
        
        # Check if PyInstaller is installed
        try:
            import PyInstaller
            print(f"✓ PyInstaller found: {PyInstaller.__version__}")
        except ImportError:
            print("✗ PyInstaller not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
        
        print()
        
        # Clean previous builds
        print("Cleaning previous builds...")
        for folder in ['build', 'dist']:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    print(f"  ✓ Removed {folder}/")
                except Exception as e:
                    print(f"  ⚠ Warning: Could not remove {folder}/: {e}")
        
        # Remove old spec file
        spec_file = "main.spec"
        if os.path.exists(spec_file):
            try:
                os.remove(spec_file)
                print(f"  ✓ Removed {spec_file}")
            except Exception as e:
                print(f"  ⚠ Warning: Could not remove {spec_file}: {e}")
        
        print()
        
        # Build command
        print("Building executable with PyInstaller...")
        print()
        
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--onefile",                    # Single executable file
            "--windowed",                   # No console window (GUI app)
            "--name", "FiveNightsAtMrIngles",  # Output name
            "--add-data", "assets;assets",  # Include assets folder
            "--icon", "assets/img/office.png" if os.path.exists("assets/img/office.png") else "NONE",
            "--clean",                      # Clean PyInstaller cache
            "main.py"
        ]
        
        print("Command:", " ".join(cmd))
        print()
        
        # Run PyInstaller (show all output)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Always show output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print()
            print("=" * 60)
            print("✗ BUILD FAILED")
            print("=" * 60)
            print(f"PyInstaller exited with code {result.returncode}")
            print()
            print("Common issues:")
            print("  1. Missing dependencies - run: pip install -r requirements.txt")
            print("  2. Antivirus blocking PyInstaller")
            print("  3. File permissions in build/dist folders")
            print()
            input("Press Enter to exit...")
            sys.exit(1)
        
        print()
        print("=" * 60)
        print("✓ BUILD SUCCESSFUL")
        print("=" * 60)
        
        # Check if executable exists
        exe_path = os.path.join("dist", "FiveNightsAtMrIngles.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Executable: {exe_path}")
            print(f"Size: {size_mb:.2f} MB")
            print()
            print("You can now run the game from the dist/ folder!")
        else:
            print(f"⚠ Warning: Expected executable not found at {exe_path}")
            print("Check the dist/ folder manually")
        
        print()
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n✗ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 60)
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Keep window open
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
