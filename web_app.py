"""
Web App with Column Mapping - Built with TaskMaster Research + Context7
"""
from flask import Flask, request, render_template_string, redirect, url_for, session, send_file
import pandas as pd
import openai
from io import BytesIO
import os
import json

app = Flask(__name__)
app.secret_key = 'dev-secret-key-123'

# API Key
openai.api_key = os.getenv('OPENAI_API_KEY')  # Use environment variable instead

# Template for upload page
UPLOAD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>CSV Email Generator</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; }
        .container { background: #f5f5f5; padding: 40px; border-radius: 10px; }
        h1 { color: #333; }
        .upload-box { background: white; padding: 30px; border-radius: 8px; margin: 20px 0; }
        input[type="file"] { margin: 20px 0; }
        button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Step 1: Upload CSV File</h1>
        <div class="upload-box">
            <form method="POST" enctype="multipart/form-data" action="{{ url_for('upload_csv') }}">
                <p>Select your CSV file containing contact information:</p>
                <input type="file" name="file" accept=".csv" required>
                <br>
                <button type="submit">Upload CSV</button>
            </form>
        </div>
    </div>
</body>
</html>
'''

# Template for column mapping
MAPPING_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Map Columns</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; }
        .container { background: #f5f5f5; padding: 40px; border-radius: 10px; }
        h1 { color: #333; }
        .mapping-box { background: white; padding: 30px; border-radius: 8px; margin: 20px 0; }
        .field-row { margin: 15px 0; display: flex; align-items: center; }
        label { width: 200px; font-weight: bold; }
        select { padding: 8px; width: 300px; }
        button { background: #28a745; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 20px; }
        button:hover { background: #218838; }
        .info { background: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .required { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Step 2: Map Your Columns</h1>
        <div class="info">
            <strong>File uploaded:</strong> {{ filename }} ({{ row_count }} rows)<br>
            <strong>Columns found:</strong> {{ headers|join(', ') }}
        </div>
        
        <div class="mapping-box">
            <form method="POST" action="{{ url_for('process_mapping') }}">
                <h3>Required Fields</h3>
                
                <div class="field-row">
                    <label>First Name <span class="required">*</span>:</label>
                    <select name="first_name" required>
                        <option value="">-- Select Column --</option>
                        {% for header in headers %}
                            <option value="{{ header }}" {% if 'first' in header.lower() and 'name' in header.lower() %}selected{% endif %}>{{ header }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="field-row">
                    <label>Company Name <span class="required">*</span>:</label>
                    <select name="company_name" required>
                        <option value="">-- Select Column --</option>
                        {% for header in headers %}
                            <option value="{{ header }}" {% if 'company' in header.lower() %}selected{% endif %}>{{ header }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <h3>Optional Fields</h3>
                
                <div class="field-row">
                    <label>Last Name:</label>
                    <select name="last_name">
                        <option value="">-- Skip --</option>
                        {% for header in headers %}
                            <option value="{{ header }}" {% if 'last' in header.lower() and 'name' in header.lower() %}selected{% endif %}>{{ header }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="field-row">
                    <label>Job Title:</label>
                    <select name="title">
                        <option value="">-- Skip --</option>
                        {% for header in headers %}
                            <option value="{{ header }}" {% if 'title' in header.lower() or 'job' in header.lower() %}selected{% endif %}>{{ header }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="field-row">
                    <label>Industry:</label>
                    <select name="industry">
                        <option value="">-- Skip --</option>
                        {% for header in headers %}
                            <option value="{{ header }}" {% if 'industry' in header.lower() %}selected{% endif %}>{{ header }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <button type="submit">Generate Emails →</button>
            </form>
        </div>
    </div>
</body>
</html>
'''

# Processing template
PROCESSING_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Generating Emails...</title>
    <meta http-equiv="refresh" content="2;url={{ url_for('download_results') }}">
    <style>
        body { font-family: Arial; max-width: 600px; margin: 100px auto; text-align: center; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #007bff; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <h2>Generating Personalized Emails...</h2>
    <div class="spinner"></div>
    <p>Processing {{ count }} contacts...</p>
    <p>Please wait, this may take a moment.</p>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(UPLOAD_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_csv():
    """Handle CSV upload and show mapping interface"""
    file = request.files['file']
    
    if not file or not file.filename.endswith('.csv'):
        return "Please upload a CSV file", 400
    
    # Read CSV
    df = pd.read_csv(file)
    
    # Store in session
    session['csv_data'] = df.to_json()
    session['filename'] = file.filename
    session['headers'] = list(df.columns)
    session['row_count'] = len(df)
    
    return render_template_string(
        MAPPING_TEMPLATE,
        headers=session['headers'],
        filename=session['filename'],
        row_count=session['row_count']
    )

@app.route('/process', methods=['POST'])
def process_mapping():
    """Process the mapping and generate emails"""
    # Get mapping from form
    mapping = {
        'first_name': request.form.get('first_name'),
        'company_name': request.form.get('company_name'),
        'last_name': request.form.get('last_name', ''),
        'title': request.form.get('title', ''),
        'industry': request.form.get('industry', '')
    }
    
    # Validate required fields
    if not mapping['first_name'] or not mapping['company_name']:
        return "Please map both First Name and Company Name", 400
    
    # Store mapping
    session['mapping'] = mapping
    
    # Get CSV data
    df = pd.read_json(session['csv_data'])
    
    # Generate emails
    emails = []
    for _, row in df.iterrows():
        # Extract data using mapping
        first_name = str(row.get(mapping['first_name'], '')).strip()
        company = str(row.get(mapping['company_name'], '')).strip()
        last_name = str(row.get(mapping['last_name'], '')).strip() if mapping['last_name'] else ''
        title = str(row.get(mapping['title'], '')).strip() if mapping['title'] else ''
        industry = str(row.get(mapping['industry'], '')).strip() if mapping['industry'] else ''
        
        # Build prompt
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        prompt = f"Write a brief, professional cold email to {full_name} at {company}"
        if title:
            prompt += f" who works as {title}"
        if industry:
            prompt += f" in the {industry} industry"
        prompt += ". Keep it under 150 words, be friendly and offer value. Don't be too salesy."
        
        try:
            # Generate email
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            email_content = response.choices[0].message.content.strip()
        except Exception as e:
            email_content = f"Error generating email: {str(e)}"
        
        # Store all data plus email
        row_data = row.to_dict()
        row_data['GENERATED_EMAIL'] = email_content
        emails.append(row_data)
    
    # Store results
    session['results'] = emails
    
    # Show processing page
    return render_template_string(PROCESSING_TEMPLATE, count=len(df))

@app.route('/download')
def download_results():
    """Download the results as Excel"""
    if 'results' not in session:
        return redirect(url_for('index'))
    
    # Create Excel file
    results = session['results']
    df = pd.DataFrame(results)
    
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    
    # Clear session
    session.clear()
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='generated_emails.xlsx'
    )

if __name__ == '__main__':
    print("\n" + "="*60)
    print("WEB APP WITH COLUMN MAPPING")
    print("="*60)
    print("1. Upload CSV")
    print("2. Map columns")
    print("3. Generate emails")
    print("4. Download Excel")
    print("="*60)
    print("\nStarting at http://localhost:5000\n")
    
    app.run(port=5000, debug=True)