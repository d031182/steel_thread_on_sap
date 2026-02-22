# AI-Powered Data Query Architecture - Industry Standards & Gap Analysis

**Date**: 2026-02-21  
**Purpose**: Identify missing components for production-ready AI query system  
**Goal**: Enable queries like "show me sales history of last 3 years", "total payment amount 2025"

---

## Industry Best Practices (2024-2026)

### 1. Text-to-SQL Architecture Layers

Based on industry leaders (Tableau, ThoughtSpot, Power BI, Looker):

```
┌─────────────────────────────────────────────────────┐
│ 1. Natural Language Interface (User Input)         │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 2. Intent Recognition & Query Understanding         │
│    - Parse user intent (filter, aggregate, time)    │
│    - Extract entities (supplier, invoice, amount)   │
│    - Identify query type (analytical, operational)  │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 3. Semantic Layer (Business Logic Abstraction) ⭐   │
│    - Business term → Technical mapping              │
│    - Pre-defined metrics & calculations             │
│    - Access control & data security                 │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 4. Query Generation (SQL Builder)                   │
│    - Template-based generation                      │
│    - LLM-powered generation (with validation)       │
│    - Query optimization                             │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 5. Query Execution & Caching                        │
│    - Database execution                             │
│    - Result caching                                 │
│    - Error handling                                 │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 6. Result Presentation & Visualization              │
│    - Format results                                 │
│    - Generate charts/graphs                         │
│    - Explain SQL generated                          │
└─────────────────────────────────────────────────────┘
```

---

## Current Architecture Analysis

### ✅ What We HAVE

1. **AI Assistant Module**:
   - ✅ Pydantic AI integration (LLM orchestration)
   - ✅ SAP AI Core connectivity
   - ✅ Conversation management
   - ✅ Backend APIs functional

2. **Knowledge Graph V2**:
   - ✅ CSN schema parsing (entities, fields)
   - ✅ Entity relationship discovery
   - ✅ Graph visualization (Vis.js)
   - ✅ Cache layer (SQLite)

3. **Data Products V2**:
   - ✅ Repository pattern (data access)
   - ✅ SQLite/HANA abstraction
   - ✅ Transaction data (invoices, POs, suppliers)

### ❌ What's MISSING (Critical Gaps)

#### Gap 1: **Semantic Layer** ⭐ HIGHEST PRIORITY

**What It Is**: Business logic abstraction between user language and database

**Why It's Critical**:
```
User: "Show me unpaid invoices"
❌ Without Semantic Layer: AI doesn't know "unpaid" means WHERE Status = 'OPEN'
✅ With Semantic Layer: Mapped business rule executes correctly
```

**Missing Components**:
1. **Business Term Dictionary**:
   ```python
   {
     "sales": {
       "tables": ["SupplierInvoice", "PurchaseOrder"],
       "measure": "SUM(NetAmount)",
       "filters": {"type": "InvoiceType = 'SALES'"}
     },
     "unpaid": {
       "filter": "Status = 'OPEN' OR Status = 'PENDING'"
     },
     "payment": {
       "tables": ["SupplierInvoice"],
       "measure": "SUM(PaymentAmount)"
     }
   }
   ```

2. **Pre-defined Metrics**:
   ```python
   {
     "total_sales": "SELECT SUM(NetAmount) FROM SupplierInvoice WHERE InvoiceType = 'SALES'",
     "unpaid_amount": "SELECT SUM(NetAmount) FROM SupplierInvoice WHERE Status IN ('OPEN', 'PENDING')",
     "payment_history": "SELECT PaymentDate, SUM(PaymentAmount) FROM Payments GROUP BY PaymentDate"
   }
   ```

3. **Time Intelligence**:
   ```python
   {
     "last_3_years": "InvoiceDate >= DATE_SUB(CURRENT_DATE, INTERVAL 3 YEAR)",
     "2025": "YEAR(InvoiceDate) = 2025",
     "this_quarter": "InvoiceDate BETWEEN quarter_start AND quarter_end"
   }
   ```

**Industry Standard**: dbt semantic layer, Cube.js, LookML (Looker)

---

#### Gap 2: **Query Generation Service** ⭐ HIGH PRIORITY

**What It Is**: Convert user intent → validated SQL

**Current State**: ❌ Not implemented (AI Assistant cannot generate SQL)

