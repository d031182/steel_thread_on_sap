-- Graph Ontology Persistence Schema (Composite PK Design)
-- Uses composite primary key (data_source, mode) for flexibility
-- Version: 4.0.0
-- Created: 2026-02-03

-- ============================================================================
-- GRAPH ONTOLOGY (Parent Table - Composite PK)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_ontology (
    data_source TEXT NOT NULL CHECK(data_source IN ('sqlite', 'hana')),
    mode TEXT NOT NULL CHECK(mode IN ('schema', 'data')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (data_source, mode)
);

-- ============================================================================
-- GRAPH NODES (Child Table - Composite FK)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_source TEXT NOT NULL,
    mode TEXT NOT NULL,
    node_type TEXT NOT NULL CHECK(node_type IN ('product', 'table', 'column', 'record')),
    node_key TEXT NOT NULL,
    label TEXT NOT NULL,
    title TEXT,
    group_name TEXT,
    properties_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_source, mode) REFERENCES graph_ontology(data_source, mode) ON DELETE CASCADE,
    UNIQUE(data_source, mode, node_key)
);

-- ============================================================================
-- GRAPH EDGES (Child Table - Composite FK)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_source TEXT NOT NULL,
    mode TEXT NOT NULL,
    source_node_key TEXT NOT NULL,
    target_node_key TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    label TEXT,
    confidence REAL DEFAULT 1.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
    discovery_method TEXT,
    properties_json TEXT,
    is_active BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_source, mode) REFERENCES graph_ontology(data_source, mode) ON DELETE CASCADE,
    UNIQUE(data_source, mode, source_node_key, target_node_key, edge_type)
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Node lookups
CREATE INDEX IF NOT EXISTS idx_nodes_data_source_mode 
    ON graph_nodes(data_source, mode);

CREATE INDEX IF NOT EXISTS idx_nodes_type 
    ON graph_nodes(node_type);

CREATE INDEX IF NOT EXISTS idx_nodes_key 
    ON graph_nodes(data_source, mode, node_key);

-- Edge lookups
CREATE INDEX IF NOT EXISTS idx_edges_data_source_mode 
    ON graph_edges(data_source, mode);

CREATE INDEX IF NOT EXISTS idx_edges_source 
    ON graph_edges(data_source, mode, source_node_key);

CREATE INDEX IF NOT EXISTS idx_edges_target 
    ON graph_edges(data_source, mode, target_node_key);

CREATE INDEX IF NOT EXISTS idx_edges_active 
    ON graph_edges(is_active);

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- Get summaries by data source and mode
CREATE VIEW IF NOT EXISTS v_ontology_summary AS
SELECT 
    o.data_source,
    o.mode,
    o.description,
    COUNT(DISTINCT n.node_id) as node_count,
    COUNT(DISTINCT e.edge_id) as edge_count,
    o.created_at,
    o.updated_at
FROM graph_ontology o
LEFT JOIN graph_nodes n ON o.data_source = n.data_source AND o.mode = n.mode
LEFT JOIN graph_edges e ON o.data_source = e.data_source AND o.mode = e.mode AND e.is_active = 1
GROUP BY o.data_source, o.mode;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create default data sources (2 sources x 2 modes = 4 combinations)
INSERT OR IGNORE INTO graph_ontology (data_source, mode, description)
VALUES 
    ('sqlite', 'schema', 'Schema graph for SQLite data source'),
    ('sqlite', 'data', 'Data graph for SQLite data source'),
    ('hana', 'schema', 'Schema graph for HANA data source'),
    ('hana', 'data', 'Data graph for HANA data source');

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Graph Ontology Schema v4.0 Created!' as status;
SELECT 'Composite PK (data_source, mode) with composite FK in children' as design;