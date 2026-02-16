"""
Test script to verify SAP AI Core configuration

Tests:
1. OAuth2 token acquisition
2. Model endpoint connectivity  
3. Simple chat completion
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_oauth2_token():
    """Test: Can we get OAuth2 token from AI Core?"""
    print("\n=== Test 1: OAuth2 Token Acquisition ===")
    
    try:
        from modules.ai_assistant.backend.services.ai_core_auth import get_ai_core_auth
        
        auth = get_ai_core_auth()
        token = auth.get_access_token()
        
        print(f"✅ Token acquired successfully")
        print(f"   Token length: {len(token)} chars")
        print(f"   Token preview: {token[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Token acquisition failed: {e}")
        return False


def test_model_endpoint():
    """Test: Can we reach AI Core model endpoint?"""
    print("\n=== Test 2: Model Endpoint Connectivity ===")
    
    try:
        from modules.ai_assistant.backend.services.ai_core_auth import get_ai_core_auth
        import requests
        
        auth = get_ai_core_auth()
        deployment_url = os.getenv("AI_CORE_DEPLOYMENT_URL")
        model_name = os.getenv("AI_CORE_MODEL_NAME", "gpt-4o-mini")
        
        # SAP AI Core chat completions endpoint
        url = f"{deployment_url}/chat/completions?api-version=2023-05-15"
        
        headers = auth.get_headers()
        
        payload = {
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        print(f"   Endpoint: {url}")
        print(f"   Model: {model_name}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Model endpoint reachable")
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                print(f"   Response: {data['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ Model endpoint error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False


def test_pydantic_ai_integration():
    """Test: Can Pydantic AI use AI Core?"""
    print("\n=== Test 3: Pydantic AI Integration ===")
    
    try:
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIModel
        from modules.ai_assistant.backend.services.ai_core_auth import get_ai_core_auth
        from openai import AsyncOpenAI
        import httpx
        
        # Get OAuth2 token
        auth = get_ai_core_auth()
        token = auth.get_access_token()
        resource_group = os.getenv("AI_CORE_RESOURCE_GROUP", "default")
        
        # Get deployment configuration
        deployment_url = os.getenv("AI_CORE_DEPLOYMENT_URL")
        model_name = os.getenv("AI_CORE_MODEL_NAME", "gpt-4o-mini")
        
        # Set environment variables for OpenAI-compatible API
        os.environ["OPENAI_API_KEY"] = token
        os.environ["OPENAI_BASE_URL"] = deployment_url
        
        # Create httpx client with SAP AI Core headers  
        http_client = httpx.AsyncClient(
            headers={"AI-Resource-Group": resource_group},
            timeout=30.0
        )
        
        # Create custom OpenAI client
        client = AsyncOpenAI(
            api_key=token,
            base_url=deployment_url,
            http_client=http_client
        )
        
        # Try using 'openai-chat' provider with environment variables
        # Pydantic AI should pick up OPENAI_API_KEY and OPENAI_BASE_URL
        agent = Agent(
            OpenAIModel(model_name, provider='openai-chat'),
            system_prompt="You are a helpful assistant"
        )
        
        # Run simple test
        result = agent.run_sync("Say 'Hello from AI Core' in exactly 5 words")
        
        print(f"✅ Pydantic AI integration works")
        print(f"   Response: {result.data}")
        return True
        
    except Exception as e:
        print(f"❌ Pydantic AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("SAP AI Core Configuration Test")
    print("=" * 60)
    
    # Check environment variables first
    print("\n=== Environment Variables ===")
    required_vars = [
        "AI_CORE_CLIENT_ID",
        "AI_CORE_CLIENT_SECRET", 
        "AI_CORE_AUTH_URL",
        "AI_CORE_DEPLOYMENT_URL",
        "AI_CORE_MODEL_NAME"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show preview (hide secrets)
            if "SECRET" in var or "TOKEN" in var:
                preview = f"{value[:20]}... (hidden)"
            else:
                preview = value
            print(f"✅ {var}: {preview}")
        else:
            print(f"❌ {var}: NOT SET")
            missing.append(var)
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("   Please update your .env file")
        return False
    
    # Run tests
    results = []
    results.append(("OAuth2 Token", test_oauth2_token()))
    results.append(("Model Endpoint", test_model_endpoint()))
    results.append(("Pydantic AI", test_pydantic_ai_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! AI Core is configured correctly.")
        print("   You can now use Joule with SAP AI Core.")
    else:
        print("\n⚠️  Some tests failed. Check configuration above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)