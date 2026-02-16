"""
Quick test to debug AI Assistant chat error
"""
import requests
import json

# Test the chat endpoint with actual message
url = "http://localhost:5000/api/ai-assistant/chat"

payload = {
    "message": "show invoice with highst value",
    "conversation_id": None,
    "stream": False
}

print("Sending request to:", url)
print("Payload:", json.dumps(payload, indent=2))
print("-" * 60)

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")