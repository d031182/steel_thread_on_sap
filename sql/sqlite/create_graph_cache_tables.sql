-- Graph Cache Schema (Clean Design)
-- Version: 2.0.0
-- Created: 2026-02-01
-- Purpose: Pre-computed graph structure for instant visualization

-- ============================================================================
-- GRAPH ONTOLOGY (Graph Type Definition)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_ontology (
    ontology_id INTEGER PRIMARY KEY AUTOINCREMENT,
    graph_type TEXT NOT NULL CHECK(graph_type IN ('schema', 'data')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(graph_type)
);

-- ============================================================================
-- GRAPH NODES (Pre-computed nodes)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    node_key TEXT NOT NULL,         -- Business key (e.g., 'SUPP-001', 'Supplier')
    node_label TEXT,                -- Display label
    node_type TEXT,                 -- Type (e.g., 'table', 'record', 'entity')
    properties_json TEXT,           -- vis.js properties (color, shape, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE,
    UNIQUE(ontology_id, node_key)
);

-- ============================================================================
-- GRAPH EDGES (Pre-computed edges)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    from_node_key TEXT NOT NULL,
    to_node_key TEXT NOT NULL,
    edge_type TEXT,                 -- Type (e.g., 'foreign_key', 'contains')
    edge_label TEXT,                -- Display label (optional)
    properties_json TEXT,           -- vis.js properties (color, arrows, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_graph_nodes_ontology 
    ON graph_nodes(ontology_id);

CREATE INDEX IF NOT EXISTS idx_graph_nodes_key 
    ON graph_nodes(node_key);

CREATE INDEX IF NOT EXISTS idx_graph_edges_ontology 
    ON graph_edges(ontology_id);

CREATE INDEX IF NOT EXISTS idx_graph_edges_from 
    ON graph_edges(from_node_key);

CREATE INDEX IF NOT EXISTS idx_graph_edges_to 
    ON graph_edges(to_node_key);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Graph Cache Schema Created (v2.0)' as status;
SELECT 'Tables: graph_ontology, graph_nodes, graph_edges' as info;