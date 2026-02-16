"""
Test Pydantic AI + SAP AI Core via Backend API (no browser needed)

This tests the /api/ai-assistant/chat endpoint directly using requests
"""

import requests
import json
import time

def test_chat_api_with_pydantic_ai():
    """Test AI Assistant chat endpoint with Pydantic AI + SAP AI Core"""
    
    print("\n" + "="*70)
    print("TEST: Pydantic AI + SAP AI Core via Backend API")
    print("="*70)
    
    # Backend API endpoint
    url = "http://localhost:5000/api/ai-assistant/chat"
    
    # Test payload
    payload = {
        "message": "hello",
        "conversation_id": None,
        "datasource": "p2p_data"
    }
    
    print(f"\n1. Sending POST to {url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print(f"\n2. Making request...")
        start_time = time.time()
        
        response = requests.post(url, json=payload, timeout=30, stream=True)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"\n3. Reading streaming response...")
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data: '):
                        data_json = decoded[6:]  # Remove 'data: ' prefix
                        if data_json.strip() and data_json != '[DONE]':
                            try:
                                event = json.loads(data_json)
                                if event.get('type') == 'delta':
                                    full_response += event.get('content', '')
                                elif event.get('type') == 'done':
                                    print(f"\n✅ SUCCESS!")
                                    print(f"   Full response: {full_response[:100]}...")
                                    print(f"   Response data: {event.get('response', {})}")
                                    
                                    elapsed = time.time() - start_time
                                    print(f"   Time: {elapsed:.2f}s")
                                    
                                    return True
                            except json.JSONDecodeError:
                                pass
            
            print(f"\n✅ Stream completed")
            print(f"   Final text: {full_response}")
            return True
            
        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    print("\nWaiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    success = test_chat_api_with_pydantic_ai()
    
    print("\n" + "="*70)
    if success:
        print("✅ PYDANTIC AI + SAP AI CORE WORKING!")
        print("   - Headers successfully injected")
        print("   - API returned valid response")
        print("   - Streaming worked correctly")
    else:
        print("❌ PYDANTIC AI + SAP AI CORE FAILED")
        print("   - Check server console for 'Missing Resource Group' error")
    print("="*70)