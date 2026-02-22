# 🚀 P2P Data Products - Project Tracker

**Version**: 4.2  
**Last Updated**: 2026-02-22 (Restored missing HIGH priority tasks)

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

### Key Commands
```bash
pytest tests/ -v                       # All tests
python -m tools.fengshui analyze       # Architecture audit
python -m tools.shifu --session-start  # Ecosystem insights
taskkill /F /IM python.exe             # Kill test servers
git tag -l                             # List all version tags
git show v4.2                          # View specific version snapshot
```

### 📖 Documentation
- [[Module Federation Standard]] - Module architecture
- `docs/knowledge/INDEX.md` - All documentation
- [[Gu Wu API Contract Testing Foundation]] - Testing methodology

---

## 📋 ACTIVE TASKS

### 🔴 CRITICAL (Production Blockers)
| ID | Priority | Task | Effort | Status | Completed Date | Notes |
|---|---|---|---|---|---|---|
| CRIT-23 | CRITICAL | AI Query System - Week 6-7: Access Control & Security | 8d | NEW | | Phase 2 security implementation |
| CRIT-4 | CRITICAL | Complete login_manager module | 4-6h | IN PROGRESS | | Authentication required for production |

### 🟠 HIGH (Quality & Architecture)
| ID | Priority | Task | Effort | Status | Completed Date | Notes |
|---|---|---|---|---|---|---|
| HIGH-43.1 | HIGH | CSS !important Analysis & Remediation | 4-6h | COMPLETED | 2026-02-22 | CSS audit complete, design tokens defined |
| HIGH-43.2 | HIGH | BEM Architecture Migration | 6-8h | PLANNED | | Depends on HIGH-43.1 |
| HIGH-43.3 | HIGH | CSS Magic Number Extraction | 3-4h | COMPLETED | 2026-02-22 | Analysis complete, auto-increment tasks created |
| HIGH-50 | HIGH | KG V2 Edge Labels: Display Association Metadata | 2-3h | COMPLETED | 2026-02-22 | Edge metadata tooltips with cardinality/ON conditions |
| HIGH-51 | HIGH | KG V2 Semantic Visualization: API Contract Tests | 2h | COMPLETED | 2026-02-22 | Fixed FK edge enrichment bug, 8 tests passing |
| HIGH-49 | HIGH | KG V2 Schema Filtering API: Handle Large Responses | 2-3h | COMPLETED | 2026-02-22 | API filtering for AI assistants |
| HIGH-25 | HIGH | AI Query System - Week 1: Semantic Layer | 3d | PLANNED | | Business term dictionary service |
| HIGH-26 | HIGH | AI Query System - Week 2: Time Intelligence Parser | 2d | PLANNED | | Parse time expressions |
| HIGH-27 | HIGH | AI Query System - Week 3: Query Generation Service | 5d | PLANNED | | SQL template engine |
| HIGH-28 | HIGH | AI Query System - Week 4: AI Assistant Integration | 4d | PLANNED | | Query intent extractor |
| HIGH-17 | HIGH | WP-LAZY-LOADING: Quality Ecosystem Optimization | 6-10h | PLANNED | | Apply eager/lazy loading patterns |
| HIGH-13 | HIGH | Knowledge Graph Connection Pooling | 2-3h | PLANNED | | Implement connection pooling |
| HIGH-5 | HIGH | DDD Pattern Integration Phase 6: Shi Fu Meta-Architecture | 12-18h | PLANNED | | Shi Fu validates quality tool architecture |
| HIGH-7 | HIGH | End-to-End Systematic Testing | 1-2w | PLANNED | | Replace trial-and-error with E2E tests |
| HIGH-8 | HIGH | Fix architecture issues | 2-3d | IN PROGRESS | | 66% reduction in HIGH issues achieved |
| HIGH-9 | HIGH | Fix Shi Fu failing tests (3/21) | 1-2h | PLANNED | | Update test data |

### 🟢 MEDIUM (Features & Enhancements)
| ID | Task | Effort | Status | Completed Date | Dependencies | Notes |
|---|---|---|---|---|---|---|
| t-001 | Replace Spacing Magic Numbers with Design Tokens | 3-4h | PLANNED | | HIGH-43.3 ✅ | Phase 1: Spacing system |
| t-002 | Replace Sizing Magic Numbers with Design Tokens | 3-4h | PLANNED | | t-001 | Phase 2: Component sizing |
| t-003 | Replace Timing Magic Numbers with Design Tokens | 1-2h | PLANNED | | t-002 | Phase 3: Animation timing |
| t-004 | Create CSS Validation Tests for Design Tokens | 2-3h | PLANNED | | t-003 | Phase 4: Automated validation |
| t-005 | Implement Pre-Commit CSS Validation Hook | 1-2h | PLANNED | | t-004 | Phase 5: CI/CD integration |
| KGV-001 | KG V2 Column Explorer Panel: Detailed Column Inspection | 4-6h | COMPLETED | 2026-02-22 | HIGH-51 ✅ | Column details panel with filters |
| KGV-002 | KG V2 Semantic Filtering: Filter Graph by Semantic Type | 3-4h | COMPLETED | 2026-02-22 | KGV-001 ✅ | Fixed duplicate tooltip issue |
| MED-027 | Gu Wu Resolver Phase 3.3: Extended Resolver Coverage | 4-6h | PLANNED | | | Additional resolvers |
| MED-022 | AI Query System - Week 5: Query Result Cache | 3d | PLANNED | | HIGH-25-28 | Redis cache service |
| MED-023 | AI Query System - Week 8: Query Explanation | 3d | PLANNED | | CRIT-023 | Natural language explanations |
| MED-024 | AI Query System - Week 9: Error Handling | 2d | PLANNED | | MED-023 | User-friendly errors |
| APP-004 | AI Assistant Phase 5: Frontend-Backend Integration | 1-2w | PLANNED | | APP-003 ✅ | Chat UI |
| APP-003 | Phase 3: Module Migration (7 modules) | 2-3w | IN PROGRESS | | APP-002 ✅ | 7 modules |
| E2E-004 | Phase 8.4: Multi-Module Coverage | 2-3h | PLANNED | | E2E-003 ✅ | Multi-module tests |
| UIX-001 | Phase 1: Coverage Enforcement | 3-4h | PLANNED | | | Frontend test quality gates |
| MED-006 | P2P Dashboard Phase 2: Frontend UX | 1-2w | PLANNED | | | Repository Pattern backend ✅ |

