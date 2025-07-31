#!/usr/bin/env python3
"""
Debug script to test process_leads_with_mapping function directly.
"""

import os
import pandas as pd
from email_generator import EmailGenerator

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
    load_env()
    
    print("TESTING process_leads_with_mapping FUNCTION")
    print("=" * 50)
    
    # Check OpenAI API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print("ERROR: OPENAI_API_KEY not found!")
        return False
    
    print(f"OK: OpenAI API Key: {openai_key[:20]}...")
    
    # Test data - exactly as Flask would create it
    test_lead = {
        'first_name': 'John',
        'company_name': 'Acme Corp',
        'job_title': 'Lead Developer',
        'industry': 'Software',
        'city': 'San Francisco',
        'state': 'CA',
        'country': 'United States'
    }
    
    # Convert to DataFrame like Flask does
    mapped_df = pd.DataFrame([test_lead])
    
    # Mapping like Flask creates
    mapping = {
        'first_name': 'first_name',
        'company_name': 'company_name',
        'job_title': 'job_title',
        'industry': 'industry',
        'city': 'city',
        'state': 'state',
        'country': 'country'
    }
    
    print(f"OK: Test DataFrame: {len(mapped_df)} rows")
    print(f"OK: Mapping: {mapping}")
    
    try:
        print("\nInitializing EmailGenerator...")
        email_gen = EmailGenerator()
        print("OK: EmailGenerator initialized")
        
        print("\nCalling process_leads_with_mapping...")
        result_df = email_gen.process_leads_with_mapping(mapped_df, mapping)
        
        print("SUCCESS! Generated emails:")
        print("-" * 40)
        if 'Personalized' in result_df.columns:
            for i, email in enumerate(result_df['Personalized']):
                print(f"Email {i+1}:")
                try:
                    print(email)
                except UnicodeEncodeError:
                    safe_email = email.encode('ascii', 'replace').decode('ascii')
                    print("(Unicode characters replaced with ?)")
                    print(safe_email)
                print("-" * 40)
        else:
            print("No 'Personalized' column found!")
            print(f"Columns: {list(result_df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"\nIT FAILED. HERE'S THE ERROR: {e}")
        import traceback
        print("\nFull Stack Trace:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nOK: process_leads_with_mapping WORKING")
    else:
        print("\nERROR: process_leads_with_mapping BROKEN")