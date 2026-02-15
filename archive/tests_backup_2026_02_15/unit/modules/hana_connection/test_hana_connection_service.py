"""
HANA Connection Service Unit Tests
===================================
Comprehensive tests for HanaConnectionService core functionality.

Test Coverage:
- Connection CRUD operations (save, get, delete)
- Validation logic (connection details)
- File persistence (load, save)
- Health monitoring (test_connection, get_health_status)
- Edge cases and error handling

Author: P2P Development Team
Created: 2026-02-05 (WP-GW-002 Phase 2)
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from modules.hana_connection.backend.hana_connection_service import (
    HanaConnectionService,
    get_hana_connection_service
)


# ============================================================================
# Test Suite: Connection CRUD Operations
# ============================================================================

class TestConnectionCRUD:
    """Test create, read, update, delete operations for connections."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_save_connection_success(self, tmp_path):
        """
        Test save_connection with valid connection details.
        
        AAA Pattern:
        - ARRANGE: Create service with temp file, prepare valid connection data
        - ACT: Save connection
        - ASSERT: Connection saved correctly, file exists
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        connection_details = {
            'host': 'test.hanacloud.ondemand.com',
            'port': 443,
            'user': 'TEST_USER',
            'password': 'test_password',
            'schema': 'TEST_SCHEMA'
        }
        
        # ACT
        result = service.save_connection('test1', connection_details)
        
        # ASSERT
        assert result is True
        assert 'test1' in service.connections
        assert service.connections['test1']['host'] == 'test.hanacloud.ondemand.com'
        assert storage_file.exists()
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_save_connection_missing_required_field(self, tmp_path):
        """
        Test save_connection fails with missing required field.
        
        AAA Pattern:
        - ARRANGE: Create service, prepare incomplete connection data
        - ACT: Attempt to save connection
        - ASSERT: Save fails, no connection stored
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        connection_details = {
            'host': 'test.hanacloud.ondemand.com',
            'port': 443,
            # Missing 'user' and 'password'
        }
        
        # ACT
        result = service.save_connection('test1', connection_details)
        
        # ASSERT
        assert result is False
        assert 'test1' not in service.connections
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_connection_success(self, tmp_path):
        """
        Test get_connection retrieves saved connection.
        
        AAA Pattern:
        - ARRANGE: Create service, save a connection
        - ACT: Get the connection
        - ASSERT: Retrieved connection matches saved data
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        connection_details = {
            'host': 'test.hanacloud.ondemand.com',
            'port': 443,
            'user': 'TEST_USER',
            'password': 'test_password'
        }
        service.save_connection('test1', connection_details)
        
        # ACT
        retrieved = service.get_connection('test1')
        
        # ASSERT
        assert retrieved is not None
        assert retrieved['host'] == 'test.hanacloud.ondemand.com'
        assert retrieved['user'] == 'TEST_USER'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_connection_not_found(self, tmp_path):
        """
        Test get_connection returns None for non-existent connection.
        
        AAA Pattern:
        - ARRANGE: Create empty service
        - ACT: Get non-existent connection
        - ASSERT: Returns None
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        # ACT
        retrieved = service.get_connection('nonexistent')
        
        # ASSERT
        assert retrieved is None
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_delete_connection_success(self, tmp_path):
        """
        Test delete_connection removes connection.
        
        AAA Pattern:
        - ARRANGE: Create service, save connection
        - ACT: Delete the connection
        - ASSERT: Connection removed, file updated
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        connection_details = {
            'host': 'test.hanacloud.ondemand.com',
            'port': 443,
            'user': 'TEST_USER',
            'password': 'test_password'
        }
        service.save_connection('test1', connection_details)
        
        # ACT
        result = service.delete_connection('test1')
        
        # ASSERT
        assert result is True
        assert 'test1' not in service.connections
        assert service.get_connection('test1') is None
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_all_connections(self, tmp_path):
        """
        Test get_all_connections returns all saved connections.
        
        AAA Pattern:
        - ARRANGE: Create service, save multiple connections
        - ACT: Get all connections
        - ASSERT: All connections returned
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        service.save_connection('test1', {
            'host': 'test1.com', 'port': 443, 'user': 'user1', 'password': 'pass1'
        })
        service.save_connection('test2', {
            'host': 'test2.com', 'port': 443, 'user': 'user2', 'password': 'pass2'
        })
        
        # ACT
        all_connections = service.get_all_connections()
        
        # ASSERT
        assert len(all_connections) == 2
        assert 'test1' in all_connections
        assert 'test2' in all_connections


