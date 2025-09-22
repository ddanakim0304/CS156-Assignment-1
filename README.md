# Cuphead Boss Keystroke Logger

A data collection tool for recording keystrokes during Cuphead boss fights. This application provides an always-on-top control panel for starting/stopping recording sessions and automatically logs all relevant gameplay keystrokes to structured data files.

## Features

- 🎮 Records keystrokes for: left, right, up, down, jump, dash, shoot, special, lock, swap, pause
- ⏱️ High-precision timestamps (milliseconds since fight start)
- 🎯 Supports 4 boss types: Cagney Carnation, Baroness Von Bon Bon, Grim Matchstick, Glumstone the Giant
- 🔄 Global hotkeys (F1/F2/F8/F9) work regardless of window focus
- 📊 Real-time event counter and elapsed time display
- 💾 Immediate writes to prevent data loss on crashes
- 📁 Structured output: JSONL event logs + CSV summaries

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd CS156-Assignment-1
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **macOS Setup (if applicable):**
   - Grant Accessibility permissions when prompted
   - No screen recording permissions needed

## Usage

### Quick Start

1. **Launch the application:**
   ```bash
   python run_logger.py
   ```

2. **Basic workflow:**
   - Select boss from dropdown
   - Optionally modify loadout (defaults to "Peashooter + Smoke Bomb")
   - Start Cuphead and navigate to boss fight
   - Press **F1** (or click Start) right before "WALLUP!"
   - Play the fight normally
   - Press **F2** (or click End) when fight ends (KO or death screen)
   - Press **F9** (Win) or **F8** (Lose) to mark the outcome

### Global Hotkeys

- **F1** - Start recording
- **F2** - End recording  
- **F8** - Mark as Loss
- **F9** - Mark as Win

*Note: Hotkeys work regardless of which window has focus*

### UI Controls

- **Boss Selector**: Choose from 4 available bosses
- **Loadout Field**: Customize weapon/charm loadout description
- **Difficulty**: Set to Regular (default), Simple, or Expert
- **Pin on top**: Keep control panel visible above all windows

### Button States

- **Idle**: Start enabled, others disabled
- **Recording**: Only End enabled
- **Ended**: Only Win/Lose enabled

## Output Files

### Raw Event Logs
**Location**: `data/raw/<fight_id>.jsonl`

Each fight generates a JSONL file with:
```json
{"fight_id":"2025-10-02T21-13-05Z_12345","meta":{"boss":"Cagney Carnation","loadout":"Peashooter+Smoke","difficulty":"Regular","start_utc":"2025-10-02T21:13:05Z"}}
{"fight_id":"2025-10-02T21-13-05Z_12345","event":"keydown","key":"Key.space","t_ms":1234}
{"fight_id":"2025-10-02T21-13-05Z_12345","event":"keyup","key":"Key.space","t_ms":1280}
{"fight_id":"2025-10-02T21-13-05Z_12345","summary":{"outcome":"win","duration_ms":92500,"end_utc":"2025-10-02T21:14:37Z"}}
```

### Summary CSV
**Location**: `data/summaries/fight_summaries.csv`

Columns: `fight_id,boss,loadout,difficulty,outcome,duration_s,n_events,recorded_utc`

## Configuration

### Default Config
**Location**: `data/meta/config.yaml`

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
log:
  write_mode: "append"
  flush_every_event: true
qa:
  min_duration_s: 10
  min_events: 30
```

## Data Quality

- Fights shorter than 10 seconds or with fewer than 30 events are flagged for review
- All events are written immediately to prevent data loss
- Monotonic timestamps ensure accuracy even with system clock changes
- Control keys (Cmd, Alt, Ctrl) and hotkeys are automatically filtered out

## Troubleshooting

### "No DISPLAY environment variable found"
- This application requires a graphical environment
- Use X11 forwarding for remote connections: `ssh -X user@host`

### Hotkeys not working
- On macOS: Grant Accessibility permissions in System Preferences
- On Linux: Ensure your user can access input devices

### UI not staying on top
- Toggle the "Pin on top" checkbox
- Some window managers may override this behavior

## Testing

Run the core functionality test:
```bash
python test_core.py
```

This verifies data logging, file creation, and output formats.

## File Structure

```
project_root/
├── app/                    # Application code
│   ├── main.py            # Main UI application
│   ├── data_logger.py     # Data logging functionality
│   └── keyboard_listener.py # Keyboard event handling
├── data/                   # Generated data
│   ├── raw/               # Per-fight JSONL logs
│   ├── summaries/         # fight_summaries.csv
│   └── meta/              # Configuration files
├── requirements.txt        # Python dependencies
├── run_logger.py          # Application launcher
├── test_core.py           # Test script
└── README.md              # This file
```

## Development

### Adding New Bosses
1. Edit `data/meta/boss_manifest.csv`
2. Update `data/meta/config.yaml` bosses list

### Customizing Key Mappings
Modify `GAMEPLAY_KEYS` in `app/keyboard_listener.py`

### Changing Hotkeys
Update the hotkey callbacks in `app/main.py` and configuration file

## License

This project is for educational/research purposes as part of CS156 Assignment 1.