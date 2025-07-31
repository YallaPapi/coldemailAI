#!/usr/bin/env python3
"""
Debug script to isolate email generation issues
"""

import os
import sys
import pandas as pd
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_email_generator_directly():
    """Test the email generator directly to isolate issues"""
    print("=== Testing Email Generator Directly ===")
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if OpenAI API key is set
        openai_key = os.environ.get("OPENAI_API_KEY")
        print(f"OpenAI API Key present: {bool(openai_key)}")
        
        if not openai_key:
            print("[CRITICAL] OpenAI API key not found in environment")
            print("This will cause the email generator to fail!")
            return False
        
        # Test with small dataset
        test_data = pd.DataFrame([
            {
                'first_name': 'John',
                'company_name': 'TestCorp',
                'title': 'CEO',
                'industry': 'Technology',
                'city': 'Las Vegas',
                'state': 'Nevada'
            }
        ])
        
        print(f"Testing with {len(test_data)} test leads...")
        
        # Try to import and test email generator
        from email_generator import EmailGenerator
        
        email_gen = EmailGenerator()
        
        # Test the process_leads_with_mapping method
        mapping = {
            'first_name': 'first_name',
            'company_name': 'company_name',
            'job_title': 'title',
            'industry': 'industry',
            'city': 'city',
            'state': 'state'
        }
        
        print("Calling process_leads_with_mapping...")
        result = email_gen.process_leads_with_mapping(test_data, mapping)
        
        if len(result) > 0 and 'Personalized' in result.columns:
            print("[SUCCESS] Email generation worked!")
            print(f"Generated {len(result)} emails")
            print(f"Sample email: {result['Personalized'].iloc[0][:100]}...")
            return True
        else:
            print("[FAIL] Email generation returned no results")
            return False
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        print(f"Full traceback:")
        traceback.print_exc()
        return False

def test_mock_email_generator():
    """Test the mock email generator as fallback"""
    print("\n=== Testing Mock Email Generator ===")
    
    try:
        # Test with mock generator
        from mock_email_generator import MockEmailGenerator
        
        test_data = pd.DataFrame([
            {
                'first_name': 'John',
                'company_name': 'TestCorp',
                'title': 'CEO',
                'industry': 'Technology',
                'city': 'Las Vegas',
                'state': 'Nevada'
            }
        ])
        
        mock_gen = MockEmailGenerator()
        
        mapping = {
            'first_name': 'first_name',
            'company_name': 'company_name',
            'job_title': 'title',
            'industry': 'industry',
            'city': 'city',
            'state': 'state'
        }
        
        result = mock_gen.process_leads_with_mapping(test_data, mapping)
        
        if len(result) > 0 and 'Personalized' in result.columns:
            print("[SUCCESS] Mock email generation worked!")
            print(f"Generated {len(result)} emails")
            print(f"Sample email: {result['Personalized'].iloc[0][:100]}...")
            return True
        else:
            print("[FAIL] Mock email generation failed")
            return False
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("ColdEmailAI Email Generation Debug")
    print("=" * 50)
    
    # Test real email generator
    real_success = test_email_generator_directly()
    
    # Test mock email generator
    mock_success = test_mock_email_generator()
    
    print("\n" + "=" * 50)
    print("DEBUG RESULTS:")
    print(f"Real Email Generator: {'[PASS]' if real_success else '[FAIL]'}")
    print(f"Mock Email Generator: {'[PASS]' if mock_success else '[FAIL]'}")
    
    if not real_success:
        print("\n[CRITICAL ISSUE FOUND]")
        print("Real email generator is failing - likely OpenAI API key issue")
        print("This explains why the Flask server crashes during email generation")
        
    return real_success or mock_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)