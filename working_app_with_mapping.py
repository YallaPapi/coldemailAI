import os
from flask import Flask, render_template_string, request, send_file, session, redirect, url_for
import pandas as pd
from io import BytesIO
import openai
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Set OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# HTML Templates
UPLOAD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Cold Email Generator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f0f0f0; padding: 30px; border-radius: 10px; }
        h1 { color: #333; }
        .upload-box { 
            border: 2px dashed #ccc; 
            padding: 40px; 
            text-align: center; 
            margin: 20px 0;
            background: white;
            border-radius: 8px;
        }
        input[type="file"] { margin: 20px 0; }
        input[type="submit"] { 
            background: #007bff; 
            color: white; 
            padding: 10px 30px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px;
        }
        input[type="submit"]:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Cold Email Generator</h1>
        <p>Step 1: Upload your CSV file with contact information</p>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <div class="upload-box">
                <p>Choose a CSV file containing your leads</p>
                <input type="file" name="file" accept=".csv" required>
                <br>
                <input type="submit" value="Upload and Continue →">
            </div>
        </form>
    </div>
</body>
</html>
'''

MAPPING_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Map Columns - Cold Email Generator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f0f0f0; padding: 30px; border-radius: 10px; }
        h1 { color: #333; }
        .info-box { background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .mapping-section { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .field-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .required { color: #dc3545; }
        .optional { color: #6c757d; }
        .buttons { margin-top: 20px; display: flex; justify-content: space-between; }
        input[type="submit"] { 
            background: #28a745; 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px;
        }
        input[type="submit"]:hover { background: #218838; }
        .back-btn { 
            background: #6c757d; 
            color: white; 
            padding: 12px 20px; 
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Step 2: Map Your Columns</h1>
        <div class="info-box">
            <strong>File:</strong> {{ filename }} | <strong>Rows:</strong> {{ row_count }} | <strong>Columns found:</strong> {{ columns|length }}
        </div>
        
        <form method="POST" action="/generate">
            <div class="mapping-section">
                <h3>Required Fields <span class="required">*</span></h3>
                
                <div class="field-group">
                    <label for="first_name">First Name <span class="required">*</span></label>
                    <select name="first_name" required>
                        <option value="">-- Select Column --</option>
                        {% for col in columns %}
                            <option value="{{ col }}" {% if 'first' in col.lower() and 'name' in col.lower() %}selected{% endif %}>{{ col }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="field-group">
                    <label for="company">Company Name <span class="required">*</span></label>
                    <select name="company" required>
                        <option value="">-- Select Column --</option>
                        {% for col in columns %}
                            <option value="{{ col }}" {% if 'company' in col.lower() %}selected{% endif %}>{{ col }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="mapping-section">
                <h3>Optional Fields</h3>
                
                <div class="field-group">
                    <label for="title">Job Title <span class="optional">(optional)</span></label>
                    <select name="title">
                        <option value="">-- Skip This Field --</option>
                        {% for col in columns %}
                            <option value="{{ col }}" {% if 'title' in col.lower() or 'job' in col.lower() %}selected{% endif %}>{{ col }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="field-group">
                    <label for="industry">Industry <span class="optional">(optional)</span></label>
                    <select name="industry">
                        <option value="">-- Skip This Field --</option>
                        {% for col in columns %}
                            <option value="{{ col }}" {% if 'industry' in col.lower() %}selected{% endif %}>{{ col }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="buttons">
                <a href="/" class="back-btn">← Start Over</a>
                <input type="submit" value="Generate {{ row_count }} Emails →">
            </div>
        </form>
    </div>
</body>
</html>
'''

PROCESSING_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Generating Emails...</title>
    <meta http-equiv="refresh" content="0;url=/download">
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 100px auto; text-align: center; }
        .spinner { 
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <h2>Generating Personalized Emails...</h2>
    <div class="spinner"></div>
    <p>Please wait while we create your emails. This may take a moment.</p>
    <p><small>You'll be redirected automatically when complete.</small></p>
</body>
</html>
'''

@app.route('/')
def index():
    """Show upload form"""
    return render_template_string(UPLOAD_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and show mapping interface"""
    file = request.files.get('file')
    if not file or not file.filename.endswith('.csv'):
        return redirect(url_for('index'))
    
    # Read CSV
    file_content = file.read()
    df = pd.read_csv(BytesIO(file_content))
    
    # Store in session
    session['file_data'] = base64.b64encode(file_content).decode('utf-8')
    session['filename'] = file.filename
    session['columns'] = list(df.columns)
    session['row_count'] = len(df)
    
    return render_template_string(
        MAPPING_TEMPLATE,
        filename=file.filename,
        columns=list(df.columns),
        row_count=len(df)
    )

@app.route('/generate', methods=['POST'])
def generate_emails():
    """Generate emails based on mapping"""
    # Get mapping
    mapping = {
        'first_name': request.form.get('first_name'),
        'company': request.form.get('company'),
        'title': request.form.get('title', ''),
        'industry': request.form.get('industry', '')
    }
    
    # Get stored data
    file_data = base64.b64decode(session['file_data'])
    df = pd.read_csv(BytesIO(file_data))
    
    # Generate emails
    emails = []
    for _, row in df.iterrows():
        # Extract mapped fields
        first_name = str(row.get(mapping['first_name'], '')).strip() if mapping['first_name'] else ''
        company = str(row.get(mapping['company'], '')).strip() if mapping['company'] else ''
        title = str(row.get(mapping['title'], '')).strip() if mapping['title'] else ''
        industry = str(row.get(mapping['industry'], '')).strip() if mapping['industry'] else ''
        
        # Skip if no useful data
        if not (first_name or company):
            continue
        
        # Build prompt
        prompt = f"Write a brief, professional cold email to {first_name}"
        if company:
            prompt += f" at {company}"
        if title:
            prompt += f" who is a {title}"
        if industry:
            prompt += f" in the {industry} industry"
        prompt += ". Keep it under 150 words, friendly and focused on offering value. Make it conversational and avoid being too salesy."
        
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
        
        # Store all original data plus generated email
        email_row = row.to_dict()
        email_row['Generated_Email'] = email_content
        emails.append(email_row)
    
    # Create Excel file
    output_df = pd.DataFrame(emails)
    output = BytesIO()
    output_df.to_excel(output, index=False)
    output.seek(0)
    
    # Store for download
    session['output_file'] = base64.b64encode(output.getvalue()).decode('utf-8')
    
    return render_template_string(PROCESSING_TEMPLATE)

@app.route('/download')
def download_file():
    """Download generated emails"""
    if 'output_file' not in session:
        return redirect(url_for('index'))
    
    output_data = base64.b64decode(session['output_file'])
    
    # Clear session
    session.clear()
    
    return send_file(
        BytesIO(output_data),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='generated_cold_emails.xlsx'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)