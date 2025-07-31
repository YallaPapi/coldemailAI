from flask import Flask, request, send_file
import pandas as pd
import openai
import os
from io import BytesIO

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return '''
        <html>
        <body style="font-family: Arial; max-width: 600px; margin: 50px auto;">
            <h1>CSV → Emails</h1>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="csv" accept=".csv" required>
                <button type="submit">Generate Emails</button>
            </form>
        </body>
        </html>
        '''
    
    # Process the file
    file = request.files['csv']
    df = pd.read_csv(file)
    
    # Generate emails
    results = []
    for _, row in df.iterrows():
        # Try to find name and company from ANY column
        row_dict = row.to_dict()
        name = ""
        company = ""
        
        # Find name
        for col, val in row_dict.items():
            if 'name' in str(col).lower() and 'first' in str(col).lower():
                name = str(val)
                break
        if not name:  # Try any column with 'name'
            for col, val in row_dict.items():
                if 'name' in str(col).lower():
                    name = str(val)
                    break
        
        # Find company
        for col, val in row_dict.items():
            if 'company' in str(col).lower():
                company = str(val)
                break
        
        # Generate email
        if name or company:
            prompt = f"Write a short cold email to {name} at {company}. 2-3 sentences max."
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100
                )
                email = response.choices[0].message.content
            except:
                email = "Error generating email"
        else:
            email = "Missing name/company data"
        
        # Add to results
        result_row = row_dict.copy()
        result_row['GENERATED_EMAIL'] = email
        results.append(result_row)
    
    # Save to Excel
    output = BytesIO()
    pd.DataFrame(results).to_excel(output, index=False)
    output.seek(0)
    
    return send_file(output, 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     download_name='emails.xlsx')

if __name__ == '__main__':
    app.run(port=5000)