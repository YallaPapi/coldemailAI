import requests

response = requests.get("http://localhost:5000")
print(f"Status: {response.status_code}")
print(f"Content preview:\n{response.text[:200]}")

# Check which app is running
if "Upload CSV File" in response.text:
    print("\n✓ web_app.py is running")
elif "CSV → Emails" in response.text:
    print("\n✗ Wrong app running (simple version)")
elif "Cold Email Generator" in response.text:
    print("\n✗ Wrong app running (other version)")
else:
    print("\n? Unknown app running")