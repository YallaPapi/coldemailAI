# debug_email_generator.py

import os
import pandas as pd
from email_generator import EmailGenerator # Or wherever your class is located

# Load environment variables from .env file
def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("Loaded .env file")
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

# --- DO NOT MODIFY THIS DATA ---
# This is our single, hardcoded test case.
test_lead_data = {
    'First Name': 'John',
    'Company': 'Acme Corp',
    'Job Title': 'Lead Developer',
    'Industry': 'Software'
}
# --- END OF DATA ---


def debug_core_function():
    """
    This function directly calls the broken EmailGenerator to find the real error.
    """
    print("--- INITIALIZING DEBUGGING SCRIPT ---")
    
    # Load environment variables
    load_env()
    
    # Ensure your OPENAI_API_KEY is set in your environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        return

    print("Attempting to initialize EmailGenerator...")
    try:
        email_gen = EmailGenerator()
        print("SUCCESS: EmailGenerator initialized.")
    except Exception as e:
        print(f"ERROR: FAILED TO INITIALIZE EmailGenerator. ERROR: {e}")
        return

    print("\n--- CALLING THE BROKEN FUNCTION ---")
    print(f"Input Data: {test_lead_data}")
    
    try:
        # We pass the data inside a list, as the function likely expects an iterable
        # NOTE: The function expects a list of dictionaries.
        # The column mapping logic in app.py would have transformed the data.
        # We must simulate that here. The keys in the dictionary
        # MUST match what the build_prompt() method expects.
        # This is likely the point of failure.
        
        # Create the mapped data as a pandas DataFrame (like Flask does)
        mapped_lead = {
            'first_name': test_lead_data['First Name'],
            'company_name': test_lead_data['Company'],
            'job_title': test_lead_data['Job Title'],
            'industry': test_lead_data['Industry']
        }
        
        # Convert to DataFrame like Flask does
        mapped_df = pd.DataFrame([mapped_lead])
        
        # Create the mapping dictionary (like Flask does)
        mapping = {
            'first_name': 'First Name',
            'company_name': 'Company',
            'job_title': 'Job Title', 
            'industry': 'Industry'
        }

        # Call the function with both parameters
        result_df = email_gen.process_leads_with_mapping(mapped_df, mapping)
        
        print("\nSUCCESS! THE CORE FUNCTION WORKS.")
        print("--- Generated Email: ---")
        if 'Personalized' in result_df.columns:
            print(result_df['Personalized'].iloc[0]) # Print the first generated email
        else:
            print("No 'Personalized' column found in result")
            print(f"Columns: {list(result_df.columns)}")

    except Exception as e:
        print(f"\nIT FAILED. HERE IS THE REAL ERROR:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_core_function()