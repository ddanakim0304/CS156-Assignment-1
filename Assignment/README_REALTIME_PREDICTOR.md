# Real-time Cuphead Boss Predictor

This application predicts which Cuphead boss you are currently fighting based on your live keystrokes.

## Requirements

The application requires the following Python packages:
- tkinter (usually included with Python)
- pynput
- joblib
- pandas
- numpy
- scipy
- scikit-learn

Install the dependencies:
```bash
pip install -r ../requirements.txt
```

## Model File

The application requires `cuphead_predictor.joblib` in the same directory as the script. This file contains:
- Trained LogisticRegression model with StandardScaler
- CountVectorizer for N-gram features
- LabelEncoder for boss names
- List of aggregate feature column names

## Usage

1. Make sure `cuphead_predictor.joblib` is in the same directory as the script
2. Run the application:
   ```bash
   python3 realtime_predictor_app.py
   ```
3. Click "Start Recording" to begin capturing keystrokes
4. Play Cuphead - the application will update predictions every 2 seconds
5. Click "Stop Recording" when done

## Features

- **Always On Top Window**: The window stays visible over other applications
- **Real-time Predictions**: Updates every 2 seconds with probability percentages for each boss
- **Comprehensive Feature Engineering**: 
  - Pace metrics (APM)
  - Action frequency (percentage of each action)
  - Overall rhythm features (mean, std, median, min, max press durations)
  - Action-specific timing features
  - Time-aware N-gram sequences
- **Thread-safe Event Capture**: Global keyboard listener captures events without interfering with gameplay

## Key Mappings

The application recognizes these game controls:
- `Space`: Jump
- `f`: Shoot
- `d`: Dash
- `x`: EX Move
- `a`: Lock
- `Arrow keys`: Movement (up, down, left, right)

## How It Works

1. **Keystroke Capture**: Uses `pynput` to capture all keyboard events globally
2. **Feature Engineering**: Every 2 seconds, the app:
   - Converts events to a DataFrame
   - Maps raw keys to action names
   - Calculates pace, frequency, rhythm, and timing features
   - Creates a time-aware combo sentence (inserts `.` for 1+ second gaps)
   - Generates N-gram features from the combo sequence
   - Combines aggregate and N-gram features into a sparse matrix
3. **Prediction**: The feature matrix is passed through the trained pipeline (scaler + logistic regression)
4. **UI Update**: Probabilities are displayed as percentages for each boss

## Minimum Requirements

- At least 15 events (keydown/keyup pairs) are required before the first prediction
- Events must include mapped keys (game controls) to be counted

## Boss Names

The model predicts one of these bosses:
- Baroness Von Bon Bon
- Cagney Carnation
- Glumstone the Giant
- Grim Matchstick
