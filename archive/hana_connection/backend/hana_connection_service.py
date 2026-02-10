"""
HANA Connection Service - Core business logic for HANA Cloud connections

This service provides:
1. Connection management (create, test, close)
2. Credential storage and retrieval
3. Connection health monitoring
4. SQL query execution
5. Multiple instance support

Part of: HANA Connection Module
Version: 1.0
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime


class HanaConnectionService:
    """
    Core service for managing HANA Cloud connections.
    
    Features:
    - Multiple connection instances
    - Credential storage (JSON file)
    - Connection testing
    - Health monitoring
    - Query execution (when hdbcli available)
    """
    
    def __init__(self, storage_file: str = "hana_connections.json"):
        """
        Initialize HANA connection service.
        
        Args:
            storage_file: Path to JSON file for storing connection details
        """
        self.storage_file = Path(storage_file)
        self.connections: Dict[str, dict] = {}
        self.active_connections: Dict[str, Any] = {}  # Actual hdbcli connections
        
        # Load existing connections
        self.load()
        
        # Create empty file if it doesn't exist
        if not self.storage_file.exists():
            self.save()
    
    def load(self) -> bool:
        """
        Load connections from storage file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.connections = data.get('connections', {})
                print(f"[HanaConnectionService] ✓ Loaded {len(self.connections)} connections from {self.storage_file}")
                return True
            else:
                print(f"[HanaConnectionService] ✓ No existing connections file")
                return True
        except Exception as e:
            print(f"[HanaConnectionService] ✗ Error loading connections: {e}")
            return False
    
    def save(self) -> bool:
        """
        Save connections to storage file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directory if needed
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            data = {
                "version": "1.0",
                "lastModified": datetime.now().isoformat(),
                "connections": self.connections
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"[HanaConnectionService] ✓ Saved {len(self.connections)} connections to {self.storage_file}")
            return True
        except Exception as e:
            print(f"[HanaConnectionService] ✗ Error saving connections: {e}")
            return False
    
    def save_connection(self, instance_id: str, connection_details: dict) -> bool:
        """
        Save a HANA connection configuration.
        
        Args:
            instance_id: Unique identifier for this connection
            connection_details: Dict with host, port, user, password, schema
        
        Returns:
            True if saved successfully, False otherwise
        """
        # Validate required fields
        required_fields = ['host', 'port', 'user', 'password']
        for field in required_fields:
            if field not in connection_details:
                print(f"[HanaConnectionService] ✗ Missing required field: {field}")
                return False
        
        # Store connection details
        self.connections[instance_id] = {
            'host': connection_details['host'],
            'port': connection_details['port'],
            'user': connection_details['user'],
            'password': connection_details['password'],
            'schema': connection_details.get('schema', 'P2P_SCHEMA'),
            'displayName': connection_details.get('displayName', instance_id),
            'created': datetime.now().isoformat(),
            'lastModified': datetime.now().isoformat()
        }
        
        self.save()
        print(f"[HanaConnectionService] ✓ Saved connection: {instance_id}")
        return True
    
    def get_connection(self, instance_id: str) -> Optional[dict]:
        """
        Get connection details for a specific instance.
        
        Args:
            instance_id: Connection identifier
        
        Returns:
            Connection details dict or None if not found
        """
        return self.connections.get(instance_id)
    
    def get_all_connections(self) -> Dict[str, dict]:
        """
        Get all stored connections.
        
        Returns:
            Dictionary of instance_id -> connection_details
        """
        return self.connections.copy()
    
    def delete_connection(self, instance_id: str) -> bool:
        """
        Delete a connection configuration.
        
        Args:
            instance_id: Connection identifier
        
        Returns:
            True if deleted successfully, False if not found
        """
        if instance_id in self.connections:
            # Close active connection if exists
            if instance_id in self.active_connections:
                self.close_connection(instance_id)
            
            del self.connections[instance_id]
            self.save()
            print(f"[HanaConnectionService] ✓ Deleted connection: {instance_id}")
            return True
        
        print(f"[HanaConnectionService] ✗ Connection not found: {instance_id}")
        return False
    
    def test_connection(self, instance_id: str) -> dict:
        """
        Test if connection can be established.
        
        Args:
            instance_id: Connection identifier
        
        Returns:
            Dict with success status and message
        """
        connection = self.get_connection(instance_id)
        
        if not connection:
            return {
                'success': False,
                'message': 'Connection not found',
                'code': 'NOT_FOUND'
            }
        
        try:
            # Try to import hdbcli
            from hdbcli import dbapi
            
            # Attempt connection
            conn = dbapi.connect(
                address=connection['host'],
                port=connection['port'],
                user=connection['user'],
                password=connection['password'],
                encrypt=True,
                sslValidateCertificate=False
            )
            
            # Test with simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM DUMMY")
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            print(f"[HanaConnectionService] ✓ Connection test successful: {instance_id}")
            
            return {
                'success': True,
                'message': 'Connection successful',
                'host': connection['host'],
                'user': connection['user']
            }
            
        except ImportError:
            print(f"[HanaConnectionService] ✗ hdbcli not installed")
            return {
                'success': False,
                'message': 'hdbcli not installed',
                'code': 'HDBCLI_NOT_FOUND'
            }
        except Exception as e:
            print(f"[HanaConnectionService] ✗ Connection test failed: {e}")
            return {
                'success': False,
                'message': str(e),
                'code': 'CONNECTION_FAILED'
            }
    
    def get_health_status(self, instance_id: str) -> dict:
        """
        Get health status of a connection.
        
        Args:
            instance_id: Connection identifier
        
        Returns:
            Dict with health status information
        """
        connection = self.get_connection(instance_id)
        
        if not connection:
            return {
                'instanceId': instance_id,
                'status': 'not_found',
                'message': 'Connection not found'
            }
        
        # Test connection
        test_result = self.test_connection(instance_id)
        
        return {
            'instanceId': instance_id,
            'status': 'healthy' if test_result['success'] else 'unhealthy',
            'message': test_result['message'],
            'host': connection['host'],
            'user': connection['user'],
            'lastChecked': datetime.now().isoformat()
        }
    
    def validate_connection_details(self, details: dict) -> dict:
        """
        Validate connection details format.
        
        Args:
            details: Connection details dict
        
        Returns:
            Dict with validation result
        """
        errors = []
        
        # Check required fields
        required_fields = ['host', 'port', 'user', 'password']
        for field in required_fields:
            if field not in details or not details[field]:
                errors.append(f"Missing or empty field: {field}")
        
        # Validate port
        if 'port' in details:
            try:
                port = int(details['port'])
                if port < 1 or port > 65535:
                    errors.append("Port must be between 1 and 65535")
            except (ValueError, TypeError):
                errors.append("Port must be a valid integer")
        
        # Validate host format (basic check)
        if 'host' in details and details['host']:
            host = details['host']
            if not all(c.isalnum() or c in '.-' for c in host):
                errors.append("Host contains invalid characters")
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        
        return {
            'valid': True,
            'message': 'Connection details are valid'
        }
    
    def clear_all_connections(self) -> bool:
        """
        Clear all stored connections.
        
        Returns:
            True if cleared successfully
        """
        # Close all active connections
        for instance_id in list(self.active_connections.keys()):
            self.close_connection(instance_id)
        
        self.connections = {}
        self.save()
        print(f"[HanaConnectionService] ✓ Cleared all connections")
        return True
    
    def close_connection(self, instance_id: str) -> bool:
        """
        Close an active connection.
        
        Args:
            instance_id: Connection identifier
        
        Returns:
            True if closed, False if not active
        """
        if instance_id in self.active_connections:
            try:
                conn = self.active_connections[instance_id]
                conn.close()
                del self.active_connections[instance_id]
                print(f"[HanaConnectionService] ✓ Closed connection: {instance_id}")
                return True
            except Exception as e:
                print(f"[HanaConnectionService] ✗ Error closing connection: {e}")
                return False
        
        return False
    
    def get_connection_count(self) -> int:
        """
        Get total number of stored connections.
        
        Returns:
            Count of connections
        """
        return len(self.connections)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<HanaConnectionService: {self.get_connection_count()} connections>"


# Global instance (singleton pattern)
_hana_service_instance: Optional[HanaConnectionService] = None


def get_hana_connection_service(storage_file: str = "hana_connections.json") -> HanaConnectionService:
    """
    Get the global HANA connection service instance.
    
    Args:
        storage_file: Path to storage file
    
    Returns:
        HanaConnectionService instance
    """
    global _hana_service_instance
    
    if _hana_service_instance is None:
        _hana_service_instance = HanaConnectionService(storage_file)
    
    return _hana_service_instance


if __name__ == "__main__":
    # Test HANA connection service
    print("=== HANA Connection Service Test ===\n")
    
    # Create instance
    service = HanaConnectionService("test_hana_connections.json")
    
    print(f"\nService: {service}")
    print(f"Total connections: {service.get_connection_count()}")
    
    # Test save connection
    print("\n--- Testing Save Connection ---")
    result = service.save_connection("test1", {
        "host": "test.hanacloud.ondemand.com",
        "port": 443,
        "user": "TEST_USER",
        "password": "test_password",
        "schema": "TEST_SCHEMA"
    })
    print(f"Save result: {result}")
    
    # Test get connection
    print("\n--- Testing Get Connection ---")
    conn = service.get_connection("test1")
    print(f"Retrieved: {conn['host']} / {conn['user']}")
    
    # Test validate
    print("\n--- Testing Validation ---")
    validation = service.validate_connection_details({
        "host": "test.com",
        "port": 443,
        "user": "user",
        "password": "pass"
    })
    print(f"Validation: {validation}")
    
    # Cleanup test file
    if Path("test_hana_connections.json").exists():
        Path("test_hana_connections.json").unlink()
        print("\n✓ Test cleanup complete")