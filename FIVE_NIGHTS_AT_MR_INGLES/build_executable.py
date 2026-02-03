#!/usr/bin/env python3
"""
Simple Cross-Platform Build Script
Builds standalone executable for Five Nights at Mr Ingles's
"""

import sys
import os
import shutil
import subprocess
import platform

def main():
    """Simple build process with clear step-by-step output"""
    
    # Move to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "="*60)
    print("  Five Nights at Mr Ingles's - Build Script")
    print("="*60 + "\n")
    
    # STEP 1: Clean old builds
    print("[1/4] Cleaning old builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"      Removing {folder}/")
            shutil.rmtree(folder)
    
    # Remove old spec files
    for spec in ['Five Nights At Mr Ingles.spec', 'main.spec']:
        if os.path.exists(spec):
            os.remove(spec)
    
    print("      ✓ Cleanup complete\n")
    
    # STEP 2: Check PyInstaller
    print("[2/4] Checking PyInstaller...")
    try:
        import PyInstaller
        print(f"      ✓ PyInstaller {PyInstaller.__version__} found\n")
    except ImportError:
        print("      Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("      ✓ PyInstaller installed\n")
    
    # STEP 3: Verify assets
    print("[3/4] Verifying assets...")
    if not os.path.exists("assets"):
        print("      ✗ ERROR: assets/ folder not found!")
        sys.exit(1)
    
    icon = "assets/img/title.png"
    if not os.path.exists(icon):
        print("      ⚠ Warning: Icon not found, using default")
        icon = "NONE"
    else:
        print(f"      ✓ Icon: {icon}")
    
    asset_count = sum(len(files) for _, _, files in os.walk("assets"))
    print(f"      ✓ Found {asset_count} asset files\n")
    
    # STEP 4: Build executable
    print("[4/4] Building executable...")
    print("      This may take 1-2 minutes...\n")
    print("-"*60)
    
    # Detect platform
    is_windows = platform.system() == "Windows"
    separator = ";" if is_windows else ":"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Five Nights At Mr Ingles",
        "--add-data", f"assets{separator}assets",
        "--icon", icon,
        "--clean",
        "main.py"
    ]
    
    # Run PyInstaller with live output
    result = subprocess.run(cmd, text=True)
    
    print("-"*60 + "\n")
    
    if result.returncode != 0:
        print("✗ BUILD FAILED!")
        print("\nCommon fixes:")
        print("  • Run: pip install -r requirements.txt")
        print("  • Check if antivirus is blocking PyInstaller")
        print("  • Make sure main.py and assets/ exist")
        sys.exit(1)
    
    # Verify output
    exe_name = "Five Nights At Mr Ingles.exe" if is_windows else "Five Nights At Mr Ingles"
    exe_path = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("="*60)
        print("  ✓ BUILD SUCCESSFUL!")
        print("="*60)
        print(f"  File: {exe_path}")
        print(f"  Size: {size_mb:.1f} MB")
        print("\n  Ready to distribute!")
        print("="*60 + "\n")
    else:
        print("⚠ Build completed but executable not found")
        print(f"  Expected: {exe_path}")
        print("  Check dist/ folder manually\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Build cancelled by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
