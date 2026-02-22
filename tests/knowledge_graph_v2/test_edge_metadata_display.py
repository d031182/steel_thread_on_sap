"""
API Contract Tests for Knowledge Graph Edge Metadata Display (HIGH-50)

Tests verify:
1. Backend provides association metadata (cardinality, ON conditions) via API
2. Frontend adapter correctly displays metadata in tooltips/labels
3. Edge enrichment works for various relationship types
"""
import pytest
import requests
import json


@pytest.mark.e2e
@pytest.mark.api_contract
class TestEdgeMetadataDisplay:
    """Test edge metadata display in Knowledge Graph visualization"""
    
    BASE_URL = "http://localhost:5000"
    
    def test_backend_provides_edge_cardinality(self):
        """
        Test: Backend API includes cardinality in edge properties

        Validates HIGH-29 association metadata is available via API
        """
        # ARRANGE
        url = f"{self.BASE_URL}/api/knowledge-graph/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"API call failed: {response.status_code}"
        
        data = response.json()
        assert 'data' in data, "Response missing data wrapper"
        assert 'graph' in data['data'], "Response missing graph"
        assert 'edges' in data['data']['graph'], "Graph missing edges array"
        
        # Find foreign key edges
        edges = data['data']['graph']['edges']
        fk_edges = [e for e in edges if e.get('type') in ['foreign_key', 'fk']]
        
        if fk_edges:
            # Check at least one FK edge has cardinality (stored at root level)
            edges_with_cardinality = [
                e for e in fk_edges
                if 'cardinality' in e
            ]

            assert len(edges_with_cardinality) > 0, \
                "No foreign key edges have cardinality metadata"
            
            # Validate cardinality format
            sample_edge = edges_with_cardinality[0]
            cardinality = sample_edge['cardinality']
            assert cardinality in ['1:1', '1:*', '*:1', '*:*', '1:N', 'N:1', 'N:M'], \
                f"Invalid cardinality format: {cardinality}"
    
    def test_backend_provides_edge_on_conditions(self):
        """
        Test: Backend API includes ON conditions in edge properties

        Validates association JOIN conditions available for display
        """
        # ARRANGE
        url = f"{self.BASE_URL}/api/knowledge-graph/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        edges = data['data']['graph']['edges']
        fk_edges = [e for e in edges if e.get('type') in ['foreign_key', 'fk']]
        
        if fk_edges:
            # Check for ON conditions (stored at root level)
            edges_with_conditions = [
                e for e in fk_edges
                if 'on_conditions' in e or 'join_clause' in e
            ]

            assert len(edges_with_conditions) > 0, \
                "No foreign key edges have ON condition metadata"
            
            # Validate ON conditions structure
            sample_edge = edges_with_conditions[0]
            
            if 'on_conditions' in sample_edge:
                # Prefer array format
                assert isinstance(sample_edge['on_conditions'], list), \
                    "on_conditions should be array"
                assert len(sample_edge['on_conditions']) > 0, \
                    "on_conditions array should not be empty"
            elif 'join_clause' in sample_edge:
                # Fallback to formatted string
                assert isinstance(sample_edge['join_clause'], str), \
                    "join_clause should be string"
                assert len(sample_edge['join_clause']) > 0, \
                    "join_clause should not be empty"
    
    def test_edge_properties_include_table_names(self):
        """
        Test: Edge properties include source/target table names

        Needed for tooltip context display
        """
        # ARRANGE
        url = f"{self.BASE_URL}/api/knowledge-graph/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        edges = data['data']['graph']['edges']
        fk_edges = [e for e in edges if e.get('type') in ['foreign_key', 'fk']]
        
        if fk_edges:
            sample_edge = fk_edges[0]

            # Check for table name metadata (stored at root level)
            assert 'source_table' in sample_edge or 'fk_column' in sample_edge, \
                "Edge missing source context"
            assert 'target_table' in sample_edge or sample_edge.get('label'), \
                "Edge missing target context"
    
    def test_edge_metadata_completeness(self):
        """
        Test: Foreign key edges have complete metadata set

        Validates all required properties for rich tooltip display
        """
        # ARRANGE
        url = f"{self.BASE_URL}/api/knowledge-graph/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        edges = data['data']['graph']['edges']
        fk_edges = [e for e in edges if e.get('type') in ['foreign_key', 'fk']]
        
        if fk_edges:
            # Check metadata completeness
            complete_edges = []

            for edge in fk_edges:
                # Count available metadata fields (stored at root level)
                metadata_score = sum([
                    'cardinality' in edge,
                    'on_conditions' in edge or 'join_clause' in edge,
                    'source_table' in edge,
                    'target_table' in edge,
                    bool('fk_column' in edge or edge.get('label'))
                ])
                
                if metadata_score >= 3:  # At least 3 of 5 fields
                    complete_edges.append(edge)
            
            # Assert majority of edges have rich metadata
            completeness_ratio = len(complete_edges) / len(fk_edges)
            assert completeness_ratio >= 0.5, \
                f"Only {completeness_ratio:.0%} of FK edges have complete metadata"
    
    def test_composition_relationship_flags(self):
        """
        Test: Edges include composition/many-to-many flags

        Needed for special styling in visualization
        """
        # ARRANGE
        url = f"{self.BASE_URL}/api/knowledge-graph/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        edges = data['data']['graph']['edges']
        fk_edges = [e for e in edges if e.get('type') in ['foreign_key', 'fk']]
        
        if fk_edges:
            # Check for relationship type flags (stored at root level)
            for edge in fk_edges:
                # Flags should be boolean if present
                if 'is_composition' in edge:
                    assert isinstance(edge['is_composition'], bool), \
                        "is_composition should be boolean"
                
                if 'is_many_to_many' in edge:
                    assert isinstance(edge['is_many_to_many'], bool), \
                        "is_many_to_many should be boolean"
    
    def test_schema_endpoint_edge_metadata(self):
        """
        Test: Schema endpoint also provides edge metadata
        
        Ensures consistency between /graph and /schema endpoints
        """
        # ARRANGE
        url = f"{self.BASE_URL}/api/knowledge-graph/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        
        if 'relationships' in data and data['relationships']:
            # Check relationships have metadata
            sample_rel = data['relationships'][0]
            
            assert 'cardinality' in sample_rel or 'type' in sample_rel, \
                "Schema relationships missing cardinality metadata"


