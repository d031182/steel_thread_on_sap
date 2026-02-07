"""
Repository Package - Factory Pattern Implementation

Exports ONLY:
- AbstractRepository interface (for type hints and DI)
- create_repository() factory function (for instantiation)

Private Implementations:
- _SqliteRepository (internal, do not import directly)
- _HanaRepository (internal, do not import directly)

Usage:
    from core.repositories import AbstractRepository, create_repository
    
    # Create repository via factory
    repository: AbstractRepository = create_repository(
        backend='sqlite',
        db_path='database/p2p_data_products.db'
    )
    
    # Use via interface only
    products = repository.get_data_products()

Benefits:
- Encapsulation: Implementation details hidden
- Testability: Easy to mock AbstractRepository
- Multi-backend: Config-driven backend selection
- Industry Standard: Repository Pattern (DDD)
"""

import os
import sys
from typing import Optional

# Add project root to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(backend_dir))
sys.path.insert(0, project_root)

from core.repositories.base import AbstractRepository


def create_repository(backend: str, **config) -> AbstractRepository:
    """
    Factory function for creating repository instances.
    
    This is the ONLY way to obtain a repository instance. Direct instantiation
    of concrete repositories is forbidden to maintain encapsulation.
    
    Args:
        backend: Repository backend type ('sqlite' or 'hana')
        **config: Backend-specific configuration parameters
        
            For SQLite:
                db_path (str, optional): Path to SQLite database file
                    If not provided, uses default path
            
            For HANA:
                host (str, required): HANA server hostname
                port (int, optional): HANA server port (default: 443)
                user (str, required): HANA username
                password (str, required): HANA password
                database (str, optional): HANA database name
                schema (str, optional): Default schema
    
    Returns:
        AbstractRepository: Repository instance (concrete type hidden)
    
    Raises:
        ValueError: If backend type is unknown
        ImportError: If required dependencies not available
    
    Examples:
        >>> # SQLite repository
        >>> repo = create_repository('sqlite', db_path='/path/to/db.db')
        >>> 
        >>> # HANA repository
        >>> repo = create_repository(
        ...     'hana',
        ...     host='hana.example.com',
        ...     user='SYSTEM',
        ...     password='secret'
        ... )
    """
    if backend == 'sqlite':
        # Import only when needed (lazy loading)
        from core.repositories._sqlite_repository import _SqliteRepository
        
        db_path = config.get('db_path')
        return _SqliteRepository(db_path=db_path)
    
    elif backend == 'hana':
        # Import only when needed (lazy loading)
        from core.repositories._hana_repository import _HanaRepository
        
        # Extract HANA-specific config
        host = config.get('host')
        port = config.get('port', 443)
        user = config.get('user')
        password = config.get('password')
        database = config.get('database')
        schema = config.get('schema')
        
        if not host or not user or not password:
            raise ValueError("HANA backend requires: host, user, password")
        
        return _HanaRepository(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            schema=schema
        )
    
    else:
        raise ValueError(
            f"Unknown backend type: '{backend}'. "
            f"Supported backends: 'sqlite', 'hana'"
        )


# Public API - ONLY these should be imported by other modules
__all__ = ['AbstractRepository', 'create_repository']