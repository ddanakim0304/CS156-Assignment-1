#!/usr/bin/env python3
"""
Real-time Cuphead Boss Predictor Application

This script creates a GUI application that predicts the Cuphead boss being fought
based on real-time keystroke patterns.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack
from pynput import keyboard
from pathlib import Path
from collections import defaultdict

# Configuration
UPDATE_INTERVAL_MS = 2000  # Prediction update interval (2 seconds)
MIN_EVENTS_FOR_PREDICTION = 15  # Minimum events required before attempting prediction
MODEL_FILE = 'cuphead_predictor.joblib'

# Key mapping from raw key strings to action names
KEY_ACTION_MAP = {
    'Key.space': 'jump',
    'f': 'shoot',
    'd': 'dash',
    'x': 'ex_move',
    'a': 'lock',
    'Key.up': 'up',
    'Key.down': 'down',
    'Key.left': 'left',
    'Key.right': 'right'
}


class CupheadPredictorApp:
    """Real-time Cuphead boss predictor application"""

    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.root.title("Cuphead - Live Boss Predictor")
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Application state
        self.is_recording = False
        self.events = []
        self.events_lock = threading.Lock()
        self.start_time = None
        self.keyboard_listener = None
        self.prediction_thread = None
        self.stop_prediction = threading.Event()
        
        # Model components
        self.model_pipeline = None
        self.ngram_vectorizer = None
        self.label_encoder = None
        self.agg_feature_columns = None
        self.boss_names = []
        
        # Load the model
        self.load_model()
        
        # Create UI
        self.create_ui()
        
    def load_model(self):
        """Load the trained model and preprocessors"""
        try:
            model_path = Path(__file__).parent / MODEL_FILE
            if not model_path.exists():
                messagebox.showerror(
                    "Model Not Found",
                    f"Could not find {MODEL_FILE} in the script directory.\n"
                    f"Please ensure the model file is present."
                )
                self.model_loaded = False
                return
            
            # Load the joblib file
            model_data = joblib.load(model_path)
            
            # Extract components
            self.model_pipeline = model_data['model_pipeline']
            self.ngram_vectorizer = model_data['ngram_vectorizer']
            self.label_encoder = model_data['label_encoder']
            self.agg_feature_columns = model_data['agg_feature_columns']
            
            # Get boss names
            self.boss_names = self.label_encoder.classes_.tolist()
            
            self.model_loaded = True
            print(f"Model loaded successfully. Bosses: {self.boss_names}")
            
        except Exception as e:
            messagebox.showerror(
                "Model Load Error",
                f"Error loading model: {str(e)}"
            )
            self.model_loaded = False
    
    def create_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Start/Stop button
        self.record_button = ttk.Button(
            main_frame,
            text="Start Recording",
            command=self.toggle_recording
        )
        self.record_button.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Status: Idle",
            font=('Arial', 10, 'bold')
        )
        self.status_label.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Prediction display frame
        prediction_frame = ttk.LabelFrame(
            main_frame,
            text="Live Predictions",
            padding="10"
        )
        prediction_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create labels for each boss
        self.boss_labels = {}
        if self.model_loaded:
            for i, boss_name in enumerate(self.boss_names):
                label = ttk.Label(
                    prediction_frame,
                    text=f"{boss_name}: (---%)",
                    font=('Arial', 9)
                )
                label.grid(row=i, column=0, pady=2, sticky=tk.W)
                self.boss_labels[boss_name] = label
        else:
            error_label = ttk.Label(
                prediction_frame,
                text="Model not loaded!",
                foreground='red',
                font=('Arial', 9, 'bold')
            )
            error_label.grid(row=0, column=0, pady=2)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Disable button if model not loaded
        if not self.model_loaded:
            self.record_button.config(state='disabled')
    
    def toggle_recording(self):
        """Toggle keystroke recording on/off"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording keystrokes"""
        self.is_recording = True
        self.start_time = time.time()
        
        # Clear previous events
        with self.events_lock:
            self.events.clear()
        
        # Update UI
        self.record_button.config(text="Stop Recording")
        self.status_label.config(text="Status: Recording...")
        
        # Reset prediction display
        for boss_name, label in self.boss_labels.items():
            label.config(text=f"{boss_name}: (---%)")
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()
        
        # Start prediction loop
        self.stop_prediction.clear()
        self.prediction_thread = threading.Thread(
            target=self.prediction_loop,
            daemon=True
        )
        self.prediction_thread.start()
    
    def stop_recording(self):
        """Stop recording keystrokes"""
        self.is_recording = False
        
        # Stop keyboard listener
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        # Stop prediction loop
        self.stop_prediction.set()
        
        # Update UI
        self.record_button.config(text="Start Recording")
        self.status_label.config(text="Status: Idle")
    
    def on_key_press(self, key):
        """Handle key press event"""
        if not self.is_recording:
            return
        
        try:
            # Convert key to string
            key_str = str(key).replace("'", "")
            
            # Record event
            elapsed_ms = int((time.time() - self.start_time) * 1000)
            
            with self.events_lock:
                self.events.append({
                    'event': 'keydown',
                    'key': key_str,
                    't_ms': elapsed_ms
                })
        except Exception as e:
            print(f"Error in on_key_press: {e}")
    
    def on_key_release(self, key):
        """Handle key release event"""
        if not self.is_recording:
            return
        
        try:
            # Convert key to string
            key_str = str(key).replace("'", "")
            
            # Record event
            elapsed_ms = int((time.time() - self.start_time) * 1000)
            
            with self.events_lock:
                self.events.append({
                    'event': 'keyup',
                    'key': key_str,
                    't_ms': elapsed_ms
                })
        except Exception as e:
            print(f"Error in on_key_release: {e}")
    
    def prediction_loop(self):
        """Run prediction loop every UPDATE_INTERVAL_MS"""
        while not self.stop_prediction.is_set():
            # Wait for the update interval
            if self.stop_prediction.wait(UPDATE_INTERVAL_MS / 1000.0):
                break
            
            # Make prediction if we have enough events
            with self.events_lock:
                events_copy = self.events.copy()
            
            if len(events_copy) >= MIN_EVENTS_FOR_PREDICTION:
                self.update_prediction(events_copy)
    
    def update_prediction(self, events):
        """Generate prediction and update UI"""
        try:
            # Update status
            self.root.after(0, lambda: self.status_label.config(
                text="Status: Predicting..."
            ))
            
            # Engineer features
            features = self.engineer_features(events)
            
            if features is not None:
                # Make prediction
                probabilities = self.model_pipeline.predict_proba(features)[0]
                
                # Update UI with predictions
                self.root.after(0, lambda: self.update_boss_probabilities(probabilities))
            
            # Restore status
            self.root.after(0, lambda: self.status_label.config(
                text="Status: Recording..."
            ))
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            import traceback
            traceback.print_exc()
    
    def engineer_features(self, events):
        """
        Engineer features from event list following the exact process from the notebook.
        
        Args:
            events: List of event dictionaries with 'event', 'key', and 't_ms' keys
            
        Returns:
            Sparse feature matrix ready for model prediction, or None if error
        """
        try:
            # Step 1: Convert to DataFrame
            df = pd.DataFrame(events)
            
            if df.empty or len(df) < MIN_EVENTS_FOR_PREDICTION:
                return None
            
            # Step 2: Map keys to clean action names
            df['action'] = df['key'].map(KEY_ACTION_MAP)
            
            # Filter out unmapped keys
            df = df[df['action'].notna()].copy()
            
            if len(df) < MIN_EVENTS_FOR_PREDICTION:
                return None
            
            # Step 3: Calculate Pace & Frequency Features (from keydown events only)
            keydown_df = df[df['event'] == 'keydown'].copy()
            
            if len(keydown_df) < 2:
                return None
            
            total_keydowns = len(keydown_df)
            duration_s = df['t_ms'].max() / 1000.0
            
            if duration_s <= 0:
                return None
            
            # APM (Actions Per Minute)
            apm = (total_keydowns / duration_s) * 60
            
            # Percentage of each action
            action_counts = keydown_df['action'].value_counts()
            pct_features = {}
            for action in ['dash', 'down', 'ex_move', 'jump', 'left', 'lock', 'right', 'shoot', 'up']:
                pct_features[f'pct_{action}'] = action_counts.get(action, 0) / total_keydowns
            
            # Step 4 & 5: Match keydown and keyup events to calculate press durations
            durations = []
            action_durations = defaultdict(list)
            
            # Group events by key
            for key in df['key'].unique():
                key_events = df[df['key'] == key].sort_values('t_ms')
                
                # Match keydown with subsequent keyup
                keydowns = key_events[key_events['event'] == 'keydown']
                keyups = key_events[key_events['event'] == 'keyup']
                
                for _, down_event in keydowns.iterrows():
                    # Find next keyup after this keydown
                    next_ups = keyups[keyups['t_ms'] > down_event['t_ms']]
                    if not next_ups.empty:
                        up_event = next_ups.iloc[0]
                        duration = up_event['t_ms'] - down_event['t_ms']
                        durations.append(duration)
                        
                        # Store by action
                        action = down_event['action']
                        if pd.notna(action):
                            action_durations[action].append(duration)
            
            # Step 4 continued: Overall Rhythm Features
            overall_rhythm_features = {}
            if durations:
                overall_rhythm_features['overall_duration_mean'] = np.mean(durations)
                overall_rhythm_features['overall_duration_std'] = np.std(durations)
                overall_rhythm_features['overall_duration_median'] = np.median(durations)
                overall_rhythm_features['overall_duration_min'] = np.min(durations)
                overall_rhythm_features['overall_duration_max'] = np.max(durations)
            else:
                overall_rhythm_features['overall_duration_mean'] = 0
                overall_rhythm_features['overall_duration_std'] = 0
                overall_rhythm_features['overall_duration_median'] = 0
                overall_rhythm_features['overall_duration_min'] = 0
                overall_rhythm_features['overall_duration_max'] = 0
            
            # Step 5: Action-Specific Timing Features
            action_timing_features = {}
            for action in ['dash', 'down', 'ex_move', 'jump', 'left', 'lock', 'right', 'shoot', 'up']:
                if action in action_durations and action_durations[action]:
                    action_timing_features[f'mean_{action}'] = np.mean(action_durations[action])
                    action_timing_features[f'std_{action}'] = np.std(action_durations[action])
                else:
                    action_timing_features[f'mean_{action}'] = 0
                    action_timing_features[f'std_{action}'] = 0
            
            # Step 6: Combine all aggregate features into a Series
            all_features = {'apm': apm}
            all_features.update(pct_features)
            all_features.update(overall_rhythm_features)
            all_features.update(action_timing_features)
            
            # Create Series and reindex using agg_feature_columns
            agg_series = pd.Series(all_features)
            agg_series = agg_series.reindex(self.agg_feature_columns, fill_value=0)
            
            # Convert to numpy array for sparse matrix
            agg_array = agg_series.values.reshape(1, -1)
            
            # Step 7: Create time-aware combo sentence
            combo_sentence = self.create_combo_sentence(keydown_df)
            
            # Step 8: Transform with N-gram vectorizer
            ngram_features = self.ngram_vectorizer.transform([combo_sentence])
            
            # Step 9: Combine aggregate and N-gram features
            final_features = hstack([agg_array, ngram_features])
            
            return final_features
            
        except Exception as e:
            print(f"Error in feature engineering: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_combo_sentence(self, keydown_df):
        """
        Create a time-aware combo sentence from keydown events.
        Inserts '.' as a break if time between actions exceeds 1000ms.
        
        Args:
            keydown_df: DataFrame of keydown events with 'action' and 't_ms' columns
            
        Returns:
            String representing the combo sentence
        """
        if keydown_df.empty:
            return ""
        
        # Sort by timestamp
        keydown_df = keydown_df.sort_values('t_ms')
        
        tokens = []
        prev_time = None
        
        for _, row in keydown_df.iterrows():
            current_time = row['t_ms']
            action = row['action']
            
            if pd.notna(action):
                # Insert break if gap is > 1000ms
                if prev_time is not None and (current_time - prev_time) > 1000:
                    tokens.append('.')
                
                tokens.append(action)
                prev_time = current_time
        
        return ' '.join(tokens)
    
    def update_boss_probabilities(self, probabilities):
        """Update the UI with new prediction probabilities"""
        for i, boss_name in enumerate(self.boss_names):
            prob_pct = probabilities[i] * 100
            label_text = f"{boss_name}: ({prob_pct:.0f}%)"
            self.boss_labels[boss_name].config(text=label_text)
    
    def on_closing(self):
        """Handle window closing event"""
        if self.is_recording:
            self.stop_recording()
        self.root.destroy()


def main():
    """Main entry point"""
    # Create main window
    root = tk.Tk()
    
    # Create application
    app = CupheadPredictorApp(root)
    
    # Handle window close event
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Set minimum window size
    root.minsize(300, 250)
    
    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
