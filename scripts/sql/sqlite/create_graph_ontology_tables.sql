-- Graph Ontology Persistence Schema
-- Aligns with HANA Property Graph engine architecture
-- Version: 1.0.0
-- Created: 2026-01-31

-- ============================================================================
-- SCHEMA GRAPH (Metadata: Tables, Columns, Relationships)
-- ============================================================================

-- Schema Nodes: Tables and Columns
CREATE TABLE IF NOT EXISTS graph_schema_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_type TEXT NOT NULL CHECK(node_type IN ('table', 'column')),
    name TEXT NOT NULL,
    parent_table TEXT,  -- NULL for tables, table name for columns
    data_type TEXT,     -- NULL for tables, CDS type for columns
    is_key BOOLEAN DEFAULT 0,
    is_nullable BOOLEAN DEFAULT 1,
    max_length INTEGER,
    precision INTEGER,
    scale INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(node_type, name, parent_table)
);

-- Schema Edges: Relationships between tables
CREATE TABLE IF NOT EXISTS graph_schema_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_table TEXT NOT NULL,
    source_column TEXT NOT NULL,
    target_table TEXT NOT NULL,
    target_column TEXT,  -- NULL if relationship to entire table
    relationship_type TEXT NOT NULL,  -- 'foreign_key', 'one_to_many', 'many_to_one', etc.
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    discovery_method TEXT NOT NULL CHECK(discovery_method IN (
        'csn_metadata',      -- Discovered from CSN associations
        'csn_inference',     -- Inferred from CSN patterns
        'manual_verified',   -- Manually verified by admin
        'manual_override'    -- Manually added by admin
    )),
    is_active BOOLEAN DEFAULT 1,  -- Can be disabled without deleting
    notes TEXT,  -- Admin notes about the relationship
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_table, source_column, target_table, target_column)
);

-- Ontology Metadata: Track schema versions, last updates, etc.
CREATE TABLE IF NOT EXISTS graph_ontology_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Node lookups
CREATE INDEX IF NOT EXISTS idx_schema_nodes_type_name 
    ON graph_schema_nodes(node_type, name);

CREATE INDEX IF NOT EXISTS idx_schema_nodes_parent 
    ON graph_schema_nodes(parent_table);

-- Edge lookups (most common queries)
CREATE INDEX IF NOT EXISTS idx_schema_edges_source 
    ON graph_schema_edges(source_table);

CREATE INDEX IF NOT EXISTS idx_schema_edges_target 
    ON graph_schema_edges(target_table);

CREATE INDEX IF NOT EXISTS idx_schema_edges_confidence 
    ON graph_schema_edges(confidence DESC);

CREATE INDEX IF NOT EXISTS idx_schema_edges_active 
    ON graph_schema_edges(is_active);

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- High-confidence relationships only
CREATE VIEW IF NOT EXISTS v_graph_schema_edges_confident AS
SELECT * FROM graph_schema_edges 
WHERE is_active = 1 AND confidence >= 0.9
ORDER BY confidence DESC;

-- Manually verified relationships
CREATE VIEW IF NOT EXISTS v_graph_schema_edges_verified AS
SELECT * FROM graph_schema_edges 
WHERE is_active = 1 
AND discovery_method IN ('manual_verified', 'manual_override')
ORDER BY source_table, target_table;

-- All tables with their relationships
CREATE VIEW IF NOT EXISTS v_graph_schema_summary AS
SELECT 
    source_table,
    COUNT(*) as relationship_count,
    AVG(confidence) as avg_confidence,
    MAX(updated_at) as last_updated
FROM graph_schema_edges
WHERE is_active = 1
GROUP BY source_table
ORDER BY relationship_count DESC;

-- ============================================================================
-- TRIGGERS for Audit Trail
-- ============================================================================

-- Update timestamp on changes
CREATE TRIGGER IF NOT EXISTS update_schema_nodes_timestamp 
AFTER UPDATE ON graph_schema_nodes
BEGIN
    UPDATE graph_schema_nodes 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE node_id = NEW.node_id;
END;

CREATE TRIGGER IF NOT EXISTS update_schema_edges_timestamp 
AFTER UPDATE ON graph_schema_edges
BEGIN
    UPDATE graph_schema_edges 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE edge_id = NEW.edge_id;
END;

-- ============================================================================
-- INITIAL METADATA
-- ============================================================================

INSERT OR REPLACE INTO graph_ontology_metadata (key, value) VALUES
    ('schema_version', '1.0.0'),
    ('created_at', CURRENT_TIMESTAMP),
    ('last_discovery', NULL),
    ('total_relationships', '0');

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Graph Ontology Schema Created Successfully!' as status;
SELECT 'Tables: graph_schema_nodes, graph_schema_edges, graph_ontology_metadata' as tables;
SELECT 'Views: v_graph_schema_edges_confident, v_graph_schema_edges_verified, v_graph_schema_summary' as views;