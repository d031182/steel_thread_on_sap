-- ============================================================================
-- HANA Property Graph Workspace for P2P Data Model
-- ============================================================================
-- Purpose: Map existing P2P tables to HANA Property Graph for graph algorithms
-- Created: 2026-01-31
-- 
-- Prerequisites:
--   1. P2P schema tables exist in HANA Cloud
--   2. User has CREATE GRAPH WORKSPACE privilege
--   3. Tables have PRIMARY KEY constraints defined
--
-- Usage:
--   Execute in HANA Database Explorer or via hdbsql
--
-- Benefits:
--   - Native HANA graph algorithms (shortest path, centrality, clustering)
--   - 10-100x faster than NetworkX for large graphs
--   - SQL integration (use in same queries as relational data)
--   - Production-scale graph analytics
-- ============================================================================

-- Drop existing workspace if it exists (for clean rebuild)
DROP GRAPH WORKSPACE P2P_GRAPH CASCADE;

-- Create graph workspace with P2P entities
CREATE GRAPH WORKSPACE P2P_GRAPH

  -- ========================================================================
  -- VERTEX TABLES (Entities/Nodes)
  -- ========================================================================
  
  -- Core Master Data
  VERTEX TABLE "Supplier" 
    KEY ("Supplier")
    
  VERTEX TABLE "Product"
    KEY ("Product")
    
  VERTEX TABLE "CompanyCode"
    KEY ("CompanyCode")
    
  VERTEX TABLE "CostCenter"
    KEY ("CostCenter")
    
  VERTEX TABLE "PaymentTerms"
    KEY ("PaymentTerms")
  
  -- Transactional Documents
  VERTEX TABLE "PurchaseOrder"
    KEY ("PurchaseOrder")
    
  VERTEX TABLE "SupplierInvoice"
    KEY ("SupplierInvoice")
    
  VERTEX TABLE "JournalEntry"
    KEY ("AccountingDocument", "CompanyCode", "FiscalYear")
    
  VERTEX TABLE "ServiceEntrySheet"
    KEY ("ServiceEntrySheet")
  
  -- ========================================================================
  -- EDGE TABLES (Relationships)
  -- ========================================================================
  
  -- Purchase Order Relationships
  EDGE TABLE "PurchaseOrderItem"
    KEY ("PurchaseOrder", "PurchaseOrderItem")
    SOURCE KEY ("PurchaseOrder") 
      REFERENCES "PurchaseOrder"("PurchaseOrder")
    TARGET KEY ("Material")
      REFERENCES "Product"("Product")
  
  -- Supplier Invoice Relationships  
  EDGE TABLE "SupplierInvoiceItem"
    KEY ("SupplierInvoice", "SupplierInvoiceItem")
    SOURCE KEY ("SupplierInvoice")
      REFERENCES "SupplierInvoice"("SupplierInvoice")
    TARGET KEY ("PurchaseOrder")
      REFERENCES "PurchaseOrder"("PurchaseOrder");

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check workspace created successfully
SELECT * FROM SYS.GRAPH_WORKSPACES 
WHERE WORKSPACE_NAME = 'P2P_GRAPH';

-- List all vertices in workspace
SELECT * FROM SYS.GRAPH_WORKSPACE_VERTICES
WHERE WORKSPACE_NAME = 'P2P_GRAPH'
ORDER BY TABLE_NAME;

-- List all edges in workspace
SELECT * FROM SYS.GRAPH_WORKSPACE_EDGES
WHERE WORKSPACE_NAME = 'P2P_GRAPH'
ORDER BY TABLE_NAME;

-- Count nodes and edges (performance check)
SELECT 
    'Vertices' as TYPE,
    COUNT(*) as COUNT
FROM SYS.GRAPH_WORKSPACE_VERTICES
WHERE WORKSPACE_NAME = 'P2P_GRAPH'

UNION ALL

SELECT 
    'Edges' as TYPE,
    COUNT(*) as COUNT
FROM SYS.GRAPH_WORKSPACE_EDGES
WHERE WORKSPACE_NAME = 'P2P_GRAPH';

-- ============================================================================
-- EXAMPLE GRAPH QUERIES (Test the workspace)
-- ============================================================================

-- Example 1: Shortest path between two suppliers (via POs)
/*
SELECT * FROM GRAPH_SHORTEST_PATH(
    GRAPH => 'P2P_GRAPH',
    START_VERTEX => 'Supplier:SUP001',
    END_VERTEX => 'Supplier:SUP002',
    MAX_HOPS => 5
);
*/

-- Example 2: Find all products ordered by a supplier
/*
SELECT * FROM GRAPH_NEIGHBORS(
    GRAPH => 'P2P_GRAPH',
    START_VERTEX => 'Supplier:SUP001',
    DIRECTION => 'OUTGOING',
    MIN_DEPTH => 1,
    MAX_DEPTH => 2
);
*/

-- Example 3: Calculate supplier centrality (most connected)
/*
SELECT * FROM GRAPH_BETWEENNESS_CENTRALITY(
    GRAPH => 'P2P_GRAPH',
    VERTEX_TABLE => 'Supplier',
    TOP_K => 10
) ORDER BY CENTRALITY DESC;
*/

-- ============================================================================
-- NEXT STEPS
-- ============================================================================
--
-- 1. Execute this script in HANA Database Explorer
-- 2. Verify workspace created: Check SYS.GRAPH_WORKSPACES
-- 3. Test with example queries above
-- 4. Implement HANAGraphQueryEngine (core/services/hana_graph_query_engine.py)
-- 5. Integrate with Knowledge Graph module
--
-- Documentation: docs/knowledge/components/sap-hana-graph-engines-comparison.md
-- ============================================================================