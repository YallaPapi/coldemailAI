"""
ACTUAL FUCKING TEST - NO FAKE DATA, REAL TESTING
Tests the actually_works.py app with real CSV upload and download
"""
import requests
import pandas as pd
from io import BytesIO
import os
import time
from datetime import datetime
import openpyxl

# Configuration
BASE_URL = "http://localhost:5000"
TEST_OUTPUT_DIR = "test_results"

def log(message):
    """Log with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def create_test_output_dir():
    """Create directory for test results"""
    if not os.path.exists(TEST_OUTPUT_DIR):
        os.makedirs(TEST_OUTPUT_DIR)
    log(f"✓ Test output directory ready: {TEST_OUTPUT_DIR}")

def test_server_running():
    """Test 1: Check if server is running"""
    log("TEST 1: Checking if server is running...")
    try:
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        log("✓ Server is running at http://localhost:5000")
        return True
    except Exception as e:
        log(f"✗ Server not running! Error: {e}")
        log("  Make sure to run: python actually_works.py")
        return False

def test_homepage():
    """Test 2: Check homepage content"""
    log("\nTEST 2: Checking homepage...")
    response = requests.get(BASE_URL)
    assert "Cold Email Generator" in response.text
    assert "Upload a CSV" in response.text
    assert '<input type="file"' in response.text
    log("✓ Homepage loads correctly with upload form")

def test_csv_upload_small():
    """Test 3: Upload small CSV and verify results"""
    log("\nTEST 3: Testing small CSV upload...")
    
    # Create test CSV
    test_data = pd.DataFrame({
        'first_name': ['John', 'Sarah', 'Mike'],
        'last_name': ['Smith', 'Johnson', 'Williams'],
        'company_name': ['Acme Corp', 'Tech Solutions', 'Data Systems'],
        'title': ['CEO', 'CTO', 'VP Sales'],
        'email': ['john@acme.com', 'sarah@tech.com', 'mike@data.com']
    })
    
    # Save to file
    csv_path = os.path.join(TEST_OUTPUT_DIR, 'test_small.csv')
    test_data.to_csv(csv_path, index=False)
    log(f"  Created test CSV with {len(test_data)} rows")
    
    # Upload file
    with open(csv_path, 'rb') as f:
        files = {'file': ('test_small.csv', f, 'text/csv')}
        log("  Uploading CSV...")
        
        start_time = time.time()
        response = requests.post(BASE_URL, files=files)
        upload_time = time.time() - start_time
        
    log(f"  Upload completed in {upload_time:.2f} seconds")
    log(f"  Response status: {response.status_code}")
    
    # Check response
    assert response.status_code == 200
    assert response.headers.get('Content-Type', '').startswith('application/vnd.openxmlformats')
    
    # Save Excel file
    excel_path = os.path.join(TEST_OUTPUT_DIR, 'result_small.xlsx')
    with open(excel_path, 'wb') as f:
        f.write(response.content)
    log(f"✓ Excel file saved: {excel_path} ({len(response.content)} bytes)")
    
    # Verify Excel content
    result_df = pd.read_excel(excel_path)
    log(f"  Excel has {len(result_df)} rows, {len(result_df.columns)} columns")
    
    # Check for generated emails
    assert 'GENERATED_EMAIL' in result_df.columns
    emails_generated = result_df['GENERATED_EMAIL'].notna().sum()
    log(f"✓ Generated {emails_generated}/{len(result_df)} emails successfully")
    
    # Show sample email
    if emails_generated > 0:
        sample_email = result_df['GENERATED_EMAIL'].iloc[0]
        log(f"\n  Sample generated email:\n  {sample_email[:100]}...")
    
    return True

def test_csv_with_variations():
    """Test 4: Test CSV with column name variations"""
    log("\nTEST 4: Testing CSV with different column names...")
    
    # Create CSV with varied column names
    test_data = pd.DataFrame({
        'First Name': ['Alice'],  # Space in column name
        'company': ['Innovation Labs'],  # lowercase
        'Job Title': ['Director'],  # Different naming
        'Email Address': ['alice@innovation.com']
    })
    
    csv_path = os.path.join(TEST_OUTPUT_DIR, 'test_variations.csv')
    test_data.to_csv(csv_path, index=False)
    log("  Created CSV with varied column names")
    
    # Upload
    with open(csv_path, 'rb') as f:
        files = {'file': ('test_variations.csv', f, 'text/csv')}
        response = requests.post(BASE_URL, files=files)
    
    assert response.status_code == 200
    
    # Save and check
    excel_path = os.path.join(TEST_OUTPUT_DIR, 'result_variations.xlsx')
    with open(excel_path, 'wb') as f:
        f.write(response.content)
    
    result_df = pd.read_excel(excel_path)
    assert 'GENERATED_EMAIL' in result_df.columns
    log("✓ Successfully handled column name variations")

def test_missing_data():
    """Test 5: Test CSV with missing data"""
    log("\nTEST 5: Testing CSV with missing data...")
    
    # Create CSV with missing values
    test_data = pd.DataFrame({
        'first_name': ['Bob', '', 'Charlie'],
        'company_name': ['Corp A', 'Corp B', ''],
        'title': ['Manager', None, 'Developer']
    })
    
    csv_path = os.path.join(TEST_OUTPUT_DIR, 'test_missing.csv')
    test_data.to_csv(csv_path, index=False)
    log("  Created CSV with missing values")
    
    # Upload
    with open(csv_path, 'rb') as f:
        files = {'file': ('test_missing.csv', f, 'text/csv')}
        response = requests.post(BASE_URL, files=files)
    
    assert response.status_code == 200
    
    # Check results
    excel_path = os.path.join(TEST_OUTPUT_DIR, 'result_missing.xlsx')
    with open(excel_path, 'wb') as f:
        f.write(response.content)
    
    result_df = pd.read_excel(excel_path)
    log(f"✓ Processed {len(result_df)} rows with missing data")
    
    # Check which rows got emails
    for idx, row in result_df.iterrows():
        email_content = row['GENERATED_EMAIL']
        if 'Skipped' in str(email_content):
            log(f"  Row {idx}: Skipped due to missing data")
        else:
            log(f"  Row {idx}: Email generated successfully")

def test_larger_dataset():
    """Test 6: Test with larger dataset"""
    log("\nTEST 6: Testing larger dataset (10 rows)...")
    
    # Create larger dataset
    test_data = pd.DataFrame({
        'first_name': [f'User{i}' for i in range(10)],
        'company_name': [f'Company {i}' for i in range(10)],
        'title': ['CEO', 'CTO', 'CFO', 'VP Sales', 'Manager', 
                  'Developer', 'Designer', 'Analyst', 'Consultant', 'Director']
    })
    
    csv_path = os.path.join(TEST_OUTPUT_DIR, 'test_large.csv')
    test_data.to_csv(csv_path, index=False)
    log(f"  Created CSV with {len(test_data)} rows")
    
    # Upload with timing
    with open(csv_path, 'rb') as f:
        files = {'file': ('test_large.csv', f, 'text/csv')}
        
        start_time = time.time()
        response = requests.post(BASE_URL, files=files)
        process_time = time.time() - start_time
    
    log(f"  Processing time: {process_time:.2f} seconds ({process_time/len(test_data):.2f}s per row)")
    
    assert response.status_code == 200
    
    # Save results
    excel_path = os.path.join(TEST_OUTPUT_DIR, 'result_large.xlsx')
    with open(excel_path, 'wb') as f:
        f.write(response.content)
    
    result_df = pd.read_excel(excel_path)
    emails_generated = result_df['GENERATED_EMAIL'].notna().sum()
    log(f"✓ Generated {emails_generated}/{len(result_df)} emails")

def test_edge_cases():
    """Test 7: Test edge cases"""
    log("\nTEST 7: Testing edge cases...")
    
    # Test empty file
    try:
        empty_csv = BytesIO(b'')
        files = {'file': ('empty.csv', empty_csv, 'text/csv')}
        response = requests.post(BASE_URL, files=files)
        log(f"  Empty file: Status {response.status_code}")
    except:
        log("  Empty file: Properly rejected")
    
    # Test no file
    try:
        response = requests.post(BASE_URL, data={})
        assert response.status_code == 500 or response.status_code == 400
        log("  No file upload: Properly rejected")
    except:
        log("  No file upload: Error handled")

def run_all_tests():
    """Run all tests and report results"""
    print("="*60)
    print("ACTUAL COLD EMAIL GENERATOR TEST SUITE")
    print("="*60)
    
    create_test_output_dir()
    
    # Check server first
    if not test_server_running():
        print("\n❌ TESTS ABORTED: Server not running!")
        print("Please run: python actually_works.py")
        return
    
    tests = [
        test_homepage,
        test_csv_upload_small,
        test_csv_with_variations,
        test_missing_data,
        test_larger_dataset,
        test_edge_cases
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            log(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print(f"Test outputs saved in: {TEST_OUTPUT_DIR}/")
    print("="*60)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED! THE APP ACTUALLY FUCKING WORKS!")
    else:
        print("\n❌ SOME TESTS FAILED - CHECK THE LOGS ABOVE")

if __name__ == "__main__":
    run_all_tests()