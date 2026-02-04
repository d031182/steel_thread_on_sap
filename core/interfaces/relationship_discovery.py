"""
Relationship Discovery Interface

Defines the contract for discovering foreign key relationships between tables.
Enables multiple discovery strategies (database-based, CSN-based, hybrid, etc.)
that can be swapped via dependency injection.

@author P2P Development Team
@version 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class IRelationshipDiscovery(ABC):
    """
    Interface for foreign key relationship discovery strategies.
    
    Implementations might use:
    - Database metadata (INFORMATION_SCHEMA)
    - CSN metadata files
    - Ontology cache
    - Manual inference patterns
    - AI/ML-based discovery
    
    The contract ensures all strategies return the same data structure,
    enabling seamless swapping via dependency injection.
    """
    
    @abstractmethod
    def discover_fk_mappings(self, tables: List[Dict[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
        """
        Discover foreign key relationships for the given tables.
        
        Args:
            tables: List of dicts with 'schema' and 'table' keys
                   Example: [{'schema': 'Supplier', 'table': 'Supplier'}, ...]
        
        Returns:
            Dictionary mapping source table to list of (fk_column, target_table) tuples
            Example: {
                'PurchaseOrder': [
                    ('Supplier', 'Supplier'),
                    ('CompanyCode', 'CompanyCode')
                ],
                'SupplierInvoice': [
                    ('Supplier', 'Supplier'),
                    ('CompanyCode', 'CompanyCode')
                ]
            }
        
        Raises:
            Exception: If discovery fails for any reason
        """
        pass