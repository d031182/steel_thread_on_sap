-- Migration for Full Graph Cache (v3.13)
-- Adds columns needed for caching complete graph nodes
-- Run this before using v3.13 cache features

-- Add graph_mode column to distinguish schema vs data cache
ALTER TABLE graph_schema_nodes ADD COLUMN graph_mode TEXT CHECK(graph_mode IN ('schema', 'data'));

-- Add metadata_json to store complete vis.js node objects
ALTER TABLE graph_schema_nodes ADD COLUMN metadata_json TEXT;

-- Add visual_properties_json for quick color/shape lookup
ALTER TABLE graph_schema_nodes ADD COLUMN visual_properties_json TEXT;

-- Update schema version
UPDATE graph_ontology_metadata 
SET value = '1.1.0' 
WHERE key = 'schema_version';

INSERT OR REPLACE INTO graph_ontology_metadata (key, value) VALUES
    ('cache_version', '3.13'),
    ('cache_enabled', 'true');

SELECT 'Graph Cache Migration Complete (v3.13)' as status;