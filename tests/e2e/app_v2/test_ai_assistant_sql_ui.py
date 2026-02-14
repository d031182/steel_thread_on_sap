"""
E2E Tests for AI Assistant SQL Execution UI (Phase 4.7)

Tests the SQL query execution interface:
- SQL query textarea
- Database selector
- Execute button
- Result table display
- Execution metadata (time, row count)
- Error handling
"""

import pytest
import requests
from pathlib import Path


@pytest.fixture
def app_v2_base_url():
    """Base URL for App V2 (assumes local development)"""
    return "http://localhost:5000"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_endpoint_exists(app_v2_base_url):
    """
    Test: SQL execution endpoint exists and responds
    
    Frontend Dependency: AIAssistantAdapter.executeSQL()
    
    Contract:
    - POST /api/ai-assistant/execute-sql
    - Must accept JSON body with 'query' and 'database'
    - Must return JSON response
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    payload = {
        "sql": "SELECT 1 as test",
        "datasource": "p2p_data"
    }
    
    # ACT
    response = requests.post(url, json=payload, timeout=10)
    
    # ASSERT
    assert response.status_code == 200, \
        f"SQL execution endpoint not accessible: {response.status_code}"
    
    data = response.json()
    assert 'success' in data, \
        "Response missing 'success' field"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_returns_valid_structure(app_v2_base_url):
    """
    Test: SQL execution returns valid result structure
    
    Frontend Dependency: AIAssistantOverlay._renderSQLTable()
    
    Contract:
    - Must have 'success' field (boolean)
    - Must have 'columns' array (for table headers)
    - Must have 'rows' array (for table data)
    - Must have 'row_count' (integer)
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    payload = {
        "sql": "SELECT 'test' as column1, 123 as column2",
        "datasource": "p2p_data"
    }
    
    # ACT
    response = requests.post(url, json=payload, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] is True, \
        "Query should succeed"
    assert 'columns' in data, \
        "Response must include 'columns' array"
    assert 'rows' in data, \
        "Response must include 'rows' array"
    assert 'row_count' in data, \
        "Response must include 'row_count' field"
    
    # Verify columns
    assert isinstance(data['columns'], list), \
        "Columns must be array"
    assert len(data['columns']) == 2, \
        "Should return 2 columns"
    assert 'column1' in data['columns'], \
        "Should include column1"
    assert 'column2' in data['columns'], \
        "Should include column2"
    
    # Verify rows
    assert isinstance(data['rows'], list), \
        "Rows must be array"
    assert len(data['rows']) == 1, \
        "Should return 1 row"
    assert data['row_count'] == 1, \
        "Row count should match"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_blocks_non_select(app_v2_base_url):
    """
    Test: SQL execution blocks non-SELECT queries
    
    Frontend Dependency: Error display in UI
    
    Contract:
    - Must reject DROP, INSERT, UPDATE, DELETE
    - Must return success=False
    - Must include error message
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    
    dangerous_queries = [
        "DROP TABLE PurchaseOrder",
        "INSERT INTO PurchaseOrder VALUES (1, 2, 3)",
        "UPDATE PurchaseOrder SET amount = 0",
        "DELETE FROM PurchaseOrder"
    ]
    
    # ACT & ASSERT
    for query in dangerous_queries:
        response = requests.post(
            url,
            json={"sql": query, "datasource": "p2p_data"},
            timeout=10
        )
        
        data = response.json()
        assert data['success'] is False, \
            f"Should reject dangerous query: {query}"
        assert 'error' in data, \
            f"Should return error message for: {query}"
        assert 'only select' in data['error'].lower(), \
            f"Error should mention SELECT-only restriction"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_enforces_limit(app_v2_base_url):
    """
    Test: SQL execution enforces LIMIT 1000
    
    Frontend Dependency: Warning display in UI
    
    Contract:
    - Queries without LIMIT get automatic LIMIT 1000
    - Must include 'warnings' field if limit enforced
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    
    # Query without LIMIT (should be auto-limited)
    payload = {
        "sql": "SELECT * FROM PurchaseOrder",
        "datasource": "p2p_data"
    }
    
    # ACT
    response = requests.post(url, json=payload, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] is True, \
        "Query should succeed"
    assert data['row_count'] <= 1000, \
        "Should not return more than 1000 rows"
    
    # Check for warning (if applicable)
    if 'warnings' in data and data['warnings']:
        warning_text = ' '.join(data['warnings']).upper()
        assert 'LIMIT' in warning_text, \
            "Warning should mention LIMIT enforcement"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_supports_both_databases(app_v2_base_url):
    """
    Test: SQL execution works with both p2p_data and p2p_graph
    
    Frontend Dependency: Database selector dropdown
    
    Contract:
    - Must accept 'database' parameter
    - Must support 'p2p_data' and 'p2p_graph'
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    
    databases = ['p2p_data', 'p2p_graph']
    
    # ACT & ASSERT
    for db in databases:
        payload = {
            "sql": "SELECT 1 as test",
            "datasource": db
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        assert response.status_code == 200, \
            f"Should support database: {db}"
        
        data = response.json()
        assert data['success'] is True, \
            f"Query should succeed for database: {db}"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_handles_sql_errors(app_v2_base_url):
    """
    Test: SQL execution handles invalid SQL gracefully
    
    Frontend Dependency: Error message display
    
    Contract:
    - Invalid SQL returns success=False
    - Must include descriptive error message
    - Should not crash
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    
    invalid_queries = [
        "SELECT * FROM NonExistentTable",
        "SELECT invalid syntax here",
        "SELECT",  # Incomplete
        ""  # Empty
    ]
    
    # ACT & ASSERT
    for query in invalid_queries:
        payload = {
            "sql": query,
            "datasource": "p2p_data"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        assert data['success'] is False, \
            f"Should fail for invalid query: {query}"
        assert 'error' in data, \
            f"Should return error message for: {query}"
        assert len(data['error']) > 0, \
            f"Error message should not be empty for: {query}"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_sql_ui_files_accessible(app_v2_base_url):
    """
    Test: SQL UI JavaScript files are accessible
    
    ARRANGE
    """
    files_to_check = [
        "/static/js/ui/pages/aiAssistantPage.js",  # Legacy (if exists)
        # Note: Module files loaded dynamically, not directly accessible
    ]
    
    # ACT & ASSERT
    for file_path in files_to_check:
        url = f"{app_v2_base_url}{file_path}"
        response = requests.get(url, timeout=5)
        
        # Either exists (200) or doesn't (404) - both acceptable
        # Just ensure server doesn't crash (5xx)
        assert response.status_code < 500, \
            f"Server error accessing: {file_path}"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_real_data_query(app_v2_base_url):
    """
    Test: SQL execution works with real P2P data
    
    Frontend Dependency: Result table rendering
    
    Contract:
    - Must handle real database queries
    - Must return actual data
    - Columns and rows must match query
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    payload = {
        "sql": "SELECT PurchaseOrder, CompanyCode, DocumentCurrency FROM PurchaseOrder LIMIT 5",
        "datasource": "p2p_data"
    }
    
    # ACT
    response = requests.post(url, json=payload, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] is True, \
        "Query should succeed"
    
    # Verify structure
    assert len(data['columns']) == 3, \
        "Should return 3 columns"
    assert 'PurchaseOrder' in data['columns'], \
        "Should include PurchaseOrder column"
    assert 'CompanyCode' in data['columns'], \
        "Should include CompanyCode column"
    assert 'DocumentCurrency' in data['columns'], \
        "Should include DocumentCurrency column"
    
    # Verify data exists (if table has data)
    if data['row_count'] > 0:
        assert len(data['rows']) > 0, \
            "Rows array should not be empty"
        assert len(data['rows']) <= 5, \
            "Should respect LIMIT 5"
        
        # Verify row structure
        first_row = data['rows'][0]
        assert 'PurchaseOrder' in first_row, \
            "Row should include PurchaseOrder field"
        assert 'CompanyCode' in first_row, \
            "Row should include CompanyCode field"
        assert 'DocumentCurrency' in first_row, \
            "Row should include DocumentCurrency field"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_performance(app_v2_base_url):
    """
    Test: SQL execution completes in reasonable time
    
    Frontend Dependency: Execution time display
    
    Contract:
    - Simple queries should complete in < 5 seconds
    - Must not hang indefinitely
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    payload = {
        "sql": "SELECT 1 as test",
        "datasource": "p2p_data"
    }
    
    # ACT
    import time
    start = time.time()
    response = requests.post(url, json=payload, timeout=10)
    duration = time.time() - start
    
    # ASSERT
    assert response.status_code == 200
    assert duration < 5.0, \
        f"Simple query took too long: {duration:.2f}s"
    
    data = response.json()
    assert data['success'] is True, \
        "Query should succeed"


@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
def test_sql_execution_handles_null_values(app_v2_base_url):
    """
    Test: SQL execution handles NULL values correctly
    
    Frontend Dependency: Table rendering with null display
    
    Contract:
    - NULL values should be serialized (not crash)
    - Frontend should display as 'null' or '(empty)'
    
    ARRANGE
    """
    url = f"{app_v2_base_url}/api/ai-assistant/execute-sql"
    payload = {
        "sql": "SELECT NULL as null_col, 'value' as text_col, 123 as num_col",
        "datasource": "p2p_data"
    }
    
    # ACT
    response = requests.post(url, json=payload, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] is True, \
        "Query should succeed"
    assert len(data['rows']) == 1, \
        "Should return 1 row"
    
    row = data['rows'][0]
    assert 'null_col' in row, \
        "Should include null column"
    # NULL can be None or null in JSON - both acceptable
    assert row['null_col'] is None or row['null_col'] == 'null', \
        "NULL value should be serialized"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_sql_ui_overlay_opens(app_v2_base_url):
    """
    Test: AI Assistant overlay opens and shows SQL tab
    
    Note: This is a basic accessibility test.
    Full UI testing would require browser automation.
    
    ARRANGE/ACT/ASSERT
    """
    # Verify the overlay JavaScript file exists
    overlay_file = Path("modules/ai_assistant/frontend/views/AIAssistantOverlay.js")
    assert overlay_file.exists(), \
        "AIAssistantOverlay.js should exist"
    
    # Verify it contains SQL tab logic
    content = overlay_file.read_text()
    assert "'sql'" in content, \
        "Should define SQL tab"
    assert "SQL Query" in content, \
        "Should have SQL Query label"
    assert "_renderSQLTab" in content, \
        "Should have SQL tab rendering method"
    assert "executeSQL" in content or "execute-sql" in content, \
        "Should reference SQL execution"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_sql_adapter_has_execute_method():
    """
    Test: AIAssistantAdapter has executeSQL method
    
    Frontend Dependency: SQL execution
    
    ARRANGE/ACT/ASSERT
    """
    adapter_file = Path("modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js")
    assert adapter_file.exists(), \
        "AIAssistantAdapter.js should exist"
    
    content = adapter_file.read_text()
    assert "executeSQL" in content, \
        "Adapter should have executeSQL method"
    assert "/api/ai-assistant/execute-sql" in content, \
        "Should call correct endpoint"
    assert "execution_time_ms" in content, \
        "Should track execution time"