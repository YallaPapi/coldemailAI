"""
Manual test - upload CSV and save result
"""
import requests
import pandas as pd
from io import BytesIO

# Create test CSV
df = pd.DataFrame({
    'first_name': ['John', 'Sarah'],
    'company_name': ['Acme Corp', 'Tech Inc'],
    'title': ['CEO', 'CTO']
})

print("Test data:")
print(df)
print("\nUploading to http://localhost:5000...")

# Save to file
df.to_csv('manual_test.csv', index=False)

# Upload
with open('manual_test.csv', 'rb') as f:
    # Try both field names
    for field_name in ['file', 'csv']:
        print(f"\nTrying field name: {field_name}")
        f.seek(0)
        files = {field_name: ('test.csv', f, 'text/csv')}
        
        response = requests.post('http://localhost:5000', files=files)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Save result
            filename = f'result_{field_name}.xlsx'
            with open(filename, 'wb') as out:
                out.write(response.content)
            print(f"✓ Saved: {filename}")
            
            # Check content
            result = pd.read_excel(filename)
            print(f"Columns: {list(result.columns)}")
            if 'GENERATED_EMAIL' in result.columns:
                print("\nGenerated emails:")
                for idx, row in result.iterrows():
                    print(f"{row['first_name']}: {row['GENERATED_EMAIL'][:50]}...")
            break
        else:
            print(f"Error: {response.text[:100]}")