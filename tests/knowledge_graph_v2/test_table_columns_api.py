"""
API Contract Tests for Knowledge Graph Table Columns Endpoint (KGV-001)

Tests the /api/knowledge-graph/tables/<table_name>/columns endpoint.
This validates the Column Explorer Panel API contract.

Test Strategy:
- Test successful column retrieval
- Test filtering by semantic_type
- Test search functionality
- Test error handling (table not found)
- Verify response structure matches API contract
"""
import pytest
import requests


class TestTableColumnsAPI:
    """Test suite for table columns endpoint (KGV-001)"""
    
    BASE_URL = "http://localhost:5000"
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_get_table_columns_success(self):
        """
        Test: GET /api/knowledge-graph/tables/{table_name}/columns returns columns
        
        Validates:
        - 200 status code
        - Response contains 'success': true
        - Response contains 'data' with table_name and columns array
        - Columns have expected metadata fields
        """
        # ARRANGE
        table_name = "PurchaseOrder"
        url = f"{self.BASE_URL}/api/knowledge-graph/tables/{table_name}/columns"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] is True, "Expected success=True"
        assert 'data' in data, "Response must contain 'data' key"
        
        result_data = data['data']
        assert result_data['table_name'] == table_name, f"Expected table_name={table_name}"
        assert 'columns' in result_data, "Data must contain 'columns' array"
        assert isinstance(result_data['columns'], list), "columns must be array"
        assert len(result_data['columns']) > 0, "Should have at least one column"
        
        # Validate column structure
        first_column = result_data['columns'][0]
        required_fields = [
            'name', 'type', 'is_key', 'is_nullable',
            'display_label', 'description', 'semantic_type'
        ]
        for field in required_fields:
            assert field in first_column, f"Column must have '{field}' field"
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_get_table_columns_with_semantic_type_filter(self):
        """
        Test: Filtering by semantic_type parameter
        
        Validates:
        - Query parameter semantic_type filters columns correctly
        - Only columns with matching semantic_type are returned
        - filters_applied metadata is correct
        """
        # ARRANGE
        table_name = "PurchaseOrder"
        semantic_type = "amount"
        url = f"{self.BASE_URL}/api/knowledge-graph/tables/{table_name}/columns"
        params = {'semantic_type': semantic_type}
        
        # ACT
        response = requests.get(url, params=params, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        
        result_data = data['data']
        columns = result_data['columns']
        
        # All returned columns should have the semantic_type filter
        for col in columns:
            assert col['semantic_type'] == semantic_type, \
                f"Column {col['name']} has semantic_type={col['semantic_type']}, expected {semantic_type}"
        
        # Verify filter metadata
        filters = result_data.get('filters_applied', {})
        assert filters.get('semantic_type') == semantic_type
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_get_table_columns_with_search(self):
        """
        Test: Search parameter filters columns by name/label/description
        
        Validates:
        - Query parameter search filters columns correctly
        - Search is case-insensitive
        - filters_applied metadata is correct
        """
        # ARRANGE
        table_name = "PurchaseOrder"
        search_term = "id"  # Common in column names
        url = f"{self.BASE_URL}/api/knowledge-graph/tables/{table_name}/columns"
        params = {'search': search_term}
        
        # ACT
        response = requests.get(url, params=params, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        
        result_data = data['data']
        columns = result_data['columns']
        
        # All returned columns should match search term (case-insensitive)
        search_lower = search_term.lower()
        for col in columns:
            name_match = search_lower in col['name'].lower()
            label_match = search_lower in col['display_label'].lower()
            desc_match = search_lower in col.get('description', '').lower()
            
            assert name_match or label_match or desc_match, \
                f"Column {col['name']} does not match search term '{search_term}'"
        
        # Verify filter metadata
        filters = result_data.get('filters_applied', {})
        assert filters.get('search') == search_term.lower()
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_get_table_columns_table_not_found(self):
        """
        Test: 404 error when table not found
        
        Validates:
        - 404 status code for non-existent table
        - Error response has success=False
        - Error message is descriptive
        """
        # ARRANGE
        table_name = "NonExistentTable123"
        url = f"{self.BASE_URL}/api/knowledge-graph/tables/{table_name}/columns"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        data = response.json()
        assert data['success'] is False, "Expected success=False for not found"
        assert 'error' in data, "Error response must contain 'error' field"
        assert 'not found' in data['error'].lower(), "Error should mention 'not found'"
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_get_table_columns_multiple_filters(self):
        """
        Test: Combining multiple filters (semantic_type + search)
        
        Validates:
        - Both filters are applied correctly
        - filters_applied metadata shows both filters
        """
        # ARRANGE
        table_name = "PurchaseOrder"
        url = f"{self.BASE_URL}/api/knowledge-graph/tables/{table_name}/columns"
        params = {
            'semantic_type': 'amount',
            'search': 'gross'
        }
        
        # ACT
        response = requests.get(url, params=params, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        
        result_data = data['data']
        columns = result_data['columns']
        
        # Verify both filters applied
        for col in columns:
            # Check semantic_type filter
            assert col['semantic_type'] == params['semantic_type']
            
            # Check search filter
            search_lower = params['search'].lower()
            name_match = search_lower in col['name'].lower()
            label_match = search_lower in col['display_label'].lower()
            desc_match = search_lower in col.get('description', '').lower()
            assert name_match or label_match or desc_match
        
        # Verify filter metadata
        filters = result_data.get('filters_applied', {})
        assert filters.get('semantic_type') == params['semantic_type']
        assert filters.get('search') == params['search'].lower()
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_get_table_columns_total_count(self):
        """
        Test: Response includes total_columns count
        
        Validates:
        - total_columns field present
        - Count matches array length
        """
        # ARRANGE
        table_name = "PurchaseOrder"
        url = f"{self.BASE_URL}/api/knowledge-graph/tables/{table_name}/columns"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        result_data = data['data']
        
        assert 'total_columns' in result_data, "Response must include total_columns"
        assert result_data['total_columns'] == len(result_data['columns']), \
            "total_columns must match columns array length"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])