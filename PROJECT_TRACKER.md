# PROJECT_TRACKER.md - P2P Data Products Development

**Version**: 5.16.0
**Last Updated**: 2026-02-21 (HIGH-46.1 COMPLETE: Preview Mode Core Engine + Comprehensive Test Suite)
**Standards**: [.clinerules v4.2](/​.clinerules) | **Next Review**: 2026-02-28

**⭐ VERSION SCHEME**: PROJECT_TRACKER.md version follows git tag versioning (v5.5.4 = latest tag)

---

## 🚀 QUICK START

### API-First Development (MANDATORY ⭐)
> **Core Principle**: "Test the contract, trust the implementation"

1. **Design API Contracts**: Backend + Frontend endpoints (BEFORE implementation)
2. **Write API Contract Tests**: Use `@pytest.mark.api_contract` in `/tests/[module]/`
3. **Run Tests via requests** (< 1 second): `pytest tests/[module]/ -v`
4. **Verify APIs stable**: All contract tests passing
5. **THEN build UX**: On stable API foundation
6. **Update Docs**: `docs/knowledge/` vault with [[wikilinks]]

### Test File Organization (MANDATORY ⭐)
```
tests/
├── ai_assistant/              # AI Assistant module tests
│   ├── test_ai_assistant_backend.py
│   ├── test_ai_assistant_frontend_api.py
│   └── test_ai_assistant_hana_e2e.py
├── data_products_v2/          # Data Products V2 module tests
│   ├── test_data_products_v2_backend.py
│   └── test_data_products_v2_frontend_api.py
├── logger/                    # Logger module tests
│   ├── test_log_backend.py
│   └── test_log_frontend_api.py
├── knowledge_graph_v2/        # Knowledge Graph V2 module tests
│   ├── test_knowledge_graph_v2_backend_api.py
│   ├── test_knowledge_graph_v2_frontend_api.py
│   └── test_knowledge_graph_v2_analytics_api.py
├── integration/               # Integration tests
├── debug/                     # Debug/experimental tests
└── test_smoke.py              # Smoke tests
```
**RULE**: ALL test files MUST be in `/tests/[module]/` subdirectories. Creating tests in root or module directories is forbidden.

### Key Commands
```bash
# API contract tests by module
pytest tests/ai_assistant/ -v          # AI Assistant tests
pytest tests/data_products_v2/ -v      # Data Products tests
pytest tests/logger/ -v                # Logger tests
pytest tests/knowledge_graph_v2/ -v    # Knowledge Graph V2 tests
pytest tests/ -v                       # All tests

# Architecture quality (7 agents)
python -m tools.fengshui analyze       # Architecture audit
python -m tools.fengshui fix           # Autonomous fixes

# Ecosystem health
python -m tools.shifu --session-start  # Ecosystem insights

# Pre-commit cleanup
taskkill /F /IM python.exe             # Kill test servers
```

### Documentation Standards
- **Knowledge Vault**: `docs/knowledge/` (all .md files only)
- **Index**: `docs/knowledge/INDEX.md` (updated with every doc)
- **Architecture**: [[Module Federation Standard]] (v1.0, 950+ lines)
- **Testing**: [[Gu Wu API Contract Testing Foundation]] (core methodology)
- **Module Isolation**: [[Module Isolation Enforcement Standard]] (600+ lines)

---

## 📋 ACTIVE TASKS

### 🔴 CRITICAL (Production Blockers)
| ID | Task | Effort | Status | Completed Date | Notes |
|----|------|--------|--------|----------------|-------|
| **CRIT-25** | Feng Shui Analysis - Critical Findings Stabilization | 13 hours | 🟡 IN PROGRESS | | PHASE 1 ✅ COMPLETE (5h): HIGH-41 kgv2 tests ✅ + HIGH-42 ai_assistant tests ✅. PHASE 2 (6h): CSS Refactoring (HIGH-43). PHASE 3 (2h): Performance (HIGH-44, HIGH-45). Total 45 API contract tests ready for CI/CD. [[feng-shui-comprehensive-analysis-2026-02-21]] |
| **CRIT-23** | AI Query System - Week 6-7: Access Control & Security | 8 days | 🟢 PLANNED | | HIGH-25-28, MED-22 | Row-level security, column masking, audit logging. [[ai-query-system-implementation-proposal]] Phase 2 |
| **CRIT-4** | Complete login_manager module | 4-6 hours | 🔴 URGENT | | Authentication required for production |

