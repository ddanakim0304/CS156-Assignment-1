#!/usr/bin/env python3
"""
Quick setup and launcher for the Cuphead keystroke logger.
"""

import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import pynput
        import yaml
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "pynput", "PyYAML"
        ], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def main():
    """Main setup and launcher."""
    print("Cuphead Boss Keystroke Logger - Setup")
    print("=" * 40)
    
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}")
    
    # Check dependencies
    if not check_dependencies():
        print("\nInstalling missing dependencies...")
        if not install_dependencies():
            print("Setup failed. Please install dependencies manually:")
            print("pip install pynput PyYAML")
            return 1
    
    # Check permissions on macOS
    if sys.platform == "darwin":
        print("\n" + "="*50)
        print("IMPORTANT: macOS Accessibility Permissions")
        print("="*50)
        print("This app requires Accessibility permissions to capture")
        print("global keyboard events. To grant permissions:")
        print()
        print("1. Open System Preferences > Security & Privacy")
        print("2. Click 'Privacy' tab")
        print("3. Select 'Accessibility' from left sidebar")
        print("4. Click lock icon and enter password")
        print("5. Add Terminal or Python to the list")
        print("6. Restart this application")
        print("="*50)
    
    print("\n✓ Setup complete!")
    print("\nAvailable commands:")
    print("  python main.py        - GUI version (recommended)")
    print("  python cli_logger.py  - Command-line version")
    print("  python demo.py        - Create sample data")
    print("  python test_logger.py - Run tests")
    
    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Launch GUI version")
    print("2. Launch CLI version") 
    print("3. Run demo (create sample data)")
    print("4. Run tests")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                print("\nLaunching GUI version...")
                subprocess.run([sys.executable, "main.py"])
                break
            elif choice == "2":
                print("\nLaunching CLI version...")
                subprocess.run([sys.executable, "cli_logger.py"])
                break
            elif choice == "3":
                print("\nRunning demo...")
                subprocess.run([sys.executable, "demo.py"])
                break
            elif choice == "4":
                print("\nRunning tests...")
                subprocess.run([sys.executable, "test_logger.py"])
                break
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    
    return 0


if __name__ == "__main__":
    sys.exit(main())