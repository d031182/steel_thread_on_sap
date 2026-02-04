-- Graph Ontology Persistence Schema (Data Source Based)
-- Schema + Data graphs share tables, differentiated by data_source key
-- Version: 3.0.0
-- Created: 2026-02-03

-- ============================================================================
-- GRAPH ONTOLOGY (Parent Table - Data Source Registry)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_ontology (
    data_source TEXT PRIMARY KEY,        -- e.g., 'schema-sqlite', 'data-sqlite', 'schema-hana'
    mode TEXT NOT NULL CHECK(mode IN ('schema', 'data')),
    source_type TEXT NOT NULL CHECK(source_type IN ('sqlite', 'hana')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- GRAPH NODES (Child Table)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_source TEXT NOT NULL,           -- FK to graph_ontology
    node_type TEXT NOT NULL CHECK(node_type IN ('product', 'table', 'column', 'record')),
    node_key TEXT NOT NULL,              -- Unique identifier within data_source
    label TEXT NOT NULL,
    title TEXT,
    group_name TEXT,
    properties_json TEXT,                -- vis.js node properties (color, shape, size, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_source) REFERENCES graph_ontology(data_source) ON DELETE CASCADE,
    UNIQUE(data_source, node_key)
);

-- ============================================================================
-- GRAPH EDGES (Child Table)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_source TEXT NOT NULL,           -- FK to graph_ontology
    source_node_key TEXT NOT NULL,       -- References node_key in graph_nodes
    target_node_key TEXT NOT NULL,
    edge_type TEXT NOT NULL,             -- 'foreign_key', 'contains', 'references', etc.
    label TEXT,
    confidence REAL DEFAULT 1.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
    discovery_method TEXT,               -- 'csn', 'inference', 'manual', etc.
    properties_json TEXT,                -- vis.js edge properties (color, width, arrows, etc.)
    is_active BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_source) REFERENCES graph_ontology(data_source) ON DELETE CASCADE,
    UNIQUE(data_source, source_node_key, target_node_key, edge_type)
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Node lookups
CREATE INDEX IF NOT EXISTS idx_nodes_data_source 
    ON graph_nodes(data_source);

CREATE INDEX IF NOT EXISTS idx_nodes_type 
    ON graph_nodes(node_type);

CREATE INDEX IF NOT EXISTS idx_nodes_key 
    ON graph_nodes(data_source, node_key);

-- Edge lookups
CREATE INDEX IF NOT EXISTS idx_edges_data_source 
    ON graph_edges(data_source);

CREATE INDEX IF NOT EXISTS idx_edges_source 
    ON graph_edges(data_source, source_node_key);

CREATE INDEX IF NOT EXISTS idx_edges_target 
    ON graph_edges(data_source, target_node_key);

CREATE INDEX IF NOT EXISTS idx_edges_active 
    ON graph_edges(is_active);

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- Get data source summaries
CREATE VIEW IF NOT EXISTS v_ontology_summary AS
SELECT 
    o.data_source,
    o.mode,
    o.source_type,
    o.description,
    COUNT(DISTINCT n.node_id) as node_count,
    COUNT(DISTINCT e.edge_id) as edge_count,
    o.created_at,
    o.updated_at
FROM graph_ontology o
LEFT JOIN graph_nodes n ON o.data_source = n.data_source
LEFT JOIN graph_edges e ON o.data_source = e.data_source AND e.is_active = 1
GROUP BY o.data_source;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create default data sources
INSERT OR IGNORE INTO graph_ontology (data_source, mode, source_type, description)
VALUES 
    ('schema-sqlite', 'schema', 'sqlite', 'Schema graph for SQLite data source'),
    ('data-sqlite', 'data', 'sqlite', 'Data graph for SQLite data source'),
    ('schema-hana', 'schema', 'hana', 'Schema graph for HANA data source'),
    ('data-hana', 'data', 'hana', 'Data graph for HANA data source');

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Graph Ontology Schema v3.0 Created!' as status;
SELECT 'data_source is the key - nodes and edges reference it via FK' as design;