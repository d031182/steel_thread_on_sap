-- Graph Ontology Persistence Schema (Versioned)
-- Multiple ontology versions can coexist - edges/nodes reference parent ontology
-- Version: 2.0.0
-- Created: 2026-02-03

-- ============================================================================
-- GRAPH ONTOLOGY (Parent Table - Versions/Snapshots)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_ontology (
    ontology_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,        -- e.g., 'v1.0', 'v1.1', 'snapshot_2026-02-03'
    mode TEXT NOT NULL CHECK(mode IN ('schema', 'data')),
    source TEXT NOT NULL CHECK(source IN ('sqlite', 'hana')),
    description TEXT,
    is_active BOOLEAN DEFAULT 1,         -- Only one active version per mode+source
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'system',
    UNIQUE(mode, source, is_active)      -- Only one active version allowed
);

-- ============================================================================
-- GRAPH NODES (Child Table)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,        -- FK to parent ontology
    node_type TEXT NOT NULL CHECK(node_type IN ('product', 'table', 'column', 'record')),
    node_key TEXT NOT NULL,              -- Unique identifier within ontology
    label TEXT NOT NULL,
    title TEXT,
    group_name TEXT,
    properties_json TEXT,                -- vis.js node properties (color, shape, size, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE,
    UNIQUE(ontology_id, node_key)
);

-- ============================================================================
-- GRAPH EDGES (Child Table)
-- ============================================================================

CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,        -- FK to parent ontology
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
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE,
    UNIQUE(ontology_id, source_node_key, target_node_key, edge_type)
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Ontology lookups
CREATE INDEX IF NOT EXISTS idx_ontology_mode_source 
    ON graph_ontology(mode, source);

CREATE INDEX IF NOT EXISTS idx_ontology_active 
    ON graph_ontology(is_active);

-- Node lookups
CREATE INDEX IF NOT EXISTS idx_nodes_ontology 
    ON graph_nodes(ontology_id);

CREATE INDEX IF NOT EXISTS idx_nodes_type 
    ON graph_nodes(node_type);

CREATE INDEX IF NOT EXISTS idx_nodes_key 
    ON graph_nodes(ontology_id, node_key);

-- Edge lookups
CREATE INDEX IF NOT EXISTS idx_edges_ontology 
    ON graph_edges(ontology_id);

CREATE INDEX IF NOT EXISTS idx_edges_source 
    ON graph_edges(ontology_id, source_node_key);

CREATE INDEX IF NOT EXISTS idx_edges_target 
    ON graph_edges(ontology_id, target_node_key);

CREATE INDEX IF NOT EXISTS idx_edges_active 
    ON graph_edges(is_active);

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- Get active ontology with stats
CREATE VIEW IF NOT EXISTS v_active_ontology_summary AS
SELECT 
    o.ontology_id,
    o.version,
    o.mode,
    o.source,
    o.description,
    COUNT(DISTINCT n.node_id) as node_count,
    COUNT(DISTINCT e.edge_id) as edge_count,
    o.created_at
FROM graph_ontology o
LEFT JOIN graph_nodes n ON o.ontology_id = n.ontology_id
LEFT JOIN graph_edges e ON o.ontology_id = e.ontology_id AND e.is_active = 1
WHERE o.is_active = 1
GROUP BY o.ontology_id;

-- Get complete graph for vis.js (active ontology)
CREATE VIEW IF NOT EXISTS v_active_graph_structure AS
SELECT 
    o.ontology_id,
    o.version,
    o.mode,
    o.source,
    n.node_key,
    n.label as node_label,
    n.node_type,
    n.properties_json as node_properties,
    e.source_node_key,
    e.target_node_key,
    e.edge_type,
    e.label as edge_label,
    e.properties_json as edge_properties
FROM graph_ontology o
LEFT JOIN graph_nodes n ON o.ontology_id = n.ontology_id
LEFT JOIN graph_edges e ON o.ontology_id = e.ontology_id AND e.is_active = 1
WHERE o.is_active = 1;

-- ============================================================================
-- TRIGGERS for Data Integrity
-- ============================================================================

-- Only one active ontology per mode+source
CREATE TRIGGER IF NOT EXISTS enforce_single_active_ontology
BEFORE INSERT ON graph_ontology
WHEN NEW.is_active = 1
BEGIN
    UPDATE graph_ontology 
    SET is_active = 0 
    WHERE mode = NEW.mode 
    AND source = NEW.source 
    AND is_active = 1;
END;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create default active ontology (empty, will be populated on first cache refresh)
INSERT OR IGNORE INTO graph_ontology (version, mode, source, description, is_active)
VALUES 
    ('v1.0-schema-sqlite', 'schema', 'sqlite', 'Default schema ontology for SQLite', 1),
    ('v1.0-data-sqlite', 'data', 'sqlite', 'Default data ontology for SQLite', 1);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Graph Ontology Schema v2.0 Created Successfully!' as status;
SELECT 'Parent: graph_ontology | Children: graph_nodes, graph_edges (with FK)' as structure;