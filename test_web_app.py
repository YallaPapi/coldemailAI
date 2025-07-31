"""
Test the web app with column mapping
"""
import requests
import pandas as pd
from io import BytesIO

BASE_URL = "http://localhost:5000"

print("TESTING WEB APP WITH COLUMN MAPPING")
print("="*50)

# Test 1: Homepage
print("\n1. Testing homepage...")
response = requests.get(BASE_URL)
assert response.status_code == 200
assert "Upload CSV File" in response.text
print("✓ Homepage loads")

# Test 2: Upload CSV
print("\n2. Testing CSV upload...")
test_data = pd.DataFrame({
    'First Name': ['John', 'Sarah'],  # Note: different column names
    'Company': ['Acme Corp', 'Tech Inc'],
    'Job Title': ['CEO', 'CTO'],
    'Industry': ['Software', 'Technology']
})

csv_buffer = BytesIO()
test_data.to_csv(csv_buffer, index=False)
csv_buffer.seek(0)

# Need session for multi-step process
session = requests.Session()

files = {'file': ('test.csv', csv_buffer, 'text/csv')}
response = session.post(f"{BASE_URL}/upload", files=files)

assert response.status_code == 200
assert "Map Your Columns" in response.text
assert "First Name" in response.text
assert "Company" in response.text
print("✓ CSV uploaded, mapping page shown")

# Test 3: Submit mapping
print("\n3. Testing column mapping...")
# The form should auto-detect most mappings
mapping_data = {
    'first_name': 'First Name',
    'company_name': 'Company', 
    'last_name': '',
    'title': 'Job Title',
    'industry': 'Industry'
}

response = session.post(f"{BASE_URL}/process", data=mapping_data)
assert response.status_code == 200
assert "Generating Personalized Emails" in response.text
print("✓ Mapping submitted, processing started")

# Test 4: Download results
print("\n4. Testing download...")
response = session.get(f"{BASE_URL}/download")
assert response.status_code == 200
assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

# Save and verify
with open('web_app_test_result.xlsx', 'wb') as f:
    f.write(response.content)

print(f"✓ Downloaded Excel file ({len(response.content)} bytes)")

# Verify content
result_df = pd.read_excel('web_app_test_result.xlsx')
print(f"\nResults: {len(result_df)} rows")
print(f"Columns: {list(result_df.columns)}")

if 'GENERATED_EMAIL' in result_df.columns:
    print("\nGenerated emails:")
    for idx, row in result_df.iterrows():
        print(f"\n{row['First Name']} at {row['Company']}:")
        email = str(row['GENERATED_EMAIL'])[:100]
        print(f"{email}...")

print("\n" + "="*50)
print("✅ ALL TESTS PASSED - WEB APP WORKS!")