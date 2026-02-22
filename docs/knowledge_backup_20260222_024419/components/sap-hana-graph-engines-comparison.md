# SAP HANA Cloud Graph Engines: Knowledge Graph vs Property Graph

**Created**: 2026-01-30  
**Research Source**: Perplexity AI (SAP official sources, Q1 2025)  
**Purpose**: Understand SAP HANA's dual graph engines to inform our application's knowledge graph vision

---

## Executive Summary

SAP HANA Cloud offers **TWO distinct graph engines** (as of Q1 2025), each optimized for different analytical needs:

1. **Property Graph Engine** - Structural network analysis (paths, clusters, optimization)
2. **Knowledge Graph Engine** - Semantic reasoning and contextual intelligence (NEW in Q1 2025)

**Key Insight**: These are **complementary, not competing** - use both together for complete insights! 🎯

---

## Quick Comparison Table

| Aspect | Property Graph Engine | Knowledge Graph Engine |
|--------|----------------------|------------------------|
| **Data Model** | Nodes + Edges (key-value properties) | RDF Triples (subject-predicate-object) |
| **Standards** | Graph algorithms (centrality, clustering) | RDF, SPARQL, RDFS, OWL |
| **Query Language** | SQL + Graph traversal | SPARQL + SQL integration |
| **Focus** | "HOW connected?" (structure) | "WHAT does it mean?" (semantics) |
| **Use Cases** | Supply chain optimization, fraud detection | AI grounding, semantic search, inference |
| **Availability** | Available since HANA 2.0 | NEW - Q1 2025+ |
| **Integration** | SQL native | SQL + SPARQL hybrid |

---

## Property Graph Engine (Structural Analysis)

### What Is It?

**Data Model**: Nodes (entities) and Edges (relationships) with key-value properties
- **Node**: `{id: "SUP001", name: "ACME Corp", country: "Germany"}`
- **Edge**: `{from: "SUP001", to: "FAC001", type: "supplies", volume: 10000}`

### Core Capabilities

**Graph Algorithms Built-In**:
1. **Shortest Path** - Find optimal routes
2. **Centrality Analysis** - Identify critical nodes (PageRank, Betweenness)
3. **Community Detection** - Discover clusters (Louvain algorithm)
4. **Pattern Matching** - Find subgraph patterns

**Technical Features**:
- ✅ Embedded in SQL environment (ACID transactions)
- ✅ Graph workspaces as catalog objects
- ✅ SQL integration via graph functions
- ✅ Optimized for traversal and path analysis

### Real-World Example: Supply Chain Disruption

**Scenario**: Supplier failure impact analysis

```sql
-- Model: Factories (nodes) ↔ Suppliers (nodes) ↔ Routes (edges)
-- Use Louvain community detection to find interconnected clusters

SELECT cluster_id, COUNT(*) as supplier_count
FROM GRAPH_COMMUNITY_DETECTION(
  GRAPH_WORKSPACE => 'SUPPLY_CHAIN',
  ALGORITHM => 'LOUVAIN'
)
GROUP BY cluster_id;

-- If supplier in Cluster 3 fails → All Cluster 3 suppliers at risk
-- Result: Identify ripple effects instantly
```

**Use Cases**:
- 🏭 Supply chain path optimization
- 🔍 Fraud detection (unusual transaction patterns)
- 📊 Organizational network analysis
- 🚚 Logistics route optimization
- 💰 Financial risk assessment (credit networks)

### When to Use Property Graphs

✅ **Choose Property Graph when you need**:
- Network optimization (shortest path, lowest cost)
- Cluster identification (community detection)
- Bottleneck discovery (centrality analysis)
- Structural relationship analysis
- Performance-critical path queries

---

## Knowledge Graph Engine (Semantic Reasoning)

### What Is It?

**Data Model**: RDF Triples (Resource Description Framework)
- **Triple**: `(Subject, Predicate, Object)`
- **Example**: `(Supplier_ACME, certified_for, ISO_14001)`
- **Example**: `(Product_X, has_attribute, Biodegradable)`

