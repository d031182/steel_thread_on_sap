# AI-Powered Query System - Detailed Implementation Proposal

**Date**: 2026-02-21  
**Version**: 1.0  
**Status**: APPROVED - Ready for Implementation  
**Effort**: 9 weeks total (3 phases)

---

## Executive Summary

This proposal outlines the implementation of a production-ready AI query system that enables users to ask natural language questions like:
- "Show me unpaid invoices from last 3 years"
- "What is the total payment amount for 2025?"
- "Which invoices are not paid and still open?"

**Current State**: We have the foundation (AI Assistant, Knowledge Graph V2, Data Products V2) but lack the integration layer.

**Goal**: Bridge the gap between user language and database queries through a semantic layer and query generation service.

**Timeline**: 9 weeks (4 weeks foundation + 3 weeks security + 2 weeks UX)

---

## Phase 1: Foundation (4 weeks) ⭐ CRITICAL

### Week 1: Semantic Layer - Business Terms (HIGH-25)

**Goal**: Enable business term mapping

**Deliverables**:
1. **Business Term Dictionary Service**
   ```python
   # core/services/semantic_layer_service.py
   class SemanticLayerService:
       def __init__(self):
           self.terms = self._load_business_terms()
       
       def resolve_term(self, term: str) -> Dict:
           """Map business term to technical definition"""
           return self.terms.get(term.lower(), {})
   ```

2. **Business Terms Configuration**
   ```json
   // config/business_terms.json
   {
     "unpaid": {
       "type": "filter",
       "sql": "Status IN ('OPEN', 'PENDING')",
       "description": "Invoices not yet paid"
     },
     "sales": {
       "type": "metric",
       "tables": ["SupplierInvoice"],
       "measure": "SUM(NetAmount)",
       "filters": {"InvoiceType": "SALES"}
     }
   }
   ```

3. **API Endpoints**
   - `GET /api/semantic-layer/terms` - List all business terms
   - `GET /api/semantic-layer/terms/{term}` - Resolve specific term
   - `POST /api/semantic-layer/validate` - Validate query terms

**Testing**:
- Unit tests: 20 business term resolutions
- Integration test: AI Assistant calls semantic layer

**Effort**: 3 days

---

### Week 2: Semantic Layer - Time Intelligence (HIGH-26)

**Goal**: Parse time expressions to SQL

**Deliverables**:
1. **Time Intelligence Parser**
   ```python
   # core/services/time_intelligence.py
   class TimeIntelligence:
       def parse(self, expression: str) -> Dict[str, str]:
           """Convert natural language time to SQL"""
           # "last 3 years" → date range
           # "2025" → YEAR(date_field) = 2025
           # "Q1 2025" → date BETWEEN ...
   ```

2. **Time Expression Mappings**
   ```python
   {
     "last 3 years": "date_field >= DATE_SUB(CURRENT_DATE, INTERVAL 3 YEAR)",
     "2025": "YEAR(date_field) = 2025",
     "Q1 2025": "date_field BETWEEN '2025-01-01' AND '2025-03-31'",
     "YTD": "date_field >= DATE_TRUNC('year', CURRENT_DATE)",
     "this month": "MONTH(date_field) = MONTH(CURRENT_DATE)"
   }
   ```

3. **API Endpoints**
   - `POST /api/semantic-layer/time/parse` - Parse time expression
   - `GET /api/semantic-layer/time/supported` - List supported expressions

**Testing**:
- Unit tests: 30 time expression conversions
- Edge cases: "last month", "next quarter", "fiscal year"

**Effort**: 2 days

---

### Week 3: Query Generation Service (HIGH-27)

**Goal**: Convert intent → validated SQL

**Deliverables**:
1. **SQL Template Engine**
   ```python
   # core/services/query_generator.py
   class QueryGenerator:
       def generate_sql(self, intent: Dict) -> str:
           """Build SQL from intent components"""
           template = self.templates[intent['type']]
           return template.format(**intent['parameters'])
   ```

