import os
from flask import Flask, render_template, request, send_file
import pandas as pd
from io import BytesIO
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Set OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def index():
    """Simple upload form"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cold Email Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .container { background: #f0f0f0; padding: 30px; border-radius: 10px; }
            h1 { color: #333; }
            input[type="file"] { margin: 20px 0; }
            input[type="submit"] { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            input[type="submit"]:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Cold Email Generator</h1>
            <p>Upload a CSV file with contact information to generate personalized cold emails.</p>
            <form method="POST" action="/process" enctype="multipart/form-data">
                <input type="file" name="file" accept=".csv" required>
                <br>
                <input type="submit" value="Generate Emails">
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/process', methods=['POST'])
def process_file():
    """Process uploaded CSV and generate emails"""
    try:
        # Get uploaded file
        file = request.files.get('file')
        if not file:
            return "No file uploaded", 400
        
        # Read CSV data
        df = pd.read_csv(file)
        
        # Generate emails for each row
        emails = []
        for _, row in df.iterrows():
            # Extract basic info (handle missing data gracefully)
            first_name = str(row.get('first_name', '')).strip()
            company = str(row.get('company_name', row.get('company', ''))).strip()
            title = str(row.get('title', row.get('job_title', ''))).strip()
            
            # Skip if no useful data
            if not (first_name or company):
                continue
            
            # Create simple prompt
            prompt = f"Write a brief, professional cold email to {first_name} at {company}"
            if title:
                prompt += f" who is a {title}"
            prompt += ". Keep it under 150 words, friendly and focused on offering value."
            
            try:
                # Generate email using OpenAI
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7
                )
                
                email_content = response.choices[0].message.content.strip()
                emails.append({
                    'First Name': first_name,
                    'Company': company,
                    'Title': title,
                    'Email': email_content
                })
            except Exception as e:
                print(f"Error generating email: {e}")
                emails.append({
                    'First Name': first_name,
                    'Company': company,
                    'Title': title,
                    'Email': f"Error generating email: {str(e)}"
                })
        
        # Create Excel file
        output_df = pd.DataFrame(emails)
        output = BytesIO()
        output_df.to_excel(output, index=False)
        output.seek(0)
        
        # Return Excel file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='cold_emails.xlsx'
        )
        
    except Exception as e:
        return f'''
        <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2>Error Processing File</h2>
            <p>{str(e)}</p>
            <a href="/">Try Again</a>
        </body>
        </html>
        ''', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)