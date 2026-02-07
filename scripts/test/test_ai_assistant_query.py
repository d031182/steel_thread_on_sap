#!/usr/bin/env python3
"""
Test script to verify AI Assistant database querying via DI
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.sqlite_connection.backend import SQLiteDataSource
from modules.ai_assistant.backend.agent_service import AgentService

def main():
    print("=" * 60)
    print("AI Assistant Database Query Test")
    print("=" * 60)
    
    # Initialize SQLite data source (same as app.py does)
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'p2p_data_products.db')
    print(f"\n1. Initializing SQLite data source...")
    print(f"   Database: {db_path}")
    print(f"   Exists: {os.path.exists(db_path)}")
    print(f"   Size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes")
    
    data_source = SQLiteDataSource(db_path=db_path)
    
    # Test data source directly
    print(f"\n2. Testing data source connection...")
    products = data_source.get_data_products()
    print(f"   Data products found: {len(products)}")
    for p in products:
        print(f"   - {p['productName']} ({p.get('tableCount', 0)} tables)")
    
    # Initialize AI agent with injected data source
    print(f"\n3. Initializing AI Agent with injected data source...")
    try:
        agent_service = AgentService(data_source)
        print(f"   ✓ Agent initialized successfully")
        print(f"   Model: {agent_service.config.model}")
    except ValueError as e:
        print(f"   ✗ Failed: {e}")
        print(f"\n   NOTE: You need GROQ_API_KEY in .env file to test AI queries")
        return
    
    # Test query
    print(f"\n4. Testing AI query: 'Show me blocked invoices'")
    print(f"   (This will call Groq API and may use database tools)")
    print(f"   -" * 30)
    
    result = agent_service.query("Show me blocked invoices from SupplierInvoice table")
    
    print(f"\n5. Query Result:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Response: {result['response'][:500]}...")
        print(f"   Tokens used: {result['tokens_used']}")
    else:
        print(f"   Error: {result['error']}")
    
    print(f"\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()