### Core Capabilities

**Semantic Intelligence**:
1. **Inference** - Derive new facts from existing data
2. **Contextual Reasoning** - Understand meaning, not just structure
3. **Ontology Support** - RDFS, OWL for domain models
4. **SPARQL Queries** - Semantic query language (W3C standard)

**Technical Features**:
- ✅ Native RDF triple store (must be enabled in HANA instance)
- ✅ SPARQL query support
- ✅ SQL integration via `SPARQL_EXECUTE()` function
- ✅ Vector Engine integration (semantic + similarity search)
- ✅ Multi-model: Graph + Vector + Spatial + SQL
- ✅ AI-ready (GraphRAG, VectorRAG support)

### Real-World Example: Sustainable Supplier Search

**Scenario**: Complex contextual supplier query

```sparql
-- Question: "Which suppliers follow certified sustainable sourcing,
--            provide biodegradable packaging,
--            deliver eco-friendly products,
--            and comply with EU regulations?"

PREFIX ex: <http://example.org/>

SELECT ?supplier ?certification ?packaging ?compliance
WHERE {
  ?supplier ex:has_certification ex:ISO_14001 .
  ?supplier ex:packaging_type ex:Biodegradable .
  ?supplier ex:product_category ex:EcoFriendly .
  ?supplier ex:complies_with ex:EU_Green_Deal .
}

-- Combined with SQL and Vector for ranked results:
SELECT * FROM SPARQL_EXECUTE('...query above...', 'SUPPLY_CHAIN_GRAPH')
WHERE VECTOR_SIMILARITY(narrative, 'sustainability excellence') > 0.8
ORDER BY ranking DESC;
```

**Result**: Answers complex business questions that require **understanding context**, not just finding connections.

### When to Use Knowledge Graphs

✅ **Choose Knowledge Graph when you need**:
- Semantic search ("What does this mean?")
- AI/LLM grounding (provide context for GenAI)
- Complex contextual queries
- Inference and reasoning
- External vocabulary integration (industry standards)
- Multi-domain data integration (different definitions)

---

## Hybrid Approach: The Power of Both 🎯

### Why Use Both Together?

SAP HANA Cloud enables **hybrid usage on the same platform** with shared data:

**Example: Complete Supply Chain Intelligence**
1. **Property Graph** → Analyze network disruption patterns (structure)
2. **Knowledge Graph** → Answer sustainability compliance questions (semantics)
3. **Combined** → "Find alternative suppliers with shortest path AND sustainability certification"

### Hybrid Query Example

```sql
-- Step 1: Use Property Graph to find connected suppliers
WITH alternative_suppliers AS (
  SELECT supplier_id 
  FROM GRAPH_SHORTEST_PATH(
    GRAPH => 'SUPPLY_CHAIN',
    START => 'FAILED_SUPPLIER',
    MAX_DISTANCE => 2
  )
)
-- Step 2: Use Knowledge Graph to filter by certifications
SELECT s.* FROM alternative_suppliers a
JOIN SPARQL_EXECUTE('
  SELECT ?supplier WHERE {
    ?supplier ex:has_certification ex:ISO_14001
  }', 'COMPLIANCE_GRAPH'
) kg ON a.supplier_id = kg.supplier
-- Step 3: Use Vector for similarity ranking
ORDER BY VECTOR_SIMILARITY(s.description, 'reliable delivery') DESC;
```

**Result**: Structural analysis + Semantic intelligence + Similarity ranking = Complete business answer

---

## Integration with Other HANA Engines

### Multi-Model Capabilities (Q4 2025+)

**SAP HANA Cloud provides 5 engines working together**:
1. **Relational/SQL** - Traditional tables
2. **Property Graph** - Network analysis
3. **Knowledge Graph** - Semantic reasoning
4. **Vector Engine** - AI similarity search
5. **Spatial Engine** - Geographic analysis

