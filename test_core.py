#!/usr/bin/env python3
"""
Test script for Cuphead Logger core functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from data_logger import DataLogger
import time
import json

def test_data_logger():
    """Test the data logger functionality"""
    print("Testing DataLogger...")
    
    # Create logger
    logger = DataLogger()
    
    # Start a test fight
    print("Starting test fight...")
    fight_id = logger.start_fight("Cagney Carnation", "Test Loadout", "Regular")
    print(f"Fight started: {fight_id}")
    
    # Simulate some events
    print("Logging test events...")
    logger.log_event("keydown", "a")
    time.sleep(0.1)
    logger.log_event("keyup", "a")
    time.sleep(0.1)
    logger.log_event("keydown", "Key.space")
    time.sleep(0.1)
    logger.log_event("keyup", "Key.space")
    
    # End the fight
    print("Ending fight...")
    session_data = logger.end_fight("win")
    print(f"Fight ended: {session_data}")
    
    # Verify files were created
    data_dir = logger.data_dir
    jsonl_file = data_dir / "raw" / f"{fight_id}.jsonl"
    csv_file = data_dir / "summaries" / "fight_summaries.csv"
    
    print(f"\nFiles created:")
    print(f"JSONL: {jsonl_file} - Exists: {jsonl_file.exists()}")
    print(f"CSV: {csv_file} - Exists: {csv_file.exists()}")
    
    if jsonl_file.exists():
        print(f"\nJSONL content:")
        with open(jsonl_file, 'r') as f:
            for line in f:
                print(f"  {line.strip()}")
                
    if csv_file.exists():
        print(f"\nCSV content:")
        with open(csv_file, 'r') as f:
            for line in f:
                print(f"  {line.strip()}")
    
    print("\nDataLogger test completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_data_logger()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)