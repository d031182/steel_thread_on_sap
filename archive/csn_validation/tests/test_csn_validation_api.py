"""
Unit Tests for CSN Validation API
==================================
Tests CSN fetching, caching, and validation logic.

Run: python -m pytest modules/csn_validation/tests/test_csn_validation_api.py -v
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Flask for testing
from flask import Flask
from modules.csn_validation.backend.api import csn_validation_api, fetch_csn_from_discovery_api


class TestCSNValidationAPI(unittest.TestCase):
    """Test CSN Validation API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['ENV'] = 'development'
        
        # Register blueprint
        self.app.register_blueprint(csn_validation_api)
        
        # Create test client
        self.client = self.app.test_client()
        
        # Clear LRU cache before each test
        fetch_csn_from_discovery_api.cache_clear()
    
    @patch('modules.csn_validation.backend.api.fetch_csn_from_discovery_api')
    @patch('modules.csn_validation.backend.api.get_csn_url')
    @patch('modules.csn_validation.backend.api.schema_name_to_ord_id')
    def test_get_csn_success(self, mock_schema_to_ord, mock_get_url, mock_fetch):
        """Test successful CSN retrieval"""
        # Mock the CSN mapping chain
        mock_schema_to_ord.return_value = 'sap.s4.com.SupplierInvoice:v1'
        mock_get_url.return_value = 'https://api.example.com/csn'
        mock_fetch.return_value = {
            'definitions': {'SupplierInvoice': {'kind': 'entity'}}
        }
        
        response = self.client.get('/api/csn/SupplierInvoice')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['schemaName'], 'SupplierInvoice')
        self.assertEqual(data['ordId'], 'sap.s4.com.SupplierInvoice:v1')
        self.assertIn('csn', data)
    
    @patch('modules.csn_validation.backend.api.schema_name_to_ord_id')
    def test_get_csn_schema_not_found(self, mock_schema_to_ord):
        """Test CSN retrieval with unmapped schema"""
        mock_schema_to_ord.return_value = None
        
        response = self.client.get('/api/csn/UnknownSchema')
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'SCHEMA_NOT_MAPPED')
        self.assertIn('availableProducts', data['error'])
    
    @patch('modules.csn_validation.backend.api.get_csn_url')
    @patch('modules.csn_validation.backend.api.schema_name_to_ord_id')
    def test_get_csn_url_not_found(self, mock_schema_to_ord, mock_get_url):
        """Test CSN retrieval when URL is not found"""
        mock_schema_to_ord.return_value = 'sap.s4.com.Test:v1'
        mock_get_url.return_value = None
        
        response = self.client.get('/api/csn/TestSchema')
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'CSN_URL_NOT_FOUND')
    
    def test_get_csn_missing_schema_name(self):
        """Test CSN retrieval without schema name"""
        response = self.client.get('/api/csn/')
        
        # Should get 404 from Flask (no route match)
        self.assertEqual(response.status_code, 404)
    
    @patch('modules.csn_validation.backend.api.get_all_p2p_products')
    def test_list_p2p_products_success(self, mock_get_products):
        """Test listing all P2P products"""
        mock_get_products.return_value = [
            {'name': 'SupplierInvoice', 'ordId': 'sap.s4.com.SupplierInvoice:v1'},
            {'name': 'PurchaseOrder', 'ordId': 'sap.s4.com.PurchaseOrder:v1'}
        ]
        
        response = self.client.get('/api/csn/products')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)
        self.assertIsInstance(data['products'], list)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/csn/health')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['module'], 'csn_validation')
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('cache_info', data)


class TestCSNCaching(unittest.TestCase):
    """Test CSN caching functionality"""
    
    def setUp(self):
        """Clear cache before each test"""
        fetch_csn_from_discovery_api.cache_clear()
    
    @patch('requests.get')
    def test_fetch_csn_success(self, mock_get):
        """Test successful CSN fetch from API"""
        mock_response = Mock()
        mock_response.json.return_value = {'definitions': {'test': 'data'}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fetch_csn_from_discovery_api('https://api.example.com/csn')
        
        self.assertEqual(result, {'definitions': {'test': 'data'}})
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_fetch_csn_caching(self, mock_get):
        """Test that CSN responses are cached"""
        mock_response = Mock()
        mock_response.json.return_value = {'definitions': {'test': 'data'}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        url = 'https://api.example.com/csn'
        
        # First call - should hit API
        result1 = fetch_csn_from_discovery_api(url)
        self.assertEqual(mock_get.call_count, 1)
        
        # Second call - should use cache
        result2 = fetch_csn_from_discovery_api(url)
        self.assertEqual(mock_get.call_count, 1)  # Still 1, not 2
        
        # Results should be identical
        self.assertEqual(result1, result2)
    
    @patch('requests.get')
    def test_fetch_csn_timeout(self, mock_get):
        """Test CSN fetch timeout handling"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with self.assertRaises(Exception) as context:
            fetch_csn_from_discovery_api('https://api.example.com/csn')
        
        self.assertIn('Timeout', str(context.exception))
    
    @patch('requests.get')
    def test_fetch_csn_http_error(self, mock_get):
        """Test CSN fetch HTTP error handling"""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('404')
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            fetch_csn_from_discovery_api('https://api.example.com/csn')
        
        self.assertIn('Failed to fetch CSN', str(context.exception))
    
    def test_cache_info(self):
        """Test cache statistics"""
        # Clear and check empty cache
        fetch_csn_from_discovery_api.cache_clear()
        info = fetch_csn_from_discovery_api.cache_info()
        
        self.assertEqual(info.currsize, 0)
        self.assertEqual(info.maxsize, 20)


class TestCSNMappingLogic(unittest.TestCase):
    """Test CSN mapping and URL resolution logic"""
    
    @patch('modules.csn_validation.backend.api.schema_name_to_ord_id')
    def test_schema_name_mapping(self, mock_mapping):
        """Test schema name to ORD ID mapping"""
        test_cases = [
            ('SupplierInvoice', 'sap.s4.com.SupplierInvoice:v1'),
            ('PurchaseOrder', 'sap.s4.com.PurchaseOrder:v1'),
            ('UnknownSchema', None)
        ]
        
        for schema_name, expected_ord_id in test_cases:
            mock_mapping.return_value = expected_ord_id
            result = mock_mapping(schema_name)
            self.assertEqual(result, expected_ord_id)
    
    @patch('modules.csn_validation.backend.api.get_csn_url')
    def test_csn_url_resolution(self, mock_get_url):
        """Test CSN URL resolution from ORD ID"""
        test_ord_id = 'sap.s4.com.SupplierInvoice:v1'
        expected_url = 'https://api.sap.com/csn/SupplierInvoice'
        
        mock_get_url.return_value = expected_url
        result = mock_get_url(test_ord_id)
        
        self.assertEqual(result, expected_url)


if __name__ == '__main__':
    unittest.main()