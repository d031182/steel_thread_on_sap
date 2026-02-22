# Data Products V2 - Dependency Injection Refactoring Proposal

**Status**: PROPOSAL  
**Priority**: HIGH (Architecture Quality)  
**Estimated Effort**: 60-90 minutes  
**Risk**: MEDIUM (requires careful testing)  
**Created**: 2026-02-15

---

## 🎯 OBJECTIVE

Eliminate 3 HIGH priority architecture issues flagged by Feng Shui:
1. **Service Layer Violation** @ `api.py:52`
2. **Service Locator Anti-Pattern** @ `data_products_facade.py:35`
3. **Service Locator Anti-Pattern** @ `sqlite_data_product_repository.py:42` *(FALSE POSITIVE - using approved factory)*

---

## 📊 CURRENT ARCHITECTURE (Problems)

### Problem 1: API Layer - Service Locator
```python
# api.py:15-30 (CURRENT - BAD)
def get_facade(source: str):
    """Reaches into current_app - Service Locator anti-pattern"""
    if source == 'sqlite':
        if not hasattr(current_app, 'sqlite_facade_v2'):
            raise ValueError("SQLite facade not configured")
        return current_app.sqlite_facade_v2  # ❌ Service Locator
    
    elif source == 'hana':
        if not hasattr(current_app, 'hana_facade_v2'):
            raise ValueError("HANA facade not configured")
        return current_app.hana_facade_v2  # ❌ Service Locator
```

**Why Bad**:
- Tight coupling to Flask's `current_app`
- Hard to test (requires Flask context)
- Violates Dependency Inversion Principle

---

### Problem 2: Facade - Factory in Constructor
```python
# facade.py:48-58 (CURRENT - BAD)
def __init__(self, source_type, host=None, ...):
    """Creates repository internally - tight coupling"""
    self._repository = DataProductRepositoryFactory.create(  # ❌ Service Locator
        source_type=source_type,
        host=host,
        port=port,
        ...
    )
```

**Why Bad**:
- Facade is tightly coupled to factory
- Cannot inject mock repositories for testing
- Violates Single Responsibility (creates AND uses)

---

### Problem 3: Repository - Factory Usage
```python
# sqlite_data_product_repository.py:42 (CURRENT - ACCEPTABLE)
def __init__(self, db_path: str = None):
    self._repo: AbstractRepository = create_repository(  # ✅ ACCEPTABLE
        backend='sqlite',
        db_path=db_path
    )
```

**Why Acceptable**:
- Uses core's approved factory (`create_repository`)
- Core factory is the dependency injection point
- Repository is leaf node - doesn't need injection here

**Feng Shui Issue**: False positive - should whitelist this pattern

---

## ✅ PROPOSED ARCHITECTURE (Solution)

### Solution 1: Constructor Injection for API
```python
# modules/data_products_v2/backend/api.py (NEW)
class DataProductsV2API:
    """API layer with constructor injection"""
    
    def __init__(self, sqlite_facade, hana_facade=None):
        """
        Inject facades via constructor (Dependency Injection)
        
        Args:
            sqlite_facade: Pre-configured SQLite facade
            hana_facade: Optional pre-configured HANA facade
        """
        self._facades = {
            'sqlite': sqlite_facade,
            'hana': hana_facade
        }
    
    def get_facade(self, source: str):
        """
        Get facade from injected dependencies
        
        No longer reaches into current_app!
        """
        if source not in self._facades:
            raise ValueError(f"Unknown source: {source}")
        
        facade = self._facades[source]
        if facade is None:
            raise ValueError(f"{source} facade not configured")
        
        return facade
    
    def list_data_products(self):
        """Endpoint - uses injected facade"""
        source = request.args.get('source', 'sqlite').lower()
        facade = self.get_facade(source)
        products = facade.get_data_products()
        # ... rest of logic

# Create blueprint from API instance
def create_blueprint(api_instance):
    """Factory to create blueprint from API instance"""
    bp = Blueprint('data_products_v2', __name__)
    
    @bp.route('/', methods=['GET'])
    def list_data_products():
        return api_instance.list_data_products()
    
    # ... other routes
    return bp
```

