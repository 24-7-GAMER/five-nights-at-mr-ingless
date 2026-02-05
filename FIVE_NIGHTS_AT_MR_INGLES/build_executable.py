#!/usr/bin/env python3
"""
Build executable for Five Nights at Mr Ingles's
Creates a standalone .exe with PyInstaller
"""

import sys
import os
import shutil
import subprocess
from collections import deque

def set_terminal_progress(progress):
    """Update Windows Terminal progress bar (OSC 9;4)."""
    progress = max(0.0, min(1.0, progress))
    percent = int(progress * 100)
    # Works in Windows Terminal and some modern terminals
    sys.stdout.write(f"\x1b]9;4;1;{percent}\x07")
    sys.stdout.flush()

def clear_terminal_progress():
    """Clear Windows Terminal progress bar (OSC 9;4)."""
    sys.stdout.write("\x1b]9;4;0\x07")
    sys.stdout.flush()

def render_progress(progress, message=""):
    """Render a single overall progress bar in-place."""
    progress = max(0.0, min(1.0, progress))
    bar_length = 40
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)
    percent = int(progress * 100)
    line = f"[{bar}] {percent:3d}%"
    if message:
        line += f" {message}"
    # Clear the line to avoid leftover text
    print("\r\x1b[2K" + line, end="", flush=True)
    set_terminal_progress(progress)

def main():
    """Build the executable with error handling"""
    try:
        # Change to script directory to ensure we're in the right place
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        desired_name = "Five Nights At Mr Ingles's"
        safe_name = "Five Nights At Mr Ingles"
        data_sep = ";" if os.name == "nt" else ":"
        
        print("Five Nights at Mr Ingles's - Build Tool")
        print(f"Working directory: {os.getcwd()}")

        progress = 0.0
        def update_progress(target, message=""):
            nonlocal progress
            if target > progress:
                progress = target
            render_progress(progress, message)

        update_progress(0.02, "Starting")
        
        # Step 1: Ensure dependencies
        update_progress(0.10, "Installing dependencies")
        
        # Install game requirements first (pygame, etc.)
        requirements_file = "requirements.txt"
        if os.path.exists(requirements_file):
            print("- Installing game requirements")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", requirements_file],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    update_progress(0.20, "Requirements installed")
                else:
                    print("  ✗ Failed to install requirements")
                    print(f"  Error: {result.stderr}")
                    print("  Please run: pip install -r requirements.txt")
                    sys.exit(1)
            except Exception as e:
                print(f"  ✗ Error installing requirements: {e}")
                sys.exit(1)
        else:
            print(f"  ⚠ Warning: {requirements_file} not found")
        
        # Install PyInstaller for building
        update_progress(0.25, "Ensuring PyInstaller")
        try:
            import PyInstaller
            update_progress(0.30, "PyInstaller ready")
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
                update_progress(0.30, "PyInstaller ready")
            except subprocess.CalledProcessError as e:
                print("  ✗ Failed to install PyInstaller")
                print("  Please run: pip install pyinstaller")
                sys.exit(1)
        
        # Step 2: Clean previous builds
        update_progress(0.35, "Cleaning previous builds")
        for i, folder in enumerate(['build', 'dist'], 1):
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                except Exception as e:
                    print(f"\n- Warning removing {folder}/: {e}")
        
        # Remove old spec files
        for spec_file in (f"{safe_name}.spec", f"{desired_name}.spec", "main.spec"):
            if os.path.exists(spec_file):
                os.remove(spec_file)
        update_progress(0.40, "Cleanup complete")
        
        # Step 3: Verify assets
        update_progress(0.45, "Verifying assets")
        icon_path = "assets/img/title.png"
        if os.path.exists(icon_path):
            pass
        else:
            icon_path = "NONE"
        
        if os.path.exists("assets"):
            asset_count = sum([len(files) for _, _, files in os.walk("assets")])
        else:
            print("\n- Warning: assets folder not found")
        
        # Step 4: Build executable
        update_progress(0.50, "Building executable")
        
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--onefile",                    # Single executable file
            "--windowed",                   # No console window (GUI app)
            "--name", safe_name,             # Safe output name for .spec generation
            "--add-data", f"assets{data_sep}assets",  # Include assets folder
            "--icon", icon_path,            # Use title.png as icon
            "--clean",                      # Clean PyInstaller cache
            "main.py"
        ]
        
        recent_lines = deque(maxlen=60)
        
        # Run PyInstaller with live output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output and update progress based on PyInstaller milestones
        milestone_map = [
            ("analyzing", 0.60, "Analyzing"),
            ("building pyz", 0.70, "Building PYZ"),
            ("building pkg", 0.80, "Building PKG"),
            ("building exe", 0.88, "Building EXE"),
            ("copying bootloader", 0.90, "Copying bootloader"),
            ("appending", 0.93, "Finalizing"),
            ("writing", 0.94, "Finalizing"),
            ("completed successfully", 0.95, "Finalizing"),
        ]

        for line in process.stdout:
            line_stripped = line.rstrip()
            if line_stripped:
                recent_lines.append(line_stripped)
            lower = line_stripped.lower()
            for pattern, prog, msg in milestone_map:
                if pattern in lower:
                    update_progress(prog, msg)
                    break
        
        process.wait()
        result_code = process.returncode
        
        if result_code != 0:
            print("\nBuild failed")
            print(f"PyInstaller exited with code {result_code}")
            print("Common issues:")
            print("- Missing dependencies: pip install -r requirements.txt")
            print("- Antivirus blocking PyInstaller")
            print("- File permissions in build/dist folders")
            if recent_lines:
                print("\nLast output:")
                for line in recent_lines:
                    print(line)
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        update_progress(0.97, "Verifying output")
        
        exe_path = os.path.join("dist", f"{safe_name}.exe")
        desired_exe_path = os.path.join("dist", f"{desired_name}.exe")
        if os.path.exists(exe_path):
            if os.path.exists(desired_exe_path):
                os.remove(desired_exe_path)
            os.rename(exe_path, desired_exe_path)
            exe_path = desired_exe_path
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            update_progress(1.0, "Done")
            print("\nBuild successful")
            print(f"Output: {exe_path}")
            print(f"Size: {size_mb:.2f} MB")
            print("The game is ready to distribute.")
        else:
            update_progress(1.0, "Done")
            print("\nWarning: Expected executable not found")
            print(f"Looking for: {exe_path}")
            print("Check the dist/ folder manually")
        clear_terminal_progress()
        
    except KeyboardInterrupt:
        print("\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print("\nUnexpected error")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print()
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Keep window open
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
