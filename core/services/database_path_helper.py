"""
Simplified Database Path Helper

Replaces the complex strategy pattern (400+ lines, 5 resolver classes) with
a simple convention-based approach: modules/{module_name}/database/{db_name}.db

This simplification removes:
- IDatabasePathResolver interface
- ModuleOwnedPathResolver, SharedPathResolver, ConfigurablePathResolver, etc.
- DatabasePathResolverFactory
- Dependency Injection complexity

Key Insight (from MED-031):
"The module ownership is already clear from the database mapping. Why add
another layer of abstraction?"

Database Mapping Convention:
- p2p_data → modules/data_products_v2/database/p2p_data.db
- p2p_graph → modules/knowledge_graph_v2/database/p2p_graph.db
- ai_assistant → modules/ai_assistant/database/ai_assistant.db (future)
- logger → modules/logger/database/logger.db (future)
"""

import os
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

# Database to module mapping (single source of truth)
DATABASE_MODULE_MAP: Dict[str, str] = {
    'p2p_data': 'data_products_v2',
    'p2p_graph': 'knowledge_graph_v2',
    'ai_assistant': 'ai_assistant',
    'logger': 'logger',
}


def get_database_path(database_name: str, base_dir: str = None) -> str:
    """
    Get the path to a database file using convention: modules/{module}/database/{db}.db
    
    Args:
        database_name: Name of the database (e.g., 'p2p_data', 'p2p_graph')
        base_dir: Base directory for path resolution (defaults to project root)
    
    Returns:
        Absolute path to the database file
    
    Raises:
        ValueError: If database_name is not in DATABASE_MODULE_MAP
    
    Examples:
        >>> get_database_path('p2p_data')
        'c:/Users/.../steel_thread_on_sap/modules/data_products_v2/database/p2p_data.db'
        
        >>> get_database_path('p2p_graph')
        'c:/Users/.../steel_thread_on_sap/modules/knowledge_graph_v2/database/p2p_graph.db'
    """
    # Validate database name
    if database_name not in DATABASE_MODULE_MAP:
        raise ValueError(
            f"Unknown database '{database_name}'. "
            f"Valid databases: {list(DATABASE_MODULE_MAP.keys())}"
        )
    
    # Get module name from mapping
    module_name = DATABASE_MODULE_MAP[database_name]
    
    # Determine base directory
    if base_dir is None:
        # Default to project root (2 levels up from this file)
        base_dir = Path(__file__).parent.parent.parent
    else:
        base_dir = Path(base_dir)
    
    # Construct path using convention
    db_path = base_dir / 'modules' / module_name / 'database' / f'{database_name}.db'
    
    # Ensure database directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to absolute path and normalize
    db_path = db_path.resolve()
    
    logger.debug(f"Database path resolved: {database_name} → {db_path}")
    
    return str(db_path)


def get_test_database_path(database_name: str = 'test') -> str:
    """
    Get an in-memory database path for testing.
    
    Args:
        database_name: Name for the test database (default: 'test')
    
    Returns:
        SQLite in-memory path (':memory:')
    
    Example:
        >>> get_test_database_path()
        ':memory:'
    """
    logger.debug(f"Test database path: {database_name} → :memory:")
    return ':memory:'


def register_database(database_name: str, module_name: str) -> None:
    """
    Register a new database-to-module mapping.
    
    Args:
        database_name: Name of the database
        module_name: Name of the owning module
    
    Example:
        >>> register_database('custom_db', 'custom_module')
        >>> get_database_path('custom_db')
        'modules/custom_module/database/custom_db.db'
    """
    DATABASE_MODULE_MAP[database_name] = module_name
    logger.info(f"Registered database: {database_name} → {module_name}")