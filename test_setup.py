#!/usr/bin/env python3
"""
Test script to verify project setup and module imports
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported correctly"""
    print("Testing module imports...")
    
    try:
        # Test utility imports
        from utils import get_user_input, validate_credentials, setup_logging
        print("✓ utils module imported successfully")
        
        # Test data manager imports
        from data_manager import DataManager
        print("✓ data_manager module imported successfully")
        
        # Test job searcher imports
        from job_searcher import LinkedInJobSearcher
        print("✓ job_searcher module imported successfully")
        
        # Test config imports
        from config import Config
        print("✓ config module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration settings"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        
        # Test directory creation
        Config.create_directories()
        print("✓ Directories created successfully")
        
        # Test user agent
        user_agent = Config.get_user_agent()
        print(f"✓ User agent: {user_agent[:50]}...")
        
        # Test CSV columns
        print(f"✓ CSV columns: {len(Config.CSV_COLUMNS)} columns defined")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_data_manager():
    """Test data manager functionality"""
    print("\nTesting data manager...")
    
    try:
        from data_manager import DataManager
        
        # Create data manager instance
        dm = DataManager()
        print("✓ DataManager instance created")
        
        # Test job summary
        summary = dm.get_job_summary()
        print(f"✓ Job summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data manager error: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    try:
        from utils import clean_text, extract_salary_range, extract_qualifications
        
        # Test text cleaning
        test_text = "  This   is   a   test   "
        cleaned = clean_text(test_text)
        print(f"✓ Text cleaning: '{cleaned}'")
        
        # Test salary extraction
        salary_text = "Salary: $50,000 - $70,000 per year"
        salary = extract_salary_range(salary_text)
        print(f"✓ Salary extraction: {salary}")
        
        # Test qualification extraction
        qual_text = "Requirements: Python, JavaScript, 2+ years experience"
        quals = extract_qualifications(qual_text)
        print(f"✓ Qualification extraction: {len(quals)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Utility function error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("JOB SEARCH BOT - SETUP TEST")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Data Manager", test_data_manager),
        ("Utility Functions", test_utils)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The project is ready to use.")
        print("\nTo run the job search bot:")
        print("python main.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nMake sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 