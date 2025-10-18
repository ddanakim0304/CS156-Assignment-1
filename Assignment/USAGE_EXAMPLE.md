# Usage Example: realtime_predictor_app.py

## Prerequisites

1. Ensure all dependencies are installed:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Verify the model file exists:
   ```bash
   ls -lh cuphead_predictor.joblib
   ```

## Running the Application

### Basic Usage

```bash
cd Assignment/
python3 realtime_predictor_app.py
```

### Expected Behavior

1. **On Startup:**
   - Window appears titled "Cuphead - Live Boss Predictor"
   - Window stays on top of other applications
   - "Start Recording" button is enabled
   - Status shows "Idle"
   - All boss predictions show "(---)"

2. **When You Click "Start Recording":**
   - Button changes to "Stop Recording"
   - Status changes to "Recording..."
   - Application begins capturing all keyboard events globally
   - Every 2 seconds, if you've pressed at least 15 keys, predictions update

3. **During Recording:**
   - Play Cuphead normally (or type test keys)
   - The app captures: Space, f, d, x, a, arrow keys
   - Predictions update showing percentages like:
     ```
     Baroness Von Bon Bon: (45%)
     Cagney Carnation: (12%)
     Glumstone the Giant: (38%)
     Grim Matchstick: (5%)
     ```

4. **When You Click "Stop Recording":**
   - Button changes back to "Start Recording"
   - Status changes to "Idle"
   - Keyboard capture stops
   - Last prediction remains visible

## Test Without Playing Cuphead

You can test the application by generating keyboard events:

```python
# Run this in another terminal while the app is recording
import time
from pynput.keyboard import Controller, Key

keyboard = Controller()

# Simulate a boss fight sequence
actions = [
    (Key.space, 0.05),  # jump
    ('f', 0.08),        # shoot
    (Key.right, 0.06),  # move right
    (Key.space, 0.07),  # jump
    ('d', 0.04),        # dash
    ('f', 0.09),        # shoot
] * 5  # Repeat 5 times for 30 actions

for key, duration in actions:
    keyboard.press(key)
    time.sleep(duration)
    keyboard.release(key)
    time.sleep(0.12)  # Small gap between actions
```

## Interpreting Results

- **High percentage (>50%)**: Strong prediction - you're likely fighting this boss
- **Multiple similar percentages**: Model is uncertain, needs more data
- **Predictions change over time**: Normal - as you collect more keystroke data, the model becomes more confident

## Troubleshooting

### "Model not loaded!" error
- Check that `cuphead_predictor.joblib` is in the same directory as the script
- Verify the file is not corrupted: `python3 -c "import joblib; joblib.load('cuphead_predictor.joblib')"`

### No predictions appearing
- Make sure you've pressed at least 15 keys (30 events with keydown+keyup)
- Check that you're pressing recognized keys (Space, f, d, x, a, arrow keys)

### Keyboard events not captured
- On Linux: You may need to run with sudo or grant input permissions
- On macOS: Grant Accessibility permissions in System Preferences
- On Windows: May need to run as administrator

### Window not staying on top
- This is controlled by `root.attributes('-topmost', True)` in the code
- Some window managers may override this setting
- Try manually keeping the window focused

## Advanced Usage

### Custom Update Interval

Edit `realtime_predictor_app.py` and change:
```python
UPDATE_INTERVAL_MS = 2000  # Change to 1000 for 1-second updates
```

### Minimum Events Threshold

Edit `realtime_predictor_app.py` and change:
```python
MIN_EVENTS_FOR_PREDICTION = 15  # Change to 30 for more stable predictions
```

## Architecture Notes

The application uses:
- **Main thread**: Runs tkinter GUI event loop
- **Keyboard listener thread**: Captures keyboard events globally
- **Prediction thread**: Updates predictions every 2 seconds
- **Thread-safe communication**: Uses locks and `root.after()` for UI updates

This ensures the GUI remains responsive while capturing keystrokes and making predictions in the background.
