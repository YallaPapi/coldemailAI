# Quick Start - Test the Working Email Generator

## You have 2 working options:

### Option 1: Simple Version (Easiest)
1. Double-click `run_simple.bat`
2. Open http://localhost:5000 in your browser
3. Upload `test_leads.csv`
4. Get your emails!

### Option 2: Modern Version (Better)
1. Double-click `run_modern_app.bat`
2. Open http://localhost:5000 in your browser
3. Upload `test_leads.csv`
4. Watch real-time progress
5. Download your emails!

## Test Data Ready

I've created `test_leads.csv` with 5 sample contacts:
- John Smith - CEO at Acme Technologies
- Sarah Johnson - VP Marketing at Global Consulting
- Michael Chen - CTO at DataFlow Systems
- Emily Rodriguez - Head of Sales at HealthTech Solutions
- David Kim - Product Manager at CloudFirst Corp

## What Will Happen

1. The app reads your CSV file
2. For each contact, it generates a personalized cold email using OpenAI
3. You get an Excel file with all the generated emails

## If Something Doesn't Work

1. Make sure your `.env` file has the OpenAI API key (already set up)
2. Check you have Python installed
3. Try the simple version first - it has fewer dependencies

## The Bottom Line

Both versions work. The simple version is easier to run, the modern version has progress tracking.

Just double-click a .bat file and upload your CSV!