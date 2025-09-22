#!/usr/bin/env python3
"""
Test the UI components without requiring a display
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("Testing imports...")
    
    try:
        from data_logger import DataLogger, FightSession
        print("✅ data_logger imports OK")
        
        from keyboard_listener import KeyboardListener
        print("✅ keyboard_listener imports OK") 
        
        # Test UI imports (may fail in headless environment)
        try:
            import tkinter as tk
            from main import CupheadLoggerUI, AppState
            print("✅ main UI imports OK")
        except Exception as e:
            print(f"⚠️  UI imports failed (expected in headless): {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_keyboard_listener():
    """Test keyboard listener initialization"""
    print("\nTesting keyboard listener...")
    
    try:
        from keyboard_listener import KeyboardListener
        
        def dummy_event_callback(event_type, key):
            print(f"Event: {event_type} - Key: {key}")
            
        def dummy_hotkey():
            print("Hotkey pressed!")
            
        listener = KeyboardListener(
            event_callback=dummy_event_callback,
            hotkey_callbacks={'start': dummy_hotkey}
        )
        
        # Test key normalization
        from pynput.keyboard import Key
        test_key = Key.space
        normalized = listener._normalize_key(test_key)
        print(f"Key normalization test: {test_key} -> {normalized}")
        
        # Test gameplay key detection
        is_gameplay = listener._is_gameplay_key(test_key)
        print(f"Gameplay key detection: {test_key} -> {is_gameplay}")
        
        print("✅ KeyboardListener test OK")
        return True
        
    except Exception as e:
        print(f"❌ KeyboardListener test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_logger_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting data logger edge cases...")
    
    try:
        from data_logger import DataLogger
        
        logger = DataLogger()
        
        # Test starting fight when one is already active
        fight_id1 = logger.start_fight("Cagney Carnation")
        
        try:
            fight_id2 = logger.start_fight("Baroness Von Bon Bon")
            print("❌ Should have failed to start second fight")
            return False
        except ValueError as e:
            print(f"✅ Correctly prevented second fight: {e}")
        
        # Test getting session info
        session_info = logger.get_session_info()
        print(f"✅ Session info: {session_info}")
        
        # Clean up
        logger.end_fight("test")
        
        # Test ending when no fight active
        try:
            logger.end_fight("test")
            print("❌ Should have failed to end non-existent fight")
            return False
        except ValueError as e:
            print(f"✅ Correctly prevented ending non-existent fight: {e}")
            
        print("✅ Data logger edge cases OK")
        return True
        
    except Exception as e:
        print(f"❌ Data logger edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    try:
        from data_logger import DataLogger
        
        logger = DataLogger()
        config = logger.config
        
        print(f"✅ Config loaded: {config}")
        
        # Verify expected keys
        expected_keys = ['difficulty', 'loadout', 'bosses', 'qa']
        for key in expected_keys:
            if key in config:
                print(f"✅ Config has {key}: {config[key]}")
            else:
                print(f"⚠️  Config missing {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading test failed: {e}")
        return False

if __name__ == "__main__":
    print("Cuphead Logger Component Tests")
    print("==============================")
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_keyboard_listener()
    all_passed &= test_data_logger_edge_cases()
    all_passed &= test_config_loading()
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✅ All component tests passed!")
        print("\nTo test the full UI, run: python run_logger.py")
        print("(Requires graphical environment)")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)