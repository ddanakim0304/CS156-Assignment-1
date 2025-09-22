#!/usr/bin/env python3
"""
Mock UI demonstration - shows what the actual UI looks like
"""

def show_ui_mockup():
    print("Cuphead Boss Keystroke Logger - UI Layout")
    print("=" * 50)
    print("┌─────────────────────────────────────────────────┐")
    print("│          Cuphead Boss Keystroke Logger         │")
    print("├─────────────────────────────────────────────────┤")
    print("│                                                 │")
    print("│ Boss: [Cagney Carnation     ▼]                 │")
    print("│                                                 │")
    print("│ Loadout: [Peashooter + Smoke Bomb            ] │")
    print("│                                                 │")
    print("│ Difficulty: [Regular         ▼]                │")
    print("│                                                 │")
    print("│     [Start (F1)]    [End (F2)]                 │")
    print("│     [Lose (F8)]     [Win (F9)]                 │")
    print("│                                                 │")
    print("│ Status: Idle                                    │")
    print("│                                                 │")
    print("│ ┌─── Session Info ────────────────────────────┐ │")
    print("│ │ Events: 0              Elapsed: 00:00      │ │")
    print("│ └─────────────────────────────────────────────┘ │")
    print("│                                                 │")
    print("│ ☑ Pin on top                                   │")
    print("│                                                 │")
    print("└─────────────────────────────────────────────────┘")
    print()
    print("Features:")
    print("• Always-on-top window (stays above Cuphead)")
    print("• Global hotkeys work regardless of focus")
    print("• Real-time event counter and timer during recording")
    print("• Button states change based on recording state")
    print("• Dropdown menus for boss and difficulty selection")
    print("• Status updates show current fight info")

def show_state_examples():
    print("\nUI State Examples:")
    print("=" * 30)
    
    print("\n1. IDLE State:")
    print("   • Start button: ENABLED")
    print("   • End/Win/Lose buttons: DISABLED")
    print("   • Status: 'Idle'")
    
    print("\n2. RECORDING State:")
    print("   • Start button: DISABLED")
    print("   • End button: ENABLED")
    print("   • Win/Lose buttons: DISABLED")
    print("   • Status: 'Recording: 2025-09-22T15-55-48Z_48457 — Boss: Grim Matchstick'")
    print("   • Telemetry: 'Events: 47', 'Elapsed: 01:23'")
    
    print("\n3. ENDED State:")
    print("   • Start/End buttons: DISABLED")
    print("   • Win/Lose buttons: ENABLED")
    print("   • Status: 'Fight ended. Mark outcome.'")

def show_data_format_examples():
    print("\nData Format Examples:")
    print("=" * 35)
    
    print("\nJSONL Event Log (data/raw/<fight_id>.jsonl):")
    print("─" * 50)
    print('{"fight_id":"2025-09-22T15-55-48Z_48457","meta":{"boss":"Grim Matchstick","loadout":"Spreadshot + Smoke Bomb","difficulty":"Regular","start_utc":"2025-09-22T15:55:48.457123+00:00"}}')
    print('{"fight_id":"2025-09-22T15-55-48Z_48457","event":"keydown","key":"Key.left","t_ms":0}')
    print('{"fight_id":"2025-09-22T15-55-48Z_48457","event":"keyup","key":"Key.left","t_ms":50}')
    print('{"fight_id":"2025-09-22T15-55-48Z_48457","event":"keydown","key":"z","t_ms":100}')
    print('...')
    print('{"fight_id":"2025-09-22T15-55-48Z_48457","summary":{"outcome":"win","duration_ms":3002,"end_utc":"2025-09-22T15:55:51.460194+00:00"}}')
    
    print("\nCSV Summary (data/summaries/fight_summaries.csv):")
    print("─" * 50)
    print("fight_id,boss,loadout,difficulty,outcome,duration_s,n_events,recorded_utc")
    print("2025-09-22T15-55-48Z_48457,Grim Matchstick,Spreadshot + Smoke Bomb,Regular,win,3.002,20,2025-09-22T15:55:51.460194+00:00")

if __name__ == "__main__":
    show_ui_mockup()
    show_state_examples()
    show_data_format_examples()
    
    print("\n" + "=" * 60)
    print("🚀 To run the actual UI application:")
    print("   python run_logger.py")
    print()
    print("🧪 To test without UI (headless):")
    print("   python test_headless.py")
    print()
    print("📊 To analyze collected data:")
    print("   python analyze_data.py")
    print("=" * 60)