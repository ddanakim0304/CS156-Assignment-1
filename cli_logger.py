#!/usr/bin/env python3
"""
Command-line version of the Cuphead keystroke logger.
Use this if tkinter is not available in your Python environment.
"""

import sys
import time
import threading
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.data_models import FightSession, Config, DataLogger
from app.keyboard_logger import KeyboardLogger
from app.hotkeys import GlobalHotkeyManager


class CLILogger:
    """Command-line interface for the keystroke logger."""
    
    def __init__(self, data_root: Path):
        self.data_root = Path(data_root)
        self.config = Config(self.data_root / "meta" / "config.yaml")
        self.data_logger = DataLogger(self.data_root)
        self.keyboard_logger = KeyboardLogger(self.data_logger)
        self.hotkey_manager = GlobalHotkeyManager()
        
        self.running = True
        self.current_session = None
        
        # Set up callbacks
        self.keyboard_logger.on_event_logged = self.on_event_logged
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        """Set up global hotkey bindings."""
        self.hotkey_manager.register_handler('start', self.start_fight)
        self.hotkey_manager.register_handler('end', self.end_recording)
        self.hotkey_manager.register_handler('win', self.mark_win)
        self.hotkey_manager.register_handler('lose', self.mark_lose)
        
        # Start listening for hotkeys
        self.hotkey_manager.start_listening()
    
    def print_status(self):
        """Print current status information."""
        status = self.keyboard_logger.get_status()
        
        if status['is_recording']:
            elapsed_s = status['elapsed_ms'] / 1000
            print(f"\r[RECORDING] Fight: {status['current_fight'][:20]}... | "
                  f"Events: {status['event_count']} | "
                  f"Time: {elapsed_s:.1f}s", end="", flush=True)
        elif self.current_session:
            print(f"\r[ENDED] Fight ended. Press F8 (lose) or F9 (win)           ", end="", flush=True)
        else:
            print(f"\r[IDLE] Ready. Press F1 to start recording                    ", end="", flush=True)
    
    def on_event_logged(self, event_count: int, elapsed_ms: int):
        """Callback when events are logged."""
        # Update display every 10 events to avoid too much output
        if event_count % 10 == 0:
            self.print_status()
    
    def start_fight(self):
        """Start a new fight recording."""
        if self.keyboard_logger.get_status()['is_recording']:
            print("\n[WARNING] Already recording! Press F2 to end first.")
            return
        
        # For CLI, use defaults or prompt user
        boss = self.config.bosses[0]  # Default to first boss
        loadout = self.config.default_loadout
        
        print(f"\n[START] Starting new fight: {boss}")
        print(f"        Loadout: {loadout}")
        
        session = FightSession.create_new(boss, loadout)
        success, message = self.keyboard_logger.start_recording(session)
        
        if success:
            self.current_session = session
            print(f"[SUCCESS] {message}")
            print("         Play your fight! Press F2 when done.")
        else:
            print(f"[ERROR] {message}")
    
    def end_recording(self):
        """End the current recording."""
        if not self.keyboard_logger.get_status()['is_recording']:
            print("\n[WARNING] No active recording to end.")
            return
        
        success, message = self.keyboard_logger.stop_recording()
        if success:
            print(f"\n[END] {message}")
            print("      Press F8 (lose) or F9 (win) to mark outcome.")
        else:
            print(f"\n[ERROR] {message}")
    
    def mark_win(self):
        """Mark the current fight as a win."""
        self._mark_outcome("win")
    
    def mark_lose(self):
        """Mark the current fight as a loss."""
        self._mark_outcome("lose")
    
    def _mark_outcome(self, outcome: str):
        """Mark fight outcome and finalize."""
        if not self.current_session:
            print(f"\n[WARNING] No active fight to mark as {outcome}.")
            return
        
        # Auto-end if still recording
        if self.keyboard_logger.get_status()['is_recording']:
            self.end_recording()
        
        success, message = self.keyboard_logger.end_fight(outcome)
        
        if success:
            print(f"\n[SAVED] {message}")
            print("        Fight data saved successfully!")
            self.current_session = None
        else:
            print(f"\n[ERROR] {message}")
    
    def show_help(self):
        """Show help information."""
        print("\nCuphead Boss Keystroke Logger - CLI Mode")
        print("=" * 50)
        print("Global Hotkeys:")
        print("  F1 - Start recording a new fight")
        print("  F2 - End current recording")
        print("  F8 - Mark fight as LOSE")
        print("  F9 - Mark fight as WIN")
        print("  Ctrl+C - Quit application")
        print()
        print("Monitored Keys:")
        print("  Movement: arrow keys, WASD")
        print("  Actions: space, Z (shoot), X (jump), C (dash)")
        print("  Advanced: V (special), S (lock), A (swap), Esc/P (pause)")
        print()
        print("Data saved to:")
        print(f"  Raw events: {self.data_root}/raw/<fight_id>.jsonl")
        print(f"  Summaries:  {self.data_root}/summaries/fight_summaries.csv")
        print()
    
    def run(self):
        """Run the CLI logger."""
        self.show_help()
        
        print("Logger is active. Use hotkeys to control recording...")
        print("Press Ctrl+C to quit.")
        
        try:
            while self.running:
                self.print_status()
                time.sleep(0.5)  # Update display twice per second
                
        except KeyboardInterrupt:
            print("\n\n[SHUTDOWN] Stopping logger...")
            
        finally:
            # Clean shutdown
            if self.keyboard_logger.get_status()['is_recording']:
                self.keyboard_logger.stop_recording()
            
            self.keyboard_logger.shutdown()
            self.hotkey_manager.stop_listening()
            
            print("[SHUTDOWN] Logger stopped.")


def main():
    """Main entry point for CLI logger."""
    project_root = Path(__file__).parent
    data_root = project_root / "data"
    
    print("Cuphead Boss Keystroke Logger - CLI Mode")
    
    # Check for accessibility permissions
    if sys.platform == "darwin":
        print("Note: This application requires Accessibility permissions.")
        print("      Grant permissions in System Preferences > Security & Privacy > Accessibility")
        print()
    
    try:
        logger = CLILogger(data_root)
        logger.run()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())