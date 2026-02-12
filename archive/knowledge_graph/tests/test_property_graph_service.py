"""
Property Graph Service Tests

Tests NetworkX implementation of Property Graph algorithms.

@author P2P Development Team
@version 1.0.0
"""

import unittest
from modules.knowledge_graph.backend.property_graph_service import NetworkXPropertyGraph


class TestNetworkXPropertyGraph(unittest.TestCase):
    """Test NetworkX Property Graph implementation"""
    
    def setUp(self):
        """Create test graph before each test"""
        self.graph = NetworkXPropertyGraph()
        
        # Create simple test graph
        self.test_graph_dict = {
            'nodes': [
                {'id': 'A', 'label': 'Node A', 'group': 'test'},
                {'id': 'B', 'label': 'Node B', 'group': 'test'},
                {'id': 'C', 'label': 'Node C', 'group': 'test'},
                {'id': 'D', 'label': 'Node D', 'group': 'test'},
                {'id': 'E', 'label': 'Node E', 'group': 'test'}
            ],
            'edges': [
                {'from': 'A', 'to': 'B', 'label': 'connects'},
                {'from': 'B', 'to': 'C', 'label': 'connects'},
                {'from': 'C', 'to': 'D', 'label': 'connects'},
                {'from': 'D', 'to': 'E', 'label': 'connects'},
                {'from': 'A', 'to': 'C', 'label': 'shortcut'}  # Creates shortest path
            ]
        }
        
        self.graph.load_from_dict(self.test_graph_dict)
    
    def test_load_from_dict(self):
        """Test loading graph from dictionary"""
        graph = NetworkXPropertyGraph()
        graph.load_from_dict(self.test_graph_dict)
        
        stats = graph.get_graph_stats()
        self.assertEqual(stats['node_count'], 5)
        self.assertEqual(stats['edge_count'], 5)
    
    def test_shortest_path_exists(self):
        """Test shortest path when path exists"""
        path = self.graph.shortest_path('A', 'D')
        
        # Should find: A → C → D (using shortcut, not A → B → C → D)
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 3)  # A, C, D
        self.assertEqual(path[0], 'A')
        self.assertEqual(path[-1], 'D')
    
    def test_shortest_path_no_path(self):
        """Test shortest path when no path exists"""
        # Add disconnected node
        graph_dict = {
            'nodes': [{'id': 'X', 'label': 'Isolated'}],
            'edges': []
        }
        self.graph.load_from_dict({
            'nodes': self.test_graph_dict['nodes'] + graph_dict['nodes'],
            'edges': self.test_graph_dict['edges']
        })
        
        path = self.graph.shortest_path('A', 'X')
        self.assertEqual(path, [])  # No path
    
    def test_shortest_path_invalid_node(self):
        """Test shortest path with non-existent node"""
        path = self.graph.shortest_path('A', 'NONEXISTENT')
        self.assertEqual(path, [])
    
    def test_centrality_betweenness(self):
        """Test betweenness centrality calculation"""
        scores = self.graph.centrality('betweenness')
        
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(scores), 5)
        
        # Node C should be most central (on multiple shortest paths)
        self.assertIn('C', scores)
        self.assertGreater(scores['C'], 0)
    
    def test_centrality_pagerank(self):
        """Test PageRank centrality calculation"""
        scores = self.graph.centrality('pagerank')
        
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(scores), 5)
        
        # All scores should sum to ~1.0
        total = sum(scores.values())
        self.assertAlmostEqual(total, 1.0, places=5)
    
    def test_centrality_degree(self):
        """Test degree centrality calculation"""
        scores = self.graph.centrality('degree')
        
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(scores), 5)
        
        # Scores should be normalized (0.0 to 1.0)
        for score in scores.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_centrality_closeness(self):
        """Test closeness centrality calculation"""
        scores = self.graph.centrality('closeness')
        
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(scores), 5)
    
    def test_centrality_invalid_algorithm(self):
        """Test centrality with invalid algorithm"""
        scores = self.graph.centrality('invalid_algorithm')
        self.assertEqual(scores, {})  # Should return empty dict on error
    
    def test_community_detection_louvain(self):
        """Test Louvain community detection"""
        communities = self.graph.community_detection('louvain')
        
        self.assertIsInstance(communities, dict)
        self.assertEqual(len(communities), 5)  # All nodes assigned
        
        # Check cluster ID format
        for node, cluster in communities.items():
            self.assertTrue(cluster.startswith('cluster_'))
    
    def test_community_detection_label_propagation(self):
        """Test label propagation community detection"""
        communities = self.graph.community_detection('label_propagation')
        
        self.assertIsInstance(communities, dict)
        self.assertEqual(len(communities), 5)
    
    def test_community_detection_greedy_modularity(self):
        """Test greedy modularity community detection"""
        communities = self.graph.community_detection('greedy_modularity')
        
        self.assertIsInstance(communities, dict)
        self.assertEqual(len(communities), 5)
    
    def test_get_graph_stats(self):
        """Test graph statistics calculation"""
        stats = self.graph.get_graph_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['node_count'], 5)
        self.assertEqual(stats['edge_count'], 5)
        self.assertTrue(stats['is_directed'])
        self.assertGreaterEqual(stats['density'], 0.0)
        self.assertLessEqual(stats['density'], 1.0)
        self.assertGreater(stats['avg_degree'], 0.0)
    
    def test_get_graph_stats_empty_graph(self):
        """Test stats for empty graph"""
        empty_graph = NetworkXPropertyGraph()
        stats = empty_graph.get_graph_stats()
        
        self.assertEqual(stats['node_count'], 0)
        self.assertEqual(stats['edge_count'], 0)
        self.assertEqual(stats['density'], 0.0)
    
    def test_get_neighbors_distance_1(self):
        """Test getting direct neighbors"""
        neighbors = self.graph.get_neighbors('A', max_distance=1)
        
        self.assertIsInstance(neighbors, list)
        # A connects to B and C directly
        self.assertIn('B', neighbors)
        self.assertIn('C', neighbors)
        self.assertEqual(len(neighbors), 2)
    
    def test_get_neighbors_distance_2(self):
        """Test getting neighbors within distance 2"""
        neighbors = self.graph.get_neighbors('A', max_distance=2)
        
        # A can reach: B (1), C (1), D (2)
        self.assertIn('B', neighbors)
        self.assertIn('C', neighbors)
        self.assertIn('D', neighbors)
        self.assertGreaterEqual(len(neighbors), 3)
    
    def test_get_neighbors_invalid_node(self):
        """Test neighbors for non-existent node"""
        neighbors = self.graph.get_neighbors('NONEXISTENT', max_distance=1)
        self.assertEqual(neighbors, [])
    
    def test_get_subgraph(self):
        """Test extracting subgraph"""
        node_ids = ['A', 'B', 'C']
        subgraph = self.graph.get_subgraph(node_ids)
        
        self.assertIsInstance(subgraph, dict)
        self.assertIn('nodes', subgraph)
        self.assertIn('edges', subgraph)
        
        # Should have 3 nodes
        self.assertEqual(len(subgraph['nodes']), 3)
        
        # Should have 2 edges (A→B, B→C, A→C)
        self.assertGreaterEqual(len(subgraph['edges']), 2)
    
    def test_empty_graph_operations(self):
        """Test operations on empty graph"""
        empty_graph = NetworkXPropertyGraph()
        
        # Should handle gracefully
        path = empty_graph.shortest_path('A', 'B')
        self.assertEqual(path, [])
        
        scores = empty_graph.centrality('betweenness')
        self.assertEqual(scores, {})
        
        neighbors = empty_graph.get_neighbors('A')
        self.assertEqual(neighbors, [])


if __name__ == '__main__':
    unittest.main()