### 🔵 LOW (Nice to Have)
| ID | Priority | Task | Effort | Status | Completed Date | Notes |
|---|---|---|---|---|---|---|
| LOW-001 | LOW | Rebuild sqlite_connection database from CSN | 2-3h | PLANNED | | HANA Cloud compatibility |
| LOW-002 | LOW | Delete obsolete `database/` folder | 5min | PLANNED | | Causes repeated AI confusion |

---

## 📚 VERSION HISTORY

### v4.2 (2026-02-22) - Knowledge Graph Enhancements (KGV-001, KGV-002)
**Completed**: 
- KGV-001: Schema filtering UI with collapsible filter panel
- KGV-002: Fixed duplicate tooltip issue in edge visualization
- HIGH-49: Schema filtering API for large responses
- HIGH-50: Edge metadata display with cardinality/ON conditions
- HIGH-51: Fixed FK edge enrichment bug

**Key Learnings - KGV-002 (Duplicate Tooltip Fix)**:
- **WHAT**: Replaced vis.js default `title` property with custom `tooltipHtml` property to prevent duplicate tooltips
- **WHY**: vis.js was displaying both its built-in tooltip (from `title`) and our custom HTML tooltip simultaneously
- **PROBLEM**: Edge tooltips showing duplicate content - raw HTML at top, formatted HTML below
- **SOLUTION**: Changed VisJsGraphAdapter to use `tooltipHtml` custom property instead of `title`, updated event handlers to read from `tooltipHtml`
- **ALTERNATIVES**: Could have disabled vis.js tooltips globally, but custom property approach is cleaner
- **CONSTRAINTS**: Must maintain backward compatibility with existing graph visualization
- **VALIDATION**: Browser tested - single, clean HTML tooltip now displays with cardinality and JOIN conditions
- **WARNINGS**: Never use `title` property for custom tooltips in vis.js - it always triggers default tooltip
- **CONTEXT**: Completes HIGH-50 edge metadata display enhancement, provides rich relationship information

**Technical Details - KGV-002**:
- **Root Cause**: vis.js automatically displays `title` property as plain text tooltip
- **Fix**: `convertNode()` and `convertEdge()` now store HTML in `tooltipHtml` (not `title`)
- **Handler Updates**: `setupTooltipHandlers()` reads from `node.tooltipHtml` and `edge.tooltipHtml`
- **Result**: Clean single tooltip showing cardinality, ON conditions, relationship type with proper styling
- **No Breaking Changes**: Existing graph visualization and interaction behavior preserved

### v4.1 (2026-02-22) - Knowledge Graph Schema Filtering
**Completed**:
- KGV-001: Knowledge Graph schema filtering UI with collapsible panels and multi-select

**Key Learnings**:
- **WHAT**: Implemented schema filtering for Knowledge Graph V2 with entity/relationship selection
- **WHY**: Users needed ability to focus on specific schemas without overwhelming graph visualization
- **PROBLEM**: Full schema graph too complex for targeted analysis, no UI controls for filtering
- **SOLUTION**: Created FilterPanel component with collapsible sections, multi-select checkboxes, integrated with backend API
- **ALTERNATIVES**: Could use search/autocomplete, but multi-select provides better overview
- **CONSTRAINTS**: Must maintain performance with 100+ entities/relationships
- **VALIDATION**: API contract tests passing, browser testing confirms filter panel functionality
- **CONTEXT**: Enables focused analysis of specific domains (e.g., PurchaseOrder relationships only)

### v4.0 (2026-02-15) - CSS Magic Number Analysis
**Completed**:
- HIGH-43.3: CSS magic number analysis complete
- Created comprehensive analysis script (`scripts/python/extract_css_magic_numbers.py`)
- Generated design token mapping document (`docs/knowledge/css-design-tokens.md`)
- Defined 5-phase implementation plan with auto-increment tasks (t-001 through t-005)

**Key Learnings**:
- **WHAT**: Identified 200+ magic numbers across CSS codebase requiring design token extraction
- **WHY**: Magic numbers hurt maintainability, inconsistent spacing/sizing creates UX friction
- **PROBLEM**: No centralized design system, values duplicated across components, hard to maintain consistency
- **SOLUTION**: Created comprehensive audit, mapped to design tokens (spacing, sizing, timing, colors)
- **ALTERNATIVES**: Could migrate to CSS-in-JS, but design tokens maintain separation of concerns
- **CONSTRAINTS**: Must not break existing layouts, gradual migration required
- **VALIDATION**: Analysis script generates detailed mappings, pre-commit hooks planned for enforcement
- **CONTEXT**: Foundation for BEM architecture migration (HIGH-43.2)

### Earlier Versions
See git tags for detailed version history:
- v3.x: Module Federation standardization, Feng Shui quality gates
- v2.x: Knowledge Graph V2 architecture, Clean Architecture adoption
- v1.x: Initial P2P data products, SQLite/HANA integration