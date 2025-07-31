# nuclear_debug.py

import os
import pandas as pd
import traceback
from email_generator import EmailGenerator

def load_env():
    """Loads .env file variables into the environment."""
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("[INFO] .env file loaded.")
    except Exception as e:
        print(f"[WARN] Could not load .env file: {e}")

def run_nuclear_test():
    """
    This function performs a single, isolated test of the EmailGenerator.
    Its only purpose is to make the process_leads_with_mapping function work.
    """
    print("--- STARTING NUCLEAR DEBUG PROTOCOL ---")
    load_env()

    if not os.environ.get("OPENAI_API_KEY"):
        print("[FATAL] OPENAI_API_KEY environment variable not set. Aborting.")
        return

    # This is the hardcoded input DataFrame. It simulates the data
    # after it has been uploaded and parsed by the Flask app.
    input_df = pd.DataFrame([{
        'first_name': 'John',
        'company_name': 'Acme Corp',
        'job_title': 'Lead Developer',
        'industry': 'Software'
    }])

    # This is the hardcoded mapping dictionary, simulating what the
    # user would select on the mapping screen.
    mapping_dict = {
        'first_name': 'first_name',
        'company_name': 'company_name',
        'job_title': 'job_title',
        'industry': 'industry'
    }

    print(f"[INFO] Input DataFrame:\n{input_df.to_string()}")
    print(f"[INFO] Mapping Dictionary: {mapping_dict}")

    try:
        print("[EXEC] Initializing EmailGenerator...")
        email_gen = EmailGenerator()
        
        print("[EXEC] Calling process_leads_with_mapping...")
        result_df = email_gen.process_leads_with_mapping(input_df, mapping_dict)
        
        print("\n\n--- NUCLEAR PROTOCOL SUCCESSFUL ---")
        print("THE CORE FUNCTION IS WORKING. FINAL OUTPUT:")
        print("-------------------------------------------------")
        print(result_df['Personalized'].iloc[0])
        print("-------------------------------------------------")

    except Exception:
        print("\n\n--- NUCLEAR PROTOCOL FAILED ---")
        print("THE CORE FUNCTION IS BROKEN. FULL TRACEBACK:")
        print("-------------------------------------------------")
        traceback.print_exc()
        print("-------------------------------------------------")

if __name__ == "__main__":
    run_nuclear_test()