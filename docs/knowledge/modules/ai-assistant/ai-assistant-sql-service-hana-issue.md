# AI Assistant SQL Service HANA Issue

## Problem

The SQL Execution Service (`modules/ai_assistant/backend/services/sql_execution_service.py`) directly accesses SQLite database files. It doesn't support HANA queries through facades.

**Current Implementation**:
```python
class SQLExecutionService:
    def __init__(self, p2p_data_db: str, p2p_graph_db: str):
        self.p2p_data_db = Path(p2p_data_db)  # SQLite file path
        self.p2p_graph_db = Path(p2p_graph_db)  # SQLite file path
    
    def execute_query(self, sql: str, datasource: str = "p2p_data"):
        if datasource == "p2p_data":
            db_path = self.p2p_data_db  # ← Direct SQLite access
        elif datasource == "p2p_graph":
            db_path = self.p2p_graph_db
        # ... connects to SQLite directly
```

**Issue**: When `datasource="hana"`, the service has no way to query HANA! It only knows SQLite file paths.

## Root Cause

**Architecture Mismatch**:
1. **Data Products API**: Uses facades (`get_facade('hana')` → `HANADataProductFacade`)
2. **SQL Execution Service**: Uses direct SQLite connections (no facade support)

**Why This Breaks**:
- AI Assistant passes `datasource="hana"` from conversation context
- SQL Execution Service doesn't recognize "hana" as a valid datasource
- Falls back to default or fails

## Solution Options

### Option 1: Inject Facade into SQL Service (RECOMMENDED)

Update SQL service to accept a facade instead of database paths:

```python
class SQLExecutionService:
    def __init__(self, facade: IDataProductRepository):
        self.facade = facade
    
    def execute_query(self, sql: str):
        # Use facade's execute_sql method
        return self.facade.execute_sql(sql)
```

**Pros**:
- Clean architecture (uses interface)
- Supports any backend (SQLite, HANA, PostgreSQL)
- No datasource parameter needed

**Cons**:
- Need to create SQL service per conversation (one per facade)
- More complex DI setup

### Option 2: Pass Facade at Query Time (SIMPLEST)

Keep service singleton, pass facade when executing:

```python
def execute_query(self, sql: str, facade: IDataProductRepository):
    return facade.execute_sql(sql)
```

**Pros**:
- Minimal changes
- Service stays singleton
- Supports any backend

**Cons**:
- Facade must implement `execute_sql` method
- Changes service interface

### Option 3: Map Datasource to Facade (CURRENT ATTEMPT)

Map string datasource to facade lookup:

```python
def execute_query(self, sql: str, datasource: str):
    if datasource == "hana":
        facade = data_products_api.get_facade("hana")
    else:
        facade = data_products_api.get_facade("sqlite")
    return facade.execute_sql(sql)
```

**Pros**:
- Backwards compatible
- No interface changes

**Cons**:
- Service needs Data Products API reference
- Tight coupling
- Service locator antipattern

## Recommended Approach

**Use Option 2** (Pass facade at query time):

1. Update SQLExecutionService to accept facade parameter
2. Agent already has facade from DI
3. Pass facade when calling execute_query

**Implementation**:
```python
# In agent_service.py execute_sql_impl:
result = service.execute_query(sql_query, facade=ctx.deps.data_product_repository)

# In sql_execution_service.py:
def execute_query(self, sql: str, facade: IDataProductRepository):
    return facade.execute_sql(sql)
```

## Current Workaround

**Immediate fix**: Don't use SQL Execution Service for HANA queries. Use repository directly:

```python
if datasource == "hana":
    # Use repository execute_sql
    result = ctx.deps.data_product_repository.execute_sql(sql_query)
else:
    # Use SQL service for SQLite
    result = service.execute_query(sql_query, datasource)
```

## Status

**Problem**: SQL service doesn't support HANA
**Impact**: AI always queries SQLite even when conversation context says "hana"
**Priority**: HIGH - Blocks HANA datasource functionality
**Estimated Effort**: 30 minutes (Option 2)