2. **Query Templates**
   ```python
   # config/query_templates.json
   {
     "aggregation": """
       SELECT {time_dimension}, {aggregation}({measure})
       FROM {entity}
       WHERE {filters}
       GROUP BY {time_dimension}
     """,
     "filter": """
       SELECT *
       FROM {entity}
       WHERE {filters}
       LIMIT {limit}
     """
   }
   ```

3. **Query Validator**
   ```python
   # core/services/query_validator.py
   class QueryValidator:
       def validate(self, sql: str) -> Tuple[bool, List[str]]:
           """Check SQL safety and validity"""
           # SQL injection prevention
           # Table/column existence check
           # Permission validation
   ```

4. **API Endpoints**
   - `POST /api/query-generator/generate` - Generate SQL from intent
   - `POST /api/query-generator/validate` - Validate SQL
   - `GET /api/query-generator/templates` - List templates

**Testing**:
- Unit tests: 50 query generations
- Security tests: SQL injection attempts (should fail)
- Integration test: Generate + execute query

**Effort**: 5 days

---

### Week 4: AI Assistant Integration (HIGH-28)

**Goal**: Connect all components

**Deliverables**:
1. **Query Intent Extractor**
   ```python
   # modules/ai_assistant/backend/services/query_intent_service.py
   class QueryIntentService:
       def extract_intent(self, natural_query: str) -> Dict:
           """Extract structured intent from NL query"""
           # Use Pydantic AI to parse
           return {
               'type': 'aggregation',
               'entity': 'SupplierInvoice',
               'measure': 'NetAmount',
               'filters': ['unpaid'],
               'time_range': 'last 3 years'
           }
   ```

2. **Query Orchestrator**
   ```python
   # modules/ai_assistant/backend/services/query_orchestrator.py
   class QueryOrchestrator:
       def process_query(self, natural_query: str) -> Dict:
           """End-to-end query processing"""
           # 1. Extract intent (AI)
           # 2. Resolve business terms (Semantic Layer)
           # 3. Generate SQL (Query Generator)
           # 4. Validate SQL
           # 5. Execute query (Data Products)
           # 6. Format results
   ```

3. **API Endpoint**
   - `POST /api/ai-assistant/query` - Process natural language query

**Testing**:
- E2E tests: 20 complete query flows
- User queries: "unpaid invoices last 3 years", "total sales 2025"

**Effort**: 4 days

**Phase 1 Complete**: AI can answer basic business questions

---

## Phase 2: Production Readiness (3 weeks)

### Week 5: Query Result Cache (MED-22)

**Goal**: Cache expensive queries for performance

**Deliverables**:
1. **Redis Cache Service**
   ```python
   # core/services/query_cache_service.py
   class QueryCacheService:
       def __init__(self, redis_client):
           self.cache = redis_client
           self.ttl = 3600  # 1 hour
       
       def get_cached_result(self, query_hash: str):
           return self.cache.get(f"query:{query_hash}")
       
       def cache_result(self, query_hash: str, result: Dict):
           self.cache.setex(f"query:{query_hash}", self.ttl, json.dumps(result))
   ```

2. **Cache Invalidation**
   ```python
   # Invalidate on:
   - Data changes (listen to INSERT/UPDATE/DELETE events)
   - Manual refresh (user clicks "Refresh")
   - TTL expiry (automatic after 1 hour)
   ```

3. **Cache Configuration**
   ```json
   // config/cache_config.json
   {
     "ttl_seconds": 3600,
     "max_cache_size_mb": 1024,
     "eviction_policy": "LRU"
   }
   ```

**Testing**:
- Performance test: Query 5s → 100ms (cached)
- Cache hit rate: Should be > 60%

**Effort**: 3 days

---

### Week 6-7: Access Control & Security (CRIT-23)

**Goal**: Row-level security and role-based access

**Deliverables**:
1. **Security Service**
   ```python
   # core/services/data_security_service.py
   class DataSecurityService:
       def apply_row_filter(self, user_role: str, entity: str) -> str:
           """Add WHERE clause based on user role"""
           rules = self.security_rules[user_role][entity]
           return rules.get('row_filter', '')
       
       def mask_columns(self, user_role: str, columns: List[str]) -> List[str]:
           """Remove sensitive columns"""
           allowed = self.security_rules[user_role]['allowed_columns']
           return [c for c in columns if c in allowed]
   ```

