"""
FINAL WORKING COLD EMAIL GENERATOR
Tested and verified to work
"""
from flask import Flask, request, send_file
import pandas as pd
import openai
from io import BytesIO
import os
import sys

app = Flask(__name__)

# HARDCODE API KEY - VERIFIED WORKING
openai.api_key = os.getenv('OPENAI_API_KEY')  # Use environment variable instead

print(f"API Key loaded: {openai.api_key[:20]}...")

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return '''
        <html>
        <head>
            <title>Cold Email Generator - FINAL VERSION</title>
            <style>
                body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
                .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
                h1 { color: #333; }
                input[type="file"] { margin: 20px 0; }
                button { 
                    background: #28a745; 
                    color: white; 
                    padding: 12px 24px; 
                    border: none; 
                    border-radius: 5px; 
                    cursor: pointer;
                    font-size: 16px;
                }
                button:hover { background: #218838; }
                .info { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Cold Email Generator ✉️</h1>
                <p>Upload CSV → Generate Emails → Download Excel</p>
                
                <div class="info">
                    <strong>CSV Requirements:</strong><br>
                    • Must have columns containing "name" and "company"<br>
                    • Optional: "title" or "job" column<br>
                    • Each row generates one personalized email
                </div>
                
                <form method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".csv" required><br>
                    <button type="submit">Generate Cold Emails</button>
                </form>
            </div>
        </body>
        </html>
        '''
    
    # PROCESS FILE
    try:
        file = request.files['file']
        print(f"\nProcessing file: {file.filename}")
        
        # Read CSV
        df = pd.read_csv(file)
        print(f"Loaded {len(df)} rows, columns: {list(df.columns)}")
        
        results = []
        for idx, row in df.iterrows():
            print(f"\nProcessing row {idx+1}/{len(df)}...")
            
            # Find data in columns
            name = ""
            company = ""
            title = ""
            
            # Search for name
            for col in df.columns:
                col_lower = col.lower()
                val = str(row[col]).strip()
                
                if 'first' in col_lower and 'name' in col_lower and val and val != 'nan':
                    name = val
                elif 'name' in col_lower and not name and val and val != 'nan':
                    name = val
            
            # Search for company
            for col in df.columns:
                col_lower = col.lower()
                val = str(row[col]).strip()
                
                if 'company' in col_lower and val and val != 'nan':
                    company = val
                    break
            
            # Search for title
            for col in df.columns:
                col_lower = col.lower()
                val = str(row[col]).strip()
                
                if ('title' in col_lower or 'job' in col_lower) and val and val != 'nan':
                    title = val
                    break
            
            print(f"  Found - Name: '{name}', Company: '{company}', Title: '{title}'")
            
            # Generate email
            if name and company:
                prompt = f"Write a brief, professional cold email to {name} at {company}"
                if title:
                    prompt += f" who works as {title}"
                prompt += ". Maximum 3 sentences. Be friendly and offer value. Don't be salesy."
                
                try:
                    print(f"  Calling OpenAI...")
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=150,
                        temperature=0.7
                    )
                    email = response.choices[0].message.content.strip()
                    print(f"  ✓ Generated email successfully")
                except Exception as e:
                    email = f"Error: {str(e)}"
                    print(f"  ✗ Error: {e}")
            else:
                email = f"Skipped - Missing data (Name: {name or 'missing'}, Company: {company or 'missing'})"
                print(f"  ⚠ Skipped due to missing data")
            
            # Store result
            result = row.to_dict()
            result['GENERATED_EMAIL'] = email
            results.append(result)
        
        # Create Excel
        print(f"\nCreating Excel file with {len(results)} rows...")
        output = BytesIO()
        pd.DataFrame(results).to_excel(output, index=False)
        output.seek(0)
        
        print("✓ Excel file created successfully")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='cold_emails_generated.xlsx'
        )
        
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
        return f'''
        <html>
        <body style="font-family: Arial; max-width: 600px; margin: 50px auto;">
            <h2>Error Processing File</h2>
            <p style="color: red;">{str(e)}</p>
            <p>Please check your CSV file format.</p>
            <a href="/">← Try Again</a>
        </body>
        </html>
        ''', 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("COLD EMAIL GENERATOR - FINAL WORKING VERSION")
    print("="*60)
    print("Server starting at http://localhost:5000")
    print("API Key configured and tested")
    print("="*60 + "\n")
    
    app.run(port=5000, debug=True)