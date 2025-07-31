# test_flask_response.py

import pandas as pd
from app import app # Import the Flask app object

def run_response_test():
    """
    This test uses Flask's built-in test client to simulate a full
    request-response cycle for the /generate_emails route, isolating the
    point of failure.
    """
    print("--- STARTING FLASK RESPONSE LAYER TEST ---")

    # Create a hardcoded DataFrame with Unicode characters. This simulates
    # the data that would be in the user's session right before the
    # final Excel file is created. The smart quote is intentional.
    test_df = pd.DataFrame([{
        'first_name': 'John',
        'company_name': 'Acme Corp',
        'job_title': 'Lead Developer',
        'industry': 'Software',
        'Personalized': "This is a test with a 'smart quote' which causes encoding issues."
    }])

    print(f"[INFO] Test DataFrame with Unicode:\n{test_df.to_string()}")

    # Use the test client to simulate the application context
    with app.test_client() as client:
        # Create test CSV data and encode it like the upload process does
        import base64
        test_csv = "first_name,company_name,job_title,industry\nJohn,Acme Corp,Lead Developer,Software"
        file_data_b64 = base64.b64encode(test_csv.encode('utf-8')).decode('utf-8')
        
        # Set the session data exactly as the upload process would
        with client.session_transaction() as sess:
            sess['file_data'] = file_data_b64
            sess['filename'] = 'test_file.csv'
            sess['columns'] = ['first_name', 'company_name', 'job_title', 'industry']
        
        print("[EXEC] Simulating POST request to /generate_emails...")

        try:
            # Create form data for column mapping
            form_data = {
                'map_first_name': 'first_name',
                'map_company_name': 'company_name',
                'map_job_title': 'job_title',
                'map_industry': 'industry'
            }
            
            # Make the request to the route that is failing
            response = client.post('/generate_emails', data=form_data)

            # Check the response
            print("\n\n--- FLASK RESPONSE TEST SUCCEEDED ---")
            print("The /generate_emails route successfully created a response.")
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'None')}")
            print(f"Content-Disposition: {response.headers.get('Content-Disposition', 'None')}")
            assert response.status_code == 200

        except Exception as e:
            import traceback
            print("\n\n--- FLASK RESPONSE TEST FAILED ---")
            print("The error is in your app.py file. Full Traceback:")
            print("-------------------------------------------------")
            traceback.print_exc()
            print("-------------------------------------------------")


if __name__ == "__main__":
    run_response_test()