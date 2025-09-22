"""
Keyboard event logger for capturing gameplay keystrokes.
"""
import time
import threading
from typing import Set, Callable, Optional
from pathlib import Path
from pynput import keyboard

try:
    from .data_models import KeyEvent, DataLogger
except ImportError:
    from data_models import KeyEvent, DataLogger


class KeyboardLogger:
    """Global keyboard event logger for gameplay capture."""
    
    # Keys to monitor for gameplay
    GAMEPLAY_KEYS = {
        'left', 'right', 'up', 'down',
        'jump', 'dash', 'shoot', 'special',
        'lock', 'swap', 'pause'
    }
    
    # Map common key names to our standard format
    KEY_MAPPING = {
        # Arrow keys
        keyboard.Key.left: 'left',
        keyboard.Key.right: 'right', 
        keyboard.Key.up: 'up',
        keyboard.Key.down: 'down',
        
        # Common gameplay keys (these may need customization per player)
        keyboard.Key.space: 'jump',
        'z': 'shoot',
        'x': 'jump',
        'c': 'dash',
        'v': 'special',
        's': 'lock',
        'a': 'swap',
        keyboard.Key.esc: 'pause',
        'p': 'pause',
        
        # Alternative mappings
        'w': 'up',
        'a': 'left', 
        's': 'down',
        'd': 'right',
    }
    
    # Hotkeys to ignore in event logging
    HOTKEYS_TO_IGNORE = {
        keyboard.Key.f1, keyboard.Key.f2, 
        keyboard.Key.f8, keyboard.Key.f9
    }
    
    def __init__(self, data_logger: DataLogger):
        self.data_logger = data_logger
        self.is_recording = False
        self.current_session = None
        self.current_jsonl_path = None
        self.event_count = 0
        self.start_time_ms = None
        
        # Threading
        self.listener_thread = None
        self.listener = None
        self.lock = threading.Lock()
        
        # Callbacks for UI updates
        self.on_event_logged: Optional[Callable] = None
    
    def normalize_key(self, key) -> Optional[str]:
        """Normalize a key to our standard format."""
        try:
            # Handle special keys
            if hasattr(key, 'name'):
                if key in self.KEY_MAPPING:
                    return self.KEY_MAPPING[key]
                return None
            
            # Handle character keys
            if hasattr(key, 'char') and key.char:
                char = key.char.lower()
                if char in self.KEY_MAPPING:
                    return self.KEY_MAPPING[char]
                # Direct character mapping for letters
                if char in self.GAMEPLAY_KEYS:
                    return char
            
            # Handle string representation
            key_str = str(key).replace("'", "").lower()
            if key_str in self.KEY_MAPPING.values():
                return key_str
                
        except Exception:
            pass
        
        return None
    
    def should_ignore_key(self, key) -> bool:
        """Check if this key should be ignored (hotkeys, meta keys, etc.)."""
        # Ignore hotkeys
        if key in self.HOTKEYS_TO_IGNORE:
            return True
        
        # Ignore modifier keys
        modifiers = {
            keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
            keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, 
            keyboard.Key.alt_gr,
            keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
            keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
            keyboard.Key.tab, keyboard.Key.caps_lock
        }
        
        if key in modifiers:
            return True
        
        return False
    
    def on_key_press(self, key):
        """Handle key press events."""
        if not self.is_recording:
            return
        
        if self.should_ignore_key(key):
            return
        
        normalized_key = self.normalize_key(key)
        if not normalized_key:
            return
        
        self._log_event('keydown', normalized_key)
    
    def on_key_release(self, key):
        """Handle key release events."""
        if not self.is_recording:
            return
        
        if self.should_ignore_key(key):
            return
        
        normalized_key = self.normalize_key(key)
        if not normalized_key:
            return
        
        self._log_event('keyup', normalized_key)
    
    def _log_event(self, event_type: str, key: str):
        """Log a keyboard event with timestamp."""
        with self.lock:
            if not self.is_recording or not self.current_session:
                return
            
            # Calculate time since fight start
            current_time_ms = time.perf_counter() * 1000
            t_ms = int(current_time_ms - self.start_time_ms)
            
            # Create event
            event = KeyEvent(
                fight_id=self.current_session.fight_id,
                event=event_type,
                key=key,
                t_ms=t_ms
            )
            
            # Log to file
            try:
                self.data_logger.log_event(event, self.current_jsonl_path)
                self.event_count += 1
                
                # Notify UI
                if self.on_event_logged:
                    self.on_event_logged(self.event_count, t_ms)
                    
            except Exception as e:
                print(f"Error logging event: {e}")
    
    def start_recording(self, session):
        """Start recording keyboard events for a fight session."""
        with self.lock:
            if self.is_recording:
                return False, "Already recording"
            
            try:
                # Initialize session
                self.current_session = session
                self.current_jsonl_path = self.data_logger.start_fight(session)
                self.event_count = 0
                self.start_time_ms = time.perf_counter() * 1000
                self.is_recording = True
                
                # Start keyboard listener if not already running
                if not self.listener or not self.listener.running:
                    self._start_listener()
                
                return True, f"Started recording fight: {session.fight_id}"
                
            except Exception as e:
                self.is_recording = False
                return False, f"Error starting recording: {e}"
    
    def stop_recording(self):
        """Stop recording keyboard events."""
        with self.lock:
            if not self.is_recording:
                return False, "Not currently recording"
            
            self.is_recording = False
            duration_ms = int((time.perf_counter() * 1000) - self.start_time_ms)
            
            return True, f"Stopped recording. Duration: {duration_ms}ms, Events: {self.event_count}"
    
    def end_fight(self, outcome: str):
        """End the current fight and write summary."""
        with self.lock:
            if not self.current_session:
                return False, "No active fight session"
            
            # Stop recording if still active
            if self.is_recording:
                self.stop_recording()
            
            try:
                # Calculate final stats
                end_time = time.perf_counter() * 1000
                duration_ms = int(end_time - self.start_time_ms)
                
                # Create summary
                try:
                    from .data_models import FightSummary
                except ImportError:
                    from data_models import FightSummary
                from datetime import datetime, timezone
                
                summary = FightSummary(
                    fight_id=self.current_session.fight_id,
                    outcome=outcome,
                    duration_ms=duration_ms,
                    end_utc=datetime.now(timezone.utc).isoformat(),
                    n_events=self.event_count
                )
                
                # Write summary
                self.data_logger.end_fight(summary, self.current_jsonl_path, self.current_session)
                
                # Reset session
                fight_id = self.current_session.fight_id
                self.current_session = None
                self.current_jsonl_path = None
                
                return True, f"Fight {fight_id} ended: {outcome}. Duration: {duration_ms/1000:.1f}s, Events: {self.event_count}"
                
            except Exception as e:
                return False, f"Error ending fight: {e}"
    
    def _start_listener(self):
        """Start the global keyboard listener in a background thread."""
        try:
            if self.listener:
                self.listener.stop()
            
            self.listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            
            self.listener.start()
            
        except Exception as e:
            print(f"Error starting keyboard listener: {e}")
    
    def shutdown(self):
        """Clean shutdown of the keyboard logger."""
        with self.lock:
            self.is_recording = False
            
            if self.listener:
                self.listener.stop()
                self.listener = None
    
    def get_status(self) -> dict:
        """Get current logging status."""
        with self.lock:
            return {
                'is_recording': self.is_recording,
                'event_count': self.event_count,
                'current_fight': self.current_session.fight_id if self.current_session else None,
                'elapsed_ms': int((time.perf_counter() * 1000) - self.start_time_ms) if self.start_time_ms else 0
            }