"""
Knowledge Graph v2 Backend

Flask API endpoints for knowledge graph operations.
Version 2.0.0 - Constructor Injection Pattern
"""
from .api import KnowledgeGraphV2API, create_blueprint

__all__ = ['KnowledgeGraphV2API', 'create_blueprint']