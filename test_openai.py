import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

print(f"API Key loaded: {openai.api_key[:10]}...")

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'API works!'"}],
        max_tokens=10
    )
    print(f"Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"ERROR: {e}")
    print(f"Error type: {type(e)}")