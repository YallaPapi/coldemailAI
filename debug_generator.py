#!/usr/bin/env python3
"""
Debug script to isolate the email generation failure.
This tests the core EmailGenerator without Flask complexity.
"""

import os
import sys
from email_generator import EmailGenerator

# Load environment variables from .env file
def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("OK: Loaded .env file")
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

def main():
    load_env()  # Load .env file first
    
    print("DEBUGGING EMAIL GENERATION CORE FAILURE")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print("ERROR: OPENAI_API_KEY not found in environment!")
        print("   Set it with: export OPENAI_API_KEY=your_key_here")
        return False
    
    print(f"OK: OpenAI API Key: {openai_key[:20]}...")
    
    # Create test lead data - exactly like what would come from CSV
    test_lead = {
        'first_name': 'John',
        'company_name': 'Acme Corp', 
        'job_title': 'Lead Developer',
        'industry': 'Software',
        'city': 'San Francisco',
        'state': 'CA',
        'country': 'United States'
    }
    
    print(f"OK: Test Lead Data: {test_lead}")
    
    try:
        print("\nInitializing EmailGenerator...")
        email_gen = EmailGenerator()
        print("OK: EmailGenerator initialized successfully")
        
        print("\nBuilding prompt...")
        prompt = email_gen.build_prompt(test_lead)
        print(f"OK: Prompt built successfully ({len(prompt)} characters)")
        print(f"Prompt preview: {prompt[:200]}...")
        
        print("\nGenerating email with OpenAI...")
        generated_email = email_gen.generate_email(prompt)
        
        print("\nSUCCESS! Generated Email:")
        print("-" * 40)
        try:
            print(generated_email)
        except UnicodeEncodeError:
            # Handle Unicode characters that Windows console can't display
            safe_email = generated_email.encode('ascii', 'replace').decode('ascii')
            print("(Unicode characters replaced with ?)")
            print(safe_email)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {type(e).__name__}: {str(e)}")
        import traceback
        print("\nFull Stack Trace:")
        traceback.print_exc()
        
        # Additional debugging
        print(f"\nDebug Info:")
        print(f"   - Error Type: {type(e)}")
        print(f"   - Error Message: {str(e)}")
        print(f"   - OpenAI Key Length: {len(openai_key) if openai_key else 'None'}")
        
        return False

if __name__ == "__main__":
    print("Starting email generation debug test...")
    success = main()
    
    if success:
        print("\nOK: EMAIL GENERATION WORKING - Problem is elsewhere")
        sys.exit(0)
    else:
        print("\nERROR: EMAIL GENERATION BROKEN - This is the core issue")
        sys.exit(1)