**Missing Components**:
1. **SQL Template Engine**:
   ```python
   class SQLTemplateEngine:
       def build_aggregation_query(self, entity, measure, filters, time_range):
           """Build SQL from components"""
           template = """
           SELECT {time_dimension}, {aggregation}({measure_field})
           FROM {entity}
           WHERE {filters}
           GROUP BY {time_dimension}
           """
           return template.format(...)
   ```

2. **Query Validator**:
   ```python
   class QueryValidator:
       def validate_sql(self, sql: str) -> Tuple[bool, str]:
           """Ensure SQL is safe and valid"""
           # Check for SQL injection
           # Validate table/column existence
           # Check permissions
           return (True, "Valid")
   ```

3. **Query Optimizer**:
   ```python
   class QueryOptimizer:
       def optimize(self, sql: str) -> str:
           """Add indexes, rewrite inefficient queries"""
           # Add WHERE clause pushdown
           # Use indexed columns
           # Limit result sets
           return optimized_sql
   ```

**Industry Standard**: Text-to-SQL with LLM + validation (not raw LLM output)

---

#### Gap 3: **Query Result Cache** ⭐ MEDIUM PRIORITY

**What It Is**: Cache expensive query results

**Current State**: ❌ Not implemented

**Why It Matters**:
```
User: "Show me sales history of last 3 years"
❌ Without Cache: Query takes 5-10 seconds every time
✅ With Cache: First query 5s, subsequent queries <100ms
```

**Missing Components**:
1. **Cache Service**:
   ```python
   class QueryResultCache:
       def __init__(self, redis_client):
           self.cache = redis_client
           self.ttl = 3600  # 1 hour
       
       def get(self, query_hash: str) -> Optional[Dict]:
           """Retrieve cached result"""
           return self.cache.get(query_hash)
       
       def set(self, query_hash: str, result: Dict):
           """Cache result with TTL"""
           self.cache.setex(query_hash, self.ttl, result)
   ```

2. **Cache Invalidation Strategy**:
   ```python
   # Invalidate when:
   - Data changes (INSERT, UPDATE, DELETE)
   - TTL expires
   - User explicitly refreshes
   ```

**Industry Standard**: Redis/Memcached with smart invalidation

---

#### Gap 4: **Time Intelligence** ⭐ HIGH PRIORITY

**What It Is**: Parse and convert time expressions

**Current State**: ❌ Not implemented

**Examples Needed**:
```python
{
  "last 3 years": "InvoiceDate >= '2023-01-01'",  # Current date - 3 years
  "2025": "YEAR(InvoiceDate) = 2025",
  "Q1 2025": "InvoiceDate BETWEEN '2025-01-01' AND '2025-03-31'",
  "this month": "MONTH(InvoiceDate) = MONTH(CURRENT_DATE)",
  "YTD": "InvoiceDate >= DATE_TRUNC('year', CURRENT_DATE)"
}
```

**Missing Component**:
```python
class TimeIntelligence:
    def parse_time_expression(self, expr: str) -> Tuple[datetime, datetime]:
        """Convert natural language time to date range"""
        # "last 3 years" → (2023-01-01, 2026-12-31)
        # "2025" → (2025-01-01, 2025-12-31)
        # "Q1 2025" → (2025-01-01, 2025-03-31)
        pass
```

**Industry Standard**: Power BI Time Intelligence, Tableau date functions

---

#### Gap 5: **Access Control & Data Security** ⭐ CRITICAL

**What It Is**: Row-level security, column masking, role-based access

**Current State**: ❌ Not implemented

**Why It's Critical**:
```
User (Finance): "Show me all invoices"
✅ Should see: All financial data

User (Sales): "Show me all invoices"
❌ Should NOT see: Payment details, confidential fields
```

**Missing Components**:
1. **Row-Level Security**:
   ```python
   class DataSecurity:
       def apply_row_filter(self, user_role: str, entity: str) -> str:
           """Add WHERE clause based on user role"""
           if user_role == "sales":
               return "AND AssignedTo = current_user()"
           elif user_role == "finance":
               return ""  # No filter (can see all)
           return "AND 1=0"  # Deny by default
   ```

2. **Column Masking**:
   ```python
   class ColumnSecurity:
       def mask_sensitive_columns(self, user_role: str, columns: List[str]) -> List[str]:
           """Hide sensitive columns"""
           if "PaymentDetails" in columns and user_role != "finance":
               columns.remove("PaymentDetails")
           return columns
   ```

