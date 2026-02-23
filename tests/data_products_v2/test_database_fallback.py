"""
Test: Data Products V2 Database Fallback Mechanism

Tests that HANA fallback to SQLite works correctly when HANA unavailable.
Validates the repository factory and API behavior.

Author: P2P Development Team
Date: 2026-02-23
"""

import pytest
import requests
from modules.data_products_v2.repositories.repository_factory import DataProductRepositoryFactory


class TestDatabaseFallback:
    """Test database fallback from HANA to SQLite"""
    
    def test_repository_factory_creates_sqlite(self):
        """Test: Factory creates SQLite repository"""
        repo = DataProductRepositoryFactory.create('sqlite')
        assert repo is not None
        assert hasattr(repo, 'get_data_products')
    
    def test_repository_factory_requires_hana_params(self):
        """Test: Factory requires HANA connection params"""
        with pytest.raises(ValueError, match="HANA repository requires"):
            DataProductRepositoryFactory.create('hana')
    
    def test_repository_factory_invalid_source(self):
        """Test: Factory rejects invalid source type"""
        with pytest.raises(ValueError, match="Unknown source type"):
            DataProductRepositoryFactory.create('invalid_source')
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_data_products_api_returns_sqlite_data(self):
        """
        Test: API returns data products from SQLite when HANA unavailable
        
        Contract Validation:
        - Status code 200
        - Response contains 'data_products' list
        - Response contains 'count' field
        - Each product has required fields
        """
        # ARRANGE
        url = "http://localhost:5000/api/data-products"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT - API Contract
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'data_products' in data, \
            "Response missing 'data_products' field"
        assert 'count' in data, \
            "Response missing 'count' field"
        
        assert isinstance(data['data_products'], list), \
            "'data_products' must be a list"
        assert data['count'] > 0, \
            "Expected at least one data product"
        
        # Validate first product structure
        product = data['data_products'][0]
        required_fields = [
            'product_name', 'namespace', 'source', 
            'schema_name', 'table_count'
        ]
        for field in required_fields:
            assert field in product, \
                f"Product missing required field: {field}"
        
        # Validate fallback to SQLite
        assert product['source'] == 'sqlite', \
            "Expected source='sqlite' when HANA unavailable"
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_data_products_api_product_structure(self):
        """
        Test: Each data product has correct structure
        
        Contract Validation:
        - product_name (string)
        - namespace (string)
        - source (string, one of: hana, sqlite)
        - schema_name (string)
        - table_count (integer)
        - display_name (optional string)
        - description (optional string)
        """
        # ARRANGE
        url = "http://localhost:5000/api/data-products"
        
        # ACT
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # ASSERT - Product Structure
        for product in data['data_products']:
            # Required fields with type validation
            assert isinstance(product['product_name'], str)
            assert isinstance(product['namespace'], str)
            assert isinstance(product['source'], str)
            assert isinstance(product['schema_name'], str)
            assert isinstance(product['table_count'], int)
            
            # Source must be valid
            assert product['source'] in ['hana', 'sqlite'], \
                f"Invalid source: {product['source']}"
            
            # Optional fields
            if 'display_name' in product:
                assert isinstance(product['display_name'], str)
            if 'description' in product:
                assert isinstance(product['description'], str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])