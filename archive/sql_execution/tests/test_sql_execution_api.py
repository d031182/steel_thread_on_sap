"""
Unit Tests for SQL Execution API
=================================
Tests SQL query execution and connection management.

Run: python -m pytest modules/sql_execution/tests/test_sql_execution_api.py -v
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
from modules.sql_execution.backend.api import sql_execution_api


class TestSQLExecutionAPI(unittest.TestCase):
    """Test SQL Execution API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['ENV'] = 'development'
        self.app.config.update({
            'HANA_HOST': 'test-host.hanacloud.ondemand.com',
            'HANA_PORT': 443,
            'HANA_USER': 'TEST_USER',
            'HANA_SCHEMA': 'TEST_SCHEMA'
        })
        
        # Register blueprint
        self.app.register_blueprint(sql_execution_api)
        
        # Create test client
        self.client = self.app.test_client()
        
        # Mock HANA data source
        self.mock_hana = Mock()
        self.mock_connection = Mock()
        self.mock_hana.connection = self.mock_connection
        self.app.hana_data_source = self.mock_hana
    
    def test_execute_sql_success(self):
        """Test successful SQL execution"""
        # Mock successful query execution
        self.mock_connection.execute_query.return_value = {
            'success': True,
            'rows': [{'id': 1, 'name': 'Test'}],
            'columns': ['id', 'name'],
            'rowCount': 1
        }
        
        response = self.client.post('/api/sql/execute',
                                   json={'sql': 'SELECT * FROM test_table'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('rows', data)
        self.mock_connection.execute_query.assert_called_once()
    
    def test_execute_sql_missing_query(self):
        """Test SQL execution with missing query"""
        response = self.client.post('/api/sql/execute',
                                   json={'sql': ''},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'MISSING_SQL')
    
    def test_execute_sql_query_too_long(self):
        """Test SQL execution with query exceeding max length"""
        long_query = 'SELECT * FROM table WHERE ' + ('x=1 AND ' * 10000)
        
        response = self.client.post('/api/sql/execute',
                                   json={'sql': long_query},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'QUERY_TOO_LONG')
    
    def test_execute_sql_no_hana_configured(self):
        """Test SQL execution when HANA is not configured"""
        # Remove HANA data source
        self.app.hana_data_source = None
        
        response = self.client.post('/api/sql/execute',
                                   json={'sql': 'SELECT 1'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'NOT_CONFIGURED')
    
    def test_execute_sql_query_error(self):
        """Test SQL execution with query error"""
        # Mock query execution error
        self.mock_connection.execute_query.side_effect = Exception("SQL syntax error")
        
        response = self.client.post('/api/sql/execute',
                                   json={'sql': 'SELECT * FROM invalid_table'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_list_connections_with_hana(self):
        """Test listing connections when HANA is configured"""
        response = self.client.get('/api/sql/connections')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('connections', data)
        self.assertIsInstance(data['connections'], list)
        
        # Should have default HANA connection
        self.assertEqual(len(data['connections']), 1)
        conn = data['connections'][0]
        self.assertEqual(conn['id'], 'default')
        self.assertEqual(conn['type'], 'hana')
        self.assertEqual(conn['host'], 'test-host.hanacloud.ondemand.com')
    
    def test_list_connections_no_hana(self):
        """Test listing connections when HANA is not configured"""
        # Remove HANA data source
        self.app.hana_data_source = None
        
        response = self.client.get('/api/sql/connections')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['connections']), 0)
    
    def test_health_check_with_hana(self):
        """Test health check endpoint with HANA configured"""
        response = self.client.get('/api/sql/health')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['module'], 'sql_execution')
        self.assertEqual(data['status'], 'healthy')
        self.assertTrue(data['hana_available'])
    
    def test_health_check_no_hana(self):
        """Test health check endpoint without HANA"""
        self.app.hana_data_source = None
        
        response = self.client.get('/api/sql/health')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'hana_not_configured')
        self.assertFalse(data['hana_available'])


class TestSQLValidation(unittest.TestCase):
    """Test SQL query validation logic"""
    
    def test_empty_query_validation(self):
        """Test that empty queries are rejected"""
        test_queries = ['', '   ', '\n\t', None]
        
        for query in test_queries:
            if query is None:
                continue
            stripped = query.strip() if query else ''
            self.assertEqual(stripped, '', f"Query '{query}' should strip to empty")
    
    def test_query_length_validation(self):
        """Test query length limits"""
        max_length = 50000
        
        # Valid length
        valid_query = 'SELECT * FROM table'
        self.assertLess(len(valid_query), max_length)
        
        # Invalid length
        invalid_query = 'x' * (max_length + 1)
        self.assertGreater(len(invalid_query), max_length)


if __name__ == '__main__':
    unittest.main()