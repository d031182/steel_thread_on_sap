"""
Debug script to check conversation context handling
"""
import requests
import json

# Test 1: Create conversation with HANA context
print("=" * 60)
print("TEST 1: Create conversation with HANA context")
print("=" * 60)

response1 = requests.post(
    "http://localhost:5000/api/ai-assistant/chat",
    json={
        "message": "test",
        "context": {
            "datasource": "hana"
        }
    }
)

print(f"Status: {response1.status_code}")
result1 = response1.json()
print(f"Response: {json.dumps(result1, indent=2)}")

# Extract conversation ID
conv_id = result1.get('conversation_id')
print(f"\nConversation ID: {conv_id}")

# Test 2: Get conversation context
print("\n" + "=" * 60)
print("TEST 2: Get conversation context")
print("=" * 60)

response2 = requests.get(
    f"http://localhost:5000/api/ai-assistant/conversations/{conv_id}/context"
)

print(f"Status: {response2.status_code}")
context_result = response2.json()
print(f"Context: {json.dumps(context_result, indent=2)}")

# Test 3: Send another message with conversation_id
print("\n" + "=" * 60)
print("TEST 3: Send message with existing conversation_id")
print("=" * 60)

response3 = requests.post(
    "http://localhost:5000/api/ai-assistant/chat",
    json={
        "message": "test again",
        "conversation_id": conv_id,
        "context": {
            "datasource": "hana"
        }
    }
)

print(f"Status: {response3.status_code}")
result3 = response3.json()
print(f"Response: {json.dumps(result3, indent=2)}")

# Test 4: Check context again
print("\n" + "=" * 60)
print("TEST 4: Check context again after second message")
print("=" * 60)

response4 = requests.get(
    f"http://localhost:5000/api/ai-assistant/conversations/{conv_id}/context"
)

print(f"Status: {response4.status_code}")
context_result2 = response4.json()
print(f"Context: {json.dumps(context_result2, indent=2)}")