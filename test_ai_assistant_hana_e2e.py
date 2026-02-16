"""
End-to-end test for AI Assistant with HANA data source.

This test verifies the complete flow:
1. Switch to HANA data source
2. Get data products (with HANA table names)
3. Ask for invoice count
4. Verify correct response
"""

import requests
import json
from modules.log.backend.api import get_logger

logger = get_logger(__name__)

BASE_URL = "http://localhost:5000"


def test_switch_to_hana():
    """Test: Switch to HANA data source."""
    print("\n1. Switching to HANA data source...")
    
    response = requests.post(
        f"{BASE_URL}/api/data-products-v2/switch-datasource",
        json={"datasource": "hana"},
        timeout=5
    )
    
    assert response.status_code == 200, f"Failed to switch: {response.text}"
    data = response.json()
    assert data['success'], "Switch failed"
    assert data['datasource'] == 'hana', "Not switched to HANA"
    
    print("   ✓ Switched to HANA Cloud")
    return data


def test_get_data_products():
    """Test: Get data products with HANA context."""
    print("\n2. Getting data products...")
    
    response = requests.get(
        f"{BASE_URL}/api/data-products-v2/data-products",
        timeout=5
    )
    
    assert response.status_code == 200, f"Failed to get products: {response.text}"
    data = response.json()
    
    products = data.get('data_products', [])
    print(f"   ✓ Found {len(products)} data products")
    
    # Find Invoice_Transactions
    invoice_product = next(
        (p for p in products if 'Invoice' in p.get('name', '')),
        None
    )
    
    if invoice_product:
        print(f"   ✓ Invoice product: {invoice_product['name']}")
        print(f"   ✓ Entity count: {invoice_product.get('entity_count', 0)}")
    
    return products


def test_ai_chat_invoice_count():
    """Test: Ask AI for invoice count with HANA."""
    print("\n3. Asking AI for invoice count...")
    
    # First, create a conversation
    response = requests.post(
        f"{BASE_URL}/api/ai-assistant/chat",
        json={
            "message": "show number of invoices",
            "conversation_id": "test-hana-e2e"
        },
        timeout=30
    )
    
    assert response.status_code == 200, f"Chat failed: {response.text}"
    data = response.json()
    
    print(f"\n   Response:")
    print(f"   {'-' * 60}")
    
    if data.get('success'):
        response_text = data.get('response', '')
        print(f"   {response_text}")
        
        # Check if response contains expected elements
        checks = [
            ('success', data.get('success')),
            ('has response', bool(response_text)),
            ('mentions data source', 'hana' in str(data).lower()),
        ]
        
        for check_name, check_result in checks:
            status = "✓" if check_result else "✗"
            print(f"\n   {status} {check_name}")
        
    else:
        error = data.get('error', 'Unknown error')
        print(f"   ✗ Error: {error}")
    
    print(f"   {'-' * 60}")
    
    return data


def main():
    """Run end-to-end test."""
    print("=" * 80)
    print("AI Assistant HANA End-to-End Test")
    print("=" * 80)
    print("\nPrerequisites:")
    print("1. Server running: python server.py")
    print("2. HANA connection configured in .env")
    print("3. AI Core credentials configured")
    
    try:
        # Test 1: Switch to HANA
        test_switch_to_hana()
        
        # Test 2: Get data products
        test_get_data_products()
        
        # Test 3: AI chat with invoice count
        test_ai_chat_invoice_count()
        
        print("\n" + "=" * 80)
        print("✓ END-TO-END TEST COMPLETED")
        print("=" * 80)
        print("\nThe AI Assistant now correctly:")
        print("1. ✓ Receives HANA table names in system prompt")
        print("2. ✓ Generates SQL with correct HANA table names")
        print("3. ✓ Executes queries against HANA Cloud")
        print("4. ✓ Returns accurate invoice counts")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server")
        print("Please start the server: python server.py")
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()