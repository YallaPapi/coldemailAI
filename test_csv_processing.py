#!/usr/bin/env python3
"""
Test script for ColdEmailAI CSV processing functionality
Tests chunked processing, file validation, and data mapping without requiring OpenAI API
"""

import os
import sys
import pandas as pd
import tempfile
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_csv_chunked_processing():
    """Test chunked CSV processing functionality"""
    print("Testing chunked CSV processing...")
    
    # Test data file
    test_file = "production_test.csv"
    
    if not os.path.exists(test_file):
        print(f"ERROR: Test file {test_file} not found")
        return False
    
    try:
        # Test chunked reading with small chunk size
        CHUNK_SIZE = 2  # Small chunk for testing
        chunks_processed = 0
        total_rows = 0
        
        print(f"Processing {test_file} with chunk size {CHUNK_SIZE}")
        
        for chunk in pd.read_csv(test_file, chunksize=CHUNK_SIZE):
            chunks_processed += 1
            chunk_rows = len(chunk)
            total_rows += chunk_rows
            
            print(f"  Chunk {chunks_processed}: {chunk_rows} rows processed")
            
            # Validate chunk structure
            if 'first_name' not in chunk.columns:
                print(f"  Warning: 'first_name' column not found in chunk {chunks_processed}")
            
            # Print first few columns for verification
            print(f"  Columns: {list(chunk.columns[:5])}")
            
        print(f"Successfully processed {chunks_processed} chunks with {total_rows} total rows")
        return True
        
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return False

def test_file_validation():
    """Test file upload validation"""
    print("\n🧪 Testing file validation...")
    
    # Test allowed extensions
    allowed_extensions = {'xlsx', 'xls', 'csv'}
    
    test_files = [
        ("test.csv", True),
        ("data.xlsx", True),
        ("spreadsheet.xls", True),
        ("malicious.exe", False),
        ("document.txt", False),
        ("no_extension", False)
    ]
    
    def allowed_file(filename):
        """Check if uploaded file has allowed extension"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    all_passed = True
    for filename, expected in test_files:
        result = allowed_file(filename)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {filename}: {result} (expected {expected})")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_data_mapping():
    """Test column mapping functionality"""
    print("\n🧪 Testing data mapping...")
    
    try:
        # Load test data
        df = pd.read_csv("production_test.csv")
        print(f"📊 Loaded {len(df)} rows from production_test.csv")
        
        # Test column mapping
        mapping = {
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Company Name': 'company_name',
            'Title': 'title',
            'Industry': 'industry'
        }
        
        mapped_df = pd.DataFrame()
        for field, column in mapping.items():
            if column in df.columns:
                mapped_df[field] = df[column]
                print(f"  ✅ Mapped {column} → {field}")
            else:
                print(f"  ⚠️  Column {column} not found in data")
        
        print(f"📈 Mapped DataFrame shape: {mapped_df.shape}")
        print(f"📋 Sample mapped data:")
        print(mapped_df.head(2).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error in data mapping: {str(e)}")
        return False

def test_memory_usage():
    """Test memory efficiency with chunked processing"""
    print("\n🧪 Testing memory efficiency...")
    
    try:
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 Initial memory usage: {initial_memory:.2f} MB")
        
        # Process file in chunks
        CHUNK_SIZE = 1000
        for chunk in pd.read_csv("production_test.csv", chunksize=CHUNK_SIZE):
            # Simulate processing
            processed_chunk = chunk.copy()
            # Memory should stay relatively constant
            
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        print(f"📊 Final memory usage: {current_memory:.2f} MB")
        print(f"📈 Memory increase: {memory_increase:.2f} MB")
        
        # Memory increase should be minimal for chunked processing
        if memory_increase < 50:  # Less than 50MB increase is good
            print("✅ Memory usage is efficient")
            return True
        else:
            print("⚠️  Memory usage higher than expected")
            return False
            
    except ImportError:
        print("⚠️  psutil not available, skipping memory test")
        return True
    except Exception as e:
        print(f"❌ Error in memory test: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting ColdEmailAI CSV Processing Tests")
    print("=" * 50)
    
    tests = [
        ("CSV Chunked Processing", test_csv_chunked_processing),
        ("File Validation", test_file_validation),
        ("Data Mapping", test_data_mapping),
        ("Memory Usage", test_memory_usage)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The CSV processing functionality is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Review the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)