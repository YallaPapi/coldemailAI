"""
Fixed test for the ACTUAL running app
"""
import requests
import pandas as pd
from io import BytesIO
import os
import time

BASE_URL = "http://localhost:5000"

print("Testing the ACTUAL running app...")

# Test 1: Check server
response = requests.get(BASE_URL)
print(f"\n1. Server check: {response.status_code}")
field_name = 'csv' if 'name="csv"' in response.text else 'file'
print(f"   Form field name: {field_name}")

# Test 2: Upload small CSV
test_data = pd.DataFrame({
    'first_name': ['John', 'Sarah'],
    'company_name': ['Acme Corp', 'Tech Inc'],
    'title': ['CEO', 'CTO']
})

# Create CSV in memory
csv_buffer = BytesIO()
test_data.to_csv(csv_buffer, index=False)
csv_buffer.seek(0)

# Upload with correct field name
files = {'csv': ('test.csv', csv_buffer, 'text/csv')}  # Using 'csv' as field name

print("\n2. Uploading CSV...")
start = time.time()
response = requests.post(BASE_URL, files=files)
elapsed = time.time() - start

print(f"   Status: {response.status_code}")
print(f"   Time: {elapsed:.2f}s")
print(f"   Content-Type: {response.headers.get('Content-Type', 'None')}")

if response.status_code == 200:
    # Save result
    with open('test_result.xlsx', 'wb') as f:
        f.write(response.content)
    print(f"   Saved: test_result.xlsx ({len(response.content)} bytes)")
    
    # Check content
    result_df = pd.read_excel('test_result.xlsx')
    print(f"   Rows: {len(result_df)}")
    print(f"   Columns: {list(result_df.columns)}")
    
    if 'GENERATED_EMAIL' in result_df.columns:
        print("\n   Sample email:")
        print(f"   {result_df['GENERATED_EMAIL'].iloc[0][:100]}...")
else:
    print(f"   Error: {response.text[:200]}")

# Test 3: Test with missing company
test_data2 = pd.DataFrame({
    'name': ['Bob'],  # Wrong column name
    'company': [''],  # Empty company
})

csv_buffer2 = BytesIO()
test_data2.to_csv(csv_buffer2, index=False)
csv_buffer2.seek(0)

files2 = {'csv': ('test2.csv', csv_buffer2, 'text/csv')}
print("\n3. Testing edge case (missing data)...")
response2 = requests.post(BASE_URL, files=files2)
print(f"   Status: {response2.status_code}")

if response2.status_code == 200:
    result_df2 = pd.read_excel(BytesIO(response2.content))
    print(f"   Result: {result_df2['GENERATED_EMAIL'].iloc[0][:50]}...")