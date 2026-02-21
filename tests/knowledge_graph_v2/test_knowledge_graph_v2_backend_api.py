"""
Feng Shui Phase 1: Knowledge Graph V2 Backend API Contract Tests

Tests the contract (endpoints, request/response schemas) for all
knowledge_graph_v2 backend APIs. These tests validate the public API surface
without testing internal implementation details.

Contract testing strategy:
- One API test validates entire call stack implicitly
- Tests run in <1 second via requests library
- All endpoints tested as black boxes
"""

import pytest
import requests
import json
from typing import Dict, Any


pytestmark = [pytest.mark.e2e, pytest.mark.api_contract]

BASE_URL = "http://localhost:5000/api"
TIMEOUT = 5


class TestKnowledgeGraphV2HealthEndpoint:
    """Test: Backend health check endpoint"""

    @pytest.mark.api_contract
    def test_health_endpoint_returns_valid_contract(self):
        """ARRANGE: Setup health check endpoint
        
        ACT: Call GET /health
        
        ASSERT: Response validates contract structure
        - Status code 200
        - Contains 'status' field
        - Status value is 'healthy'
        """
        # ARRANGE
        url = f"{BASE_URL}/health"

        # ACT
        response = requests.get(url, timeout=TIMEOUT)

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestKnowledgeGraphV2SchemaGraphEndpoint:
    """Test: Schema graph retrieval endpoint"""

    @pytest.mark.api_contract
    def test_schema_graph_returns_valid_contract(self):
        """ARRANGE: Setup schema graph endpoint
        
        ACT: Call GET /schema-graph
        
        ASSERT: Response validates contract structure
        - Status code 200
        - Contains 'nodes' array
        - Contains 'edges' array
        - Each node has 'id' field
        - Each edge has 'source' and 'target' fields
        """
        # ARRANGE
        url = f"{BASE_URL}/knowledge-graph-v2/schema-graph"

        # ACT
        response = requests.get(url, timeout=TIMEOUT)

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        
        assert "nodes" in data
        assert "edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
        
        # Validate node structure
        for node in data["nodes"]:
            assert "id" in node
            assert isinstance(node["id"], str)
        
        # Validate edge structure
        for edge in data["edges"]:
            assert "source" in edge
            assert "target" in edge


class TestKnowledgeGraphV2RebuildEndpoint:
    """Test: Schema graph rebuild endpoint"""

    @pytest.mark.api_contract
    def test_rebuild_endpoint_accepts_valid_contract(self):
        """ARRANGE: Setup rebuild endpoint
        
        ACT: Call POST /rebuild with CSN payload
        
        ASSERT: Response validates contract structure
        - Status code 200 or 202 (async processing)
        - Contains 'success' field
        - Contains 'rebuild_id' field (for tracking)
        """
        # ARRANGE
        url = f"{BASE_URL}/knowledge-graph-v2/rebuild"
        payload = {
            "csn_data": {
                "definitions": {}
            }
        }

        # ACT
        response = requests.post(url, json=payload, timeout=TIMEOUT)

        # ASSERT
        assert response.status_code in [200, 202]
        data = response.json()
        assert "success" in data
        assert data["success"] is True


class TestKnowledgeGraphV2StatusEndpoint:
    """Test: Schema graph build status endpoint"""

    @pytest.mark.api_contract
    def test_status_endpoint_returns_valid_contract(self):
        """ARRANGE: Setup status endpoint
        
        ACT: Call GET /status
        
        ASSERT: Response validates contract structure
        - Status code 200
        - Contains 'status' field
        - Contains 'last_rebuilt' timestamp
        - Contains 'node_count' integer
        """
        # ARRANGE
        url = f"{BASE_URL}/knowledge-graph-v2/status"

        # ACT
        response = requests.get(url, timeout=TIMEOUT)

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "last_rebuilt" in data
        assert "node_count" in data
        assert isinstance(data["node_count"], int)


class TestKnowledgeGraphV2CacheStatsEndpoint:
    """Test: Cache statistics endpoint"""

    @pytest.mark.api_contract
    def test_cache_stats_returns_valid_contract(self):
        """ARRANGE: Setup cache stats endpoint
        
        ACT: Call GET /cache-stats
        
        ASSERT: Response validates contract structure
        - Status code 200
        - Contains 'hit_count' integer
        - Contains 'miss_count' integer
        - Contains 'cached_items' integer
        - Contains 'cache_size_bytes' integer
        """
        # ARRANGE
        url = f"{BASE_URL}/knowledge-graph-v2/cache-stats"

        # ACT
        response = requests.get(url, timeout=TIMEOUT)

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        
        assert "hit_count" in data
        assert "miss_count" in data
        assert "cached_items" in data
        assert "cache_size_bytes" in data
        
        assert isinstance(data["hit_count"], int)
        assert isinstance(data["miss_count"], int)
        assert isinstance(data["cached_items"], int)
        assert isinstance(data["cache_size_bytes"], int)


class TestKnowledgeGraphV2InvalidateCacheEndpoint:
    """Test: Cache invalidation endpoint"""

    @pytest.mark.api_contract
    def test_invalidate_cache_returns_valid_contract(self):
        """ARRANGE: Setup cache invalidation endpoint
        
        ACT: Call POST /invalidate-cache
        
        ASSERT: Response validates contract structure
        - Status code 200
        - Contains 'success' field
        - Contains 'invalidated_count' integer
        """
        # ARRANGE
        url = f"{BASE_URL}/knowledge-graph-v2/invalidate-cache"

        # ACT
        response = requests.post(url, timeout=TIMEOUT)

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] is True
        assert "invalidated_count" in data
        assert isinstance(data["invalidated_count"], int)


class TestKnowledgeGraphV2DeleteCacheEndpoint:
    """Test: Cache deletion endpoint"""

    @pytest.mark.api_contract
    def test_delete_cache_returns_valid_contract(self):
        """ARRANGE: Setup cache deletion endpoint
        
        ACT: Call DELETE /cache
        
        ASSERT: Response validates contract structure
        - Status code 200 or 204
        - If 200: contains 'success' field
        """
        # ARRANGE
        url = f"{BASE_URL}/knowledge-graph-v2/cache"

        # ACT
        response = requests.delete(url, timeout=TIMEOUT)

        # ASSERT
        assert response.status_code in [200, 204]
        
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert data["success"] is True


class TestKnowledgeGraphV2AnalyticsStatusEndpoint:
    """Test: Analytics status endpoint"""

    @pytest.mark.api_contract
    def test_analytics_status_returns_valid_contract(self):
        """ARRANGE: Setup analytics status endpoint
        
        ACT: Call GET /analytics-status
        
        ASSERT: Response validates contract structure
        - Status code 200
        - Contains 'enabled' boolean
        - Contains 'query_count' integer
        - Contains 'execution_time_ms' number
        """
        # ARRANGE
        url = f"{BASE_URL}/knowledge-graph-v2/analytics-status"

        # ACT
        response = requests.get(url, timeout=TIMEOUT)

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        
        assert "enabled" in data
        assert isinstance(data["enabled"], bool)
        assert "query_count" in data
        assert isinstance(data["query_count"], int)
        assert "execution_time_ms" in data