# ============================================================================
# Test Suite: Validation Logic
# ============================================================================

class TestValidationLogic:
    """Test connection details validation."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_validate_connection_details_valid(self, tmp_path):
        """
        Test validate_connection_details with valid input.
        
        AAA Pattern:
        - ARRANGE: Create service, prepare valid connection details
        - ACT: Validate details
        - ASSERT: Validation succeeds
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        details = {
            'host': 'test.hanacloud.ondemand.com',
            'port': 443,
            'user': 'TEST_USER',
            'password': 'test_password'
        }
        
        # ACT
        result = service.validate_connection_details(details)
        
        # ASSERT
        assert result['valid'] is True
        assert 'message' in result
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_validate_connection_details_missing_fields(self, tmp_path):
        """
        Test validate_connection_details with missing required fields.
        
        AAA Pattern:
        - ARRANGE: Create service, prepare incomplete details
        - ACT: Validate details
        - ASSERT: Validation fails with error messages
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        details = {
            'host': 'test.com',
            # Missing port, user, password
        }
        
        # ACT
        result = service.validate_connection_details(details)
        
        # ASSERT
        assert result['valid'] is False
        assert 'errors' in result
        assert len(result['errors']) > 0
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_validate_connection_details_invalid_port(self, tmp_path):
        """
        Test validate_connection_details with invalid port.
        
        AAA Pattern:
        - ARRANGE: Create service, prepare details with invalid port
        - ACT: Validate details
        - ASSERT: Validation fails with port error
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        details = {
            'host': 'test.com',
            'port': 99999,  # Invalid port > 65535
            'user': 'user',
            'password': 'pass'
        }
        
        # ACT
        result = service.validate_connection_details(details)
        
        # ASSERT
        assert result['valid'] is False
        assert any('Port' in error or 'port' in error for error in result['errors'])


# ============================================================================
# Test Suite: File Persistence
# ============================================================================

