#!/usr/bin/env python3
"""
Cuphead Boss Keystroke Logger - Main Application

This application captures keyboard events during Cuphead boss fights
and logs them with precise timestamps for data collection and analysis.

Usage:
    python main.py

Requirements:
    - macOS with Accessibility permissions granted
    - Python 3.7+
    - pynput library for global keyboard capture
    - PyYAML for configuration (optional)

The application creates an always-on-top control panel that allows you to:
- Select boss and configure loadout
- Start/stop recording with F1/F2 hotkeys
- Mark fight outcomes with F8 (lose) / F9 (win) hotkeys
- View real-time event counts and elapsed time

Data is saved to:
- data/raw/<fight_id>.jsonl - Raw keystroke events
- data/summaries/fight_summaries.csv - Fight outcome summaries
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path for imports
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

try:
    from app.ui import CupheadLoggerUI
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install pynput PyYAML")
    sys.exit(1)


def check_macos_permissions():
    """Check if the app has the necessary macOS permissions."""
    try:
        from pynput import keyboard
        
        # Try to create a listener to test permissions
        def test_handler(key):
            pass
        
        test_listener = keyboard.Listener(on_press=test_handler)
        test_listener.start()
        test_listener.stop()
        
        return True
        
    except Exception as e:
        print("=" * 60)
        print("ACCESSIBILITY PERMISSION REQUIRED")
        print("=" * 60)
        print("This application requires Accessibility permissions to capture")
        print("global keyboard events.")
        print()
        print("To grant permissions:")
        print("1. Open System Preferences > Security & Privacy")
        print("2. Click the 'Privacy' tab")
        print("3. Select 'Accessibility' from the left sidebar")
        print("4. Click the lock icon and enter your password")
        print("5. Add this application or Python to the list")
        print("6. Restart this application")
        print()
        print(f"Error details: {e}")
        print("=" * 60)
        return False


def main():
    """Main application entry point."""
    print("Cuphead Boss Keystroke Logger")
    print("=" * 40)
    
    # Check permissions on macOS
    if sys.platform == "darwin":
        if not check_macos_permissions():
            return 1
    
    # Determine project root (parent of this script)
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}")
    
    # Verify data directories exist
    data_root = project_root / "data"
    if not data_root.exists():
        print(f"Creating data directory: {data_root}")
        data_root.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create and run the UI
        print("Starting logger UI...")
        app = CupheadLoggerUI(data_root)
        app.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("Logger application closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())