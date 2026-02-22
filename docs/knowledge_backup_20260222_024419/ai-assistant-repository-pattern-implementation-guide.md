# AI Assistant Repository Pattern Implementation Guide

**Status**: Ready to Execute  
**Priority**: CRITICAL (Feng Shui v4.12 violation)  
**Estimated Time**: 1-2 hours  
**Last Updated**: 2026-02-15

---

## 🎯 Executive Summary

**Violation Detected**: Feng Shui v4.12 found CRITICAL Repository Pattern violation in AI Assistant
- **File**: `modules/ai_assistant/backend/services/agent_service.py:15`
- **Issue**: Direct import of concrete `SQLiteDataProductsService`
- **Impact**: Tight coupling to SQLite, prevents database switching, untestable

**Solution**: Implement Repository Pattern with Dependency Injection
- **Pattern**: Repository Pattern + Dependency Inversion Principle (SOLID)
- **Industry**: 20+ years proven, documented in Domain-Driven Design (Evans, 2003)
- **Automation**: Script created at `scripts/python/fix_ai_assistant_repository_pattern.py`

---

## 📊 Current State (BEFORE)

### Violation Details

```python
# Line 15 - CRITICAL VIOLATION
from core.services.sqlite_data_products_service import SQLiteDataProductsService  # ❌

# Line 21 - Concrete type hint
@dataclass
class AgentDependencies:
    data_product_service: Any  # ❌ Should be IDataProductRepository

# Line 443 - Singleton pattern
def get_sqlite_data_products_service():  # ❌ Hardcoded SQLite
    global _data_product_service
    if _data_product_service is None:
        _data_product_service = SQLiteDataProductsService()  # ❌
    return _data_product_service
```

### Problems

1. **Tight Coupling**: Hardcoded to SQLite, can't switch to HANA
2. **Untestable**: Can't inject mock repository for tests
3. **Violates DIP**: High-level module (Agent) depends on low-level detail (SQLite)
4. **Singleton Anti-pattern**: Global state, not dependency injection

---

## 🎯 Target State (AFTER)

### Solution Architecture

```python
# Line 15 - USE INTERFACE
from core.interfaces.data_product_repository import IDataProductRepository  # ✅

# Line 21 - Interface type hint
@dataclass
class AgentDependencies:
    data_product_repository: IDataProductRepository  # ✅ Interface

# API Layer - INJECT DEPENDENCY
def chat():
    factory = DataProductRepositoryFactory()
    repository = factory.create("sqlite")  # ✅ or "hana"
    agent = get_joule_agent()
    result = await agent.process_message(..., repository=repository)  # ✅
```

### Benefits

1. **Loose Coupling**: Agent doesn't know about SQLite/HANA
2. **Testable**: Inject mock repository for unit tests
3. **Follows DIP**: Agent depends on interface, not concrete class
4. **Configurable**: Switch databases via factory parameter

---

## 🚀 Implementation Plan

### Phase 1: Automated Refactoring (30 min)

**Execute Script**:
```bash
cd c:\Users\D031182\gitrepo\steel_thread_on_sap
python scripts/python/fix_ai_assistant_repository_pattern.py
```

**Script Actions**:
1. ✅ Fix import (line 15): `SQLiteDataProductsService` → `IDataProductRepository`
2. ✅ Update type hint (line 21): `data_product_service` → `data_product_repository`
3. ✅ Remove SQLite mentions from prompts
4. ✅ Update tool implementations to use interface
5. ✅ Remove singleton function (line 443)
6. ✅ Update API layer to inject repository
7. ✅ Validate with Feng Shui (expect 0 CRITICAL)

### Phase 2: Manual Verification (30 min)

**1. Review Changes**:
```bash
git diff modules/ai_assistant/backend/services/agent_service.py
git diff modules/ai_assistant/backend/api.py
```

**2. Run Tests**:
```bash
pytest tests/test_ai_assistant_backend.py -v
pytest tests/test_ai_assistant_frontend_api.py -v
```

**3. Feng Shui Validation**:
```bash
python -m tools.fengshui analyze --module ai_assistant
```

**Expected**: `0 CRIT` (down from `1 CRIT`)

### Phase 3: Integration Testing (30 min)

**1. Start Server**:
```bash
python server.py
```

**2. Test Chat Endpoint**:
```bash
curl -X POST http://localhost:5000/api/ai-assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all suppliers", "history": []}'
```

**3. Verify Functionality**:
- ✅ AI responds correctly
- ✅ Database queries work
- ✅ No errors in console

---

## 📝 Detailed Changes

### File 1: `agent_service.py` (8 changes)

#### Change 1: Import (Line 15)
```python
# BEFORE
from core.services.sqlite_data_products_service import SQLiteDataProductsService

# AFTER
from core.interfaces.data_product_repository import IDataProductRepository
```

#### Change 2: Type Hint (Line 21)
```python
# BEFORE
data_product_service: Any  # Repository for P2P data queries

# AFTER
data_product_repository: IDataProductRepository  # Repository for P2P data queries
```

#### Change 3: System Prompt (Line 99)
```python
# BEFORE
Database: SQLite (use SQLite syntax, not MySQL/PostgreSQL)

# AFTER
Database: P2P datasource (syntax varies by backend)
```

