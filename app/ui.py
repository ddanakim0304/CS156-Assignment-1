"""
Always-on-top UI control panel for Cuphead boss keystroke logging.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pathlib import Path
from typing import Optional

try:
    from .data_models import FightSession, Config, DataLogger
    from .keyboard_logger import KeyboardLogger
    from .hotkeys import GlobalHotkeyManager
except ImportError:
    from data_models import FightSession, Config, DataLogger
    from keyboard_logger import KeyboardLogger
    from hotkeys import GlobalHotkeyManager


class LoggerState:
    """State management for the logger UI."""
    IDLE = "idle"
    RECORDING = "recording" 
    ENDED = "ended"


class CupheadLoggerUI:
    """Main UI window for the keystroke logger."""
    
    def __init__(self, data_root: Path):
        # Initialize core components
        self.data_root = Path(data_root)
        self.config = Config(self.data_root / "meta" / "config.yaml")
        self.data_logger = DataLogger(self.data_root)
        self.keyboard_logger = KeyboardLogger(self.data_logger)
        self.hotkey_manager = GlobalHotkeyManager()
        
        # State management
        self.state = LoggerState.IDLE
        self.current_session: Optional[FightSession] = None
        
        # UI setup
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.setup_hotkeys()
        self.update_button_states()
        
        # Set up keyboard logger callback
        self.keyboard_logger.on_event_logged = self.on_event_logged
        
        # Status update timer
        self.start_status_timer()
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title("Cuphead Boss Keystroke Logger")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Always on top
        self.root.attributes('-topmost', True)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create all UI widgets."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Boss selection
        ttk.Label(main_frame, text="Boss:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.boss_var = tk.StringVar(value=self.config.bosses[0])
        boss_combo = ttk.Combobox(main_frame, textvariable=self.boss_var, 
                                  values=self.config.bosses, state="readonly", width=25)
        boss_combo.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Loadout
        ttk.Label(main_frame, text="Loadout:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.loadout_var = tk.StringVar(value=self.config.default_loadout)
        loadout_entry = ttk.Entry(main_frame, textvariable=self.loadout_var, width=25)
        loadout_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Difficulty
        ttk.Label(main_frame, text="Difficulty:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.difficulty_var = tk.StringVar(value=self.config.default_difficulty)
        difficulty_combo = ttk.Combobox(main_frame, textvariable=self.difficulty_var,
                                        values=["Regular", "Simple", "Expert"], 
                                        state="readonly", width=25)
        difficulty_combo.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, 
                                                            sticky=(tk.W, tk.E), pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=5)
        
        self.start_btn = ttk.Button(button_frame, text="Start (F1)", 
                                   command=self.start_fight)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.end_btn = ttk.Button(button_frame, text="End (F2)", 
                                 command=self.end_recording)
        self.end_btn.grid(row=0, column=1, padx=5)
        
        self.lose_btn = ttk.Button(button_frame, text="Lose (F8)", 
                                  command=self.mark_lose)
        self.lose_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.win_btn = ttk.Button(button_frame, text="Win (F9)", 
                                 command=self.mark_win)
        self.win_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Status display
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=3, 
                                                            sticky=(tk.W, tk.E), pady=10)
        
        self.status_var = tk.StringVar(value="Idle")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("TkDefaultFont", 10, "bold"))
        status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Event counter and timer
        counter_frame = ttk.Frame(main_frame)
        counter_frame.grid(row=7, column=0, columnspan=3, pady=5)
        
        self.events_var = tk.StringVar(value="Events: 0")
        ttk.Label(counter_frame, textvariable=self.events_var).grid(row=0, column=0, padx=10)
        
        self.elapsed_var = tk.StringVar(value="Elapsed: 00:00")
        ttk.Label(counter_frame, textvariable=self.elapsed_var).grid(row=0, column=1, padx=10)
        
        # Always on top checkbox
        ttk.Separator(main_frame, orient='horizontal').grid(row=8, column=0, columnspan=3, 
                                                            sticky=(tk.W, tk.E), pady=5)
        
        self.topmost_var = tk.BooleanVar(value=True)
        topmost_check = ttk.Checkbutton(main_frame, text="Pin on top", 
                                       variable=self.topmost_var,
                                       command=self.toggle_topmost)
        topmost_check.grid(row=9, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
    
    def setup_hotkeys(self):
        """Set up global hotkey bindings."""
        self.hotkey_manager.register_handler('start', self.start_fight)
        self.hotkey_manager.register_handler('end', self.end_recording)
        self.hotkey_manager.register_handler('win', self.mark_win)
        self.hotkey_manager.register_handler('lose', self.mark_lose)
        
        # Start listening for hotkeys
        self.hotkey_manager.start_listening()
    
    def toggle_topmost(self):
        """Toggle always-on-top behavior."""
        self.root.attributes('-topmost', self.topmost_var.get())
    
    def start_fight(self):
        """Start a new fight recording."""
        if self.state != LoggerState.IDLE:
            messagebox.showwarning("Warning", "End current fight first")
            return
        
        # Create new session
        session = FightSession.create_new(
            boss=self.boss_var.get(),
            loadout=self.loadout_var.get(),
            difficulty=self.difficulty_var.get()
        )
        
        # Start recording
        success, message = self.keyboard_logger.start_recording(session)
        
        if success:
            self.current_session = session
            self.state = LoggerState.RECORDING
            self.update_status(f"Recording: {session.fight_id} — Boss: {session.boss}")
            self.update_button_states()
        else:
            messagebox.showerror("Error", f"Failed to start recording: {message}")
    
    def end_recording(self):
        """End the current recording."""
        if self.state != LoggerState.RECORDING:
            messagebox.showwarning("Warning", "No active recording to end")
            return
        
        success, message = self.keyboard_logger.stop_recording()
        
        if success:
            self.state = LoggerState.ENDED
            self.update_status("Fight ended. Mark outcome.")
            self.update_button_states()
        else:
            messagebox.showerror("Error", f"Failed to end recording: {message}")
    
    def mark_win(self):
        """Mark the current fight as a win."""
        self._mark_outcome("win")
    
    def mark_lose(self):
        """Mark the current fight as a loss."""
        self._mark_outcome("lose")
    
    def _mark_outcome(self, outcome: str):
        """Mark fight outcome and finalize."""
        if self.state == LoggerState.RECORDING:
            # Auto-end if still recording
            self.end_recording()
        
        if self.state != LoggerState.ENDED:
            messagebox.showwarning("Warning", "No fight to mark")
            return
        
        success, message = self.keyboard_logger.end_fight(outcome)
        
        if success:
            self.state = LoggerState.IDLE
            self.current_session = None
            self.update_status(f"Saved... Outcome: {outcome.upper()}")
            self.update_button_states()
            
            # Reset counters
            self.events_var.set("Events: 0")
            self.elapsed_var.set("Elapsed: 00:00")
            
            # Show brief success message, then return to idle
            self.root.after(2000, lambda: self.update_status("Idle"))
        else:
            messagebox.showerror("Error", f"Failed to mark outcome: {message}")
    
    def update_button_states(self):
        """Update button enabled/disabled states based on current state."""
        if self.state == LoggerState.IDLE:
            self.start_btn.config(state='normal')
            self.end_btn.config(state='disabled')
            self.win_btn.config(state='disabled')
            self.lose_btn.config(state='disabled')
        
        elif self.state == LoggerState.RECORDING:
            self.start_btn.config(state='disabled')
            self.end_btn.config(state='normal')
            self.win_btn.config(state='disabled')
            self.lose_btn.config(state='disabled')
        
        elif self.state == LoggerState.ENDED:
            self.start_btn.config(state='disabled')
            self.end_btn.config(state='disabled')
            self.win_btn.config(state='normal')
            self.lose_btn.config(state='normal')
    
    def update_status(self, status: str):
        """Update the status display."""
        self.status_var.set(status)
    
    def on_event_logged(self, event_count: int, elapsed_ms: int):
        """Callback when a keyboard event is logged."""
        # Update UI from main thread
        self.root.after(0, self._update_counters, event_count, elapsed_ms)
    
    def _update_counters(self, event_count: int, elapsed_ms: int):
        """Update event and time counters (called from main thread)."""
        self.events_var.set(f"Events: {event_count}")
        
        seconds = elapsed_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        self.elapsed_var.set(f"Elapsed: {minutes:02d}:{seconds:02d}")
    
    def start_status_timer(self):
        """Start a timer to periodically update status."""
        def update_timer():
            if self.state == LoggerState.RECORDING:
                status = self.keyboard_logger.get_status()
                self.root.after(0, self._update_counters, 
                               status['event_count'], status['elapsed_ms'])
            
            # Schedule next update
            self.root.after(1000, update_timer)
        
        # Start the timer
        self.root.after(1000, update_timer)
    
    def on_closing(self):
        """Handle window close event."""
        # Stop any active recording
        if self.state == LoggerState.RECORDING:
            self.keyboard_logger.stop_recording()
        
        # Shutdown components
        self.keyboard_logger.shutdown()
        self.hotkey_manager.stop_listening()
        
        # Close window
        self.root.destroy()
    
    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()