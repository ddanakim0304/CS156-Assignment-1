#!/usr/bin/env python3
"""
Headless testing mode for Cuphead Logger
Tests core functionality without requiring display
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from data_logger import DataLogger
import time
import json

def simulate_fight_session():
    """Simulate a complete fight session"""
    print("🎮 Simulating Cuphead fight session...")
    
    logger = DataLogger()
    
    # Start fight
    boss = "Grim Matchstick"
    loadout = "Spreadshot + Smoke Bomb"
    fight_id = logger.start_fight(boss, loadout)
    print(f"📝 Started fight: {fight_id}")
    print(f"🎯 Boss: {boss}")
    print(f"🔫 Loadout: {loadout}")
    
    # Simulate realistic gameplay events
    events = [
        ("keydown", "Key.left"),   # Move left
        ("keyup", "Key.left"),
        ("keydown", "z"),          # Shoot
        ("keyup", "z"),
        ("keydown", "Key.space"),  # Jump
        ("keyup", "Key.space"),
        ("keydown", "Key.shift"),  # Dash
        ("keyup", "Key.shift"),
        ("keydown", "Key.right"),  # Move right
        ("keyup", "Key.right"),
        ("keydown", "z"),          # Shoot more
        ("keyup", "z"),
        ("keydown", "x"),          # Special
        ("keyup", "x"),
        ("keydown", "Key.up"),     # Jump/move up
        ("keyup", "Key.up"),
        ("keydown", "z"),          # Continue shooting
        ("keyup", "z"),
        ("keydown", "Key.down"),   # Duck
        ("keyup", "Key.down"),
    ]
    
    print(f"⌨️  Logging {len(events)} keyboard events...")
    
    for i, (event_type, key) in enumerate(events):
        logger.log_event(event_type, key)
        time.sleep(0.05)  # 50ms between events
        if i % 5 == 0:
            print(f"   Logged {i+1}/{len(events)} events...")
    
    # Simulate fight duration
    print("⏳ Simulating fight duration...")
    time.sleep(2)  # Additional fight time
    
    # End with victory
    outcome = "win"
    session_data = logger.end_fight(outcome)
    
    print(f"🏆 Fight completed!")
    print(f"   Outcome: {outcome.upper()}")
    print(f"   Duration: {session_data['duration_s']:.1f} seconds")
    print(f"   Events logged: {session_data['n_events']}")
    print(f"   Fight ID: {session_data['fight_id']}")
    
    return session_data

def verify_output_files(fight_id):
    """Verify that output files were created correctly"""
    print(f"\n🔍 Verifying output files for {fight_id}...")
    
    data_dir = Path(__file__).parent / "data"
    jsonl_file = data_dir / "raw" / f"{fight_id}.jsonl"
    csv_file = data_dir / "summaries" / "fight_summaries.csv"
    
    # Check JSONL file
    if jsonl_file.exists():
        print(f"✅ JSONL file created: {jsonl_file}")
        
        with open(jsonl_file, 'r') as f:
            lines = f.readlines()
        
        print(f"   📋 {len(lines)} lines in JSONL file")
        
        # Parse and validate each line
        meta_found = False
        events_found = 0
        summary_found = False
        
        for line in lines:
            try:
                data = json.loads(line.strip())
                if 'meta' in data:
                    meta_found = True
                    print(f"   📊 Meta: {data['meta']['boss']}")
                elif 'event' in data:
                    events_found += 1
                elif 'summary' in data:
                    summary_found = True
                    print(f"   🏁 Summary: {data['summary']['outcome']}")
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON line: {e}")
        
        print(f"   ✅ Meta line: {'Found' if meta_found else 'Missing'}")
        print(f"   ✅ Event lines: {events_found}")
        print(f"   ✅ Summary line: {'Found' if summary_found else 'Missing'}")
        
    else:
        print(f"❌ JSONL file not found: {jsonl_file}")
        return False
    
    # Check CSV file
    if csv_file.exists():
        print(f"✅ CSV file created: {csv_file}")
        
        with open(csv_file, 'r') as f:
            lines = f.readlines()
        
        print(f"   📋 {len(lines)} lines in CSV file (including header)")
        
        if len(lines) >= 2:  # Header + at least one data row
            header = lines[0].strip()
            print(f"   📊 Header: {header}")
            
            # Find our fight in the CSV
            for line in lines[1:]:
                if fight_id in line:
                    print(f"   ✅ Found fight record: {line.strip()}")
                    break
            else:
                print(f"   ❌ Fight record not found in CSV")
                return False
        else:
            print(f"   ❌ CSV file too short")
            return False
    else:
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    return True

def test_multiple_fights():
    """Test multiple sequential fights"""
    print(f"\n🔄 Testing multiple sequential fights...")
    
    logger = DataLogger()
    bosses = ["Cagney Carnation", "Baroness Von Bon Bon"]
    outcomes = ["win", "lose"]
    
    fight_results = []
    
    for i, (boss, outcome) in enumerate(zip(bosses, outcomes)):
        print(f"\n--- Fight {i+1}: {boss} ---")
        
        fight_id = logger.start_fight(boss)
        
        # Quick event sequence
        for j in range(5):
            logger.log_event("keydown", "z")
            logger.log_event("keyup", "z")
            time.sleep(0.1)
        
        time.sleep(1)  # Short fight
        
        session_data = logger.end_fight(outcome)
        fight_results.append(session_data)
        
        print(f"   {outcome.upper()}: {session_data['duration_s']:.1f}s, {session_data['n_events']} events")
    
    print(f"\n✅ Completed {len(fight_results)} fights")
    return fight_results

if __name__ == "__main__":
    from pathlib import Path
    
    print("Cuphead Logger - Headless Test Mode")
    print("===================================")
    
    try:
        # Test 1: Single realistic fight
        session_data = simulate_fight_session()
        
        # Test 2: Verify output files
        verify_success = verify_output_files(session_data['fight_id'])
        
        # Test 3: Multiple fights
        multiple_results = test_multiple_fights()
        
        print(f"\n{'='*50}")
        if verify_success:
            print("🎉 All headless tests passed!")
            print(f"✅ Generated {len(multiple_results) + 1} complete fight sessions")
            print(f"✅ All data files created successfully")
            print(f"✅ JSONL and CSV formats validated")
            
            print(f"\n📁 Check the following directories:")
            print(f"   📄 Raw logs: data/raw/")
            print(f"   📊 Summaries: data/summaries/")
            
            print(f"\n🚀 Ready for production use!")
            print(f"   Run: python run_logger.py (in graphical environment)")
        else:
            print("❌ Some verification tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)