class TestFilePersistence:
    """Test file loading and saving functionality."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_load_from_existing_file(self, tmp_path):
        """
        Test load() reads connections from existing file.
        
        AAA Pattern:
        - ARRANGE: Create JSON file with connections, then create service
        - ACT: Service auto-loads on init
        - ASSERT: Connections loaded correctly
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        test_data = {
            "version": "1.0",
            "connections": {
                "test1": {
                    "host": "test.com",
                    "port": 443,
                    "user": "user",
                    "password": "pass"
                }
            }
        }
        storage_file.write_text(json.dumps(test_data), encoding='utf-8')
        
        # ACT
        service = HanaConnectionService(str(storage_file))
        
        # ASSERT
        assert len(service.connections) == 1
        assert 'test1' in service.connections
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_save_creates_file_and_directory(self, tmp_path):
        """
        Test save() creates file and parent directories if needed.
        
        AAA Pattern:
        - ARRANGE: Create service with nested path that doesn't exist
        - ACT: Save a connection
        - ASSERT: File and directories created
        """
        # ARRANGE
        nested_path = tmp_path / "subdir" / "test_connections.json"
        service = HanaConnectionService(str(nested_path))
        
        connection_details = {
            'host': 'test.com',
            'port': 443,
            'user': 'user',
            'password': 'pass'
        }
        
        # ACT
        service.save_connection('test1', connection_details)
        
        # ASSERT
        assert nested_path.exists()
        assert nested_path.parent.exists()
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_clear_all_connections(self, tmp_path):
        """
        Test clear_all_connections removes all connections.
        
        AAA Pattern:
        - ARRANGE: Create service with multiple connections
        - ACT: Clear all connections
        - ASSERT: All connections removed, file updated
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        service.save_connection('test1', {
            'host': 'test1.com', 'port': 443, 'user': 'user1', 'password': 'pass1'
        })
        service.save_connection('test2', {
            'host': 'test2.com', 'port': 443, 'user': 'user2', 'password': 'pass2'
        })
        
        # ACT
        result = service.clear_all_connections()
        
        # ASSERT
        assert result is True
        assert len(service.connections) == 0
        assert service.get_connection_count() == 0


# ============================================================================
# Test Suite: Health Monitoring
# ============================================================================

class TestHealthMonitoring:
    """Test connection testing and health status."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_test_connection_not_found(self, tmp_path):
        """
        Test test_connection returns NOT_FOUND for non-existent connection.
        
        AAA Pattern:
        - ARRANGE: Create empty service
        - ACT: Test non-existent connection
        - ASSERT: Returns NOT_FOUND error
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        # ACT
        result = service.test_connection('nonexistent')
        
        # ASSERT
        assert result['success'] is False
        assert result['code'] == 'NOT_FOUND'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_test_connection_hdbcli_not_installed(self, tmp_path):
        """
        Test test_connection handles missing hdbcli gracefully.
        
        AAA Pattern:
        - ARRANGE: Create service with connection, mock hdbcli import to fail
        - ACT: Test connection
        - ASSERT: Returns HDBCLI_NOT_FOUND error
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        service.save_connection('test1', {
            'host': 'test.com', 'port': 443, 'user': 'user', 'password': 'pass'
        })
        
        # ACT - Mock hdbcli import failure
        with patch('builtins.__import__', side_effect=ImportError("No module named 'hdbcli'")):
            result = service.test_connection('test1')
        
        # ASSERT
        assert result['success'] is False
        assert result['code'] == 'HDBCLI_NOT_FOUND'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_health_status_not_found(self, tmp_path):
        """
        Test get_health_status returns not_found for non-existent connection.
        
        AAA Pattern:
        - ARRANGE: Create empty service
        - ACT: Get health status for non-existent connection
        - ASSERT: Returns not_found status
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        # ACT
        result = service.get_health_status('nonexistent')
        
        # ASSERT
        assert result['status'] == 'not_found'
        assert result['instanceId'] == 'nonexistent'


# ============================================================================
# Test Suite: Utility Methods
# ============================================================================

class TestUtilityMethods:
    """Test utility methods like get_connection_count, __repr__."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_connection_count(self, tmp_path):
        """
        Test get_connection_count returns correct count.
        
        AAA Pattern:
        - ARRANGE: Create service with multiple connections
        - ACT: Get connection count
        - ASSERT: Count is correct
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        
        service.save_connection('test1', {
            'host': 'test1.com', 'port': 443, 'user': 'user1', 'password': 'pass1'
        })
        service.save_connection('test2', {
            'host': 'test2.com', 'port': 443, 'user': 'user2', 'password': 'pass2'
        })
        
        # ACT
        count = service.get_connection_count()
        
        # ASSERT
        assert count == 2
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_repr(self, tmp_path):
        """
        Test __repr__ returns string representation.
        
        AAA Pattern:
        - ARRANGE: Create service with connections
        - ACT: Get string representation
        - ASSERT: Representation includes connection count
        """
        # ARRANGE
        storage_file = tmp_path / "test_connections.json"
        service = HanaConnectionService(str(storage_file))
        service.save_connection('test1', {
            'host': 'test1.com', 'port': 443, 'user': 'user1', 'password': 'pass1'
        })
        
        # ACT
        repr_str = repr(service)
        
        # ASSERT
        assert "HanaConnectionService" in repr_str
        assert "1 connections" in repr_str


# ============================================================================
# Test Suite: Singleton Pattern
# ============================================================================

class TestSingletonPattern:
    """Test global instance management."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_hana_connection_service_singleton(self, tmp_path):
        """
        Test get_hana_connection_service returns singleton instance.
        
        AAA Pattern:
        - ARRANGE: Clear global instance
        - ACT: Get service twice
        - ASSERT: Both calls return same instance
        """
        # ARRANGE
        import modules.hana_connection.backend.hana_connection_service as service_module
        service_module._hana_service_instance = None
        
        storage_file = tmp_path / "test_connections.json"
        
        # ACT
        service1 = get_hana_connection_service(str(storage_file))
        service2 = get_hana_connection_service(str(storage_file))
        
        # ASSERT
        assert service1 is service2


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def tmp_path(tmpdir):
    """Provide a temporary directory for test files."""
    return Path(tmpdir)