### 🟠 HIGH (Quality & Architecture)

#### Architecture Enhancement - Preview Mode (HIGH-46 Breakdown)
| ID | Task | Effort | Status | Completed Date | Dependencies | Notes |
|----|------|--------|--------|----------------|--------------|-------|
| **HIGH-46.1** | Preview Mode Phase 1.1: Core Engine + Data Models | 2 hours | ✅ COMPLETE | 2026-02-21 | HIGH-41 ✅, HIGH-42 ✅ | Created `tools/fengshui/preview/` package with engine.py (PreviewEngine, PreviewResult, PreviewFinding, Severity enum) and validators.py (5 validators: Naming, Structure, Isolation, Dependency, Pattern). Comprehensive test suite: 22 tests in `tests/unit/tools/fengshui/test_preview_engine.py`, all passing in <2s. **Deliverable**: Core engine validates module designs in <1s with actionable feedback. **Files**: `__init__.py`, `engine.py` (250 lines), `validators.py` (380 lines), test suite (450 lines). |
| **HIGH-46.2** | Preview Mode Phase 1.2: 5 Core Validators | 3-4 hours | 🟢 PLANNED | | HIGH-46.1 | Create `tools/fengshui/preview/validators.py`: NamingValidator (Module Federation naming rules), StructureValidator (required files/dirs), IsolationValidator (no cross-module imports), DependencyValidator (module.json declarations), PatternValidator (Repository/Service layers). **Deliverable**: 5 validators detecting 80%+ common violations. **Files**: `validators.py` (350+ lines). |
| **HIGH-46.3** | Preview Mode Phase 1.3: CLI Interface | 1-2 hours | 🟢 PLANNED | | HIGH-46.2 | Create `tools/fengshui/preview/cli.py`: Interactive mode (guided prompts), JSON spec mode (`--spec file.json`), Output formatting (console + JSON). **Deliverable**: `python -m tools.fengshui.preview` command. **Files**: `cli.py` (150+ lines), `__main__.py`. |
| **HIGH-46.4** | Preview Mode Phase 1.4: Example Usage + Tests | 1 hour | 🟢 PLANNED | | HIGH-46.3 | Create example spec file + basic validator tests. **Deliverable**: Working demo + smoke tests. **Files**: `examples/module_spec_example.json`, `tests/unit/tools/fengshui/test_preview_validators.py`. |
| **HIGH-46.5** | Preview Mode Phase 2: Design Document Parser | 2-3 hours | 🟢 PLANNED | | HIGH-46.4 | Create parser for module.json, README.md, API specs. Extract: module_id, routes, api_endpoints, dependencies, structure. **Deliverable**: Automatic design extraction from docs. **Files**: `tools/fengshui/preview/parsers.py` (200+ lines). |
| **HIGH-46.6** | Preview Mode Phase 3: Real-time AI Integration | 2-3 hours | 🟢 PLANNED | | HIGH-46.5 | Integrate with Cline workflow: Hook into planning phase, Provide real-time feedback, Suggest fixes before implementation. **Deliverable**: AI assistant integration hooks. **Files**: `tools/fengshui/preview/ai_integration.py` (150+ lines). |
| **HIGH-46.7** | Preview Mode Phase 4: CI/CD Hooks | 1-2 hours | 🟢 PLANNED | | HIGH-46.6 | Create pre-commit hook, GitHub Actions workflow, Quality gate enforcement. **Deliverable**: Automated validation in CI/CD pipeline. **Files**: `.github/workflows/preview-validation.yml`, `scripts/pre-commit-preview.py`. |
| **HIGH-46.8** | Preview Mode Documentation + Training | 1 hour | 🟢 PLANNED | | HIGH-46.7 | Update README, Add usage examples, Create workflow guide. **Deliverable**: Complete documentation. **Files**: `tools/fengshui/preview/README.md`, knowledge vault doc. |

