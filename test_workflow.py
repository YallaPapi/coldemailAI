#!/usr/bin/env python3
"""
Test the complete ColdEmailAI workflow end-to-end
"""
import os
import sys
import requests
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

# Make sure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

BASE_URL = "http://127.0.0.1:5000"

def test_upload_and_mapping():
    """Test file upload and column mapping"""
    print("[TEST] Testing CSV upload and mapping...")
    
    # Read test CSV
    with open('test_upload.csv', 'rb') as f:
        files = {'file': ('test_upload.csv', f, 'text/csv')}
        
        # Upload file
        response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            print("[PASS] File upload successful!")
            print(f"   - Response length: {len(response.text)} bytes")
            print(f"   - Contains mapping form: {'map_first_name' in response.text}")
            return True
        else:
            print(f"[FAIL] Upload failed with status {response.status_code}")
            return False

def test_direct_email_generation():
    """Test email generation directly using the email generator"""
    print("\n[TEST] Testing direct email generation...")
    
    try:
        # Import and test email generator directly  
        from email_generator import EmailGenerator
        
        # Create test data
        test_data = pd.DataFrame([
            {
                'first_name': 'John',
                'company_name': 'TestCorp', 
                'job_title': 'CEO',
                'industry': 'Technology',
                'city': 'Las Vegas',
                'state': 'Nevada'
            }
        ])
        
        # Test email generation
        email_gen = EmailGenerator()
        result = email_gen.process_leads_with_mapping(test_data, {
            'first_name': 'first_name',
            'company_name': 'company_name',
            'job_title': 'job_title',
            'industry': 'industry', 
            'city': 'city',
            'state': 'state'
        })
        
        if len(result) > 0 and 'Personalized' in result.columns:
            print("[PASS] Email generation successful!")
            print(f"   - Generated {len(result)} emails")
            print(f"   - Sample email preview: {str(result['Personalized'].iloc[0])[:100]}...")
            return True
        else:
            print("[FAIL] Email generation failed - no emails generated")
            return False
            
    except Exception as e:
        print(f"[FAIL] Email generation failed with error: {e}")
        return False

def test_api_availability():
    """Test if the Flask API is running"""
    print("[TEST] Testing API availability...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[PASS] API is running and healthy!")
            return True
        else:
            print(f"[FAIL] API health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Cannot connect to API: {e}")
        return False

def main():
    """Run all tests"""
    print("ColdEmailAI End-to-End Testing")
    print("=" * 50)
    
    tests = [
        test_api_availability,
        test_upload_and_mapping,
        test_direct_email_generation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   Passed: {passed}/{total} tests")
    
    if passed == total:
        print("ALL TESTS PASSED! Application is working correctly.")
        return 0
    else:
        print("Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())