#### Change 4: Tool Implementation (Line 247)
```python
# BEFORE
service = ctx.deps.data_product_service
result = service.get_data_for_data_product(datasource, data_product)

# AFTER
repository = ctx.deps.data_product_repository
result = repository.get_data_for_data_product(datasource, data_product)
```

#### Change 5: Remove Singleton (Line 443-448)
```python
# BEFORE
def get_sqlite_data_products_service():
    """Get singleton SQLite data products service"""
    global _data_product_service
    if _data_product_service is None:
        _data_product_service = SQLiteDataProductsService()
    return _data_product_service

# AFTER
# ✅ DELETED - Use dependency injection instead
```

#### Change 6: Process Message (Line 306)
```python
# BEFORE
data_product_service=get_sqlite_data_products_service(),

# AFTER
data_product_repository=repository,  # ✅ Injected from caller
```

#### Change 7: Remove Global Variable (Line 439)
```python
# BEFORE
_data_product_service = None

# AFTER
# ✅ DELETED - No more global state
```

#### Change 8: Add Repository Parameter
```python
# BEFORE
async def process_message(
    self,
    user_message: str,
    conversation_history: List[Dict[str, str]],
    context: Dict[str, Any],
    sql_execution_service: Any
) -> AssistantResponse:

# AFTER
async def process_message(
    self,
    user_message: str,
    conversation_history: List[Dict[str, str]],
    context: Dict[str, Any],
    sql_execution_service: Any,
    repository: IDataProductRepository  # ✅ NEW PARAMETER
) -> AssistantResponse:
```

### File 2: `api.py` (2 changes)

#### Change 1: Add Import
```python
# ADD AFTER EXISTING IMPORTS
from modules.data_products_v2.repositories.repository_factory import DataProductRepositoryFactory
```

#### Change 2: Inject Repository in Routes
```python
# BEFORE
@blueprint.route("/chat", methods=["POST"])
def chat():
    data = request.json
    result = await agent.process_message(...)

# AFTER
@blueprint.route("/chat", methods=["POST"])
def chat():
    # Create repository via factory
    factory = DataProductRepositoryFactory()
    repository = factory.create("sqlite")  # ✅ Configuration-driven
    
    data = request.json
    result = await agent.process_message(..., repository=repository)  # ✅ Injected
```

---

## ✅ Validation Checklist

### Automated Validation

- [ ] Script executes without errors
- [ ] Feng Shui reports `0 CRIT` (was `1 CRIT`)
- [ ] All unit tests pass
- [ ] No import errors

### Manual Validation

- [ ] Code review: Changes look correct
- [ ] Integration test: Chat endpoint works
- [ ] Database queries execute successfully
- [ ] No SQLite mentions in prompts
- [ ] Repository injected properly

### Quality Gates

- [ ] Feng Shui: `0 CRITICAL` findings
- [ ] Gu Wu: All API contract tests passing
- [ ] Code coverage: No decrease
- [ ] Documentation: Updated

---

## 🔄 Rollback Plan

If issues arise:

```bash
# Rollback changes
git checkout modules/ai_assistant/backend/services/agent_service.py
git checkout modules/ai_assistant/backend/api.py

# Verify rollback
python -m tools.fengshui analyze --module ai_assistant
# Should show 1 CRIT again (known state)
```

---

## 📚 References

### Documentation
- [[Repository Pattern]]: `docs/knowledge/repository-pattern-modular-architecture.md`
- [[Feng Shui Enhancement]]: v4.12 now detects this violation
- [[Database Abstraction Analysis]]: `docs/knowledge/ai-assistant-database-abstraction-analysis.md`

### Industry Standards
- **Domain-Driven Design** (Eric Evans, 2003): Repository Pattern origin
- **SOLID Principles**: Dependency Inversion Principle (DIP)
- **Clean Architecture** (Robert C. Martin, 2017): Hexagonal Architecture
- **Cosmic Python** (2020): Modern Python implementation

### Code References
- **Good Example**: `modules/data_products_v2/backend/api.py` (already uses Repository Pattern)
- **Interface**: `core/interfaces/data_product_repository.py`
- **Factory**: `modules/data_products_v2/repositories/repository_factory.py`

---

## 🎯 Success Criteria

**DONE when**:
1. ✅ Feng Shui reports `0 CRITICAL` findings
2. ✅ All tests passing
3. ✅ Chat endpoint functional
4. ✅ Code committed with proper message

**Commit Message**:
```
fix(ai-assistant): implement Repository Pattern with DI

- Replace concrete SQLiteDataProductsService with IDataProductRepository interface
- Inject repository via constructor (Dependency Injection)
- Remove singleton anti-pattern
- Update prompts to be database-agnostic
- Clears Feng Shui v4.12 CRITICAL violation

BREAKING: JouleAgent.process_message() now requires repository parameter
```

---

## 📞 Support

**If Issues Arise**:
1. Check Feng Shui report for details
2. Review this document's troubleshooting section
3. Consult [[Repository Pattern]] documentation
4. Ask in next session with specific error message

**Next Session Handoff**:
- Run script: `python scripts/python/fix_ai_assistant_repository_pattern.py`
- Follow validation checklist above
- Commit changes when all green

---

**Ready to Execute**: All preparation complete. Script and documentation ready for next session.