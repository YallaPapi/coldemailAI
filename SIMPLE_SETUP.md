# Simple Cold Email Generator Setup

## Quick Start (The Working Solution)

This is a simplified, working version of the cold email generator that bypasses all the architectural issues in the main application.

### 1. Install Dependencies

```bash
pip install flask pandas openai python-dotenv openpyxl
```

### 2. Set Up OpenAI API Key

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-actual-openai-api-key-here
```

### 3. Run the Simple App

```bash
python simple_working_app.py
```

### 4. Use the Application

1. Open http://localhost:5000 in your browser
2. Upload a CSV file with columns like:
   - first_name
   - company_name (or company)
   - title (or job_title)
3. Click "Generate Emails"
4. Download the generated Excel file with personalized emails

## What This Version Does

1. **Simple File Upload**: Direct file processing without session management
2. **Immediate Processing**: No complex async or progress tracking
3. **Error Handling**: Graceful fallbacks for missing data
4. **Direct Excel Output**: Immediate download, no intermediate storage

## CSV Format

Your CSV should have headers like:
```
first_name,last_name,company_name,title,email,phone
John,Smith,Acme Corp,Sales Manager,john@acme.com,555-1234
```

The app will work with variations like `company` instead of `company_name` or `job_title` instead of `title`.

## Troubleshooting

1. **"No module named 'openai'"**: Run `pip install openai`
2. **"OPENAI_API_KEY not set"**: Create the .env file with your API key
3. **Connection errors**: Check your OpenAI API key is valid
4. **Large files timing out**: Keep CSV under 100 rows for best results

## Why This Works

Unlike the main app.py which has:
- Complex session management that corrupts data
- Synchronous Flask routes that timeout
- Unicode handling issues
- Memory management problems

This simple version:
- Processes files directly in memory
- Uses minimal dependencies
- Handles errors gracefully
- Returns results immediately

## Next Steps

If you need more features:
1. Add progress tracking with WebSockets
2. Use Celery for background processing
3. Implement proper database storage
4. Add user authentication

But for now, this simple version WORKS.