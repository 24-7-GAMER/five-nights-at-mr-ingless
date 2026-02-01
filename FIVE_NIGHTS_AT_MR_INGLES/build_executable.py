#!/usr/bin/env python3
"""
Cross-platform executable builder for Five Nights at Mr Ingles
Detects platform and creates appropriate executable (.exe, .app, or binary)
"""

import sys
import os
import platform
import subprocess
import shutil

def get_platform_info():
    """Detect current platform"""
    system = platform.system()
    if system == "Windows":
        return "Windows", ".exe"
    elif system == "Darwin":
        return "macOS", ".app"
    elif system == "Linux":
        return "Linux", ""
    else:
        return "Unknown", ""

def check_pyinstaller():
    """Check if PyInstaller is installed, install if needed"""
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
        return True
    except ImportError:
        print("✗ PyInstaller not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to install PyInstaller: {e}")
            return False

def check_pillow():
    """Check if Pillow is installed (optional, for icon conversion)"""
    try:
        import PIL
        print("✓ Pillow is installed (icons enabled)")
        return True
    except ImportError:
        print("⚠ Pillow not found (installing for icon support...)")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            print("✓ Pillow installed successfully")
            return True
        except Exception as e:
            print(f"⚠ Could not install Pillow - building without icon: {e}")
            return False

def build_executable():
    """Build the executable for current platform"""
    system, ext = get_platform_info()
    
    print(f"\n{'='*60}")
    print(f"Five Nights at Mr Ingles - Executable Builder")
    print(f"{'='*60}")
    print(f"Detected Platform: {system}")
    
    if not check_pyinstaller():
        print("\nFailed to install PyInstaller. Exiting.")
        sys.exit(1)
    
    # Check for Pillow (optional, for icon support)
    has_pillow = check_pillow()
    
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"\nWorking directory: {script_dir}")
    print(f"Building executable...")
    
    # PyInstaller command
    output_name = "FiveNightsAtMrIngles"
    
    # Basic PyInstaller options that work on all platforms
    pyinstaller_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",  # Single file executable
        "--windowed",  # No console window
        "--name",
        output_name,
        "--distpath",
        "./dist",  # Output directory
        "--workpath",
        "./build",
        "--add-data",
        f"assets{os.pathsep}assets",  # Include assets folder
        "main.py"
    ]
    
    # Platform-specific options
    if system == "Windows" and has_pillow:
        # Only add icon if Pillow is available
        pyinstaller_args.extend([
            "--icon",
            "assets/img/office.png",  # Window icon
        ])
    elif system == "macOS":
        pyinstaller_args.extend([
            "--osx-bundle-identifier",
            "com.fiveninghtsatmringles.game",
        ])
    
    try:
        print(f"\nRunning PyInstaller...\n")
        subprocess.run(pyinstaller_args, check=True)
        
        # Determine output file path
        if system == "Windows":
            output_file = f"dist/{output_name}.exe"
        elif system == "macOS":
            output_file = f"dist/{output_name}.app"
        elif system == "Linux":
            output_file = f"dist/{output_name}"
        else:
            output_file = f"dist/{output_name}"
        
        if os.path.exists(output_file):
            print(f"\n{'='*60}")
            print(f"✓ SUCCESS! Executable created!")
            print(f"{'='*60}")
            print(f"\nPlatform: {system}")
            print(f"Output: {output_file}")
            print(f"\nTo run the game:")
            
            if system == "Windows":
                print(f"  Double-click: {output_file}")
                print(f"  Or run: .\\{output_name}.exe")
            elif system == "macOS":
                print(f"  Double-click: {output_file}/{output_name}.app")
                print(f"  Or run: open {output_file}/{output_name}.app")
            elif system == "Linux":
                print(f"  Run: ./{output_file}")
                print(f"  Or: chmod +x {output_file} && ./{output_file}")
            
            print(f"\nNote: The 'dist' folder can be shared with others on the same platform!")
            print(f"They can run the game without Python installed.\n")
        else:
            print(f"\n✗ Build failed - output file not found at {output_file}")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error:")
        print(f"{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error:")
        print(f"{e}")
        sys.exit(1)

def main():
    """Main entry point"""
    try:
        build_executable()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
