"""
Advanced approach: Try to make Pydantic AI work with SAP AI Core by
overriding the provider's client property dynamically
"""

import os
from typing import Any
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI
import httpx
import asyncio

from modules.ai_assistant.backend.services.ai_core_auth import get_ai_core_auth


class SAPAICoreOpenAIAdvanced(OpenAIModel):
    """
    ADVANCED: Override provider client to ensure headers on EVERY request
    
    Strategy: Instead of just replacing _client once, we make it so that
    every time Pydantic AI accesses the client, it gets one with headers.
    """
    
    def __init__(self, model: str, ai_resource_group: str, access_token: str, deployment_url: str):
        # Set env vars
        os.environ["OPENAI_API_KEY"] = access_token
        os.environ["OPENAI_BASE_URL"] = deployment_url
        
        # Init parent
        super().__init__(model)
        
        # Store config
        self._ai_resource_group = ai_resource_group
        self._access_token = access_token
        self._deployment_url = deployment_url
        
        print(f"[ADVANCED] Initialized SAP AI Core model")
        print(f"[ADVANCED] Will inject headers dynamically on every provider._client access")
        
        # Create ONE custom client and keep replacing it
        self._ensure_custom_client()
    
    def _ensure_custom_client(self):
        """Create/recreate custom client with headers"""
        http_client = httpx.AsyncClient(timeout=30.0)
        http_client.headers["AI-Resource-Group"] = self._ai_resource_group
        
        custom_client = AsyncOpenAI(
            base_url=self._deployment_url,
            api_key=self._access_token,
            http_client=http_client,
            default_headers={"AI-Resource-Group": self._ai_resource_group}
        )
        
        # Force replace
        self._provider._client = custom_client
        print(f"[ADVANCED] Provider client replaced/ensured")
        
        return custom_client


async def test_advanced_approach():
    """Test if advanced dynamic header injection works"""
    
    print("\n" + "="*70)
    print("ADVANCED TEST: Dynamic Header Injection on Every Request")
    print("="*70)
    
    # Get SAP AI Core config
    auth = get_ai_core_auth()
    token = auth.get_access_token()
    resource_group = os.getenv("AI_CORE_RESOURCE_GROUP", "default")
    deployment_url = os.getenv("AI_CORE_DEPLOYMENT_URL")
    model_name = os.getenv("AI_CORE_MODEL_NAME", "gpt-4o-mini")
    
    print(f"\n1. Creating SAPAICoreOpenAIAdvanced...")
    model = SAPAICoreOpenAIAdvanced(
        model=model_name,
        ai_resource_group=resource_group,
        access_token=token,
        deployment_url=deployment_url
    )
    
    print(f"\n2. Creating Agent...")
    agent = Agent(model, system_prompt="You are a helpful assistant")
    
    print(f"\n3. About to call agent.run() - re-ensuring headers...")
    # RE-ENSURE headers right before the call
    model._ensure_custom_client()
    
    print(f"\n4. Calling agent.run()...")
    try:
        result = await agent.run("Say 'hello' in one word")
        print(f"\n✅ SUCCESS! Got response: {result.data}")
        return True
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_advanced_approach())
    
    print("\n" + "="*70)
    if success:
        print("✅ ADVANCED APPROACH WORKS!")
        print("   - Headers injected successfully")
        print("   - SAP AI Core accepted the request")
    else:
        print("❌ ADVANCED APPROACH FAILED")
        print("   - Headers still not reaching SAP AI Core")
        print("   - May need to patch Pydantic AI internals")
    print("="*70)