#### Phase 1: API Contract Testing (2-3 hours - CRITICAL BLOCKER)
| ID | Task | Effort | Status | Completed Date | Dependencies | Notes |
|----|------|--------|--------|----------------|--------------|-------|
| **HIGH-41** | Feng Shui Phase 1.1: knowledge_graph_v2 Backend API Contract Tests | 2 hours | ✅ COMPLETE | 2026-02-21 | CRIT-25 | Created 8 backend API contract tests with @pytest.mark.api_contract: health, schema-graph, rebuild, status, cache-stats, invalidate-cache, delete-cache, analytics-status. All tests use requests library with <1s timeout. Ready for CI/CD integration. |
| **HIGH-42** | Feng Shui Phase 1.2: ai_assistant API Test Decorator Fixes | 3 hours | ✅ COMPLETE | 2026-02-21 | CRIT-25 | Created 5 new ai_assistant API contract test files: backend_api (8 tests), frontend_api (6 tests), conversation_api (7 tests), query_api (8 tests), hana_e2e_api (8 tests). Total: 37 tests with @pytest.mark.api_contract + @pytest.mark.e2e. All use requests library, <1s timeout. Location: `/tests/ai_assistant/`. |

#### Phase 2: CSS Refactoring (4-6 hours - HIGH priority quality)
| ID | Task | Effort | Status | Completed Date | Dependencies | Notes |
|----|------|--------|--------|----------------|--------------|-------|
| **HIGH-43** | Feng Shui Phase 2: CSS Refactoring - Fiori Design System Integration | 6 hours | 🟢 PLANNED | | HIGH-41 ✅, HIGH-42 ✅ | Extract 96 HIGH findings: 85 !important overrides → SAP Fiori CSS tokens, 11 color accessibility issues. **Phases**: (1) Audit HIGH-34, (2) Extract tokens (--fiori-primary, --fiori-semantic-error, etc), (3) Replace !important with token variables, (4) Apply contrast validation (HIGH-40), (5) Verify light/dark mode, motion preferences. Target: Production CSS with zero !important overrides. [[high-40-kgv2-css-refactoring-phase-5b-color-redesign]] |

#### Phase 3: Performance Optimization (4 hours - HIGH priority)
| ID | Task | Effort | Status | Completed Date | Dependencies | Notes |
|----|------|--------|--------|----------------|--------------|-------|
| **HIGH-44** | Feng Shui Phase 3.1: N+1 Query Optimization | 4 hours | 🟢 PLANNED | | HIGH-41 ✅, HIGH-42 ✅ | Fix 5 N+1 patterns: kgv2 (2 patterns - schema graph eager loading, analytics prefetch), ai_assistant (2 patterns - conversation context, agent metadata), data_products_v2 (1 pattern - datasource relationships). **Each**: Replace loop queries with bulk query + JOIN or prefetch_related. Expected: 25-37x performance improvement. [[high-37-kgv2-performance-n+1-query-fixes]] |
| **HIGH-45** | Feng Shui Phase 3.2: DI Violation Fixes | 2 hours | 🟢 PLANNED | | HIGH-41 ✅, HIGH-42 ✅ | Fix data_products_v2 DI violation (hana_data_product_repository.py:285 - ServiceLocator pattern). Convert to constructor injection. Verify no service_locator usage remaining. |

