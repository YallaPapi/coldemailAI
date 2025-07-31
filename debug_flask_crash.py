#!/usr/bin/env python3
"""
Debug Flask server crash during email generation
"""

import requests
import pandas as pd
import time
import io

def create_minimal_test_csv():
    """Create the smallest possible test CSV"""
    data = {
        'first_name': ['John'],
        'company_name': ['TestCorp'],
        'title': ['CEO'],
        'industry': ['Technology'],
        'city': ['Las Vegas'],
        'state': ['Nevada']
    }
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

def test_step_by_step():
    """Test each step individually to isolate the crash"""
    print("=== Step-by-Step Flask Server Crash Debug ===")
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5000"
    
    # Step 1: Health check
    print("Step 1: Health check...")
    try:
        response = session.get(f"{base_url}/health", timeout=5)
        print(f"  Health: {response.status_code} - OK")
    except Exception as e:
        print(f"  Health check failed: {e}")
        return False
    
    # Step 2: Upload minimal CSV
    print("Step 2: Upload minimal CSV...")
    try:
        csv_content = create_minimal_test_csv()
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        upload_response = session.post(f"{base_url}/upload", files=files, timeout=30)
        print(f"  Upload: {upload_response.status_code}")
        
        if upload_response.status_code != 200:
            print(f"  Upload failed: {upload_response.text[:500]}")
            return False
            
        print("  Upload successful - mapping form should be ready")
        
    except Exception as e:
        print(f"  Upload failed with exception: {e}")
        return False
    
    # Step 3: Test server health after upload
    print("Step 3: Health check after upload...")
    try:
        response = session.get(f"{base_url}/health", timeout=5)
        print(f"  Health after upload: {response.status_code} - OK")
    except Exception as e:
        print(f"  Health check after upload failed: {e}")
        return False
    
    # Step 4: Submit email generation with minimal timeout
    print("Step 4: Submit email generation (with short timeout to catch crash)...")
    try:
        form_data = {
            'map_first_name': 'first_name',
            'map_company_name': 'company_name',
            'map_job_title': 'title',
            'map_industry': 'industry',
            'map_city': 'city',  
            'map_state': 'state'
        }
        
        print("  Submitting form data...")
        start_time = time.time()
        
        # Use short timeout to quickly detect crashes
        generate_response = session.post(f"{base_url}/generate_emails", 
                                       data=form_data, 
                                       timeout=15)
        
        end_time = time.time()
        print(f"  Generation response: {generate_response.status_code}")
        print(f"  Processing time: {end_time - start_time:.2f} seconds")
        print(f"  Content type: {generate_response.headers.get('content-type', 'unknown')}")
        
        if generate_response.status_code == 200:
            print("  [SUCCESS] Email generation completed without crash!")
            return True
        else:
            print(f"  [FAIL] Email generation failed: {generate_response.status_code}")
            print(f"  Response text: {generate_response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("  [TIMEOUT] Request timed out - server may be processing")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  [CONNECTION ERROR] Server crashed during processing: {e}")
        return False
    except Exception as e:
        print(f"  [EXCEPTION] Unexpected error: {e}")
        return False
    
    # Step 5: Final health check
    print("Step 5: Final health check...")
    try:
        response = session.get(f"{base_url}/health", timeout=5)
        print(f"  Final health: {response.status_code} - OK")
        return True
    except Exception as e:
        print(f"  Final health check failed - server crashed: {e}")
        return False

def main():
    """Main debug function"""
    print("Flask Server Crash Debug")
    print("=" * 40)
    
    success = test_step_by_step()
    
    print("\n" + "=" * 40)
    if success:
        print("[SUCCESS] No server crash detected!")
    else:
        print("[FAIL] Server crash or error detected!")
        print("\nTroubleshooting suggestions:")
        print("1. Check Flask server logs for error details")
        print("2. Verify OpenAI API key is working")
        print("3. Check memory usage during processing")
        print("4. Review session management in Flask app")
    
    return success

if __name__ == "__main__":
    main()