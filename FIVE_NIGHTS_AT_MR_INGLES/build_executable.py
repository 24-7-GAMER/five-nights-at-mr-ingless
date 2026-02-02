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

def create_icns_from_png(png_path, icns_path):
    """Convert PNG to ICNS format for macOS"""
    try:
        from PIL import Image
        img = Image.open(png_path)
        
        # Create iconset directory
        iconset_dir = "icon.iconset"
        os.makedirs(iconset_dir, exist_ok=True)
        
        # Generate all required sizes for macOS
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            # Standard resolution
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(f"{iconset_dir}/icon_{size}x{size}.png")
            
            # Retina resolution (except 1024)
            if size <= 512:
                retina_size = size * 2
                resized_retina = img.resize((retina_size, retina_size), Image.Resampling.LANCZOS)
                resized_retina.save(f"{iconset_dir}/icon_{size}x{size}@2x.png")
        
        # Convert iconset to icns using macOS tool
        result = subprocess.run(
            ["iconutil", "-c", "icns", iconset_dir, "-o", icns_path],
            capture_output=True,
            text=True
        )
        
        # Clean up iconset directory
        shutil.rmtree(iconset_dir, ignore_errors=True)
        
        if result.returncode == 0 and os.path.exists(icns_path):
            print(f"✓ Created macOS icon: {icns_path}")
            return True
        else:
            print(f"⚠ iconutil failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"⚠ Could not create .icns file: {e}")
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
        # Hidden imports for pygame (especially important for macOS)
        "--hidden-import",
        "pygame",
        "--hidden-import",
        "pygame.mixer",
        "--hidden-import",
        "pygame.font",
        "--hidden-import",
        "pygame.time",
        "--hidden-import",
        "pygame.display",
        "--hidden-import",
        "pygame.image",
        "--hidden-import",
        "pygame.transform",
        "--collect-all",
        "pygame",
        "main.py"
    ]
    
    # Platform-specific options
    if system == "Windows" and has_pillow:
        # Use title.png for Windows icon
        pyinstaller_args.extend([
            "--icon",
            "assets/img/title.png",
        ])
    elif system == "macOS":
        # macOS bundle configuration
        pyinstaller_args.extend([
            "--osx-bundle-identifier",
            "com.fiveninghtsatmringles.game",
        ])
        
        # Create .icns icon from title.png if possible
        if has_pillow and os.path.exists("assets/img/title.png"):
            icns_path = "app_icon.icns"
            if create_icns_from_png("assets/img/title.png", icns_path):
                pyinstaller_args.extend([
                    "--icon",
                    icns_path,
                ])
        
        # Add macOS-specific pygame fix
        pyinstaller_args.extend([
            "--osx-entitlements-file",
            "entitlements.plist",
        ])
        
        # Create entitlements.plist for pygame compatibility
        entitlements_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
</dict>
</plist>"""
        with open("entitlements.plist", "w") as f:
            f.write(entitlements_content)
        print("✓ Created macOS entitlements file for pygame compatibility")
    
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
                print(f"  Double-click: {output_file}")
                print(f"  Or run: open {output_file}")
            elif system == "Linux":
                print(f"  Run: ./{output_file}")
                print(f"  Or: chmod +x {output_file} && ./{output_file}")
            
            # Cleanup temporary files
            if system == "macOS":
                if os.path.exists("entitlements.plist"):
                    os.remove("entitlements.plist")
                    print("\n✓ Cleaned up temporary files")
                if os.path.exists("app_icon.icns"):
                    os.remove("app_icon.icns")
            
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
