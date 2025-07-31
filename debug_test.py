import requests

# Check what the server is actually returning
response = requests.get("http://localhost:5000")
print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Content (first 500 chars):\n{response.text[:500]}")

# Try a simple POST
print("\n\nTrying POST:")
response = requests.post("http://localhost:5000", data={})
print(f"POST Status: {response.status_code}")
print(f"POST Content: {response.text[:200]}")