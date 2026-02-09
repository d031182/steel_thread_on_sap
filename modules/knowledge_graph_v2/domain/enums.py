"""
Domain Enums for Knowledge Graph v2

Provides type-safe enumerations for graph types, node types, and edge types.
"""
from enum import Enum


class GraphType(Enum):
    """Type of knowledge graph"""
    SCHEMA = 'schema'  # Table-level relationships
    DATA = 'data'      # Record-level relationships
    CSN = 'csn'        # CSN definition relationships


class NodeType(Enum):
    """Type of graph node"""
    TABLE = 'table'      # Database table
    RECORD = 'record'    # Data record/row
    PRODUCT = 'product'  # Data product grouping
    COLUMN = 'column'    # Table column


class EdgeType(Enum):
    """Type of graph edge/relationship"""
    FOREIGN_KEY = 'fk'        # Foreign key relationship
    CONTAINS = 'contains'      # Containment (e.g., product contains tables)
    REFERENCES = 'references'  # Generic reference