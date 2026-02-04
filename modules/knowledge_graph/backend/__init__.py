"""
Knowledge Graph Backend

Backend services for data relationship graph generation.

@author P2P Development Team
@version 2.0.0 (Upgraded to api_v2 with FACADE pattern + layout endpoints)
"""

# Import api_v2 (new FACADE-based API with layout endpoints)
from modules.knowledge_graph.backend.api_v2 import knowledge_graph_api
from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder
from modules.knowledge_graph.backend.knowledge_graph_facade import KnowledgeGraphFacade

__all__ = ['knowledge_graph_api', 'DataGraphBuilder', 'KnowledgeGraphFacade']