**Industry Standard**: SAP HANA RLS, Snowflake row access policies

---

#### Gap 6: **Query Explanation** ⭐ MEDIUM PRIORITY

**What It Is**: Explain SQL generated to user

**Current State**: ❌ Not implemented

**Why It Matters**:
```
User: "Show me unpaid invoices"
AI: "Here are 47 invoices"

❌ User doesn't know: What does "unpaid" mean? What criteria was used?

✅ With Explanation:
"I found 47 invoices where Status = 'OPEN' or 'PENDING'. 
SQL: SELECT * FROM SupplierInvoice WHERE Status IN ('OPEN', 'PENDING')"
```

**Missing Component**:
```python
class QueryExplainer:
    def explain(self, sql: str, natural_query: str) -> str:
        """Generate human-readable explanation"""
        return f"""
        Your query: "{natural_query}"
        
        I searched for:
        - Table: SupplierInvoice
        - Filters: Status = 'OPEN' OR Status = 'PENDING'
        - Results: 47 records found
        
        SQL executed:
        {sql}
        """
```

**Industry Standard**: Tableau "Show Me How", Power BI Q&A explanations

---

#### Gap 7: **Error Handling & Feedback** ⭐ HIGH PRIORITY

**What It Is**: Graceful error handling with helpful messages

**Current State**: ⚠️ Minimal error handling

**Examples Needed**:
```python
class QueryErrorHandler:
    def handle_error(self, error: Exception, query: str) -> Dict:
        """Convert technical error to user-friendly message"""
        
        if "table does not exist" in str(error):
            return {
                "error": "I couldn't find that data source.",
                "suggestion": "Try: 'invoices', 'purchase orders', 'suppliers'"
            }
        
        if "ambiguous column" in str(error):
            return {
                "error": "Multiple fields match 'amount'. Which one?",
                "options": ["NetAmount", "GrossAmount", "PaymentAmount"]
            }
        
        return {
            "error": "Query failed. Please try rephrasing.",
            "technical_details": str(error)
        }
```

---

## Architecture Gaps Summary

| Gap | Priority | Impact | Effort | Current State |
|-----|----------|--------|--------|---------------|
| **Semantic Layer** | ⭐ P0 | 🔴 CRITICAL | 2-3 weeks | ❌ Missing |
| **Query Generation Service** | ⭐ P0 | 🔴 CRITICAL | 1-2 weeks | ❌ Missing |
| **Time Intelligence** | ⭐ P1 | 🟠 HIGH | 1 week | ❌ Missing |
| **Error Handling** | ⭐ P1 | 🟠 HIGH | 3-5 days | ⚠️ Minimal |
| **Query Result Cache** | ⭐ P2 | 🟢 MEDIUM | 1 week | ❌ Missing |
| **Query Explanation** | ⭐ P2 | 🟢 MEDIUM | 3-5 days | ❌ Missing |
| **Access Control** | ⭐ P0 | 🔴 CRITICAL | 2-3 weeks | ❌ Missing |

---

## Recommended Implementation Roadmap

### Phase 1: Foundation (4 weeks) ⭐ CRITICAL

**Goal**: Enable basic AI query generation

1. **Week 1-2: Semantic Layer**
   - Create business term dictionary
   - Define pre-defined metrics
   - Implement time intelligence parser
   - Testing: 20 common business queries

2. **Week 3-4: Query Generation Service**
   - SQL template engine
   - Query validator (SQL injection prevention)
   - Integration with AI Assistant
   - Testing: Generate + execute 50 queries

**Deliverable**: AI can answer "Show me unpaid invoices", "Total sales 2025"

---

### Phase 2: Production Readiness (3 weeks)

**Goal**: Performance & security

1. **Week 5-6: Security & Access Control**
   - Row-level security implementation
   - Column masking
   - Role-based query filtering
   - Testing: 10 user roles, 100 security scenarios

2. **Week 7: Caching & Optimization**
   - Query result cache (Redis)
   - Cache invalidation strategy
   - Query optimizer
   - Testing: Performance benchmarks

**Deliverable**: Secure, fast, production-ready system

---

### Phase 3: User Experience (2 weeks)

