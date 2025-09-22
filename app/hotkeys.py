"""
Global hotkey manager for F1/F2/F8/F9 controls.
"""
import threading
from typing import Callable, Dict

try:
    from pynput import keyboard
except ImportError:
    print("Warning: pynput not available. Hotkeys will not work.")
    keyboard = None


class GlobalHotkeyManager:
    """Manages global hotkey bindings for the logger controls."""
    
    def __init__(self):
        self.hotkey_handlers: Dict[str, Callable] = {}
        self.listener = None
        self.lock = threading.Lock()
        
        # Map key codes to our hotkey names
        self.key_mapping = {
            keyboard.Key.f1: 'start',
            keyboard.Key.f2: 'end', 
            keyboard.Key.f8: 'lose',
            keyboard.Key.f9: 'win'
        }
    
    def register_handler(self, hotkey: str, handler: Callable):
        """Register a handler function for a specific hotkey."""
        with self.lock:
            self.hotkey_handlers[hotkey] = handler
    
    def unregister_handler(self, hotkey: str):
        """Unregister a handler for a specific hotkey."""
        with self.lock:
            if hotkey in self.hotkey_handlers:
                del self.hotkey_handlers[hotkey]
    
    def on_key_press(self, key):
        """Handle global key press events."""
        # Check if this is one of our hotkeys
        if key in self.key_mapping:
            hotkey_name = self.key_mapping[key]
            
            with self.lock:
                if hotkey_name in self.hotkey_handlers:
                    try:
                        # Call the handler in a separate thread to avoid blocking
                        handler = self.hotkey_handlers[hotkey_name]
                        threading.Thread(target=handler, daemon=True).start()
                    except Exception as e:
                        print(f"Error executing hotkey handler for {hotkey_name}: {e}")
    
    def start_listening(self):
        """Start the global hotkey listener."""
        try:
            if self.listener and self.listener.running:
                return
            
            self.listener = keyboard.Listener(on_press=self.on_key_press)
            self.listener.start()
            
        except Exception as e:
            print(f"Error starting hotkey listener: {e}")
    
    def stop_listening(self):
        """Stop the global hotkey listener."""
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def is_listening(self) -> bool:
        """Check if the hotkey listener is active."""
        return self.listener is not None and self.listener.running