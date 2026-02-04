-- Graph Visualization Cache (Memento Pattern)
-- Stores pre-built vis.js graph structures for instant retrieval
-- Version: 1.0.0
-- Created: 2026-02-02

-- ============================================================================
-- VIS.JS GRAPH STRUCTURE CACHE
-- ============================================================================

-- Cache complete vis.js graph structures (nodes + edges JSON)
CREATE TABLE IF NOT EXISTS graph_visjs_cache (
    cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT NOT NULL CHECK(mode IN ('schema', 'data')),
    source TEXT NOT NULL CHECK(source IN ('sqlite', 'hana')),
    nodes_json TEXT NOT NULL,  -- JSON array of vis.js nodes
    edges_json TEXT NOT NULL,  -- JSON array of vis.js edges
    stats_json TEXT,           -- Statistics (node_count, edge_count, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,      -- NULL = never expires
    UNIQUE(mode, source)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_visjs_cache_mode_source 
    ON graph_visjs_cache(mode, source);

-- ============================================================================
-- HELPER VIEW
-- ============================================================================

CREATE VIEW IF NOT EXISTS v_graph_visjs_cache_summary AS
SELECT 
    mode,
    source,
    LENGTH(nodes_json) as nodes_size_bytes,
    LENGTH(edges_json) as edges_size_bytes,
    created_at,
    expires_at,
    CASE 
        WHEN expires_at IS NULL THEN 'never'
        WHEN datetime(expires_at) > datetime('now') THEN 'valid'
        ELSE 'expired'
    END as status
FROM graph_visjs_cache
ORDER BY mode, source;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Graph Vis.js Cache Created Successfully!' as status;