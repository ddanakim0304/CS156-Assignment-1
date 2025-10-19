#!/usr/bin/env python3
"""
Simple launcher script for the Cuphead Logger UI
"""
import sys
import os

# Add the app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import pynput
        import yaml
        import tkinter
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def main():
    """Main launcher function"""
    print("Cuphead Boss Keystroke Logger")
    print("=============================")
    
    # Check for --new-dataset flag
    use_new_dataset = '--new-dataset' in sys.argv
    if use_new_dataset:
        print("Using NEW dataset (raw_new / fight_summaries_new.csv)")
    else:
        print("Using default dataset (raw / fight_summaries.csv)")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check for display (required for tkinter)
    if 'DISPLAY' not in os.environ and sys.platform.startswith('linux'):
        print("Warning: No DISPLAY environment variable found.")
        print("This application requires a graphical environment.")
        print("If running in a headless environment, consider using X11 forwarding or VNC.")
    
    try:
        # Import and run the main UI
        from main import CupheadLoggerUI
        
        print("Starting Cuphead Logger UI...")
        print("Note: On macOS, you may need to grant Accessibility permissions.")
        print("Press Ctrl+C to exit.")
        
        app = CupheadLoggerUI(use_new_dataset=use_new_dataset)
        app.run()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()