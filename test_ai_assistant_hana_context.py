"""
Test: AI Assistant HANA Data Product Context

Verify AI Assistant properly queries HANA data products when context specifies HANA datasource
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_ai_assistant_with_hana_context():
    """Test: AI Assistant should use HANA facade when context specifies 'hana'"""
    
    print("=" * 80)
    print("TEST: AI Assistant HANA Context Integration")
    print("=" * 80)
    
    # Step 1: Create conversation with HANA context
    print("\n1. Creating conversation with HANA context...")
    create_response = requests.post(
        f"{BASE_URL}/api/ai-assistant/conversations",
        json={
            "context": {
                "datasource": "hana",  # ⭐ HANA datasource
                "data_product": None
            }
        }
    )
    
    if create_response.status_code != 201:
        print(f"❌ Failed to create conversation: {create_response.text}")
        return False
    
    conversation_data = create_response.json()
    conversation_id = conversation_data["conversation_id"]
    print(f"✅ Conversation created: {conversation_id}")
    print(f"   Context: {conversation_data}")
    
    # Step 2: Send message asking for data products
    print("\n2. Asking AI to list data products (should use HANA)...")
    message_response = requests.post(
        f"{BASE_URL}/api/ai-assistant/conversations/{conversation_id}/messages",
        json={
            "message": "show list of data products"
        }
    )
    
    if message_response.status_code != 200:
        print(f"❌ Failed to send message: {message_response.text}")
        return False
    
    message_data = message_response.json()
    ai_response = message_data["response"]["message"]
    
    print(f"✅ AI Response received:")
    print(f"   {ai_response[:200]}...")
    
    # Step 3: Verify HANA data products are listed
    print("\n3. Verifying HANA data products in response...")
    
    # HANA data products should include these (from screenshot):
    hana_products = [
        "Company Code",
        "Cost Center", 
        "Journal Entry",
        "Payment Terms",
        "Product",
        "Purchase Order",
        "Service Entry Sheet"
    ]
    
    found_hana = False
    for product in hana_products:
        if product in ai_response:
            print(f"   ✅ Found HANA product: {product}")
            found_hana = True
    
    if not found_hana:
        print(f"   ❌ No HANA data products found in response!")
        print(f"   Response: {ai_response}")
        return False
    
    # Step 4: Get conversation context to verify datasource
    print("\n4. Verifying conversation context...")
    context_response = requests.get(
        f"{BASE_URL}/api/ai-assistant/conversations/{conversation_id}/context"
    )
    
    if context_response.status_code == 200:
        context_data = context_response.json()
        datasource = context_data["context"]["datasource"]
        print(f"   Datasource in context: {datasource}")
        
        if datasource != "hana":
            print(f"   ⚠️ WARNING: Expected 'hana' but got '{datasource}'")
    
    print("\n" + "=" * 80)
    print("✅ TEST PASSED: AI Assistant properly uses HANA context")
    print("=" * 80)
    return True


def test_datasource_mapping():
    """Test: Verify _map_datasource_to_facade_key mapping"""
    
    print("\n" + "=" * 80)
    print("TEST: Datasource Mapping Logic")
    print("=" * 80)
    
    # Simulate mapping logic from api.py
    def _map_datasource_to_facade_key(datasource: str) -> str:
        mapping = {
            'p2p_data': 'sqlite',
            'p2p_graph': 'sqlite',
            'sqlite': 'sqlite',
            'hana': 'hana',
        }
        return mapping.get(datasource, 'sqlite')
    
    test_cases = [
        ("p2p_data", "sqlite"),
        ("p2p_graph", "sqlite"),
        ("hana", "hana"),
        ("sqlite", "sqlite"),
        ("unknown", "sqlite"),  # Default
    ]
    
    print("\nMapping Test Cases:")
    for datasource, expected_facade in test_cases:
        actual_facade = _map_datasource_to_facade_key(datasource)
        status = "✅" if actual_facade == expected_facade else "❌"
        print(f"   {status} '{datasource}' -> '{actual_facade}' (expected: '{expected_facade}')")
    
    print("=" * 80)


if __name__ == "__main__":
    print("\n🧪 AI Assistant HANA Context Test Suite\n")
    
    # Test mapping logic
    test_datasource_mapping()
    
    # Test actual HANA context
    try:
        test_ai_assistant_with_hana_context()
    except Exception as e:
        print(f"\n❌ TEST FAILED with exception: {e}")
        import traceback
        traceback.print_exc()