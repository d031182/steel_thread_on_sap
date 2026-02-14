"""
Knowledge Graph V2 API Contract Tests
======================================

Tests the API contracts that GraphPresenter and KnowledgeGraphApiClient depend on.

Following HIGH-16 breakthrough: Test frontend APIs FIRST (< 1s) before testing UI.

Test Coverage:
- GraphPresenter.loadGraph() → GET /api/knowledge-graph-v2/schema
- GraphPresenter.rebuild() → POST /api/knowledge-graph-v2/schema/rebuild  
- GraphPresenter.clearCacheAndReload() → DELETE /api/knowledge-graph-v2/cache
- GraphPresenter.updateStatus() → GET /api/knowledge-graph-v2/status
- KnowledgeGraphApiClient error handling scenarios

NOTE: Most endpoints not yet implemented (return 404/405).
      Tests marked with @pytest.mark.skip until endpoints are implemented.

@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
"""

import pytest
import requests
from typing import Dict, Any


class TestKnowledgeGraphV2APIContracts:
    """
    Test API contracts for Knowledge Graph V2 module.
    
    Philosophy: "Test the API before testing the UI" (HIGH-16)
    Speed: < 1 second per test (60-300x faster than browser)
    """
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for Knowledge Graph V2 API"""
        return "http://localhost:5000/api/knowledge-graph-v2"
    
    # ========================================
    # GET /schema - Load Graph (with cache)
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2  
    @pytest.mark.api_contract
    @pytest.mark.skip(reason="Endpoint not implemented - returns 404")
    def test_get_schema_returns_valid_structure(self, base_url: str):
        """
        Test: GET /schema returns valid graph structure
        
        Frontend Dependency: GraphPresenter.loadGraph()
        
        TODO: Implement /api/knowledge-graph-v2/schema endpoint
        
        ARRANGE
        """
        url = f"{base_url}/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Schema endpoint should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
        
        # Contract: Must have 'graph' object
        assert 'graph' in data, "Response must include 'graph' object"
        graph = data['graph']
        
        # Contract: Graph must have 'nodes' array
        assert 'nodes' in graph, "Graph must include 'nodes' array"
        assert isinstance(graph['nodes'], list), "'nodes' must be array"
        
        # Contract: Graph must have 'edges' array
        assert 'edges' in graph, "Graph must include 'edges' array"
        assert isinstance(graph['edges'], list), "'edges' must be array"
        
        # Contract: Must have 'cache_used' field
        assert 'cache_used' in data, "Response must include 'cache_used' field"
        assert isinstance(data['cache_used'], bool), "'cache_used' must be boolean"
        
        # Contract: Must have 'metadata' object
        assert 'metadata' in data, "Response must include 'metadata' object"
        metadata = data['metadata']
        
        # Contract: Metadata must have required fields
        assert 'csn_files_count' in metadata, "Metadata must include 'csn_files_count'"
        assert 'csn_directory' in metadata, "Metadata must include 'csn_directory'"
        assert isinstance(metadata['csn_files_count'], int), "'csn_files_count' must be integer"
        assert isinstance(metadata['csn_directory'], str), "'csn_directory' must be string"
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    @pytest.mark.skip(reason="Endpoint not implemented - returns 404")
    def test_get_schema_node_structure(self, base_url: str):
        """
        Test: Graph nodes have required fields
        
        Frontend Dependency: VisJsAdapter.convertToVisJs() expects specific node structure
        
        TODO: Implement /api/knowledge-graph-v2/schema endpoint
        
        ARRANGE
        """
        url = f"{base_url}/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # ASSERT
        graph = data['graph']
        nodes = graph['nodes']
        
        if len(nodes) > 0:
            # Sample first node
            node = nodes[0]
            
            # Contract: Node must have 'id'
            assert 'id' in node, "Node must have 'id' field"
            
            # Contract: Node must have 'label'
            assert 'label' in node, "Node must have 'label' field"
            
            # Contract: Node must have 'type'
            assert 'type' in node, "Node must have 'type' field"
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    @pytest.mark.skip(reason="Endpoint not implemented - returns 404")
    def test_get_schema_edge_structure(self, base_url: str):
        """
        Test: Graph edges have required fields
        
        Frontend Dependency: VisJsAdapter.convertToVisJs() expects specific edge structure
        
        TODO: Implement /api/knowledge-graph-v2/schema endpoint
        
        ARRANGE
        """
        url = f"{base_url}/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # ASSERT
        graph = data['graph']
        edges = graph['edges']
        
        if len(edges) > 0:
            # Sample first edge
            edge = edges[0]
            
            # Contract: Edge must have 'from'
            assert 'from' in edge, "Edge must have 'from' field"
            
            # Contract: Edge must have 'to'
            assert 'to' in edge, "Edge must have 'to' field"
            
            # Contract: Edge must have 'label'
            assert 'label' in edge, "Edge must have 'label' field"
    
    # ========================================
    # POST /schema/rebuild - Force Rebuild
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    @pytest.mark.skip(reason="Endpoint returns 405 Method Not Allowed")
    def test_post_schema_rebuild_returns_valid_structure(self, base_url: str):
        """
        Test: POST /schema/rebuild returns valid rebuild result
        
        Frontend Dependency: GraphPresenter.rebuild()
        
        TODO: Implement POST support for /api/knowledge-graph-v2/schema/rebuild
        
        ARRANGE
        """
        url = f"{base_url}/schema/rebuild"
        
        # ACT
        response = requests.post(url, timeout=10)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Rebuild endpoint should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
        
        # Contract: Must have 'graph' object (same structure as GET /schema)
        assert 'graph' in data, "Response must include 'graph' object"
        graph = data['graph']
        assert 'nodes' in graph, "Graph must include 'nodes' array"
        assert 'edges' in graph, "Graph must include 'edges' array"
        
        # Contract: cache_used must be false for rebuild
        assert 'cache_used' in data, "Response must include 'cache_used' field"
        assert data['cache_used'] is False, "'cache_used' must be false for rebuild"
        
        # Contract: Must have 'metadata'
        assert 'metadata' in data, "Response must include 'metadata' object"
    
    # ========================================
    # DELETE /cache - Clear Cache
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    @pytest.mark.skip(reason="Endpoint returns 405 Method Not Allowed")
    def test_delete_cache_returns_success(self, base_url: str):
        """
        Test: DELETE /cache returns success
        
        Frontend Dependency: GraphPresenter.clearCacheAndReload()
        
        TODO: Implement DELETE support for /api/knowledge-graph-v2/cache
        
        ARRANGE
        """
        url = f"{base_url}/cache"
        
        # ACT
        response = requests.delete(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Cache delete should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
        
        # Contract: Must have 'message' field
        assert 'message' in data, "Response must include 'message' field"
        assert isinstance(data['message'], str), "'message' must be string"
    
    # ========================================
    # GET /status - Get Cache Status
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    @pytest.mark.skip(reason="Endpoint not implemented - returns 404")
    def test_get_status_returns_valid_structure(self, base_url: str):
        """
        Test: GET /status returns valid cache status
        
        Frontend Dependency: GraphPresenter.updateStatus()
        
        TODO: Implement /api/knowledge-graph-v2/status endpoint
        
        ARRANGE
        """
        url = f"{base_url}/status"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Status endpoint should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
        
        # Contract: Must have 'cached' field
        assert 'cached' in data, "Response must include 'cached' field"
        assert isinstance(data['cached'], bool), "'cached' must be boolean"
        
        # Contract: Must have 'csn_files_count'
        assert 'csn_files_count' in data, "Response must include 'csn_files_count'"
        assert isinstance(data['csn_files_count'], int), "'csn_files_count' must be integer"
        
        # Contract: Must have 'csn_directory'
        assert 'csn_directory' in data, "Response must include 'csn_directory'"
        assert isinstance(data['csn_directory'], str), "'csn_directory' must be string"
    
    # ========================================
    # GET /health - Health Check
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    @pytest.mark.skip(reason="Endpoint not implemented - returns 404")
    def test_get_health_returns_healthy(self, base_url: str):
        """
        Test: GET /health returns healthy status
        
        Frontend Dependency: Module availability check
        
        TODO: Implement /api/knowledge-graph-v2/health endpoint
        
        ARRANGE
        """
        url = f"{base_url}/health"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Health endpoint should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
    
    # ========================================
    # Error Handling Scenarios
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_nonexistent_endpoint_returns_404(self, base_url: str):
        """
        Test: Nonexistent endpoint returns 404
        
        Frontend Dependency: KnowledgeGraphApiClient error handling
        
        ARRANGE
        """
        url = f"{base_url}/nonexistent"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 404, \
            f"Nonexistent endpoint should return 404, got {response.status_code}"
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_invalid_method_returns_405(self, base_url: str):
        """
        Test: Invalid HTTP method returns 405
        
        Frontend Dependency: KnowledgeGraphApiClient error handling
        
        ARRANGE
        """
        url = f"{base_url}/schema"
        
        # ACT (schema only supports GET, not POST)
        response = requests.post(url, timeout=5)
        
        # ASSERT
        assert response.status_code in [405, 404], \
            f"Invalid method should return 405 or 404, got {response.status_code}"


# ========================================
# Integration Test: Full Workflow
# ========================================

class TestKnowledgeGraphV2Workflow:
    """
    Test complete workflow that GraphPresenter orchestrates.
    
    Validates: Load → Rebuild → Status sequence
    """
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    @pytest.mark.skip(reason="Workflow depends on unimplemented endpoints")
    def test_complete_graph_workflow(self):
        """
        Test: Complete graph workflow (load, rebuild, status)
        
        Simulates: GraphPresenter full lifecycle
        
        TODO: Enable once endpoints are implemented
        
        ARRANGE
        """
        base_url = "http://localhost:5000/api/knowledge-graph-v2"
        
        # ACT & ASSERT: Step 1 - Load graph (use cache)
        response1 = requests.get(f"{base_url}/schema", timeout=5)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1['success'] is True
        assert 'graph' in data1
        
        # ACT & ASSERT: Step 2 - Get status
        response2 = requests.get(f"{base_url}/status", timeout=5)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2['success'] is True
        assert 'cached' in data2
        
        # ACT & ASSERT: Step 3 - Clear cache
        response3 = requests.delete(f"{base_url}/cache", timeout=5)
        assert response3.status_code == 200
        data3 = response3.json()
        assert data3['success'] is True
        
        # ACT & ASSERT: Step 4 - Rebuild (no cache)
        response4 = requests.post(f"{base_url}/schema/rebuild", timeout=10)
        assert response4.status_code == 200
        data4 = response4.json()
        assert data4['success'] is True
        assert data4['cache_used'] is False
        
        # ASSERT: Graph structure consistency
        assert data1['graph']['nodes'].__len__() > 0, "Graph should have nodes"
        assert data4['graph']['nodes'].__len__() > 0, "Rebuilt graph should have nodes"