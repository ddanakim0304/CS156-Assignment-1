#!/usr/bin/env python3
"""
Cuphead Boss - Real-Time Predictor UI (Corrected with Multi-Threading)
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
from pynput import keyboard
import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack
import sys

# --- Global Settings ---
UPDATE_INTERVAL_MS = 2000
MIN_EVENTS_FOR_PREDICTION = 15

class KeyboardListener:
    # (This class remains unchanged)
    def __init__(self, event_callback):
        self.event_callback = event_callback
        self.listener = None

    def start(self):
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
            self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None

    def _on_press(self, key):
        self.event_callback('keydown', self._normalize_key(key))

    def _on_release(self, key):
        self.event_callback('keyup', self._normalize_key(key))
    
    @staticmethod
    def _normalize_key(key):
        if hasattr(key, 'char') and key.char:
            return key.char
        return str(key)

class RealtimePredictorUI:
    def __init__(self, model_path='Assignment/cuphead_predictor.joblib'):
        print("Initializing UI...")
        sys.stdout.flush()
        
        self.root = tk.Tk()
        self.root.title("Cuphead - Live Boss Predictor")
        self.root.geometry("450x300")
        self.root.resizable(False, False)
        
        # --- State Management ---
        self.is_recording = False
        self.events = []
        self.start_time = None
        self.key_listener = None
        self.event_lock = threading.Lock()
        self.prediction_job = None # To hold the 'after' job ID
        self.queue_polling_job = None # To hold the queue polling 'after' job ID

        # --- Threading and Communication ---
        self.results_queue = queue.Queue()

        # --- Load Model Components ---
        print("Loading model...")
        sys.stdout.flush()
        try:
            components = joblib.load(model_path)
            self.model = components['model_pipeline']
            self.vectorizer = components['ngram_vectorizer']
            self.label_encoder = components['label_encoder']
            self.agg_feature_columns = components['agg_feature_columns']
            print(f"Model loaded successfully. Bosses: {self.label_encoder.classes_}")
            sys.stdout.flush()
        except FileNotFoundError:
            self.model = None
            print(f"ERROR: Model file not found at '{model_path}'.")
            sys.stdout.flush()
        
        print("Creating widgets...")
        sys.stdout.flush()
        self._create_widgets()
        
        print("Configuring UI...")
        sys.stdout.flush()
        
        if not self.model:
            self.status_label.config(text="ERROR: model file not found!", foreground='red')
            self.start_stop_button.config(state='disabled')

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Set topmost AFTER everything else is configured (macOS compatibility)
        print("Setting window properties...")
        sys.stdout.flush()
        self.root.attributes('-topmost', True)
        
        print("UI initialization complete. Starting main loop...")
        sys.stdout.flush()  # Ensure all output is visible

    def _create_widgets(self):
        # (This method remains unchanged)
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.start_stop_button = ttk.Button(main_frame, text="Start Recording", command=self._toggle_recording)
        self.start_stop_button.pack(pady=10, ipady=10, fill=tk.X)
        
        self.status_label = ttk.Label(main_frame, text="Status: Idle", anchor=tk.CENTER)
        self.status_label.pack(pady=5)

        prediction_frame = ttk.LabelFrame(main_frame, text="Live Prediction", padding="10")
        prediction_frame.pack(pady=10, expand=True, fill=tk.BOTH)

        self.prediction_labels = {}
        if self.model:
            for i, boss_name in enumerate(self.label_encoder.classes_):
                var = tk.StringVar(value=f"{boss_name}: (0%)")
                label = ttk.Label(prediction_frame, textvariable=var, font=("Arial", 12))
                label.pack(anchor=tk.W, pady=2)
                self.prediction_labels[boss_name] = var

    def _toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        with self.event_lock:
            self.events = []
        self.start_time = time.perf_counter()
        
        self.key_listener = KeyboardListener(self._on_key_event)
        self.key_listener.start()
        
        self.start_stop_button.config(text="Stop Recording")
        self.status_label.config(text="Status: Recording...")
        
        self.queue_polling_job = self.root.after(100, self._process_results_queue) # Start polling the results queue
        self._schedule_next_prediction() # Schedule the first prediction job

    def _stop_recording(self):
        if self.key_listener:
            self.key_listener.stop()
            self.key_listener = None
        
        if self.prediction_job:
            self.root.after_cancel(self.prediction_job)
            self.prediction_job = None
        
        if self.queue_polling_job:
            self.root.after_cancel(self.queue_polling_job)
            self.queue_polling_job = None
            
        self.start_stop_button.config(text="Start Recording")
        self.status_label.config(text="Status: Idle")
        for var in self.prediction_labels.values():
            var.set(var.get().split(':')[0] + ": (0%)")

    def _on_key_event(self, event_type, key):
        if self.is_recording:
            elapsed_time = int((time.perf_counter() - self.start_time) * 1000)
            with self.event_lock:
                self.events.append({'event': event_type, 'key': key, 't_ms': elapsed_time})

    def _schedule_next_prediction(self):
        """Schedules the prediction task to run."""
        if self.is_recording:
            self._run_prediction_in_thread()
            self.prediction_job = self.root.after(UPDATE_INTERVAL_MS, self._schedule_next_prediction)

    def _run_prediction_in_thread(self):
        """Kicks off a worker thread to perform the heavy lifting."""
        with self.event_lock:
            current_events = list(self.events)

        if len(current_events) < MIN_EVENTS_FOR_PREDICTION:
            self.status_label.config(text=f"Status: Collecting data ({len(current_events)} events)...")
            return
        
        self.status_label.config(text=f"Status: Predicting ({len(current_events)} events)...")
        
        # Create and start the worker thread
        thread = threading.Thread(target=self._worker_predict, args=(current_events,), daemon=True)
        thread.start()

    def _worker_predict(self, events):
        """(RUNS ON WORKER THREAD) Performs feature engineering and prediction."""
        try:
            features = self._realtime_feature_engineering(events)
            if features is not None:
                probabilities = self.model.predict_proba(features)[0]
                # Put the result in the queue for the main thread to pick up
                self.results_queue.put(probabilities)
        except Exception as e:
            print(f"Worker thread error: {e}")

    def _process_results_queue(self):
        """(RUNS ON MAIN UI THREAD) Checks the queue for new results and updates the UI."""
        try:
            # Check the queue without blocking
            probabilities = self.results_queue.get_nowait()
            
            # If we got a result, update the UI
            for i, boss_name in enumerate(self.label_encoder.classes_):
                prob = probabilities[i]
                display_text = f"{boss_name}: ({prob:.0%})"
                self.prediction_labels[boss_name].set(display_text)
                
        except queue.Empty:
            # This is normal, just means the worker thread isn't done yet.
            pass
        
        # Only schedule this poller to run again if we're still recording
        if self.is_recording:
            self.queue_polling_job = self.root.after(100, self._process_results_queue)

    def _realtime_feature_engineering(self, events):
        # (This method remains unchanged)
        df = pd.DataFrame(events)
        key_mapping = {
            'Key.space': 'jump', 'f': 'shoot', 'd': 'dash', 'x': 'ex_move',
            'a': 'lock', 'Key.up': 'up', 'Key.down': 'down', 'Key.left': 'left', 'Key.right': 'right'
        }
        df['action'] = df['key'].map(key_mapping)
        df.dropna(subset=['action'], inplace=True)
        keydowns = df[df['event'] == 'keydown']
        if len(keydowns) < 5: return None
        
        duration_ms = keydowns['t_ms'].max()
        event_count = len(keydowns)
        apm = (event_count / (duration_ms / 1000.0)) * 60 if duration_ms > 0 else 0
        
        action_counts = keydowns['action'].value_counts()
        action_percentages = (action_counts / event_count).add_prefix('pct_')
        
        downs = df[df['event'] == 'keydown'].copy(); ups = df[df['event'] == 'keyup'].copy()
        downs['press_num'] = downs.groupby('action').cumcount()
        ups['press_num'] = ups.groupby('action').cumcount()
        merged = pd.merge(downs, ups, on=['action', 'press_num'], suffixes=('_d', '_u'))
        valid_durations = merged[merged['t_ms_u'] > merged['t_ms_d']]
        
        overall_duration_stats = valid_durations['t_ms_u'].sub(valid_durations['t_ms_d']).agg(['mean', 'std', 'median', 'min', 'max']).add_prefix('overall_duration_')
        
        action_specific_stats = valid_durations.groupby('action').apply(lambda g: g['t_ms_u'].sub(g['t_ms_d']).agg(['mean', 'std'])).unstack().fillna(0)
        action_specific_stats.columns = ['_'.join(col) for col in action_specific_stats.columns]

        all_features = pd.concat([pd.Series({'apm': apm}), action_percentages, overall_duration_stats, action_specific_stats])
        feature_vector = all_features.reindex(self.agg_feature_columns).fillna(0)
        
        action_sentence = ' '.join(keydowns.sort_values('t_ms')['action'])
        ngram_vector = self.vectorizer.transform([action_sentence])
        
        return hstack([feature_vector.values.reshape(1, -1), ngram_vector]).tocsr()

    def run(self):
        print("Entering main loop...")
        sys.stdout.flush()
        self.root.update()  # Force initial update on macOS
        self.root.mainloop()

    def _on_closing(self):
        self.is_recording = False
        if self.key_listener:
            self.key_listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    app = RealtimePredictorUI()
    app.run()