#!/usr/bin/env python3
"""
Cuphead Boss Keystroke Data Logger - Main UI Application
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pathlib import Path
from enum import Enum

from data_logger import DataLogger
from keyboard_listener import KeyboardListener


class AppState(Enum):
    IDLE = "idle"
    RECORDING = "recording"  
    ENDED = "ended"


class CupheadLoggerUI:
    """Main UI application for Cuphead keystroke logging"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cuphead Boss Keystroke Logger")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Initialize state
        self.state = AppState.IDLE
        self.data_logger = DataLogger()
        self.keyboard_listener = None
        
        # UI update thread control
        self.update_thread_running = False
        
        # Create UI elements
        self._create_widgets()
        self._setup_keyboard_listener()
        self._update_ui_state()
        
        # Start UI update loop
        self._start_ui_updates()
        
    def _create_widgets(self):
        """Create all UI widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Boss selection
        ttk.Label(main_frame, text="Boss:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.boss_var = tk.StringVar(value="Cagney Carnation")
        self.boss_combo = ttk.Combobox(main_frame, textvariable=self.boss_var, width=25, state="readonly")
        self.boss_combo['values'] = self.data_logger.config.get('bosses', [])
        self.boss_combo.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Loadout
        ttk.Label(main_frame, text="Loadout:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.loadout_var = tk.StringVar(value=self.data_logger.config.get('loadout', 'Peashooter + Smoke Bomb'))
        self.loadout_entry = ttk.Entry(main_frame, textvariable=self.loadout_var, width=25)
        self.loadout_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Difficulty
        ttk.Label(main_frame, text="Difficulty:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.difficulty_var = tk.StringVar(value=self.data_logger.config.get('difficulty', 'Regular'))
        self.difficulty_combo = ttk.Combobox(main_frame, textvariable=self.difficulty_var, width=25, state="readonly")
        self.difficulty_combo['values'] = ['Regular', 'Simple', 'Expert']
        self.difficulty_combo.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.start_btn = ttk.Button(button_frame, text="Start (F1)", command=self._start_fight)
        self.start_btn.grid(row=0, column=0, padx=2)
        
        self.end_btn = ttk.Button(button_frame, text="End (F2)", command=self._end_fight)
        self.end_btn.grid(row=0, column=1, padx=2)
        
        self.lose_btn = ttk.Button(button_frame, text="Lose (F8)", command=self._mark_lose)
        self.lose_btn.grid(row=1, column=0, padx=2, pady=2)
        
        self.win_btn = ttk.Button(button_frame, text="Win (F9)", command=self._mark_win)
        self.win_btn.grid(row=1, column=1, padx=2, pady=2)
        
        # Status display
        self.status_var = tk.StringVar(value="Idle")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Telemetry display
        telemetry_frame = ttk.LabelFrame(main_frame, text="Session Info", padding="5")
        telemetry_frame.grid(row=5, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        self.events_var = tk.StringVar(value="Events: 0")
        ttk.Label(telemetry_frame, textvariable=self.events_var).grid(row=0, column=0, sticky=tk.W)
        
        self.elapsed_var = tk.StringVar(value="Elapsed: 00:00")
        ttk.Label(telemetry_frame, textvariable=self.elapsed_var).grid(row=0, column=1, sticky=tk.E)
        
        # Pin on top checkbox
        self.pin_var = tk.BooleanVar(value=True)
        self.pin_check = ttk.Checkbutton(main_frame, text="Pin on top", variable=self.pin_var, command=self._toggle_pin)
        self.pin_check.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        telemetry_frame.columnconfigure(0, weight=1)
        telemetry_frame.columnconfigure(1, weight=1)
        
    def _setup_keyboard_listener(self):
        """Setup global keyboard listener with hotkey callbacks"""
        hotkey_callbacks = {
            'start': self._start_fight,
            'end': self._end_fight,
            'lose': self._mark_lose,
            'win': self._mark_win
        }
        
        self.keyboard_listener = KeyboardListener(
            event_callback=self._on_keyboard_event,
            hotkey_callbacks=hotkey_callbacks
        )
        self.keyboard_listener.start()
        
    def _on_keyboard_event(self, event_type: str, key: str):
        """Handle keyboard events from the listener"""
        if self.state == AppState.RECORDING:
            self.data_logger.log_event(event_type, key)
            
    def _start_fight(self):
        """Start a new fight session"""
        if self.state != AppState.IDLE:
            messagebox.showwarning("Warning", "End current fight first!")
            return
            
        try:
            boss = self.boss_var.get()
            loadout = self.loadout_var.get()
            difficulty = self.difficulty_var.get()
            
            fight_id = self.data_logger.start_fight(boss, loadout, difficulty)
            self.state = AppState.RECORDING
            self._update_ui_state()
            
            print(f"Started fight: {fight_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start fight: {e}")
            
    def _end_fight(self):
        """End the current fight session"""
        if self.state != AppState.RECORDING:
            return
            
        self.state = AppState.ENDED
        self._update_ui_state()
        
    def _mark_lose(self):
        """Mark the fight as a loss"""
        self._complete_fight("lose")
        
    def _mark_win(self):
        """Mark the fight as a win"""
        self._complete_fight("win")
        
    def _complete_fight(self, outcome: str):
        """Complete the fight with the given outcome"""
        try:
            # Auto-end if still recording
            if self.state == AppState.RECORDING:
                self.state = AppState.ENDED
                
            if self.state != AppState.ENDED:
                return
                
            session_data = self.data_logger.end_fight(outcome)
            self.state = AppState.IDLE
            self._update_ui_state()
            
            # Show completion message
            duration = session_data['duration_s']
            events = session_data['n_events']
            fight_id = session_data['fight_id']
            
            message = f"Fight completed!\nOutcome: {outcome.upper()}\nDuration: {duration:.1f}s\nEvents: {events}\nFight ID: {fight_id}"
            messagebox.showinfo("Fight Completed", message)
            
            print(f"Completed fight {fight_id}: {outcome} ({duration:.1f}s, {events} events)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete fight: {e}")
            self.state = AppState.IDLE
            self._update_ui_state()
            
    def _update_ui_state(self):
        """Update UI elements based on current state"""
        if self.state == AppState.IDLE:
            self.start_btn.config(state="normal")
            self.end_btn.config(state="disabled")
            self.lose_btn.config(state="disabled")
            self.win_btn.config(state="disabled")
            self.status_var.set("Idle")
            self.events_var.set("Events: 0")
            self.elapsed_var.set("Elapsed: 00:00")
            
        elif self.state == AppState.RECORDING:
            self.start_btn.config(state="disabled")
            self.end_btn.config(state="normal")
            self.lose_btn.config(state="disabled")
            self.win_btn.config(state="disabled")
            
            session_info = self.data_logger.get_session_info()
            if session_info:
                boss = session_info['boss']
                fight_id = session_info['fight_id']
                self.status_var.set(f"Recording: {fight_id} — Boss: {boss}")
                
        elif self.state == AppState.ENDED:
            self.start_btn.config(state="disabled")
            self.end_btn.config(state="disabled")
            self.lose_btn.config(state="normal")
            self.win_btn.config(state="normal")
            self.status_var.set("Fight ended. Mark outcome.")
            
    def _update_telemetry(self):
        """Update telemetry display during recording"""
        if self.state == AppState.RECORDING:
            session_info = self.data_logger.get_session_info()
            if session_info:
                events = session_info['event_count']
                elapsed_ms = session_info['elapsed_ms']
                
                minutes = elapsed_ms // 60000
                seconds = (elapsed_ms // 1000) % 60
                
                self.events_var.set(f"Events: {events}")
                self.elapsed_var.set(f"Elapsed: {minutes:02d}:{seconds:02d}")
                
    def _toggle_pin(self):
        """Toggle always-on-top behavior"""
        self.root.attributes('-topmost', self.pin_var.get())
        
    def _start_ui_updates(self):
        """Start the UI update loop"""
        self.update_thread_running = True
        
        def update_loop():
            while self.update_thread_running:
                try:
                    self.root.after(0, self._update_telemetry)
                    time.sleep(0.5)  # Update every 500ms
                except:
                    break
                    
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
    def run(self):
        """Start the UI application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_closing()
            
    def _on_closing(self):
        """Handle application closing"""
        self.update_thread_running = False
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
        # Save any ongoing session
        if self.state == AppState.RECORDING:
            try:
                self.data_logger.end_fight("interrupted")
                print("Saved interrupted session")
            except:
                pass
                
        self.root.quit()
        self.root.destroy()


def main():
    """Main entry point"""
    app = CupheadLoggerUI()
    app.run()


if __name__ == "__main__":
    main()