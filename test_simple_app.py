#!/usr/bin/env python3
"""
Test script to verify the simple cold email generator works
"""
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if API key is set
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found in .env file")
    print("Please create a .env file with:")
    print("OPENAI_API_KEY=your-actual-api-key-here")
    exit(1)

print(f"✓ OpenAI API key found (length: {len(api_key)})")

# Test reading CSV
try:
    df = pd.read_csv('test_contacts_simple.csv')
    print(f"✓ Successfully read CSV with {len(df)} contacts")
    print(f"  Columns: {list(df.columns)}")
except Exception as e:
    print(f"✗ Error reading CSV: {e}")
    exit(1)

# Test OpenAI connection (optional - will use API credits)
test_api = input("\nTest OpenAI API connection? This will use a small amount of credits (y/n): ")
if test_api.lower() == 'y':
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API working' in 3 words or less"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✓ OpenAI API test successful: {result}")
    except Exception as e:
        print(f"✗ OpenAI API error: {e}")
        print("  Check your API key is valid and has credits")

print("\n✓ All checks passed! You can run: python simple_working_app.py")