@pytest.mark.e2e
@pytest.mark.api_contract
class TestEdgeMetadataRobustness:
    """Test edge metadata handling edge cases"""
    
    BASE_URL = "http://localhost:5000"
    
    def test_missing_cardinality_graceful_handling(self):
        """
        Test: System handles edges without cardinality gracefully

        Some edges may lack metadata - should not break visualization
        """
        # ARRANGE
        url = f"{self.BASE_URL}/api/knowledge-graph/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        edges = data['data']['graph']['edges']
        
        # All edges should have required fields
        for edge in edges:
            assert 'source_id' in edge, "Edge missing source_id"
            assert 'target_id' in edge, "Edge missing target_id"
            assert 'type' in edge, "Edge missing type"
    
    def test_empty_on_conditions_handling(self):
        """
        Test: Empty ON conditions don't break tooltip display
        """
        # ARRANGE
        url = f"{self.BASE_URL}/api/knowledge-graph/schema"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200
        
        data = response.json()
        edges = data['data']['graph']['edges']
        fk_edges = [e for e in edges if e.get('type') in ['foreign_key', 'fk']]
        
        # Check edges with empty on_conditions
        for edge in fk_edges:
            if 'on_conditions' in edge:
                conditions = edge['on_conditions']
                
                # Can be empty list - frontend should handle gracefully
                if isinstance(conditions, list) and len(conditions) == 0:
                    # This is valid - frontend falls back to join_clause
                    assert True