#### Ongoing High-Priority Tasks
| ID | Task | Effort | Status | Completed Date | Notes |
|----|------|--------|--------|----------------|-------|
| **HIGH-34** | KG V2 CSS Refactoring Phase 1: Audit & Documentation | 1 day | ✅ VERIFIED | 2026-02-21 | 126 !important declarations cataloged, 85% justified for vis.js overrides |
| **HIGH-35** | KG V2 Architecture - Top 5 DI Violations | 1 day | ✅ COMPLETE | 2026-02-21 | Eliminated Service Locator antipattern. KnowledgeGraphFacadeV2 full DI: constructor injection |
| **HIGH-37** | KG V2 Performance - N+1 Query Fixes | 4-6 hours | ✅ COMPLETE | 2026-02-21 | Batch eager loading: 95-99% query reduction (101+ → 2-3), 25-37x faster |
| **HIGH-38** | KG V2 CSS Refactoring Phase 2: Specificity | 3 days | ✅ COMPLETE | 2026-02-21 | Replace !important with proper CSS specificity using BEM |
| **HIGH-39** | KG V2 CSS Refactoring Phase 4: CSS Grid Components | 2 days | ✅ COMPLETE | 2026-02-21 | Legend/header/navigation grids, tooltip positioning system |
| **HIGH-25** | AI Query System - Week 1: Semantic Layer Business Terms | 3 days | 🟢 READY | | Business term dictionary service, API endpoints |
| **HIGH-26** | AI Query System - Week 2: Time Intelligence Parser | 2 days | 🟢 PLANNED | | Parse time expressions (last 3 years, Q1 2025) |
| **HIGH-27** | AI Query System - Week 3: Query Generation Service | 5 days | 🟢 PLANNED | | SQL template engine, query validator |
| **HIGH-28** | AI Query System - Week 4: AI Assistant Integration | 4 days | 🟢 PLANNED | | Query intent extractor, orchestrator |
| **HIGH-17** | WP-LAZY-LOADING: Quality Ecosystem Optimization | 6-10 hours | 🟢 READY | | Apply eager/lazy loading patterns to Feng Shui, Gu Wu, Shi Fu |
| **HIGH-13** | Knowledge Graph Connection Pooling | 2-3 hours | 🟢 PLANNED | | Implement connection pooling for SqliteGraphCacheRepository |
| **HIGH-5** | DDD Pattern Integration Phase 6: Shi Fu Meta-Architecture | 12-18 hours | 🟢 PLANNED | | Shi Fu validates quality tool architecture (self-reflection + pattern recommendations) |
| **HIGH-7** | End-to-End Systematic Testing | 1-2 weeks | 🟠 TODO | | Replace trial-and-error with systematic E2E test suite |
| **HIGH-8** | Fix architecture issues | 2-3 days | 🟡 IN PROGRESS | | 66% reduction in HIGH issues achieved (v4.8.0). Apply DI to other modules |
| **HIGH-9** | Fix Shi Fu failing tests (3/21) | 1-2 hours | 🟠 TODO | | Update test data for new pattern detectors |

### 🟢 MEDIUM (Features & Enhancements)
| ID | Task | Effort | Status | Completed Date | Dependencies | Notes |
|----|------|--------|--------|----------------|--------------|-------|
| **MED-22** | AI Query System - Week 5: Query Result Cache | 3 days | 🟢 PLANNED | | HIGH-25-28 ✅ | Redis cache service, TTL configuration |
| **MED-23** | AI Query System - Week 8: Query Explanation | 3 days | 🟢 PLANNED | | CRIT-23 ✅ | Natural language explanations for queries |
| **MED-24** | AI Query System - Week 9: Error Handling | 2 days | 🟢 PLANNED | | MED-23 ✅ | User-friendly error messages |
| **APP-4** | AI Assistant Phase 5: Frontend-Backend Integration | 1-2 weeks | 🟢 READY | | APP-3 (ai_assistant ✅) | Design API contracts, implement chat UI, integrate with backend APIs |
| **APP-3** | Phase 3: Module Migration (7 modules) | 2-3 weeks | 🟠 IN PROGRESS | | APP-2 ✅ | logger (backend ✅), data_products, p2p_dashboard, api_playground, ai_assistant (backend ✅) |
| **E2E-4** | Phase 8.4: Multi-Module Coverage | 2-3 hours | 🟠 TODO | | E2E-3 ✅ | Generate tests for all 7 pending modules using Gu Wu generators |
| **UX-1** | Phase 1: Coverage Enforcement | 3-4 hours | 🟠 TODO | | None | Frontend test quality gates with contract validation |
| **MED-6** | P2P Dashboard Phase 2: Frontend UX | 1-2 weeks | 🟢 READY | | - | Backend migrated to Repository Pattern (v4.4) ✅ |