**NEW Feature (Q4 2025)**: Property Graph → Knowledge Graph transformation (no redesign needed!)

### Example: Complete AI-Powered Query

```sql
-- Combine ALL engines in one query:
SELECT 
  supplier_name,
  certification_status,  -- Knowledge Graph
  network_centrality,     -- Property Graph
  similarity_score,       -- Vector Engine
  distance_km            -- Spatial Engine
FROM suppliers s
JOIN SPARQL_EXECUTE('...semantic query...') kg ON s.id = kg.supplier
JOIN GRAPH_CENTRALITY(...) pg ON s.id = pg.node_id
WHERE ST_DISTANCE(s.location, 'Frankfurt') < 50  -- Spatial
  AND VECTOR_SIMILARITY(s.profile, 'reliable') > 0.8  -- Vector
ORDER BY network_centrality DESC;
```

**Impact**: Single query across 5 data models = Unprecedented analytical power! ⚡

---

## Technical Implementation

### Property Graph Setup

**1. Create Graph Workspace** (catalog object):
```sql
CREATE GRAPH WORKSPACE SUPPLY_CHAIN
  VERTEX TABLE suppliers KEY (supplier_id)
  EDGE TABLE shipments KEY (shipment_id)
    SOURCE KEY (from_supplier) REFERENCES suppliers(supplier_id)
    TARGET KEY (to_factory) REFERENCES factories(factory_id);
```

**2. Run Algorithms**:
```sql
-- Community detection
CALL GRAPH_COMMUNITY_DETECTION(
  WORKSPACE => 'SUPPLY_CHAIN',
  ALGORITHM => 'LOUVAIN'
);

-- Shortest path
SELECT * FROM GRAPH_SHORTEST_PATH(
  GRAPH => 'SUPPLY_CHAIN',
  START => 'SUP001',
  END => 'FAC001'
);
```

### Knowledge Graph Setup

**Prerequisites** (CRITICAL):
- ✅ SAP HANA Cloud instance on Q1 2025+ patches
- ✅ Enable triple store in database settings
- ✅ Load RDF data or transform SQL tables to triples

**1. Enable Knowledge Graph Engine**:
```sql
-- Must be enabled per instance (one-time setup)
ALTER SYSTEM ENABLE KNOWLEDGE_GRAPH;
```

**2. Load RDF Data**:
```sql
-- Option 1: Direct triple insertion
INSERT INTO RDF_STORE VALUES (
  '<http://example.org/Supplier001>',
  '<http://example.org/has_certification>',
  '<http://example.org/ISO_14001>'
);

-- Option 2: Transform SQL to RDF (built-in tools)
-- See SAP Help Portal for transformation utilities
```

**3. Query with SPARQL**:
```sql
-- Via SQL integration
SELECT * FROM SPARQL_EXECUTE('
  PREFIX ex: <http://example.org/>
  SELECT ?supplier ?cert WHERE {
    ?supplier ex:has_certification ?cert .
    FILTER(?cert = ex:ISO_14001)
  }', 'YOUR_GRAPH_NAME'
);
```

---

## Our Application's Knowledge Graph Module

### Current Implementation

**What We Have**:
- SQLite-based graph storage (nodes, edges, properties)
- Simple entity-relationship model
- Basic CRUD operations
- Visualization in UI

**Purpose**: Track data product relationships (Schema → Tables → Columns)

### Questions to Answer

**1. What should our KG represent?**
- Option A: Data product metadata relationships (current approach)
- Option B: Business domain ontology (semantic layer)
- Option C: Hybrid (both structural + semantic)

**2. Should we leverage HANA's graph engines?**
- Option A: Keep SQLite (simple, works offline)
- Option B: Use HANA Property Graph (network analysis)
- Option C: Use HANA Knowledge Graph (semantic reasoning)
- Option D: Hybrid (SQLite fallback, HANA when available)

