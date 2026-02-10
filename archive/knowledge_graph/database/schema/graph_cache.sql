-- Graph Cache Schema (Knowledge Graph Module)
-- Generated: 2026-02-05 07:57:08
-- Purpose: Store pre-computed graph visualizations
-- Version: 1.0

CREATE TABLE IF NOT EXISTS graph_ontology (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- 'schema' or 'data'
    data_source TEXT NOT NULL,    -- 'sqlite' or 'hana'
    metadata TEXT,                -- JSON metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    label TEXT NOT NULL,
    group_name TEXT,
    node_data TEXT,               -- JSON: full vis.js node definition
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(id) ON DELETE CASCADE,
    UNIQUE (ontology_id, node_id)
);

CREATE TABLE IF NOT EXISTS graph_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    from_node TEXT NOT NULL,
    to_node TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    edge_data TEXT,               -- JSON: full vis.js edge definition
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_graph_nodes_ontology ON graph_nodes(ontology_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_ontology ON graph_edges(ontology_id);