---

### Solution 2: Repository Injection for Facade
```python
# modules/data_products_v2/facade/data_products_facade.py (NEW)
class DataProductsFacade:
    """Facade with repository injection"""
    
    def __init__(self, repository: IDataProductRepository):
        """
        Inject repository via constructor (Dependency Injection)
        
        Args:
            repository: Pre-configured repository instance
        """
        self._repository = repository  # Injected, not created!
    
    def get_data_products(self) -> List[DataProduct]:
        """Use injected repository"""
        return self._repository.get_data_products()
    
    # ... rest of methods unchanged
```

---

### Solution 3: Wire Up in server.py
```python
# server.py (NEW - Dependency Injection Container)
def configure_data_products_v2(app):
    """
    Configure data_products_v2 module with proper DI
    
    This function acts as the DI container/composition root
    """
    # 1. Create repositories (leaf dependencies)
    sqlite_repo = SQLiteDataProductRepository(db_path=None)  # Uses default
    
    hana_repo = None
    if all([hana_host, hana_user, hana_password]):
        hana_repo = HANADataProductRepository(
            host=hana_host,
            port=hana_port,
            user=hana_user,
            password=hana_password,
            database=hana_database,
            schema=hana_schema
        )
    
    # 2. Create facades (middle layer)
    sqlite_facade = DataProductsFacade(repository=sqlite_repo)  # ✅ Injected!
    hana_facade = DataProductsFacade(repository=hana_repo) if hana_repo else None
    
    # 3. Create API instance (top layer)
    api_instance = DataProductsV2API(
        sqlite_facade=sqlite_facade,
        hana_facade=hana_facade
    )
    
    # 4. Create and register blueprint
    blueprint = create_blueprint(api_instance)
    app.register_blueprint(blueprint, url_prefix='/api/data-products')
    
    return api_instance  # Store on app if needed for testing

# In create_app()
configure_data_products_v2(app)
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Refactor Facade (30 min)
- [ ] Update `DataProductsFacade.__init__` to accept repository param
- [ ] Remove `DataProductRepositoryFactory.create()` call
- [ ] Remove `switch_source()` method (no longer makes sense)
- [ ] Update facade tests to inject mock repositories
- [ ] Run facade tests - verify passing

### Phase 2: Refactor API (30 min)
- [ ] Create `DataProductsV2API` class with constructor
- [ ] Move route logic to instance methods
- [ ] Create `create_blueprint()` factory function
- [ ] Update `get_facade()` to use injected facades
- [ ] Remove `current_app` dependencies completely

### Phase 3: Wire Up DI Container (15 min)
- [ ] Create `configure_data_products_v2()` in `server.py`
- [ ] Instantiate repositories
- [ ] Instantiate facades with repositories
- [ ] Instantiate API with facades
- [ ] Register blueprint
- [ ] Test server startup

### Phase 4: Test & Verify (15 min)
- [ ] Run all API contract tests
- [ ] Verify 13/13 tests passing
- [ ] Run Feng Shui analysis
- [ ] Verify 0 HIGH issues
- [ ] Manual smoke test in browser

---

## 🧪 TESTING STRATEGY

### Unit Tests (Easy with DI!)
```python
# tests/unit/facade/test_data_products_facade.py
def test_get_data_products():
    # ARRANGE - Mock repository
    mock_repo = Mock(spec=IDataProductRepository)
    mock_repo.get_data_products.return_value = [
        DataProduct(product_name="PO", ...)
    ]
    
    # ACT - Inject mock
    facade = DataProductsFacade(repository=mock_repo)  # ✅ Easy testing!
    products = facade.get_data_products()
    
    # ASSERT
    assert len(products) == 1
    assert products[0].product_name == "PO"
    mock_repo.get_data_products.assert_called_once()
