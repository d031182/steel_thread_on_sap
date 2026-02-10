"""
Unit Tests for API Playground Service
=====================================
Tests the auto-discovery and management of module APIs.

Run: python -m pytest modules/api_playground/tests/test_playground_service.py -v
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.api_playground.backend.playground_service import PlaygroundService


class TestPlaygroundService(unittest.TestCase):
    """Test PlaygroundService API discovery"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use real modules directory for integration testing
        self.modules_dir = str(project_root / "modules")
        self.service = PlaygroundService(self.modules_dir)
    
    def test_discover_apis(self):
        """Test API discovery from modules"""
        count = self.service.discover_apis()
        
        # Should discover at least some modules with APIs
        self.assertGreater(count, 0, "Should discover at least one module with API")
        self.assertGreater(len(self.service.discovered_apis), 0)
    
    def test_get_all_apis(self):
        """Test getting all discovered APIs"""
        apis = self.service.get_all_apis()
        
        self.assertIsInstance(apis, dict)
        self.assertGreater(len(apis), 0, "Should have discovered APIs")
        
        # Check API structure
        for module_name, api_config in apis.items():
            self.assertIn('displayName', api_config)
            self.assertIn('baseUrl', api_config)
            self.assertIn('endpoints', api_config)
            self.assertIsInstance(api_config['endpoints'], list)
    
    def test_get_api_existing(self):
        """Test getting a specific existing module API"""
        # First discover to populate
        self.service.discover_apis()
        
        # Get any discovered module
        if self.service.discovered_apis:
            module_name = list(self.service.discovered_apis.keys())[0]
            api = self.service.get_api(module_name)
            
            self.assertIsNotNone(api)
            self.assertIn('displayName', api)
            self.assertIn('endpoints', api)
    
    def test_get_api_nonexistent(self):
        """Test getting a non-existent module API"""
        api = self.service.get_api('nonexistent_module_xyz')
        self.assertIsNone(api)
    
    def test_get_apis_by_category(self):
        """Test filtering APIs by category"""
        # Discover first
        self.service.discover_apis()
        
        # Get all categories
        categories = self.service.get_categories()
        
        if categories:
            # Test filtering by first category
            category = categories[0]
            filtered_apis = self.service.get_apis_by_category(category)
            
            self.assertIsInstance(filtered_apis, dict)
            
            # All filtered APIs should be in the correct category
            for api_config in filtered_apis.values():
                self.assertEqual(api_config.get('category'), category)
    
    def test_get_categories(self):
        """Test getting all unique categories"""
        self.service.discover_apis()
        categories = self.service.get_categories()
        
        self.assertIsInstance(categories, list)
        # Should be sorted
        self.assertEqual(categories, sorted(categories))
        # Should have no duplicates
        self.assertEqual(len(categories), len(set(categories)))
    
    def test_get_endpoint_count(self):
        """Test getting total endpoint count"""
        self.service.discover_apis()
        count = self.service.get_endpoint_count()
        
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
    
    def test_get_module_endpoint_count_existing(self):
        """Test getting endpoint count for existing module"""
        self.service.discover_apis()
        
        if self.service.discovered_apis:
            module_name = list(self.service.discovered_apis.keys())[0]
            count = self.service.get_module_endpoint_count(module_name)
            
            self.assertIsInstance(count, int)
            self.assertGreaterEqual(count, 0)
    
    def test_get_module_endpoint_count_nonexistent(self):
        """Test getting endpoint count for non-existent module"""
        count = self.service.get_module_endpoint_count('nonexistent_xyz')
        self.assertEqual(count, 0)
    
    def test_build_endpoint_url(self):
        """Test building complete endpoint URLs"""
        self.service.discover_apis()
        
        if self.service.discovered_apis:
            # Get first module with endpoints
            for module_name, api_config in self.service.discovered_apis.items():
                if api_config.get('endpoints'):
                    endpoint = api_config['endpoints'][0]
                    url = self.service.build_endpoint_url(module_name, endpoint)
                    
                    self.assertIsInstance(url, str)
                    # Should contain baseUrl and path
                    self.assertIn(api_config['baseUrl'], url)
                    self.assertIn(endpoint['path'], url)
                    break
    
    def test_build_endpoint_url_nonexistent(self):
        """Test building URL for non-existent module"""
        url = self.service.build_endpoint_url('nonexistent', {'path': '/test'})
        self.assertEqual(url, "")
    
    def test_get_endpoint_parameters(self):
        """Test getting endpoint parameters"""
        # Test with endpoint that has parameters
        endpoint_with_params = {
            'path': '/test',
            'parameters': [
                {'name': 'id', 'type': 'string', 'required': True}
            ]
        }
        params = self.service.get_endpoint_parameters(endpoint_with_params)
        
        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['name'], 'id')
        
        # Test with endpoint without parameters
        endpoint_no_params = {'path': '/test'}
        params = self.service.get_endpoint_parameters(endpoint_no_params)
        self.assertEqual(params, [])
    
    def test_get_summary_stats(self):
        """Test getting summary statistics"""
        self.service.discover_apis()
        stats = self.service.get_summary_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_modules', stats)
        self.assertIn('total_endpoints', stats)
        self.assertIn('categories', stats)
        self.assertIn('modules_by_category', stats)
        
        self.assertIsInstance(stats['total_modules'], int)
        self.assertIsInstance(stats['total_endpoints'], int)
        self.assertIsInstance(stats['categories'], list)
        self.assertIsInstance(stats['modules_by_category'], dict)
    
    def test_repr(self):
        """Test string representation"""
        self.service.discover_apis()
        repr_str = repr(self.service)
        
        self.assertIn('PlaygroundService', repr_str)
        self.assertIn('modules', repr_str)
        self.assertIn('endpoints', repr_str)


class TestPlaygroundServiceSingleton(unittest.TestCase):
    """Test the singleton pattern for PlaygroundService"""
    
    def test_get_playground_service(self):
        """Test getting the global service instance"""
        from modules.api_playground.backend.playground_service import get_playground_service
        
        service1 = get_playground_service()
        service2 = get_playground_service()
        
        # Should return the same instance
        self.assertIs(service1, service2)


if __name__ == '__main__':
    unittest.main()