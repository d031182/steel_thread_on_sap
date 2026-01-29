"""
Knowledge Graph Module

Visualizes data relationships as an interactive graph showing how records
are connected via foreign keys.

@author P2P Development Team
@version 1.0.0
"""

from modules.knowledge_graph.backend.api import knowledge_graph_api
from modules.knowledge_graph.backend.data_graph_service import DataGraphService

__all__ = ['knowledge_graph_api', 'DataGraphService']