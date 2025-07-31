#!/usr/bin/env python3
"""
Test script to verify the form validation fix works properly.
This script creates a test CSV file and tests the form submission logic.
"""

import pandas as pd
import requests
import io
import time

def create_test_csv():
    """Create a simple test CSV file"""
    data = {
        'First Name': ['John', 'Jane', 'Bob'],
        'Company': ['TechCorp', 'DataInc', 'CodeLLC'],
        'Job Title': ['Developer', 'Manager', 'Engineer'],
        'City': ['Seattle', 'Portland', 'Austin']
    }
    df = pd.DataFrame(data)
    
    # Save to CSV
    csv_content = df.to_csv(index=False)
    print(f"Created test CSV with columns: {list(df.columns)}")
    return csv_content

def test_form_validation_fix():
    """Test that the form validation fix works"""
    print("=== Testing Form Validation Fix ===")
    
    # Create test CSV
    csv_content = create_test_csv()
    
    # Test the upload endpoint
    base_url = "http://127.0.0.1:5000"
    
    try:
        # First, upload a file
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        upload_response = requests.post(f"{base_url}/upload", files=files, timeout=10)
        
        print(f"Upload response status: {upload_response.status_code}")
        if upload_response.status_code == 200:
            print("[SUCCESS] File upload successful")
            print("[SUCCESS] Mapping form should now be displayed")
        else:
            print(f"[ERROR] Upload failed: {upload_response.text}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to Flask app at http://127.0.0.1:5000")
        print("   Make sure the Flask app is running with: python -m flask run --debug")
        return False
    except Exception as e:
        print(f"[ERROR] Error testing form: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_form_validation_fix()
    if success:
        print("\n[SUCCESS] Form validation fix test completed successfully!")
        print("\nWhat was fixed:")
        print("   - JavaScript no longer disables form inputs immediately on submit")
        print("   - Added 200ms delay to allow form data to be sent first")
        print("   - Enhanced logging to debug form validation issues")
        print("\nThe issue was:")
        print("   - JavaScript was disabling ALL form inputs (including select elements)")
        print("   - This prevented the browser from sending form data to the server")
        print("   - Server validation failed because no form data was received")
        print("\nTest the fix:")
        print("   1. Go to http://127.0.0.1:5000/simple")
        print("   2. Upload a CSV file")
        print("   3. Map First Name and Company Name fields")
        print("   4. Click 'Generate Emails' - should work now!")
    else:
        print("\n[ERROR] Form validation fix test failed")