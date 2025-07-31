#!/usr/bin/env python3
"""
Test email generation with a small subset of real business data
"""

import os
import pandas as pd
import requests
import time

def test_email_generation_small():
    """Test email generation with just 2-3 leads"""
    print("=== Testing Email Generation with Small Dataset ===")
    
    # Create a small test dataset from the real business data
    test_data = {
        'first_name': ['Sarah', 'Michael'],
        'company_name': ['TechFlow Solutions', 'Global Manufacturing Inc'],
        'title': ['Marketing Director', 'VP of Operations'],
        'industry': ['Technology', 'Manufacturing'],
        'city': ['San Francisco', 'Detroit'],
        'state': ['CA', 'MI'],
        'country': ['United States', 'United States']
    }
    
    df = pd.DataFrame(test_data)
    csv_content = df.to_csv(index=False)
    
    # Test the full workflow
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    try:
        # Upload file
        files = {'file': ('small_test.csv', csv_content, 'text/csv')}
        upload_response = session.post(f"{base_url}/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"[FAIL] Upload failed: {upload_response.status_code}")
            return False
        
        print("[PASS] File uploaded successfully")
        
        # Generate emails with proper mapping
        form_data = {
            'map_first_name': 'first_name',
            'map_company_name': 'company_name',
            'map_job_title': 'title',
            'map_industry': 'industry',
            'map_city': 'city',
            'map_state': 'state',
            'map_country': 'country'
        }
        
        print("Submitting email generation request...")
        start_time = time.time()
        
        generate_response = session.post(f"{base_url}/generate_emails", data=form_data, timeout=120)
        
        end_time = time.time()
        print(f"Request completed in {end_time - start_time:.2f} seconds")
        
        if generate_response.status_code == 200:
            # Check if we got an Excel file
            content_type = generate_response.headers.get('content-type', '')
            if 'spreadsheet' in content_type or 'excel' in content_type:
                print("[PASS] Successfully generated emails and received Excel file")
                
                # Save and analyze the file
                with open('test_small_generation.xlsx', 'wb') as f:
                    f.write(generate_response.content)
                
                # Read and analyze the results
                result_df = pd.read_excel('test_small_generation.xlsx')
                print(f"[INFO] Generated file contains {len(result_df)} rows")
                
                if 'Personalized' in result_df.columns:
                    personalized_count = result_df['Personalized'].notna().sum()
                    print(f"[INFO] {personalized_count} personalized emails generated")
                    
                    # Show sample emails
                    for i, email in enumerate(result_df['Personalized'].dropna()):
                        print(f"\n--- Sample Email {i+1} ---")
                        print(email[:200] + "..." if len(email) > 200 else email)
                    
                    return True
                else:
                    print("[FAIL] No 'Personalized' column found in output")
                    return False
            else:
                print(f"[FAIL] Unexpected content type: {content_type}")
                print(f"Response text: {generate_response.text[:500]}")
                return False
        else:
            print(f"[FAIL] Email generation failed: {generate_response.status_code}")
            print(f"Response text: {generate_response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("[FAIL] Request timed out")
        return False
    except Exception as e:
        print(f"[FAIL] Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_email_generation_small()
    if success:
        print("\n✅ Email generation test PASSED!")
    else:
        print("\n❌ Email generation test FAILED!")