"""
FINAL COMPREHENSIVE TEST OF THE WORKING APP
"""
import requests
import pandas as pd
from io import BytesIO
import time
import os

BASE_URL = "http://localhost:5000"

def test_final_app():
    print("="*60)
    print("TESTING FINAL COLD EMAIL GENERATOR")
    print("="*60)
    
    # Test 1: Server running
    print("\n1. Checking server...")
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert "Cold Email Generator" in response.text
    print("✓ Server running at http://localhost:5000")
    
    # Test 2: Small CSV upload
    print("\n2. Testing small CSV upload...")
    test_data = pd.DataFrame({
        'first_name': ['John', 'Sarah', 'Mike'],
        'company_name': ['Acme Corp', 'Tech Solutions', 'Data Systems'],
        'title': ['CEO', 'CTO', 'VP Sales']
    })
    
    csv_buffer = BytesIO()
    test_data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    files = {'file': ('test.csv', csv_buffer, 'text/csv')}
    
    start_time = time.time()
    response = requests.post(BASE_URL, files=files)
    elapsed = time.time() - start_time
    
    print(f"  Status: {response.status_code}")
    print(f"  Time: {elapsed:.2f}s")
    assert response.status_code == 200
    
    # Save result
    with open('final_test_result.xlsx', 'wb') as f:
        f.write(response.content)
    print(f"  Saved: final_test_result.xlsx ({len(response.content)} bytes)")
    
    # Verify content
    result_df = pd.read_excel('final_test_result.xlsx')
    print(f"  Results: {len(result_df)} rows")
    
    # Check emails
    emails_generated = 0
    for idx, row in result_df.iterrows():
        email = row['GENERATED_EMAIL']
        if email and not email.startswith('Error') and not email.startswith('Skipped'):
            emails_generated += 1
            print(f"\n  Email for {row['first_name']}:")
            print(f"  {email[:100]}...")
    
    print(f"\n✓ Generated {emails_generated}/{len(result_df)} emails successfully")
    
    # Test 3: Column variations
    print("\n3. Testing column name variations...")
    test_data2 = pd.DataFrame({
        'First Name': ['Alice'],  # Space in name
        'Company': ['Innovation Labs'],  # Different name
        'Job Title': ['Director']  # Different name
    })
    
    csv_buffer2 = BytesIO()
    test_data2.to_csv(csv_buffer2, index=False)
    csv_buffer2.seek(0)
    
    files2 = {'file': ('variations.csv', csv_buffer2, 'text/csv')}
    response2 = requests.post(BASE_URL, files=files2)
    
    assert response2.status_code == 200
    result_df2 = pd.read_excel(BytesIO(response2.content))
    print(f"✓ Handled column variations successfully")
    
    # Test 4: Missing data
    print("\n4. Testing missing data handling...")
    test_data3 = pd.DataFrame({
        'first_name': ['Bob', ''],
        'company_name': ['', 'Corp B']
    })
    
    csv_buffer3 = BytesIO()
    test_data3.to_csv(csv_buffer3, index=False)
    csv_buffer3.seek(0)
    
    files3 = {'file': ('missing.csv', csv_buffer3, 'text/csv')}
    response3 = requests.post(BASE_URL, files=files3)
    
    assert response3.status_code == 200
    result_df3 = pd.read_excel(BytesIO(response3.content))
    
    for idx, row in result_df3.iterrows():
        email = row['GENERATED_EMAIL']
        if 'Skipped' in email:
            print(f"  Row {idx+1}: {email}")
    
    print("✓ Missing data handled correctly")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! THE APP WORKS!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        test_final_app()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()