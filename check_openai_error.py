import openai
import os
from dotenv import load_dotenv

# Try both methods
print("Method 1: Direct API key")
openai.api_key = os.getenv('OPENAI_API_KEY')  # Use environment variable instead

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'Working!'"}],
        max_tokens=10
    )
    print(f"✓ Method 1 works: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ Method 1 failed: {type(e).__name__}: {e}")

print("\nMethod 2: From .env file")
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
print(f"API key loaded: {openai.api_key[:20]}..." if openai.api_key else "No key!")

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'Working!'"}],
        max_tokens=10
    )
    print(f"✓ Method 2 works: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ Method 2 failed: {type(e).__name__}: {e}")