"""
Unit tests for SQLiteDataProductsService

Tests the Data Products module's SQLite service to ensure:
1. No graph_* tables are returned (module separation)
2. Business tables are properly grouped and returned
3. Database path resolution works correctly

@pytest.mark.unit - Fast, isolated tests
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path


@pytest.mark.unit
@pytest.mark.fast
def test_get_data_products_excludes_graph_tables():
    """
    Test that get_data_products() does NOT return graph_* tables.
    
    This ensures module separation between Data Products and Knowledge Graph.
    Even if graph_* tables existed in the database (they shouldn't),
    they must not appear in the Data Products list.
    """
    # ARRANGE
    from modules.data_products.backend.sqlite_data_products_service import SQLiteDataProductsService
    
    # Create temporary database with both business and graph tables
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = os.path.join(temp_dir, 'test.db')
        
        # Create test database with mixed tables
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Create business tables (should appear)
        cursor.execute("CREATE TABLE PurchaseOrder (id INTEGER PRIMARY KEY)")
        cursor.execute("CREATE TABLE Supplier (id INTEGER PRIMARY KEY)")
        
        # Create graph cache tables (should NOT appear)
        cursor.execute("CREATE TABLE graph_nodes (id INTEGER PRIMARY KEY)")
        cursor.execute("CREATE TABLE graph_edges (id INTEGER PRIMARY KEY)")
        cursor.execute("CREATE TABLE graph_ontology (id INTEGER PRIMARY KEY)")
        
        conn.commit()
        conn.close()
        
        # Initialize service with test database
        service = SQLiteDataProductsService(db_path=test_db_path)
        
        # ACT
        products = service.get_data_products()
        
        # ASSERT
        # Extract all product names
        product_names = [p['productName'] for p in products]
        
        # Business tables should be present
        assert 'PurchaseOrder' in product_names, "Business table PurchaseOrder should be in products"
        assert 'Supplier' in product_names, "Business table Supplier should be in products"
        
        # Graph tables should NOT be present
        assert 'graph_nodes' not in product_names, "Graph cache table should NOT appear in products"
        assert 'graph_edges' not in product_names, "Graph cache table should NOT appear in products"
        assert 'graph_ontology' not in product_names, "Graph cache table should NOT appear in products"
        
        # Verify no product name starts with 'graph_'
        graph_products = [p for p in product_names if p.startswith('graph_')]
        assert len(graph_products) == 0, f"Found unexpected graph products: {graph_products}"


@pytest.mark.unit
@pytest.mark.fast
def test_actual_database_has_no_graph_tables():
    """
    Test that the actual production database does NOT contain graph_* tables.
    
    This verifies that database separation (v3.28 Strategy Pattern) is working.
    Data Products module should only have business tables.
    """
    # ARRANGE
    from modules.data_products.backend.sqlite_data_products_service import SQLiteDataProductsService
    
    # Check if production database exists
    prod_db_path = Path('modules/data_products/database/p2p_data.db')
    
    if not prod_db_path.exists():
        pytest.skip("Production database not found - test only runs when database exists")
    
    # ACT
    conn = sqlite3.connect(str(prod_db_path))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'graph_%'
        ORDER BY name
    """)
    graph_tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # ASSERT
    assert len(graph_tables) == 0, f"Production database should NOT contain graph tables, found: {graph_tables}"


@pytest.mark.unit
@pytest.mark.fast  
def test_get_data_products_returns_business_tables():
    """
    Test that get_data_products() returns expected business tables.
    
    Verifies the service correctly groups and returns business data products.
    """
    # ARRANGE
    from modules.data_products.backend.sqlite_data_products_service import SQLiteDataProductsService
    
    prod_db_path = Path('modules/data_products/database/p2p_data.db')
    
    if not prod_db_path.exists():
        pytest.skip("Production database not found")
    
    service = SQLiteDataProductsService(db_path=str(prod_db_path))
    
    # ACT
    products = service.get_data_products()
    
    # ASSERT
    assert len(products) > 0, "Should return at least one data product"
    
    # Check expected business products exist
    product_names = [p['productName'] for p in products]
    expected_products = ['PurchaseOrder', 'Supplier', 'Product', 'CompanyCode']
    
    for expected in expected_products:
        assert expected in product_names, f"Expected product {expected} not found in: {product_names}"
    
    # Verify structure of returned products
    for product in products:
        assert 'productName' in product, "Product should have productName"
        assert 'displayName' in product, "Product should have displayName"
        assert 'source' in product, "Product should have source"
        assert product['source'] == 'sqlite', "Source should be 'sqlite'"
        assert 'tableCount' in product, "Product should have tableCount"
        assert product['tableCount'] > 0, "Product should have at least one table"