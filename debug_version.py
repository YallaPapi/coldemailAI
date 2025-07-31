from flask import Flask, request, send_file, jsonify
import pandas as pd
import openai
import os
from io import BytesIO
import traceback

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def home():
    return '''
    <html>
    <body style="font-family: Arial; max-width: 800px; margin: 50px auto;">
        <h1>CSV Email Generator - Debug Version</h1>
        <div style="background: #f0f0f0; padding: 20px; margin: 20px 0;">
            <p><strong>How it works:</strong></p>
            <ol>
                <li>Upload a CSV file</li>
                <li>It will find columns with "name" and "company" in them</li>
                <li>Generate emails using OpenAI</li>
                <li>Download Excel file with results</li>
            </ol>
        </div>
        <form action="/process" method="post" enctype="multipart/form-data">
            <input type="file" name="csv" accept=".csv" required>
            <button type="submit">Upload and Generate</button>
        </form>
        <div id="status"></div>
    </body>
    </html>
    '''

@app.route('/process', methods=['POST'])
def process():
    try:
        # Check if file exists
        if 'csv' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['csv']
        if file.filename == '':
            return "No file selected", 400
        
        # Read CSV
        print(f"Reading file: {file.filename}")
        df = pd.read_csv(file)
        print(f"CSV loaded: {len(df)} rows, columns: {list(df.columns)}")
        
        # Show what we found
        status_html = f"<h2>Processing {file.filename}</h2>"
        status_html += f"<p>Found {len(df)} rows</p>"
        status_html += f"<p>Columns: {', '.join(df.columns)}</p>"
        
        # Generate emails
        results = []
        for idx, row in df.iterrows():
            print(f"\nProcessing row {idx+1}/{len(df)}")
            row_dict = row.to_dict()
            
            # Find name
            name = ""
            for col in df.columns:
                if 'first' in col.lower() and 'name' in col.lower():
                    name = str(row[col])
                    break
            if not name:
                for col in df.columns:
                    if 'name' in col.lower():
                        name = str(row[col])
                        break
            
            # Find company
            company = ""
            for col in df.columns:
                if 'company' in col.lower():
                    company = str(row[col])
                    break
            
            print(f"  Name: {name}, Company: {company}")
            
            # Generate email
            if name and company:
                prompt = f"Write a brief cold outreach email to {name} at {company}. Keep it under 100 words, friendly and professional."
                print(f"  Calling OpenAI...")
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=150,
                        temperature=0.7
                    )
                    email = response.choices[0].message.content.strip()
                    print(f"  Generated email: {email[:50]}...")
                except Exception as e:
                    email = f"Error: {str(e)}"
                    print(f"  Error generating email: {e}")
            else:
                email = f"Missing data - Name: '{name}', Company: '{company}'"
            
            # Add to results
            result_row = row_dict.copy()
            result_row['GENERATED_EMAIL'] = email
            results.append(result_row)
        
        # Create Excel file
        print("\nCreating Excel file...")
        output = BytesIO()
        pd.DataFrame(results).to_excel(output, index=False)
        output.seek(0)
        
        print("Done! Sending file...")
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'emails_{file.filename.replace(".csv", "")}.xlsx'
        )
        
    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.format_exc())
        return f'''
        <html>
        <body style="font-family: Arial; max-width: 800px; margin: 50px auto;">
            <h1>Error</h1>
            <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px;">
                <p><strong>Error:</strong> {str(e)}</p>
                <pre>{traceback.format_exc()}</pre>
            </div>
            <a href="/">← Try Again</a>
        </body>
        </html>
        ''', 500

@app.route('/test')
def test():
    """Test endpoint to verify app is working"""
    return jsonify({
        "status": "working",
        "openai_key_loaded": bool(openai.api_key),
        "openai_key_prefix": openai.api_key[:10] if openai.api_key else None
    })

if __name__ == '__main__':
    print(f"OpenAI API Key loaded: {openai.api_key[:20]}..." if openai.api_key else "NO API KEY!")
    print("Starting server on http://localhost:5000")
    print("Test the API at http://localhost:5000/test")
    app.run(debug=True, port=5000)