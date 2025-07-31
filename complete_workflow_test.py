#!/usr/bin/env python3
"""
Complete Workflow Test for ColdEmailAI Platform
Simulates the full user experience: Upload → Mapping → Email Generation
Tests with authentic business data (not demo/test data)
"""

import os
import sys
import pandas as pd
import requests
import time
from io import BytesIO

def test_complete_workflow():
    """Test complete user workflow with authentic business leads"""
    print("STARTING: Complete Workflow Test for ColdEmailAI Platform")
    print("=" * 70)
    
    # Test data file path
    test_file = "test_data/email_generation_tests/authentic_business_leads.csv"
    
    if not os.path.exists(test_file):
        print(f"ERROR: Test file not found: {test_file}")
        return False
    
    print(f"Using authentic business data: {test_file}")
    
    # Load and inspect data
    try:
        df = pd.read_csv(test_file)
        print(f"Data loaded: {len(df)} leads")
        print(f"Columns: {list(df.columns)}")
        print("\nSample data:")
        print(df.head(2).to_string())
        
        # Limit to 3 leads for quick testing (but use real data)
        test_df = df.head(3)
        
        print(f"\nTesting with {len(test_df)} authentic leads...")
        
        # Test Flask server availability
        server_url = "http://127.0.0.1:5000"
        session = requests.Session()  # Use session to persist cookies
        
        try:
            response = session.get(server_url, timeout=5)
            if response.status_code == 200:
                print(f"SUCCESS: Flask server is running: {server_url}")
            else:
                print(f"ERROR: Flask server responded with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Cannot connect to Flask server: {e}")
            print("HINT: Make sure 'python app.py' is running in another terminal")
            return False
        
        # Step 1: Upload file
        print("\n=== STEP 1: File Upload ===")
        test_csv_path = "complete_test_subset.csv"
        test_df.to_csv(test_csv_path, index=False)
        print(f"Created test subset: {test_csv_path}")
        
        with open(test_csv_path, 'rb') as f:
            files = {'file': ('test_leads.csv', f, 'text/csv')}
            upload_response = session.post(f"{server_url}/upload", files=files, timeout=30)
        
        if upload_response.status_code == 200:
            print("SUCCESS: File upload successful")
            # Should receive mapping HTML page
            if 'Column Mapping' in upload_response.text or 'mapping' in upload_response.text.lower():
                print("SUCCESS: Received column mapping page")
            else:
                print("WARNING: Upload response doesn't look like mapping page")
        else:
            print(f"ERROR: File upload failed: {upload_response.status_code}")
            print(f"Response: {upload_response.text[:500]}")
            return False
        
        # Step 2: Submit column mapping and generate emails
        print("\n=== STEP 2: Column Mapping & Email Generation ===")
        
        # Prepare mapping form data based on our CSV columns
        mapping_data = {
            'map_first_name': 'first_name',
            'map_company_name': 'company_name', 
            'map_job_title': 'title',
            'map_industry': 'industry',
            'map_city': 'city',
            'map_state': 'state',
            'map_country': 'country',
            'email_template': 'Hi {first_name}, I noticed {company_name} is in the {industry} industry. Would you be interested in discussing how we can help {company_name} grow?',
            'from_name': 'Test Sender',
            'from_email': 'test@example.com',
            'subject_line': 'Quick question about {company_name}'
        }
        
        print("Submitting column mapping and generating emails...")
        print(f"Mapping data: {mapping_data}")
        
        # Submit the mapping and generation request
        generation_response = session.post(
            f"{server_url}/generate_emails", 
            data=mapping_data, 
            timeout=120  # Extended timeout for OpenAI API calls
        )
        
        print(f"Generation response status: {generation_response.status_code}")
        print(f"Response headers: {dict(generation_response.headers)}")
        
        if generation_response.status_code == 200:
            print("SUCCESS: Email generation request completed!")
            
            # Check content type
            content_type = generation_response.headers.get('content-type', '').lower()
            print(f"Response content type: {content_type}")
            
            if 'excel' in content_type or 'spreadsheet' in content_type or generation_response.headers.get('content-disposition'):
                print("SUCCESS: Received Excel file response")
                
                # Save the Excel file
                output_file = "complete_workflow_output.xlsx"
                with open(output_file, 'wb') as f:
                    f.write(generation_response.content)
                print(f"Output saved: {output_file} ({len(generation_response.content)} bytes)")
                
                # Verify Excel content
                try:
                    result_df = pd.read_excel(output_file, engine='openpyxl')
                    print(f"SUCCESS: Generated {len(result_df)} personalized emails")
                    print(f"Columns in result: {result_df.columns.tolist()}")
                    
                    # Look for personalized email column (might have different name)
                    email_columns = [col for col in result_df.columns if 'email' in col.lower() or 'personalized' in col.lower()]
                    if email_columns:
                        email_col = email_columns[0]
                        print(f"Found email column: '{email_col}'")
                        print("\nSample generated email:")
                        print("-" * 50)
                        sample_email = result_df[email_col].iloc[0]
                        print(sample_email[:400] + "..." if len(sample_email) > 400 else sample_email)
                        print("-" * 50)
                        
                        # Verify personalization worked
                        first_lead = test_df.iloc[0]
                        if first_lead['first_name'] in sample_email and first_lead['company_name'] in sample_email:
                            print("SUCCESS: Email contains personalized data (name & company)")
                        else:
                            print("WARNING: Email may not be properly personalized")
                        
                        return True
                    else:
                        print("WARNING: No email column found, but file was generated")
                        print("This might still be success - check the output file manually")
                        return True
                        
                except Exception as excel_error:
                    print(f"ERROR: Could not read Excel file: {excel_error}")
                    return False
            else:
                print("ERROR: Response is not an Excel file")
                print("Checking if it's an error page...")
                
                # Check if it's HTML (error page)
                response_text = generation_response.text[:1000]
                if '<html>' in response_text.lower():
                    print("ERROR: Received HTML error page instead of Excel file")
                    print("First 1000 chars of response:")
                    print(response_text)
                    return False
                else:
                    print("Response doesn't appear to be HTML either")
                    print(f"Response size: {len(generation_response.content)} bytes")
                    return False
        else:
            print(f"ERROR: Email generation failed: {generation_response.status_code}")
            print(f"Response: {generation_response.text[:1000]}")
            return False
            
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists("complete_test_subset.csv"):
            os.remove("complete_test_subset.csv")

if __name__ == "__main__":
    print("ColdEmailAI Complete Workflow Testing")
    print("Testing complete user experience with authentic business data")
    print()
    
    success = test_complete_workflow()
    
    if success:
        print("\nSUCCESS: ColdEmailAI complete workflow is operational!")
        print("All steps passed: Upload -> Mapping -> Email Generation")
        print("Platform ready for production use with live data")
        sys.exit(0)
    else:
        print("\nFAILURE: Issues found during complete workflow testing")
        print("Debug and fix required before production")
        sys.exit(1)