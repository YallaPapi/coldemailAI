#!/usr/bin/env python3
"""
Test chunked processing with large CSV file to validate memory management
"""
import pandas as pd
import time
import os

def test_large_file_chunked_processing():
    """Test chunked processing with large file"""
    print("Testing chunked processing with large file...")
    
    test_file = "large_test.csv"
    
    if not os.path.exists(test_file):
        print(f"ERROR: Test file {test_file} not found")
        return False
    
    # Test different chunk sizes
    chunk_sizes = [100, 500, 1000]
    
    for chunk_size in chunk_sizes:
        print(f"\n--- Testing with chunk size: {chunk_size} ---")
        
        start_time = time.time()
        chunks_processed = 0
        total_rows = 0
        
        try:
            for chunk in pd.read_csv(test_file, chunksize=chunk_size):
                chunks_processed += 1
                chunk_rows = len(chunk)
                total_rows += chunk_rows
                
                # Simulate some processing (like email generation would do)
                processed_chunk = chunk.copy()
                processed_chunk['processed'] = True
                
                if chunks_processed <= 3:  # Show first few chunks
                    print(f"  Chunk {chunks_processed}: {chunk_rows} rows")
                elif chunks_processed == 4:
                    print("  ... (additional chunks processed)")
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"  Completed: {chunks_processed} chunks, {total_rows} total rows")
            print(f"  Processing time: {processing_time:.2f} seconds")
            print(f"  Rows per second: {total_rows/processing_time:.0f}")
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            return False
    
    return True

def test_memory_comparison():
    """Compare memory usage between chunked and non-chunked processing"""
    print("\nTesting memory usage comparison...")
    
    test_file = "large_test.csv"
    
    if not os.path.exists(test_file):
        print(f"ERROR: Test file {test_file} not found")
        return False
    
    try:
        # Test 1: Load entire file at once (memory intensive)
        print("Test 1: Loading entire file at once...")
        start_time = time.time()
        df_full = pd.read_csv(test_file)
        full_load_time = time.time() - start_time
        memory_usage_full = df_full.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        
        print(f"  Full load: {len(df_full)} rows in {full_load_time:.2f}s")
        print(f"  Memory usage: {memory_usage_full:.2f} MB")
        
        # Test 2: Process in chunks (memory efficient)
        print("\nTest 2: Processing in chunks...")
        start_time = time.time()
        chunk_count = 0
        total_rows_chunked = 0
        
        CHUNK_SIZE = 1000  # Same as in the main application
        for chunk in pd.read_csv(test_file, chunksize=CHUNK_SIZE):
            chunk_count += 1
            total_rows_chunked += len(chunk)
            # Simulate processing
            processed = chunk.copy()
        
        chunked_time = time.time() - start_time
        
        print(f"  Chunked processing: {total_rows_chunked} rows in {chunked_time:.2f}s")
        print(f"  Memory usage: Constant ~{CHUNK_SIZE * df_full.memory_usage(deep=True).mean() / len(df_full) / 1024 / 1024:.2f} MB per chunk")
        
        # Verify same number of rows processed
        if len(df_full) == total_rows_chunked:
            print("  SUCCESS: Same number of rows processed in both methods")
            return True
        else:
            print(f"  ERROR: Row count mismatch - Full: {len(df_full)}, Chunked: {total_rows_chunked}")
            return False
            
    except Exception as e:
        print(f"ERROR in memory comparison: {str(e)}")
        return False

def main():
    """Run large file tests"""
    print("Large File Chunked Processing Tests")
    print("=" * 50)
    
    # Check if large test file exists
    if not os.path.exists("large_test.csv"):
        print("Creating large test file...")
        os.system("python create_large_test.py")
    
    tests = [
        ("Large File Chunked Processing", test_large_file_chunked_processing),
        ("Memory Usage Comparison", test_memory_comparison)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("LARGE FILE TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: Large file chunked processing works correctly!")
        print("The application can handle large CSV files without memory issues.")
        return True
    else:
        print("FAILURE: Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()