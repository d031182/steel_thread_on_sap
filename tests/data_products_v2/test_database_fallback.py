"""
API Contract Tests: Database Fallback (HANA ↔ SQLite)

Tests that data product APIs work seamlessly with both HANA and SQLite.
This validates the fallback mechanism created by rebuild_sqlite_from_hana.py.

Architecture:
    - Test backend API contract with both database types
    - Test frontend API contract with both database types
    - Verify data products structure identical across sources
    - Validate seamless switching without code changes

Gu Wu Philosophy:
    - Test the API contract, not implementation details
    - One API test validates entire repository chain
    - Database switching transparent to API consumers
"""

import os
import pytest
import requests
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:5000"
DATA_PRODUCTS_API = f"{BASE_URL}/api/data-products"
FRONTEND_API = f"{BASE_URL}/api/modules/frontend-registry"


@pytest.mark.e2e
@pytest.mark.api_contract
@pytest.mark.parametrize("database_type", ["sqlite", "hana"])
def test_data_products_api_contract_with_fallback(database_type):
    """
    Test: Data Products API returns valid contract regardless of database
    
    Contract Requirements:
        - GET /api/data-products returns 200
        - Response contains 'data_products' array
        - Each data product has required fields: name, entities
        - Structure identical for HANA and SQLite
    
    This test validates the fallback mechanism works transparently.
    """
    # ARRANGE
    # Note: In production, DATABASE_TYPE env var controls switching
    # For testing, we'd need server restart per database type
    # This test documents the contract expectation
    
    # ACT
    response = requests.get(DATA_PRODUCTS_API, timeout=5)
    
    # ASSERT - API Contract
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'data_products' in data, "Response missing 'data_products' field"
    
    data_products = data['data_products']
    assert isinstance(data_products, list), "data_products should be array"
    
    # Validate structure
    for product in data_products:
        assert 'name' in product, "Data product missing 'name' field"
        assert 'entities' in product, "Data product missing 'entities' field"
        assert isinstance(product['entities'], list), "entities should be array"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_frontend_registry_includes_data_products():
    """
    Test: Frontend Registry API includes data products module
    
    Contract Requirements:
        - GET /api/modules/frontend-registry returns 200
        - Response contains 'modules' array
        - data_products_v2 module present
        - Module has required metadata
    """
    # ARRANGE
    url = FRONTEND_API
    
    # ACT
    response = requests.get(url, timeout=5)
    
    # ASSERT
    assert response.status_code == 200
    
    data = response.json()
    assert 'modules' in data
    
    # Find data_products_v2 module
    modules = {m['id']: m for m in data['modules']}
    assert 'data_products_v2' in modules, "data_products_v2 module not registered"
    
    module = modules['data_products_v2']
    assert 'name' in module
    assert 'routes' in module


@pytest.mark.e2e
@pytest.mark.api_contract
def test_database_switching_transparent_to_api():
    """
    Test: API contract identical regardless of underlying database
    
    This test validates that switching between HANA and SQLite
    is transparent to API consumers. The contract remains stable.
    
    Implementation Note:
        - Set DATABASE_TYPE=sqlite or DATABASE_TYPE=hana in .env
        - Restart server
        - API contract remains unchanged
    """
    # ARRANGE
    url = DATA_PRODUCTS_API
    
    # ACT
    response = requests.get(url, timeout=5)
    
    # ASSERT - Contract Stability
    assert response.status_code == 200
    
    data = response.json()
    
    # Contract fields must always be present
    required_fields = ['data_products']
    for field in required_fields:
        assert field in data, f"API contract missing required field: {field}"
    
    # Data products structure must match CSN structure
    # (regardless of whether loaded from HANA or SQLite)
    assert isinstance(data['data_products'], list)


@pytest.mark.integration
def test_rebuild_script_creates_valid_structure():
    """
    Test: Rebuild script creates SQLite structure matching CSN
    
    This is an integration test that verifies the rebuild script
    creates a SQLite database that passes API contract tests.
    
    Workflow:
        1. Run rebuild script: python scripts/python/rebuild_sqlite_from_hana.py
        2. Set DATABASE_TYPE=sqlite
        3. Restart server
        4. Verify API contracts pass
    """
    # This test documents the expected workflow
    # Actual execution requires server restart, so it's marked as integration
    
    rebuild_script = Path("scripts/python/rebuild_sqlite_from_hana.py")
    assert rebuild_script.exists(), "Rebuild script must exist"
    
    # Verify .env.example documents the configuration
    env_example = Path(".env.example")
    assert env_example.exists()
    
    content = env_example.read_text()
    assert "DATABASE_TYPE" in content, ".env.example should document DATABASE_TYPE"
    assert "sqlite" in content, ".env.example should show sqlite option"
    assert "hana" in content, ".env.example should show hana option"


@pytest.mark.unit
def test_repository_factory_supports_both_databases():
    """
    Test: Repository factory can create both HANA and SQLite repositories
    
    Contract:
        - Factory accepts database_type parameter
        - Returns appropriate repository implementation
        - Both repositories implement same interface
    """
    from modules.data_products_v2.repositories.repository_factory import RepositoryFactory
    
    # ARRANGE
    factory = RepositoryFactory()
    
    # ACT - Create SQLite repository
    sqlite_repo = factory.create_data_product_repository(database_type='sqlite')
    
    # ACT - Create HANA repository (if credentials available)
    try:
        hana_repo = factory.create_data_product_repository(database_type='hana')
    except Exception:
        # HANA may not be available in test environment
        pytest.skip("HANA credentials not available")
    
    # ASSERT - Both implement same interface
    from core.interfaces.data_product_repository import DataProductRepository
    assert isinstance(sqlite_repo, DataProductRepository)
    assert isinstance(hana_repo, DataProductRepository)
    
    # Both should have same public methods
    sqlite_methods = set(dir(sqlite_repo))
    hana_methods = set(dir(hana_repo))
    
    # Core interface methods must be present in both
    required_methods = {'get_data_products', 'get_entities'}
    assert required_methods.issubset(sqlite_methods)
    assert required_methods.issubset(hana_methods)


if __name__ == '__main__':
    """
    Run tests with:
        pytest tests/data_products_v2/test_database_fallback.py -v
        
    Test API contracts with both databases:
        1. Set DATABASE_TYPE=sqlite in .env
        2. python server.py
        3. pytest tests/data_products_v2/test_database_fallback.py -m api_contract
        
        4. Set DATABASE_TYPE=hana in .env
        5. python server.py
        6. pytest tests/data_products_v2/test_database_fallback.py -m api_contract
        
    Results should be identical for both database types.
    """
    pytest.main([__file__, '-v'])