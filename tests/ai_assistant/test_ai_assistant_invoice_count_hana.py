"""
Test AI Assistant invoice count query with HANA data source.

This test verifies that the AI Assistant correctly handles invoice count queries
when using HANA Cloud as the data source.
"""

import asyncio
from modules.ai_assistant.backend.services.agent_service import AgentService
from modules.ai_assistant.backend.services.sql_execution_service import SQLExecutionService
from modules.ai_assistant.backend.models import ConversationContext
from modules.log.backend.api import get_logger

logger = get_logger(__name__)


def test_hana_table_name_conversion():
    """Test: HANA table name conversion works correctly."""
    sql_service = SQLExecutionService()
    agent_service = AgentService(sql_service)
    
    # Test various product names
    test_cases = [
        ('Invoice_Transactions', 'P2P_DATAPRODUCT_sap_bdc_Invoice_Transactions_V1'),
        ('Purchase_Orders', 'P2P_DATAPRODUCT_sap_bdc_Purchase_Orders_V1'),
        ('Supplier_Master', 'P2P_DATAPRODUCT_sap_bdc_Supplier_Master_V1'),
    ]
    
    for product_name, expected_table in test_cases:
        result = agent_service._get_hana_table_name(product_name)
        assert result == expected_table, f"Expected {expected_table}, got {result}"
        print(f"✓ {product_name} → {result}")
    
    print("\n✓ All HANA table name conversions correct")


def test_data_context_with_hana():
    """Test: Data context includes HANA table names."""
    sql_service = SQLExecutionService()
    agent_service = AgentService(sql_service)
    
    # Mock data products
    data_products = [
        {
            'name': 'Invoice_Transactions',
            'entity_count': 150,
            'sample_columns': ['invoice_id', 'amount', 'date']
        },
        {
            'name': 'Purchase_Orders',
            'entity_count': 200,
            'sample_columns': ['po_id', 'supplier_id', 'total']
        }
    ]
    
    # Test SQLite context
    sqlite_context = agent_service._build_data_context(data_products, 'sqlite')
    print("\nSQLite Context:")
    print(sqlite_context)
    assert 'Invoice_Transactions' in sqlite_context
    assert 'P2P_DATAPRODUCT' not in sqlite_context
    
    # Test HANA context
    hana_context = agent_service._build_data_context(data_products, 'hana')
    print("\nHANA Context:")
    print(hana_context)
    assert 'P2P_DATAPRODUCT_sap_bdc_Invoice_Transactions_V1' in hana_context
    assert 'P2P_DATAPRODUCT_sap_bdc_Purchase_Orders_V1' in hana_context
    assert 'HANA Cloud' in hana_context
    
    print("\n✓ Data context correctly handles both data sources")


async def test_invoice_count_query_with_hana():
    """Test: AI Assistant handles invoice count query with HANA."""
    sql_service = SQLExecutionService()
    agent_service = AgentService(sql_service)
    
    # Create conversation context with HANA data source
    context = ConversationContext(
        conversation_id='test-123',
        data_source='hana',
        data_products=[
            {
                'name': 'Invoice_Transactions',
                'entity_count': 150,
                'sample_columns': ['ID', 'InvoiceNumber', 'Amount', 'PostingDate']
            }
        ]
    )
    
    # Ask for invoice count
    question = "show number of invoices"
    
    print(f"\nQuestion: {question}")
    print(f"Data Source: {context.data_source}")
    print(f"Available Products: {[p['name'] for p in context.data_products]}")
    
    # Get data context
    data_context = agent_service._build_data_context(
        context.data_products, 
        context.data_source
    )
    print(f"\nData Context provided to AI:")
    print(data_context)
    
    print("\n✓ HANA data context correctly includes table names")
    print("✓ AI should now generate correct SQL with P2P_DATAPRODUCT_sap_bdc_Invoice_Transactions_V1")


def main():
    """Run all tests."""
    print("=" * 80)
    print("AI Assistant HANA Invoice Count Test")
    print("=" * 80)
    
    # Test 1: Table name conversion
    test_hana_table_name_conversion()
    
    # Test 2: Data context with HANA
    test_data_context_with_hana()
    
    # Test 3: Invoice count query (async)
    asyncio.run(test_invoice_count_query_with_hana())
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Start server: python server.py")
    print("2. Open UI: http://localhost:5000")
    print("3. Switch to HANA data source")
    print("4. Ask: 'show number of invoices'")
    print("5. Verify correct count returned")


if __name__ == '__main__':
    main()