2. **Security Rules Configuration**
   ```json
   // config/security_rules.json
   {
     "finance": {
       "SupplierInvoice": {
         "row_filter": "",
         "allowed_columns": ["*"]
       }
     },
     "sales": {
       "SupplierInvoice": {
         "row_filter": "AND AssignedTo = CURRENT_USER()",
         "allowed_columns": ["InvoiceID", "SupplierID", "NetAmount"]
       }
     }
   }
   ```

3. **Integration**
   - Query Generator applies security filters automatically
   - Data Products enforces column masking
   - Audit log for all queries

**Testing**:
- Security tests: 100 scenarios across 10 roles
- Penetration test: Attempt unauthorized access
- Audit: All queries logged with user/timestamp

**Effort**: 8 days

---

## Phase 3: User Experience (2 weeks)

### Week 8: Query Explanation (MED-23)

**Goal**: Explain queries to users

**Deliverables**:
1. **Query Explainer**
   ```python
   # core/services/query_explainer.py
   class QueryExplainer:
       def explain(self, sql: str, natural_query: str, result_count: int) -> str:
           """Generate natural language explanation"""
           return f"""
           Your question: "{natural_query}"
           
           I searched for:
           - Table: {parsed_table}
           - Filters: {parsed_filters}
           - Results: {result_count} records found
           
           SQL executed:
           {sql}
           """
   ```

2. **Explanation in Response**
   ```json
   {
     "query": "Show me unpaid invoices",
     "results": [...],
     "explanation": {
       "natural": "I found 47 unpaid invoices...",
       "sql": "SELECT * FROM...",
       "filters_applied": ["Status = 'OPEN'", "Status = 'PENDING'"]
     }
   }
   ```

**Testing**:
- User study: 90%+ understand explanations
- Edge cases: Complex queries, joins

**Effort**: 3 days

---

### Week 9: Error Handling (MED-24)

**Goal**: User-friendly error messages

**Deliverables**:
1. **Error Handler**
   ```python
   # core/services/query_error_handler.py
   class QueryErrorHandler:
       def handle(self, error: Exception, query: str) -> Dict:
           """Convert technical error to user message"""
           if "table not found" in str(error):
               return {
                   "error": "I couldn't find that data.",
                   "suggestion": "Try: invoices, purchase orders, suppliers"
               }
   ```

2. **Error Response Format**
   ```json
   {
     "success": false,
     "error": {
       "message": "I couldn't understand 'xyz'",
       "suggestions": ["Did you mean 'invoices'?"],
       "technical_details": "Table 'xyz' not found"
     }
   }
   ```

**Testing**:
- Error scenarios: 20 common failure modes
- Recovery test: User fixes query after error

**Effort**: 2 days

---

## Module Structure

### New Module: `semantic_layer`

```
modules/semantic_layer/
├── module.json
├── README.md
├── backend/
│   ├── __init__.py
│   ├── api.py                    # Flask Blueprint
│   ├── services/
│   │   ├── semantic_layer_service.py
│   │   ├── time_intelligence.py
│   │   ├── query_generator.py
│   │   ├── query_validator.py
│   │   └── query_cache_service.py
│   └── repositories/
│       └── business_term_repository.py
├── config/
│   ├── business_terms.json
│   ├── query_templates.json
│   └── security_rules.json
└── tests/
    ├── test_semantic_layer_api.py
    ├── test_time_intelligence.py
    └── test_query_generator.py
```

---

## API Contracts

### 1. Semantic Layer API

```python
# GET /api/semantic-layer/terms
Response: {
  "terms": [
    {"name": "unpaid", "type": "filter", "description": "..."},
    {"name": "sales", "type": "metric", "description": "..."}
  ]
}

# POST /api/semantic-layer/time/parse
Request: {"expression": "last 3 years", "date_field": "InvoiceDate"}
Response: {"sql": "InvoiceDate >= '2023-01-01'"}

# POST /api/query-generator/generate
Request: {
  "intent": {
    "type": "aggregation",
    "entity": "SupplierInvoice",
    "measure": "NetAmount",
    "filters": ["unpaid"],
    "time_range": "last 3 years"
  }
}
Response: {"sql": "SELECT SUM(NetAmount)..."}
```