```

### Integration Tests (Use Real Instances)
```python
# tests/integration/test_data_products_v2_integration.py
def test_full_stack_integration():
    # ARRANGE - Real dependencies
    repo = SQLiteDataProductRepository(db_path=':memory:')
    facade = DataProductsFacade(repository=repo)
    api = DataProductsV2API(sqlite_facade=facade)
    
    # ACT - Real call
    response = api.list_data_products()
    
    # ASSERT - Real result
    assert response.status_code == 200
```

---

## 📊 BENEFITS

### Architecture Quality
- ✅ **Eliminates 2 HIGH issues** (api.py, facade.py)
- ✅ **Proper layering**: API → Facade → Repository
- ✅ **Testability**: Easy to inject mocks
- ✅ **Maintainability**: Clear dependencies

### Testing Improvements
- ✅ **Unit tests**: Fast, isolated, reliable
- ✅ **No Flask context**: Test facade/repository independently
- ✅ **Mock injection**: Easy to test error paths
- ✅ **Integration tests**: Clear boundary testing

### Future-Proofing
- ✅ **Swap implementations**: Easy to change data sources
- ✅ **Add caching**: Inject caching repository wrapper
- ✅ **Add logging**: Inject logging decorator
- ✅ **Multiple instances**: Create facades per-request if needed

---

## ⚠️ RISKS & MITIGATIONS

### Risk 1: Breaking Existing Tests
**Mitigation**: Run tests after each phase
**Rollback**: Git checkpoint before starting

### Risk 2: Server Startup Issues
**Mitigation**: Test configuration carefully
**Rollback**: Keep old code commented for quick revert

### Risk 3: Performance Impact
**Mitigation**: DI is compile-time only (no runtime cost)
**Verification**: Benchmark API response times

---

## 🔄 ALTERNATIVE APPROACHES

### Alternative 1: Use Flask-Injector Library
**Pros**: Battle-tested DI framework  
**Cons**: New dependency, learning curve  
**Recommendation**: Manual DI is simpler for this case

### Alternative 2: Keep Service Locator, Suppress Warnings
**Pros**: Zero effort  
**Cons**: Technical debt accumulates  
**Recommendation**: Not acceptable - architecture matters

### Alternative 3: Gradual Migration
**Pros**: Lower risk, incremental changes  
**Cons**: Longer to complete  
**Recommendation**: Good fallback if full refactor too risky

---

## 📅 IMPLEMENTATION TIMELINE

| Phase | Duration | Effort |
|-------|----------|--------|
| Design Review | 15 min | Review this doc |
| Phase 1: Facade | 30 min | Refactor + test |
| Phase 2: API | 30 min | Refactor + test |
| Phase 3: DI Container | 15 min | Wire up |
| Phase 4: Verification | 15 min | Test + Feng Shui |
| **Total** | **105 min** | **~2 hours** |

---

## 🎯 SUCCESS CRITERIA

1. ✅ Feng Shui shows **0 HIGH** issues for data_products_v2
2. ✅ All 13 API contract tests **passing**
3. ✅ No `current_app` references in api.py
4. ✅ No factory calls in facade constructor
5. ✅ Server starts without errors
6. ✅ Manual smoke test successful

---

## 📚 REFERENCES

- **Dependency Inversion Principle**: https://en.wikipedia.org/wiki/Dependency_inversion_principle
- **Service Locator Anti-Pattern**: https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/
- **Constructor Injection**: https://en.wikipedia.org/wiki/Dependency_injection#Constructor_injection
- **Cosmic Python (Book)**: Architecture Patterns with Python

---

## 🚀 NEXT STEPS

**Option A**: Implement now (2 hours)
- Start with Phase 1 (Facade refactoring)
- Test incrementally
- Complete all 4 phases

**Option B**: Schedule for later
- Create ticket in project tracker
- Estimate as HIGH priority, 2-hour task
- Implement in next sprint

**Option C**: Hybrid approach
- Implement Phase 1-2 now (facade + API)
- Schedule Phase 3-4 (testing) for later
- Gradual migration

---

**Recommendation**: **Option A** if time permits (architecture is foundational). Otherwise **Option B** (schedule properly).