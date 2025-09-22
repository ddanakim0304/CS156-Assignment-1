# Cuphead Boss Keystroke Logger

A data collection tool for capturing keyboard events during Cuphead boss fights with precise timestamps and always-on-top UI control.

## Features

- **Real-time keystroke logging** with millisecond precision timestamps
- **Always-on-top control panel** that doesn't interfere with gameplay
- **Global hotkeys** (F1/F2/F8/F9) that work regardless of focus
- **JSONL and CSV output** for easy data analysis
- **Boss-specific sessions** with configurable loadouts
- **Automatic data validation** with event counts and duration tracking

## Target Bosses

- Cagney Carnation
- Baroness Von Bon Bon  
- Grim Matchstick
- Glumstone the Giant (DLC)

## Installation

### Prerequisites

- **macOS** (tested on macOS 10.15+)
- **Python 3.7+**
- **Accessibility permissions** for global keyboard capture

### Setup

1. **Clone or download this project**
   ```bash
   cd "Desktop/CS156/Assignments/Assignment 1"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Grant Accessibility permissions**
   - Open **System Preferences > Security & Privacy**
   - Click the **Privacy** tab
   - Select **Accessibility** from the left sidebar
   - Click the lock icon and enter your password
   - Add **Terminal** or **Python** to the allowed applications
   - Restart the terminal/application

### First Run Test

```bash
python test_logger.py
```

If all tests pass, you're ready to start logging!

## Usage

### Starting the Application

```bash
python main.py
```

This opens the always-on-top control panel.

### Recording a Fight Session

1. **Configure the session:**
   - Select boss from dropdown
   - Set loadout (defaults to "Peashooter + Smoke Bomb")
   - Difficulty is fixed to "Regular"

2. **Start recording:**
   - Click **Start (F1)** or press **F1** globally
   - The status shows "Recording: [fight_id] — Boss: [name]"

3. **Play the fight:**
   - All relevant keystrokes are captured automatically
   - Event counter and timer update in real-time

4. **End recording:**
   - Click **End (F2)** or press **F2** globally
   - Status shows "Fight ended. Mark outcome."

5. **Mark outcome:**
   - Click **Win (F9)** or press **F9** for victory
   - Click **Lose (F8)** or press **F8** for defeat
   - Data is automatically saved and summarized

### Global Hotkeys

- **F1** - Start new fight recording
- **F2** - End current recording  
- **F8** - Mark fight as loss
- **F9** - Mark fight as win

These work regardless of which application has focus.

### Monitored Keys

The logger captures these gameplay keys:
- **Movement:** left, right, up, down (arrow keys or WASD)
- **Actions:** jump (space/X), dash (C), shoot (Z), special (V)
- **Advanced:** lock (S), swap (A), pause (Esc/P)

### Session Protocol

For consistent data collection:

1. **Fix settings:** Use "Regular" difficulty and one loadout for all fights
2. **Timing:** Press Start (F1) right before "WALLUP!" appears
3. **Recording:** Play normally until KO or death screen
4. **Ending:** Press End (F2) immediately at outcome screen
5. **Outcome:** Mark Win (F9) or Lose (F8) promptly

## Data Output

### Raw Event Logs

**Location:** `data/raw/<fight_id>.jsonl`

**Format:** One JSON object per line
```json
{"fight_id":"2025-10-02T21-13-05Z_12345","meta":{"boss":"Cagney Carnation","loadout":"Peashooter+Smoke","difficulty":"Regular","start_utc":"2025-10-02T21:13:05Z"}}
{"fight_id":"2025-10-02T21-13-05Z_12345","event":"keydown","key":"space","t_ms":1234}
{"fight_id":"2025-10-02T21-13-05Z_12345","event":"keyup","key":"space","t_ms":1280}
{"fight_id":"2025-10-02T21-13-05Z_12345","summary":{"outcome":"win","duration_ms":92500,"end_utc":"2025-10-02T21:14:37Z"}}
```

### Fight Summaries

**Location:** `data/summaries/fight_summaries.csv`

**Columns:**
- `fight_id` - Unique identifier with timestamp
- `boss` - Boss name
- `loadout` - Equipment configuration  
- `difficulty` - Difficulty setting
- `outcome` - "win" or "lose"
- `duration_s` - Fight duration in seconds
- `n_events` - Total keystroke events logged
- `recorded_utc` - When the summary was recorded

## Project Structure

```
Assignment 1/
├── app/                     # Application code
│   ├── data_models.py      # Core data structures
│   ├── keyboard_logger.py  # Event capture system
│   ├── ui.py              # GUI control panel
│   ├── hotkeys.py         # Global hotkey manager
│   └── __init__.py
├── data/                   # Data output
│   ├── raw/               # Per-fight JSONL files
│   ├── summaries/         # fight_summaries.csv
│   └── meta/              # Configuration files
│       ├── boss_manifest.csv
│       └── config.yaml
├── main.py                # Application entry point
├── test_logger.py         # Test suite
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration

**File:** `data/meta/config.yaml`

```yaml
difficulty: "Regular"
loadout: "Peashooter + Smoke Bomb"
bosses:
  - "Cagney Carnation"
  - "Baroness Von Bon Bon"
  - "Grim Matchstick" 
  - "Glumstone the Giant"
hotkeys:
  start: "F1"
  end: "F2"
  lose: "F8"
  win: "F9"
qa:
  min_duration_s: 10
  min_events: 30
```

## Troubleshooting

### Permission Issues
If you get permission errors:
1. Check Accessibility permissions in System Preferences
2. Try running with `sudo python main.py` (not recommended long-term)
3. Ensure Python has the necessary entitlements

### Import Errors
If you see module import errors:
```bash
pip install --upgrade pynput PyYAML
```

### No Events Logged
1. Verify the UI shows "Recording" status
2. Check that focus is on Cuphead during gameplay
3. Ensure accessibility permissions are granted
4. Try pressing keys while UI has focus to test

### Data Not Saved
1. Check file permissions in the data/ directory
2. Ensure disk space is available
3. Verify the End (F2) button was pressed before marking outcome

## Data Quality Checks

The system automatically flags potentially invalid sessions:
- **Duration < 10 seconds** - Likely test or accidental recording
- **Events < 30** - Insufficient gameplay data
- **Missing metadata** - Incomplete session information

Review the CSV summaries to filter out invalid sessions before analysis.

## Future Enhancements

- **Key remapping** for custom control schemes
- **Replay visualization** of recorded sessions
- **Live probability** analysis during fights
- **Multi-platform** support (Windows, Linux)
- **Advanced filtering** and data export options

## License

This project is for educational/research purposes. Cuphead is a trademark of StudioMDHR Entertainment Inc.