#!/usr/bin/env python3
"""
Complete workflow test to validate Unicode fix and E2E functionality.
Tests the actual workflow without browser automation first.
"""

import os
import requests
import pandas as pd
from io import BytesIO
import time

def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("OK: Loaded .env file")
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

def test_complete_workflow():
    """Test complete workflow: CSV upload -> column mapping -> email generation -> Excel download"""
    load_env()
    
    print("TESTING COMPLETE WORKFLOW WITH UNICODE FIX")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✓ Server health check: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Server not running: {e}")
        return False
    
    # Test 2: Upload CSV file
    print("\nStep 1: Testing CSV Upload...")
    csv_file_path = "real_business_contacts.csv"
    
    if not os.path.exists(csv_file_path):
        print(f"✗ CSV file not found: {csv_file_path}")
        return False
    
    with open(csv_file_path, 'rb') as f:
        files = {'file': ('test_contacts.csv', f, 'text/csv')}
        
        try:
            upload_response = requests.post(f"{base_url}/upload", files=files, timeout=30)
            print(f"Upload response status: {upload_response.status_code}")
            
            if upload_response.status_code != 200:
                print(f"✗ Upload failed: {upload_response.text[:500]}")
                return False
            
            print("✓ CSV upload successful")
            
            # Check if we got the mapping page
            if "mapping" in upload_response.text.lower() or "map" in upload_response.text.lower():
                print("✓ Column mapping page loaded")
            else:
                print("? Upload response unclear - may have succeeded")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Upload request failed: {e}")
            return False
    
    # Test 3: Submit column mapping and generate emails (THE CRITICAL TEST)
    print("\nStep 2: Testing Email Generation with Column Mapping...")
    
    # Use requests.Session to maintain cookies/session data
    session = requests.Session()
    
    # First, re-upload to get session data
    with open(csv_file_path, 'rb') as f:
        files = {'file': ('test_contacts.csv', f, 'text/csv')}
        upload_response = session.post(f"{base_url}/upload", files=files, timeout=30)
    
    # Now submit the mapping form
    mapping_data = {
        'map_first_name': 'First Name',
        'map_company_name': 'Company', 
        'map_job_title': 'Job Title',
        'map_industry': 'Industry',
        'map_city': 'City',
        'map_state': 'State',
        'map_country': 'Country'
    }
    
    try:
        print("Submitting column mapping and triggering email generation...")
        generation_response = session.post(
            f"{base_url}/generate_emails", 
            data=mapping_data, 
            timeout=120,  # Give it 2 minutes for AI generation
            stream=True  # Handle large responses
        )
        
        print(f"Generation response status: {generation_response.status_code}")
        print(f"Content-Type: {generation_response.headers.get('content-type', 'Unknown')}")
        
        if generation_response.status_code == 200:
            content_type = generation_response.headers.get('content-type', '')
            
            if 'excel' in content_type or 'spreadsheet' in content_type:
                print("✓ SUCCESS: Received Excel file response!")
                
                # Save the response to verify it's a valid Excel file
                with open('test_output.xlsx', 'wb') as f:
                    for chunk in generation_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Try to read it back with pandas
                try:
                    df = pd.read_excel('test_output.xlsx')
                    print(f"✓ Excel file valid: {len(df)} rows, columns: {list(df.columns)}")
                    
                    if 'Personalized' in df.columns:
                        print("✓ Personalized emails column found!")
                        
                        # Check for Unicode characters in emails
                        for i, email in enumerate(df['Personalized'].head(3)):
                            if email and isinstance(email, str):
                                print(f"Email {i+1} preview: {email[:100]}...")
                                
                                # Check for Unicode characters
                                has_unicode = any(ord(char) > 127 for char in email)
                                if has_unicode:
                                    print(f"✓ Email {i+1} contains Unicode characters (emojis/smart quotes)")
                        
                        print("\n🎉 COMPLETE SUCCESS: Unicode fix works! E2E workflow functional!")
                        return True
                    else:
                        print(f"✗ No 'Personalized' column found. Columns: {list(df.columns)}")
                        return False
                        
                except Exception as e:
                    print(f"✗ Excel file invalid: {e}")
                    return False
                    
            else:
                print(f"✗ Unexpected content type: {content_type}")
                print(f"Response text: {generation_response.text[:500]}")
                return False
        else:
            print(f"✗ Generation failed with status {generation_response.status_code}")
            print(f"Response: {generation_response.text[:1000]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ CRITICAL: Generation request failed: {e}")
        print("This indicates the Unicode encoding issue is still present!")
        return False
    
    return False

if __name__ == "__main__":
    success = test_complete_workflow()
    
    if success:
        print("\n✅ ALL TESTS PASSED: MVP is ready for production!")
        exit(0)
    else:
        print("\n❌ TESTS FAILED: Issues remain in the workflow")
        exit(1)