**3. What's our KG vision?**
- Metadata catalog?
- Semantic search layer?
- AI context provider (LLM grounding)?
- Business ontology repository?
- All of the above?

---

## Potential Use Cases for Our P2P Application

### Property Graph Use Cases

**1. Purchase Order Dependency Analysis**
- Model: PO → Items → Suppliers → Invoices
- Question: "If Supplier X fails, which POs are affected?"
- Algorithm: Community detection + Path analysis

**2. Approval Workflow Bottlenecks**
- Model: Documents → Approvers → Departments
- Question: "Who are the critical approval bottlenecks?"
- Algorithm: Betweenness centrality

**3. Spending Pattern Clusters**
- Model: Cost Centers → Purchases → Categories
- Question: "Which cost centers have similar spending patterns?"
- Algorithm: Community detection

### Knowledge Graph Use Cases

**1. Semantic Procurement Search**
- Query: "Find IT equipment orders under €1000 with express shipping from certified vendors"
- Requires: Understanding categories, policies, certifications (context!)

**2. AI-Powered Invoice Matching**
- Query: "Match invoice to PO considering contract terms, delivery conditions, and payment rules"
- Requires: Semantic reasoning across multiple business rules

**3. Compliance Checking**
- Query: "Which invoices violate procurement policies based on company guidelines?"
- Requires: Understanding policy definitions and applying inference

### Hybrid Use Cases