### 2. AI Assistant Query API

```python
# POST /api/ai-assistant/query
Request: {"query": "Show me unpaid invoices from last 3 years"}
Response: {
  "success": true,
  "results": [...],
  "explanation": {
    "natural": "I found 47 unpaid invoices...",
    "sql": "SELECT * FROM...",
    "filters_applied": [...]
  },
  "metadata": {
    "result_count": 47,
    "execution_time_ms": 450,
    "cached": false
  }
}
```

---

## Dependencies

### Infrastructure
- Redis (for caching) - Install via `pip install redis`
- PostgreSQL/HANA (existing)
- Python 3.9+ (existing)

### Python Packages
```txt
redis==4.5.0
sqlparse==0.4.4  # SQL parsing
jsonschema==4.17.0  # Schema validation
```

### Integration Points
- AI Assistant (existing) - Add query orchestrator
- Knowledge Graph V2 (existing) - Use for schema metadata
- Data Products V2 (existing) - Execute generated SQL

---

## Success Metrics

### Phase 1 (Week 4)
- ✅ AI answers 20 common questions
- ✅ Query generation < 2 seconds
- ✅ Accuracy > 95%
- ✅ Zero SQL injection vulnerabilities

### Phase 2 (Week 7)
- ✅ Cache hit rate > 60%
- ✅ Cached response < 100ms
- ✅ 100% security enforcement
- ✅ Zero unauthorized access

### Phase 3 (Week 9)
- ✅ User understanding > 90%
- ✅ Error recovery > 80%
- ✅ User satisfaction > 4/5

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM hallucinations | HIGH | HIGH | Use template + validation, not pure LLM |
| Performance issues | MEDIUM | HIGH | Implement caching early (Week 5) |
| Security vulnerabilities | MEDIUM | CRITICAL | Dedicated security week (Week 6-7) |
| Scope creep | MEDIUM | MEDIUM | Strict phase boundaries, MVP focus |
| Redis infrastructure | LOW | MEDIUM | Fallback to in-memory cache if Redis unavailable |

---

## Testing Strategy

### Unit Tests (Per Week)
- Week 1-2: Semantic layer components (50+ tests)
- Week 3: Query generation (50+ tests)
- Week 4: Integration (20+ tests)
- Week 5: Caching (30+ tests)
- Week 6-7: Security (100+ tests)
- Week 8-9: UX components (30+ tests)

### Integration Tests
- E2E query flow (20 scenarios)
- Security enforcement (100 scenarios)
- Performance benchmarks (caching, query optimization)

### User Acceptance Testing
- 10 business users test 50 queries
- Feedback collection and iteration

---

## Rollout Plan

### Week 10: Beta Release
- Internal testing with 5 users
- Collect feedback
- Bug fixes

### Week 11: Production Release
- Deploy to production
- Monitor performance
- User training

### Week 12+: Continuous Improvement
- Add more business terms
- Optimize query templates
- Expand security rules

---

## Cost Estimate

### Development Time
- Phase 1: 4 weeks × 40 hours = 160 hours
- Phase 2: 3 weeks × 40 hours = 120 hours
- Phase 3: 2 weeks × 40 hours = 80 hours
- **Total**: 360 hours (9 weeks)

### Infrastructure
- Redis Cloud: ~$30/month (optional, can use local Redis)
- No additional costs (using existing SAP AI Core)

---

## References

- Gap Analysis: [[ai-data-query-architecture-gap-analysis]]
- Knowledge Graph Enhancement: [[knowledge-graph-semantic-enhancement-implementation-plan]]
- Module Standard: [[Module Federation Standard]]
- Testing Methodology: [[Gu Wu API Contract Testing Foundation]]

---

## Approval

**Status**: APPROVED  
**Start Date**: 2026-02-24  
**Target Completion**: 2026-04-25 (9 weeks)  
**Next Step**: Create PROJECT_TRACKER.md tasks