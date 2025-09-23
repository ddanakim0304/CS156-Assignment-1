#!/usr/bin/env python3
"""
Cuphead Boss Keystroke Data Logger - Main UI Application
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import csv
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
        self.root.geometry("400x450")  # Increased height for session list
        self.root.resizable(False, False)
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Initialize state
        self.state = AppState.IDLE
        self.data_logger = DataLogger()
        self.keyboard_listener = None
        
        # UI update thread control
        self.update_thread_running = False
        
        # Session history for display
        self.session_history = []
        
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
        
        self.start_btn = ttk.Button(button_frame, text="Start (F1)", command=self._toggle_fight)
        self.start_btn.grid(row=0, column=0, columnspan=2, padx=2)
        
        self.lose_btn = ttk.Button(button_frame, text="Lose (F8)", command=self._mark_lose)
        self.lose_btn.grid(row=1, column=0, padx=2, pady=2)
        
        self.win_btn = ttk.Button(button_frame, text="Win (F9)", command=self._mark_win)
        self.win_btn.grid(row=1, column=1, padx=2, pady=2)
        
        self.delete_btn = ttk.Button(button_frame, text="Delete Selected", command=self._delete_selected_session)
        self.delete_btn.grid(row=2, column=0, columnspan=2, padx=2, pady=2)
        
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
        
        # Session history
        history_frame = ttk.LabelFrame(main_frame, text="Recent Sessions (Last 5)", padding="5")
        history_frame.grid(row=7, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create Treeview for session history
        self.history_tree = ttk.Treeview(history_frame, columns=('outcome', 'duration', 'events'), show='headings', height=5)
        self.history_tree.heading('#1', text='Outcome')
        self.history_tree.heading('#2', text='Duration')
        self.history_tree.heading('#3', text='Events')
        
        # Configure column widths
        self.history_tree.column('#1', width=80, anchor='center')
        self.history_tree.column('#2', width=80, anchor='center')
        self.history_tree.column('#3', width=60, anchor='center')
        
        # Add scrollbar for history
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)  # Make history frame expandable
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        telemetry_frame.columnconfigure(0, weight=1)
        telemetry_frame.columnconfigure(1, weight=1)
        history_frame.columnconfigure(0, weight=1)
        
    def _setup_keyboard_listener(self):
        """Setup global keyboard listener with hotkey callbacks"""
        hotkey_callbacks = {
            'start': self._toggle_fight,  # F1 now toggles start/end
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
            
    def _toggle_fight(self):
        """Toggle between starting and ending a fight based on current state"""
        if self.state == AppState.IDLE:
            self._start_fight()
        elif self.state == AppState.RECORDING:
            self._end_fight()
            
    def _start_fight(self):
        """Start a new fight session"""
        if self.state != AppState.IDLE:
            self.status_var.set("Warning: End current fight first!")
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
            self.status_var.set(f"Error starting fight: {str(e)}")
            print(f"Error starting fight: {e}")
            
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
            
            # Add to session history
            duration = session_data['duration_s']
            events = session_data['n_events']
            fight_id = session_data['fight_id']
            boss = session_data.get('boss', 'Unknown')
            
            # Create session entry
            session_entry = {
                'fight_id': fight_id,
                'boss': boss,
                'outcome': outcome.upper(),
                'duration': f"{duration:.1f}s",
                'events': str(events),
                'timestamp': time.strftime("%H:%M:%S")
            }
            
            self._add_to_history(session_entry)
            
            print(f"Completed fight {fight_id}: {outcome} ({duration:.1f}s, {events} events)")
            
        except Exception as e:
            # Show error in status instead of popup
            self.status_var.set(f"Error: {str(e)}")
            print(f"Error completing fight: {e}")
            self.state = AppState.IDLE
            self._update_ui_state()
            
    def _update_ui_state(self):
        """Update UI elements based on current state"""
        if self.state == AppState.IDLE:
            self.start_btn.config(state="normal", text="Start (F1)")
            self.lose_btn.config(state="disabled")
            self.win_btn.config(state="disabled")
            self.delete_btn.config(state="normal")
            self.status_var.set("Idle")
            self.events_var.set("Events: 0")
            self.elapsed_var.set("Elapsed: 00:00")
            
        elif self.state == AppState.RECORDING:
            self.start_btn.config(state="normal", text="End (F1)")  # Button text changes to "End"
            self.lose_btn.config(state="disabled")
            self.win_btn.config(state="disabled")
            self.delete_btn.config(state="normal")
            
            session_info = self.data_logger.get_session_info()
            if session_info:
                boss = session_info['boss']
                fight_id = session_info['fight_id']
                self.status_var.set(f"Recording: {fight_id} — Boss: {boss}")
                
        elif self.state == AppState.ENDED:
            self.start_btn.config(state="disabled", text="Start (F1)")  # Reset to "Start" but disabled
            self.lose_btn.config(state="normal")
            self.win_btn.config(state="normal")
            self.delete_btn.config(state="normal")
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
        
    def _add_to_history(self, session_entry):
        """Add a session to the history list and update the display"""
        # Add to beginning of list
        self.session_history.insert(0, session_entry)
        
        # Keep only last 5 sessions
        if len(self.session_history) > 5:
            self.session_history = self.session_history[:5]
            
        # Update the treeview
        self._update_history_display()
        
    def _update_history_display(self):
        """Update the history treeview with current session data"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Add sessions to treeview
        for session in self.session_history:
            # Create display text with boss and timestamp
            display_text = f"{session['boss']} ({session['timestamp']})"
            
            # Parse duration to check for anomalies
            duration_str = session['duration']
            duration_value = float(duration_str.replace('s', ''))
            
            # Set tag for coloring based on duration anomalies
            if duration_value < 10 or duration_value > 150:
                tag = 'anomaly'  # Red for anomalous durations
            else:
                tag = 'normal'   # Normal color for regular durations
            
            self.history_tree.insert('', 'end', 
                                   text=display_text,
                                   values=(session['outcome'], session['duration'], session['events']),
                                   tags=(tag,))
        
        # Configure tags for coloring
        self.history_tree.tag_configure('anomaly', foreground='red')
        self.history_tree.tag_configure('normal', foreground='black')
        
    def _delete_selected_session(self):
        """Delete the selected session from both UI and data files"""
        # Get selected item from treeview
        selected_items = self.history_tree.selection()
        if not selected_items:
            self.status_var.set("No session selected to delete")
            return
            
        if self.state != AppState.IDLE:
            self.status_var.set("Cannot delete while recording")
            return
            
        try:
            # Get the selected item
            selected_item = selected_items[0]
            item_index = self.history_tree.index(selected_item)
            
            # Get the corresponding session from our history
            if item_index >= len(self.session_history):
                self.status_var.set("Invalid selection")
                return
                
            selected_session = self.session_history[item_index]
            fight_id = selected_session['fight_id']
            
            # Remove from UI history
            self.session_history.pop(item_index)
            self._update_history_display()
            
            # Delete the raw data file
            raw_file = self.data_logger.raw_dir / f"{fight_id}.jsonl"
            if raw_file.exists():
                raw_file.unlink()
                
            # Remove from CSV summary
            self._remove_from_csv_summary(fight_id)
            
            self.status_var.set(f"Deleted session: {fight_id}")
            print(f"Deleted session: {fight_id}")
            
            # Update delete button state
            self._update_ui_state()
            
        except Exception as e:
            self.status_var.set(f"Error deleting session: {str(e)}")
            print(f"Error deleting session: {e}")
            
    def _remove_from_csv_summary(self, fight_id: str):
        """Remove a fight from the CSV summary file"""
        import csv
        import tempfile
        
        csv_path = self.data_logger.summaries_dir / "fight_summaries.csv"
        if not csv_path.exists():
            return
            
        # Read all rows except the one to delete
        rows_to_keep = []
        with open(csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header:
                rows_to_keep.append(header)
                
            for row in reader:
                if row and row[0] != fight_id:  # fight_id is in first column
                    rows_to_keep.append(row)
        
        # Write back the filtered data
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows_to_keep)
        
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