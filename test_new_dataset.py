#!/usr/bin/env python3
"""
Test script to verify new dataset functionality
"""
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

from data_logger import DataLogger

def test_default_dataset():
    """Test default dataset configuration"""
    print("Testing Default Dataset...")
    logger = DataLogger()
    
    assert logger.raw_dir.name == "raw", f"Expected 'raw', got '{logger.raw_dir.name}'"
    assert logger.csv_filename == "fight_summaries.csv", f"Expected 'fight_summaries.csv', got '{logger.csv_filename}'"
    
    print("✓ Default dataset: raw/ → fight_summaries.csv")

def test_new_dataset():
    """Test new dataset configuration"""
    print("\nTesting New Dataset...")
    logger = DataLogger(raw_subdir="raw_new", csv_filename="fight_summaries_new.csv")
    
    assert logger.raw_dir.name == "raw_new", f"Expected 'raw_new', got '{logger.raw_dir.name}'"
    assert logger.csv_filename == "fight_summaries_new.csv", f"Expected 'fight_summaries_new.csv', got '{logger.csv_filename}'"
    
    print("✓ New dataset: raw_new/ → fight_summaries_new.csv")

def test_custom_dataset():
    """Test custom dataset configuration"""
    print("\nTesting Custom Dataset...")
    logger = DataLogger(raw_subdir="custom_raw", csv_filename="custom_summary.csv")
    
    assert logger.raw_dir.name == "custom_raw", f"Expected 'custom_raw', got '{logger.raw_dir.name}'"
    assert logger.csv_filename == "custom_summary.csv", f"Expected 'custom_summary.csv', got '{logger.csv_filename}'"
    
    print("✓ Custom dataset: custom_raw/ → custom_summary.csv")

def test_directories_exist():
    """Test that necessary directories exist"""
    print("\nVerifying Directory Structure...")
    
    data_dir = Path(__file__).parent / "data"
    
    required_dirs = [
        data_dir / "raw",
        data_dir / "raw_new",
        data_dir / "summaries",
        data_dir / "meta"
    ]
    
    for dir_path in required_dirs:
        assert dir_path.exists(), f"Directory does not exist: {dir_path}"
        print(f"✓ {dir_path.relative_to(data_dir.parent)}")
    
    # Check CSV files
    csv_files = [
        data_dir / "summaries" / "fight_summaries.csv",
        data_dir / "summaries" / "fight_summaries_new.csv"
    ]
    
    for csv_path in csv_files:
        assert csv_path.exists(), f"CSV file does not exist: {csv_path}"
        print(f"✓ {csv_path.relative_to(data_dir.parent)}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing New Dataset Feature")
    print("=" * 60)
    
    try:
        test_default_dataset()
        test_new_dataset()
        test_custom_dataset()
        test_directories_exist()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nYou can now use:")
        print("  - python run_logger.py              # Use default dataset")
        print("  - python run_logger.py --new-dataset # Use new dataset")
        print("  - python data_processing.py --new-dataset # Process new dataset")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