**Goal**: Explainability & error handling

1. **Week 8: Query Explanation**
   - Natural language explanations
   - SQL visualization
   - "Show me how" feature

2. **Week 9: Error Handling**
   - User-friendly error messages
   - Query suggestions
   - Fallback strategies

**Deliverable**: Intuitive, user-friendly AI assistant

---

## Integration Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    AI Assistant (Frontend UX)                 │
│   "Show me unpaid invoices from last 3 years"                │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│              AI Assistant Backend (Pydantic AI)               │
│  - Intent recognition                                         │
│  - Entity extraction (invoices, unpaid, last 3 years)        │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│            🆕 Semantic Layer Service (NEW)                    │
│  - Business term → Technical mapping                          │
│  - "unpaid" → Status IN ('OPEN', 'PENDING')                  │
│  - "last 3 years" → InvoiceDate >= '2023-01-01'             │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│               Knowledge Graph V2 (Metadata)                   │
│  - Entity relationships (JOIN paths)                          │
│  - Field metadata (types, labels)                             │
│  - Semantic annotations (@Semantics.amount)                   │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│          🆕 Query Generation Service (NEW)                    │
│  - Build SQL from components                                  │
│  - Validate SQL (injection prevention)                        │
│  - Optimize query (indexes, WHERE pushdown)                   │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│             🆕 Query Result Cache (NEW - Redis)               │
│  - Check cache first (query hash → result)                   │
│  - Cache miss → execute query                                 │
│  - Store result with TTL (1 hour)                             │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│              Data Products V2 (Data Access)                   │
│  - Execute SQL (SQLite/HANA)                                  │
│  - Apply row-level security (🆕)                              │
│  - Return results                                             │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│               AI Assistant (Result Presentation)               │
│  - Format results                                             │
│  - Generate explanation (🆕)                                  │
│  - Show SQL executed (🆕)                                     │
└───────────────────────────────────────────────────────────────┘
```

---

## Key Decisions

### 1. **Semantic Layer Storage**

**Options**:
- ✅ **JSON Configuration Files** (Recommended for MVP)
  - Fast to implement
  - Easy to version control
  - IDE-friendly editing
  
- **Database Table** (Future)
  - Dynamic updates without deployment
  - Admin UI for business users

### 2. **Query Generation Strategy**

**Options**:
- ❌ **Pure LLM Generation** (NOT recommended)
  - Unreliable (hallucinations)
  - SQL injection risk
  - Expensive (API costs)

- ✅ **Hybrid: Template + LLM** (Recommended)
  - Templates for common patterns
  - LLM for complex edge cases
  - Validation layer always applied

### 3. **Caching Strategy**

**Options**:
- ✅ **Redis** (Recommended)
  - Fast (in-memory)
  - TTL support
  - Distributed caching

- **SQLite Cache** (Alternative)
  - Simpler setup
  - Persistent cache
  - Slower than Redis

---

## Success Metrics

### MVP (Phase 1 Complete)
- ✅ AI can answer 20 common business questions
- ✅ Query generation time < 2 seconds
- ✅ Query execution accuracy > 95%
- ✅ Zero SQL injection vulnerabilities

### Production (Phase 2 Complete)
- ✅ Query result cache hit rate > 60%
- ✅ Cached query response time < 100ms
- ✅ Row-level security enforced 100%
- ✅ Zero unauthorized data access

### User Experience (Phase 3 Complete)
- ✅ Users understand 90%+ of AI responses
- ✅ Error recovery rate > 80%
- ✅ User satisfaction score > 4/5

---

## References

- Industry Research: Perplexity search results (2024-2026)
- Current Architecture: [[ai-assistant-implementation-status-2026-02-21]]
- Knowledge Graph Enhancement: [[knowledge-graph-semantic-enhancement-implementation-plan]]
- Module Standards: [[Module Federation Standard]]

---

## Next Steps

1. ✅ Review this gap analysis with stakeholders
2. ✅ Prioritize Phase 1 tasks (Semantic Layer + Query Generation)
3. ✅ Create detailed implementation tickets for PROJECT_TRACKER.md
4. ✅ Begin Phase 1 Week 1: Semantic Layer design
5. ✅ Update Knowledge Graph enhancement plan to include semantic layer integration

**Critical Path**: Semantic Layer → Query Generation → Knowledge Graph Enhancement → Production