from flask import Flask, request, send_file
import pandas as pd
import openai
import os
from io import BytesIO

app = Flask(__name__)

# HARDCODED API KEY FROM YOUR .ENV FILE
openai.api_key = os.getenv('OPENAI_API_KEY')  # Use environment variable instead

@app.route('/', methods=['GET', 'POST'])
def process_csv():
    if request.method == 'GET':
        return '''
        <html>
        <head>
            <title>Cold Email Generator</title>
            <style>
                body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
                .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
                h1 { color: #333; margin-bottom: 10px; }
                p { color: #666; }
                input[type="file"] { margin: 20px 0; }
                button { 
                    background: #007bff; 
                    color: white; 
                    padding: 10px 20px; 
                    border: none; 
                    border-radius: 5px; 
                    cursor: pointer;
                    font-size: 16px;
                }
                button:hover { background: #0056b3; }
                .info { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Cold Email Generator ✉️</h1>
                <p>Upload a CSV and get personalized cold emails</p>
                
                <div class="info">
                    <strong>Requirements:</strong><br>
                    • CSV must have columns containing "name" and "company"<br>
                    • Each row will generate one email<br>
                    • Results download as Excel file
                </div>
                
                <form method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".csv" required><br>
                    <button type="submit">Generate Emails</button>
                </form>
            </div>
        </body>
        </html>
        '''
    
    # PROCESS THE FILE
    try:
        file = request.files['file']
        df = pd.read_csv(file)
        
        results = []
        for _, row in df.iterrows():
            # Get data from any column containing these words
            name = ""
            company = ""
            title = ""
            
            for col in df.columns:
                col_lower = col.lower()
                val = str(row[col]).strip()
                
                if 'first' in col_lower and 'name' in col_lower and val and val != 'nan':
                    name = val
                elif 'name' in col_lower and not name and val and val != 'nan':
                    name = val
                elif 'company' in col_lower and val and val != 'nan':
                    company = val
                elif ('title' in col_lower or 'job' in col_lower) and val and val != 'nan':
                    title = val
            
            # Generate email if we have data
            if name and company:
                prompt = f"Write a brief, professional cold email to {name} at {company}"
                if title:
                    prompt += f" who works as {title}"
                prompt += ". Maximum 3 sentences. Be friendly and offer value."
                
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=150
                    )
                    email = response.choices[0].message.content.strip()
                except Exception as e:
                    email = f"Error: {str(e)}"
            else:
                email = f"Skipped - Missing data (Name: {name or 'none'}, Company: {company or 'none'})"
            
            # Keep all original data + add email
            result = row.to_dict()
            result['GENERATED_EMAIL'] = email
            results.append(result)
        
        # Create Excel
        output = BytesIO()
        pd.DataFrame(results).to_excel(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='cold_emails.xlsx'
        )
        
    except Exception as e:
        return f'''
        <html>
        <body style="font-family: Arial; max-width: 600px; margin: 50px auto;">
            <h2>Error</h2>
            <p style="color: red;">{str(e)}</p>
            <a href="/">← Try Again</a>
        </body>
        </html>
        ''', 500

if __name__ == '__main__':
    print("Starting Cold Email Generator...")
    print("Open http://localhost:5000 in your browser")
    app.run(port=5000, debug=False)