### 🔵 LOW (Nice to Have)
| ID | Task | Effort | Status | Completed Date | Notes |
|----|------|--------|--------|----------------|-------|
| **LOW-1** | Rebuild sqlite_connection database from CSN | 2-3 hours | 🔵 TODO | | Use `rebuild_sqlite_from_csn.py` to ensure HANA Cloud compatibility |
| **LOW-2** | Delete obsolete `database/` folder | 5 min | 🔵 TODO | | Causes repeated AI confusion - see KNOWN ISSUES |

---

## 📋 Task Completion Tracking

### 7-Day Removal Window (MANDATORY)
- ✅ **Tasks marked COMPLETE** enter 7-day grace period
- ✅ **Completed Date** field records the completion date (YYYY-MM-DD)
- ✅ **Day 7+**: Tasks are automatically removed from ACTIVE TASKS
- ✅ **Details preserved** in VERSION HISTORY with 8-element learnings (WHAT, WHY, PROBLEM, ALTERNATIVES, CONSTRAINTS, VALIDATION, WARNINGS, CONTEXT)
- ✅ **Git tags** store comprehensive work packages: `git show v[version]`

**Completed tasks are NOT abandoned** — they are archived in:
1. **Git tags** (run `git tag -l` to see versions)
2. **Knowledge vault** (`docs/knowledge/INDEX.md` with wikilinks)
3. **Git history** (searchable via `git log --oneline`)

---

## 🔗 Key Architecture References

### Core Standards (MANDATORY)
- **[[Module Federation Standard]]** - Official module architecture (950+ lines, v1.0)
  - `modules/[name]/module.json` (single source of truth)
  - Module isolation via Dependency Injection
  - Naming conventions (snake_case IDs, kebab-case routes)
  
- **[[Gu Wu API Contract Testing Foundation]]** - Testing methodology
  - Test backend APIs: `/api/[module]/[endpoint]`
  - Test frontend APIs: `/api/modules/frontend-registry`
  - One API test validates entire call stack implicitly
  
- **[[Module Isolation Enforcement Standard]]** - Architecture integrity (600+ lines)
  - Multi-layer defense against cross-module imports
  - Feng Shui Module Isolation Agent (9th agent) verification
  - Zero violations enforced
  
- **[[API-First Contract Testing Methodology]]** - Complete guide
  - Design contracts before implementation
  - Write tests before code
  - 60-300x faster than browser testing

### Quality Tools
- **Feng Shui** (`python -m tools.fengshui analyze`): 7-agent architecture validation
  - Architecture, Security, UX, FileOrg, Performance, Documentation, TestCoverage
  
- **Gu Wu** (`pytest tests/`): API contract testing framework
  - `@pytest.mark.api_contract` for backend/frontend API tests
  - Test Gap Display for coverage analysis
  
- **Shi Fu** (`python -m tools.shifu --session-start`): Ecosystem health
  - Pattern recognition (DDD, lazy/eager loading)
  - Growth tracking and correlations
  - Architecture observer

### Documentation
- `docs/knowledge/INDEX.md` - Master index (update with every new doc)
- `docs/knowledge/quality-ecosystem/` - Quality tools and patterns
- `.clinerules` - v4.2 development standards
- `.clinerules/create-jira-requirement-ticket.md` - JIRA workflow

---

## 🔗 Historical Context

**Project evolution and learnings** are preserved in:

| Source | Content | Access |
|--------|---------|--------|
| **Git tags** | Comprehensive work packages with context | `git tag -l` |
| **Knowledge vault** | Detailed analysis with wikilinks | `docs/knowledge/` |
| **Git history** | Searchable patterns and decisions | `git log --oneline` |
| **VERSION HISTORY** (below) | Summary with key learnings | This document |

### 📚 VERSION HISTORY

#### v5.15.0 (2026-02-21) - CRIT-25 Phase 1 COMPLETE - API Contract Testing Foundation
**Completed**:
- ✅ HIGH-41 COMPLETE: Created 8 knowledge_graph_v2 backend API contract tests
  - Location: `tests/knowledge_graph_v2/test_knowledge_graph_v2_backend_api.py`
  - Tests: health, schema-graph, rebuild, status, cache-stats, invalidate-cache, delete-cache, analytics-status
  - All with @pytest.mark.api_contract + @pytest.mark.e2e decorators
  - Uses requests library, <1s timeout per test

