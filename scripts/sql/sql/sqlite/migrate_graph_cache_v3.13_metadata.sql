-- Migration for Full Graph Cache (v3.13) - Metadata Approach
-- Uses existing graph_ontology_metadata table as key-value store
-- No new tables needed!

-- Add cache entries as key-value pairs
INSERT OR REPLACE INTO graph_ontology_metadata (key, value) VALUES
    ('cache_schema_nodes', NULL),  -- Will store JSON array of vis.js nodes
    ('cache_schema_edges', NULL),  -- Will store JSON array of vis.js edges
    ('cache_data_nodes', NULL),    -- Will store JSON array of vis.js nodes
    ('cache_data_edges', NULL),    -- Will store JSON array of vis.js edges
    ('cache_schema_updated', NULL), -- Timestamp of last schema cache
    ('cache_data_updated', NULL),   -- Timestamp of last data cache
    ('cache_version', '3.13'),
    ('cache_enabled', 'true');

-- Update schema version
UPDATE graph_ontology_metadata 
SET value = '1.1.0', updated_at = CURRENT_TIMESTAMP
WHERE key = 'schema_version';

SELECT 'Graph Cache Migration Complete (v3.13) - Metadata Approach' as status;
SELECT 'Cache keys added to graph_ontology_metadata table' as info;