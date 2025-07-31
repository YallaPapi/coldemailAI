#!/usr/bin/env python3
"""
Debug scale issues with full dataset
"""

import requests
import pandas as pd
import time

def test_full_dataset():
    """Test with the full authentic business leads dataset"""
    print("=== Testing Full Dataset (10 leads) ===")
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5000"
    
    # Load full dataset
    try:
        with open('test_data/email_generation_tests/authentic_business_leads.csv', 'rb') as f:
            csv_content = f.read()
        
        # Check dataset size
        df = pd.read_csv('test_data/email_generation_tests/authentic_business_leads.csv')
        print(f"Dataset: {len(df)} leads, {len(csv_content)} bytes")
        
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return False
    
    # Step 1: Upload full dataset
    print("Step 1: Uploading full dataset...")
    try:
        files = {'file': ('authentic_business_leads.csv', csv_content, 'text/csv')}
        upload_response = session.post(f"{base_url}/upload", files=files, timeout=30)
        
        print(f"  Upload: {upload_response.status_code}")
        if upload_response.status_code != 200:
            print(f"  Upload failed: {upload_response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"  Upload failed: {e}")
        return False
    
    # Step 2: Submit email generation with longer timeout
    print("Step 2: Generating emails for all leads...")
    try:
        form_data = {
            'map_first_name': 'first_name',
            'map_company_name': 'company_name',
            'map_job_title': 'title',
            'map_industry': 'industry',
            'map_city': 'city',  
            'map_state': 'state',
            'map_country': 'country'
        }
        
        print("  Starting email generation...")
        start_time = time.time()
        
        # Use much longer timeout for 10 leads (each lead takes ~3-5 seconds)
        generate_response = session.post(f"{base_url}/generate_emails", 
                                       data=form_data, 
                                       timeout=120)  # 2 minute timeout
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"  Generation response: {generate_response.status_code}")
        print(f"  Processing time: {processing_time:.2f} seconds")
        print(f"  Average per lead: {processing_time/10:.2f} seconds")
        print(f"  Content type: {generate_response.headers.get('content-type', 'unknown')}")
        
        if generate_response.status_code == 200:
            # Save and analyze results
            with open('full_dataset_test_output.xlsx', 'wb') as f:
                f.write(generate_response.content)
                
            print("  [SUCCESS] Full dataset processing completed!")
            print("  Results saved to: full_dataset_test_output.xlsx")
            
            # Quick analysis
            result_df = pd.read_excel('full_dataset_test_output.xlsx')
            personalized_count = result_df['Personalized'].notna().sum()
            print(f"  Generated: {personalized_count}/{len(result_df)} personalized emails")
            
            return True
        else:
            print(f"  [FAIL] Email generation failed: {generate_response.status_code}")
            print(f"  Response: {generate_response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  [TIMEOUT] Processing timed out after 2 minutes")
        print(f"  This may indicate the server is still processing or crashed")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  [CONNECTION ERROR] Server connection lost: {e}")
        return False
    except Exception as e:
        print(f"  [EXCEPTION] Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("Scale Issue Debug Test")
    print("=" * 40)
    
    success = test_full_dataset()
    
    print("\n" + "=" * 40)
    if success:
        print("[SUCCESS] Full dataset processing worked!")
        print("The original timeout may have been too short.")
    else:
        print("[FAIL] Scale issue detected!")
        print("\nPossible causes:")
        print("1. OpenAI API rate limiting")
        print("2. Memory issues with larger datasets") 
        print("3. Session timeout in Flask")
        print("4. Network timeout issues")
    
    return success

if __name__ == "__main__":
    main()