- ✅ HIGH-42 COMPLETE: Created 5 ai_assistant API contract test files
  - test_ai_assistant_backend_api.py: 8 backend endpoint tests
  - test_ai_assistant_frontend_api.py: 6 frontend metadata tests
  - test_ai_assistant_conversation_api.py: 7 conversation management tests
  - test_ai_assistant_query_api.py: 8 query processing tests
  - test_ai_assistant_hana_e2e_api.py: 8 HANA integration tests
  - Total: 37 tests with proper decorators

**PHASE 1 COMPLETE (5 hours)**:
- HIGH-41: ✅ COMPLETE (2 hours) - knowledge_graph_v2 backend tests
- HIGH-42: ✅ COMPLETE (3 hours) - ai_assistant API contract tests
- **Total API Contract Tests**: 45 tests ready for CI/CD integration
- **Foundation**: API-first testing methodology now established across both modules

**Key Learning**: API contract testing (one test validates entire call stack) is 60-300x faster than browser testing. Foundation now solid for both kgv2 and ai_assistant.

**PHASE 2 Next**: HIGH-43 CSS Refactoring (6 hours)
- Extract 96 HIGH findings from Feng Shui
- Replace !important overrides with SAP Fiori CSS tokens
- Apply color contrast validation (HIGH-40)

#### v5.13.0 (2026-02-21) - Phase 1 Project Tasks - Feng Shui API Contract Testing Roadmap
**Completed**:
- ✅ Analyzed Feng Shui findings (196 total: 1 CRITICAL, 119 HIGH, 27 MED, 49 LOW)
- ✅ Created Phase 1-3 breakdown for CRIT-25 stabilization
- ✅ Documented specific tasks for HIGH-41 (kgv2 backend API tests) and HIGH-42 (ai_assistant test decorator fixes)

**PHASE 1 (2-3h) - API Contract Testing Foundation**:
- HIGH-41: Create 8 backend API contract tests for knowledge_graph_v2 with @pytest.mark.api_contract
- HIGH-42: Fix 5 ai_assistant test files with proper decorators and requests library usage

**PHASE 2 (4-6h) - CSS Refactoring**:
- HIGH-43: Extract SAP Fiori CSS tokens from 96 HIGH findings, replace !important overrides

**PHASE 3 (4h) - Performance & DI**:
- HIGH-44: Fix 5 N+1 query patterns (25-37x improvement)
- HIGH-45: Fix data_products_v2 DI violation (constructor injection)

**Total Effort to Critical Stabilization**: 13 hours
**Ecosystem Health Baseline**: 43/100 (CRITICAL)

#### v5.12.0 (2026-02-21) - Comprehensive Feng Shui Analysis: Ecosystem Health Assessment
**Completed**:
- ✅ Ran Feng Shui multi-agent analysis on all 4 core modules
- ✅ Analyzed 196 total findings: 1 CRITICAL, 119 HIGH, 27 MED, 49 LOW
- ✅ Identified critical blockers: Missing API contract tests (kgv2 CRITICAL), Invalid API test decorators (ai_assistant HIGH), CSS crisis (96 HIGH findings)
- ✅ Generated comprehensive analysis report
- ✅ Ecosystem health score: 43/100 (CRITICAL)

**Module Health Scorecard**:
- knowledge_graph_v2: 0/100 (CRITICAL ❌)
- ai_assistant: 27/100 (CRITICAL ❌)
- logger: 80/100 (GOOD ✅)
- data_products_v2: 73/100 (GOOD ✅)

#### Earlier versions
See git tags: `git tag -l` for complete version history

---

**Maintenance Rules** (MANDATORY):
1. ✅ After each session: Update date and description in header
2. ✅ Task completion: Record Completed Date (YYYY-MM-DD)
3. ✅ Day 7+: Remove from ACTIVE TASKS, add to VERSION HISTORY
4. ✅ Update header: `Last Updated: YYYY-MM-DD (Brief description)`
5. ✅ Before git commit: Verify no completed tasks beyond 7 days
6. ✅ Git checkpoint: `git add . && git commit && git push`