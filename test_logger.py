#!/usr/bin/env python3
"""
Test script for the Cuphead keystroke logger.
This script tests basic functionality without requiring the full UI.
"""

import sys
import time
import json
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_data_models():
    """Test the core data models."""
    print("Testing data models...")
    
    try:
        from app.data_models import FightSession, KeyEvent, FightSummary, DataLogger, Config
        
        # Test session creation
        session = FightSession.create_new("Cagney Carnation", "Peashooter + Smoke Bomb")
        print(f"✓ Created session: {session.fight_id}")
        
        # Test configuration
        config = Config()
        print(f"✓ Loaded config with {len(config.bosses)} bosses")
        
        # Test data logger
        data_root = Path(__file__).parent / "data"
        logger = DataLogger(data_root)
        print("✓ Data logger initialized")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing data models: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_writing():
    """Test file writing capabilities."""
    print("\nTesting file writing...")
    
    try:
        from app.data_models import FightSession, KeyEvent, FightSummary, DataLogger
        from datetime import datetime, timezone
        
        # Create test session
        session = FightSession.create_new("Test Boss", "Test Loadout")
        
        # Initialize logger
        data_root = Path(__file__).parent / "data"
        logger = DataLogger(data_root)
        
        # Start fight (write metadata)
        jsonl_path = logger.start_fight(session)
        print(f"✓ Created JSONL file: {jsonl_path}")
        
        # Log some test events
        for i in range(5):
            event = KeyEvent(
                fight_id=session.fight_id,
                event="keydown" if i % 2 == 0 else "keyup",
                key="space",
                t_ms=i * 100
            )
            logger.log_event(event, jsonl_path)
        
        print("✓ Logged 5 test events")
        
        # End fight
        summary = FightSummary(
            fight_id=session.fight_id,
            outcome="win",
            duration_ms=500,
            end_utc=datetime.now(timezone.utc).isoformat(),
            n_events=5
        )
        
        logger.end_fight(summary, jsonl_path, session)
        print("✓ Wrote fight summary")
        
        # Verify files exist and have content
        assert jsonl_path.exists(), "JSONL file not created"
        
        csv_path = data_root / "summaries" / "fight_summaries.csv"
        assert csv_path.exists(), "CSV file not created"
        
        # Check JSONL content
        with open(jsonl_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 7, f"Expected 7 lines, got {len(lines)}"  # meta + 5 events + summary
        
        print(f"✓ JSONL file has {len(lines)} lines as expected")
        
        # Clean up test file
        jsonl_path.unlink()
        print("✓ Cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing file writing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_keyboard_logger():
    """Test keyboard logger initialization (without actually capturing keys)."""
    print("\nTesting keyboard logger...")
    
    try:
        from app.data_models import DataLogger
        from app.keyboard_logger import KeyboardLogger
        
        data_root = Path(__file__).parent / "data"
        data_logger = DataLogger(data_root)
        kb_logger = KeyboardLogger(data_logger)
        
        print("✓ Keyboard logger initialized")
        
        # Test key normalization
        test_key = "space"
        normalized = kb_logger.normalize_key(type('MockKey', (), {'char': ' ', 'name': None})())
        # Note: This might not work perfectly without actual pynput key objects
        
        print("✓ Key normalization tested")
        
        # Test status
        status = kb_logger.get_status()
        assert not status['is_recording'], "Should not be recording initially"
        print("✓ Status check passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing keyboard logger: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Cuphead Logger Test Suite")
    print("=" * 40)
    
    tests = [
        test_data_models,
        test_file_writing,
        test_keyboard_logger
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n{'='*40}")
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())