**1. Complete Supplier Intelligence**
- Property Graph: Network centrality (how critical?)
- Knowledge Graph: Certifications, compliance (what qualifications?)
- Vector: Performance similarity (who's comparable?)
- Result: Comprehensive supplier risk assessment

**2. P2P Process Optimization**
- Property Graph: Identify approval bottlenecks (structure)
- Knowledge Graph: Understand policy exceptions (semantics)
- Combined: Streamline workflows intelligently

---

## Recommendations for Our Application

### Short-Term (Current)

**Keep SQLite-based KG for now**:
- ✅ Works offline (no HANA dependency)
- ✅ Simple for data product metadata
- ✅ Fast development iteration
- ✅ Demonstration mode ready

**Current Purpose**: Catalog data product relationships
- Data Product → Schemas → Tables → Columns
- Basic entity-relationship model
- Sufficient for initial MVP

### Medium-Term (6 months)

**Evaluate HANA Integration**:
1. **If we need network analysis** → Use Property Graph Engine
   - Example: PO dependency networks, supplier clusters
2. **If we need semantic search** → Use Knowledge Graph Engine
   - Example: AI-powered procurement Q&A
3. **If we need both** → Hybrid approach with dual engines

**Architecture**: Extend DataSource interface
```python
# Add to core/interfaces/data_source.py
class DataSource:
    # Existing methods...
    
    # NEW: Graph capabilities (optional, not all sources support)
    def execute_graph_query(self, query: str) -> dict:
        """Execute Property Graph algorithm query"""
        raise NotImplementedError("Graph queries not supported")
    
    def execute_sparql_query(self, query: str) -> dict:
        """Execute Knowledge Graph SPARQL query"""
        raise NotImplementedError("SPARQL not supported")
```

### Long-Term (12 months)

**Production Vision Options**:

**Option 1: Metadata-Only (Simple)**
- Current SQLite approach (data product catalog)
- No HANA graph engines needed
- Focus: Data discovery and navigation

**Option 2: Structural Analysis (Property Graph)**
- Use HANA Property Graph Engine
- Model P2P process dependencies
- Enable: Network optimization, bottleneck detection
- Algorithms: Shortest path, centrality, clustering

**Option 3: Semantic Intelligence (Knowledge Graph)**
- Use HANA Knowledge Graph Engine
- Build P2P business ontology
- Enable: AI-powered search, GenAI grounding
- Standards: RDF, SPARQL, OWL

**Option 4: Complete Intelligence (Hybrid)** ⭐ RECOMMENDED
- Use BOTH engines on same data
- Property Graph: "How is data connected?"
- Knowledge Graph: "What does data mean?"
- Enable: Complete AI-powered analytics
- Result: Most powerful, future-proof solution

---

## Technical Prerequisites

### For Property Graph Engine

✅ **Already Available** in your HANA Cloud instance
- No special setup needed
- Part of standard HANA Cloud

**Setup Steps**:
1. Create graph workspace (SQL DDL)
2. Define vertex and edge tables
3. Run graph algorithms via SQL functions

### For Knowledge Graph Engine

⚠️ **Requires Q1 2025+ HANA Cloud**
- Must enable triple store in instance settings
- Check your instance version

**Setup Steps**:
1. Verify instance on Q1 2025+ patch level
2. Enable triple store: `ALTER SYSTEM ENABLE KNOWLEDGE_GRAPH;`
3. Load RDF data or transform SQL tables
4. Query via `SPARQL_EXECUTE()` function

**Check if Available**:
```sql
-- Query to check if Knowledge Graph is enabled
SELECT * FROM M_FEATURES 
WHERE FEATURE_NAME = 'KNOWLEDGE_GRAPH';
```

---

## Integration Architecture Options

### Option 1: SQLite Only (Current - Simple)
```
Application → SQLite KG → Visualization
```
**Pros**: Simple, offline, fast development  
**Cons**: Limited to basic entity-relationship model

### Option 2: HANA Property Graph (Structural)
```
Application → HANA Property Graph → Algorithms → Insights
            ↓
         SQLite (fallback for offline)
```
**Pros**: Network analysis, graph algorithms  
**Cons**: HANA dependency, no semantic reasoning

### Option 3: HANA Knowledge Graph (Semantic)
```
Application → HANA Knowledge Graph → SPARQL → AI Context
            ↓
         SQLite (fallback for offline)
```
**Pros**: Semantic search, AI grounding, inference  
**Cons**: HANA dependency, requires RDF modeling

### Option 4: Hybrid Multi-Model (Complete)
```
Application → [Property Graph] → Network analysis
            → [Knowledge Graph] → Semantic reasoning  
            → [Vector Engine] → Similarity search
            → [SQL] → Traditional queries
            ↓
         SQLite (fallback for all)
```
**Pros**: Complete intelligence, future-proof  
**Cons**: Most complex, highest learning curve

---

## Key Insights from Research

### 1. Complementary, Not Competing ⭐

**SAP's Strategy**: Both engines working together
- Property Graph: Analyzes "How entities connect?" (structure)
- Knowledge Graph: Answers "What does it mean?" (semantics)
- **Together**: Complete picture of data + meaning

### 2. Knowledge Graph is BRAND NEW (Q1 2025)

**Timeline**:
- Property Graph: Available since HANA 2.0 (2016+)
- Knowledge Graph: NEW - Q1 2025 (just released!)
- Transformation: Q4 2025 (Property → Knowledge conversion)

**Implication**: Cutting-edge technology, limited production examples yet

### 3. AI-First Design

**Knowledge Graph Engine designed FOR AI**:
- GraphRAG: Ground LLMs in knowledge graphs
- Vector integration: Semantic + similarity search
- SPARQL: Natural language → formal queries
- Context: Provide "why" and "what" to AI models

**This aligns with industry trends**: Every major tech company building knowledge graphs for AI (Google, Microsoft, Amazon)

### 4. SQL Integration is CRITICAL

**Both engines integrate with SQL**:
- Property Graph: Graph functions in SQL queries
- Knowledge Graph: `SPARQL_EXECUTE()` in SQL
- Multi-model: Combine graph + relational + vector in single query

**Why**: Enterprises have SQL skills, SQL tools, SQL investments. Pure SPARQL adoption is hard. Hybrid approach wins.

---

## Decision Framework for Our Application

### Questions to Guide Decision

**1. What is our KG's primary purpose?**
- [ ] Metadata catalog (data product discovery)
- [ ] Business ontology (P2P domain model)
- [ ] AI context layer (LLM grounding)
- [ ] Network analysis (process optimization)
- [ ] All of the above

**2. What queries do users need?**
- [ ] "What tables are in this data product?" (Simple SQL)
- [ ] "Which suppliers are most critical?" (Property Graph)
- [ ] "Find sustainable suppliers under EU rules" (Knowledge Graph)
- [ ] "Show me similar high-performing suppliers" (Vector + Knowledge)

**3. What's our timeline?**
- [ ] MVP (3 months): Simple metadata catalog
- [ ] Production (6 months): Network analysis
- [ ] Advanced (12 months): Full semantic intelligence

**4. What's our HANA maturity?**
- [ ] Just learning HANA Cloud (stick with SQL)
- [ ] Comfortable with HANA (add Property Graph)
- [ ] Advanced users (add Knowledge Graph)
- [ ] Experts (full multi-model)

### Suggested Roadmap

**Phase 1: Current (SQLite Metadata)** ✅
- Focus: Data product discovery
- Technology: SQLite entity-relationship
- Timeline: MVP completed

**Phase 2: Network Analysis (Property Graph)** 📋
- Focus: P2P process dependencies
- Technology: HANA Property Graph Engine
- Timeline: After HANA Cloud fully integrated
- Prerequisites: P2P schema in HANA, graph workspace created
- Delivers: Supplier criticality, approval bottlenecks, spending clusters

**Phase 3: Semantic Intelligence (Knowledge Graph)** 📋
- Focus: AI-powered procurement
- Technology: HANA Knowledge Graph Engine
- Timeline: After Property Graph stabilized
- Prerequisites: Instance on Q1 2025+, triple store enabled, P2P ontology designed
- Delivers: Contextual search, LLM grounding, policy reasoning

**Phase 4: Complete Multi-Model (All Engines)** 🎯
- Focus: Enterprise-grade intelligence
- Technology: Property + Knowledge + Vector + Spatial
- Timeline: Production maturity (12+ months)
- Delivers: Complete AI-powered P2P analytics platform

---

## Further Reading

### SAP Official Resources
1. [Choosing Between Knowledge Graphs and Property Graphs](https://community.sap.com/t5/technology-blog-posts-by-sap/choosing-between-knowledge-graphs-and-property-graphs-in-sap-hana-cloud-and/ba-p/14074575)
2. [SAP HANA Cloud Knowledge Graph Engine Guide](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-knowledge-graph-guide/)
3. [What's New in SAP HANA Cloud - December 2025](https://community.sap.com/t5/technology-blog-posts-by-sap/what-s-new-in-sap-hana-cloud-december-2025/ba-p/14295366)
4. [Unifying AI Workloads with SAP HANA Cloud](https://news.sap.com/2025/07/unifying-ai-workloads-sap-hana-cloud-one-database/)

### Video Tutorials
- [Intelligent Data Applications with Knowledge Graph Engine](https://www.youtube.com/watch?v=GQHqZeScdtI)
- [SAP Knowledge Graph + LLM Q&A Demo](https://www.youtube.com/watch?v=ZGyzKj4_JBY)
- [SAP HANA Cloud Multi-Model Capabilities](https://www.youtube.com/watch?v=FxlHVQa5l5Q)

---

## Summary

**The Answer**: Property Graph and Knowledge Graph are **different tools for different jobs**, both available in SAP HANA Cloud:

- **Property Graph** = "How is data connected?" → Network optimization
- **Knowledge Graph** = "What does data mean?" → Semantic reasoning
- **Together** = Complete intelligence (structure + semantics)

**Our Current Module**: Simple metadata catalog (sufficient for MVP)

**Future Evolution**: Can grow into HANA's graph engines when we need:
- Network analysis (Property Graph)
- Semantic search (Knowledge Graph)
- AI intelligence (Both + Vector)

**Next Steps**: Define our KG vision based on business needs, not technology features.