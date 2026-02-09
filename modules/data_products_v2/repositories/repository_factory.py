"""
Data Product Repository Factory

Creates appropriate repository based on source type.
Follows Factory Pattern with Dependency Injection.

Author: P2P Development Team
Version: 2.0.0
Date: 2026-02-08
"""

from typing import Optional
from core.interfaces.data_product_repository import IDataProductRepository
from modules.data_products_v2.repositories import (
    SQLiteDataProductRepository,
    HANADataProductRepository
)


class DataProductRepositoryFactory:
    """
    Factory for creating data product repositories
    
    Supports:
    - SQLite (testing/fallback)
    - HANA Cloud (production)
    
    Usage:
        factory = DataProductRepositoryFactory()
        repo = factory.create('sqlite')
        # or
        repo = factory.create('hana', host, port, user, password)
    """
    
    @staticmethod
    def create(
        source_type: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        db_path: Optional[str] = None
    ) -> IDataProductRepository:
        """
        Create repository for specified source type
        
        Args:
            source_type: 'hana' or 'sqlite'
            host: HANA hostname (required for HANA)
            port: HANA port (required for HANA)
            user: HANA user (required for HANA)
            password: HANA password (required for HANA)
            database: HANA database (optional)
            schema: HANA schema (optional)
            db_path: SQLite database path (optional)
        
        Returns:
            IDataProductRepository implementation
        
        Raises:
            ValueError: If source_type invalid or required params missing
        """
        source_type = source_type.lower()
        
        if source_type == 'sqlite':
            return SQLiteDataProductRepository(db_path)
        
        elif source_type == 'hana':
            # Validate required parameters
            if not all([host, port, user, password]):
                raise ValueError(
                    "HANA repository requires: host, port, user, password"
                )
            
            return HANADataProductRepository(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                schema=schema
            )
        
        else:
            raise ValueError(
                f"Unknown source type: {source_type}. "
                f"Valid options: 'hana', 'sqlite'"
            )