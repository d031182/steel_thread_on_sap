-- Graph Cache Tables v5 - Simplified 3-Table Architecture
-- Purpose: Unified cache for both schema and data graphs
-- Design: Single ontology table with type discriminator, cascade deletes

-- Enable foreign key constraints (required for cascade deletes)
PRAGMA foreign_keys = ON;

-- Drop old tables if they exist
DROP TABLE IF EXISTS graph_schema_edges;
DROP TABLE IF EXISTS graph_schema_nodes;
DROP TABLE IF EXISTS graph_ontology_metadata;
DROP TABLE IF EXISTS graph_edges;
DROP TABLE IF EXISTS graph_nodes;
DROP TABLE IF EXISTS graph_ontology;

-- 1. ONTOLOGY TABLE: Master table for graph metadata
CREATE TABLE IF NOT EXISTS graph_ontology (
    ontology_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('schema', 'data')),  -- Discriminator
    data_source TEXT NOT NULL,                              -- 'sqlite', 'hana', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                                          -- JSON metadata
    UNIQUE(type, data_source)                              -- One entry per type+source combo
);

-- 2. NODES TABLE: Graph nodes with FK to ontology
CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    node_key TEXT NOT NULL,                                 -- Unique identifier within ontology
    label TEXT NOT NULL,                                    -- Display label
    node_type TEXT,                                         -- 'table', 'entity', etc.
    properties TEXT,                                        -- JSON properties
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE,
    UNIQUE(ontology_id, node_key)                          -- Unique within ontology
);

-- 3. EDGES TABLE: Graph edges with FK to ontology
CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    from_node_key TEXT NOT NULL,                           -- References node_key
    to_node_key TEXT NOT NULL,                             -- References node_key
    edge_type TEXT NOT NULL,                               -- 'foreign_key', 'references', etc.
    label TEXT,                                             -- Display label
    properties TEXT,                                        -- JSON properties
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE,
    UNIQUE(ontology_id, from_node_key, to_node_key, edge_type)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_nodes_ontology ON graph_nodes(ontology_id);
CREATE INDEX IF NOT EXISTS idx_nodes_key ON graph_nodes(ontology_id, node_key);
CREATE INDEX IF NOT EXISTS idx_edges_ontology ON graph_edges(ontology_id);
CREATE INDEX IF NOT EXISTS idx_edges_from ON graph_edges(ontology_id, from_node_key);
CREATE INDEX IF NOT EXISTS idx_edges_to ON graph_edges(ontology_id, to_node_key);
CREATE INDEX IF NOT EXISTS idx_ontology_lookup ON graph_ontology(type, data_source);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_ontology_timestamp 
AFTER UPDATE ON graph_ontology
BEGIN
    UPDATE graph_ontology SET updated_at = CURRENT_TIMESTAMP WHERE ontology_id = NEW.ontology_id;
END;

-- Verification query
SELECT 'Graph cache tables v5 created successfully' as status;