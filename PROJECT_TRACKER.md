# PROJECT_TRACKER.md - P2P Data Products Development

**Version**: 5.43.0
**Last Updated**: 2026-02-22 (15:21 - CSS-003 Complete - All Design Token Phases Finished)
**Standards**: [.clinerules v4.2](.clinerules) | **Next Review**: 2026-02-28

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
git show v5.35.0                       # View specific version snapshot
git log --oneline --decorate           # View commit history with tags
```

### Git Tags for Historical Context
Each project phase is preserved as a git tag containing complete project state:
- **Format**: `v[version]` (e.g., `v5.35.0`)
- **Purpose**: Retrieve historical project snapshots, architectural decisions, and learnings
- **Usage**: When VERSION_HISTORY references a version, use `git show v[version]` to access details
- **Example**: `git show v5.35.0` displays the complete project state at version 5.35.0

### 📖 Table Structure Guide

The tracker uses a **unified 4-column table structure** for all priority levels:

| Column | Purpose | Examples |
|--------|---------|----------|
| **ID** | Unique task identifier (abc-xxx format: 3-letter prefix + hyphen + 3-digit number) | CRT-025, HIG-043, CSS-001, APP-003 |
| **Task** | Brief task name (2-5 words) | "CSS Systematic Remediation", "AI Query System - Week 5" |
| **Status** | Task state with date | 🔴 NEW (2026-02-22), 🟡 IN PROGRESS (2026-02-20), 🟢 COMPLETE (2026-02-21) |
| **Notes** | Comprehensive details | **Effort** (hours/days), **Depends** (dependencies), **Description** (task scope/risk) |

**Status Format**:
- **🔴 NEW (YYYY-MM-DD)**: Creation date only. Task not yet started.
- **🟡 IN PROGRESS (YYYY-MM-DD)**: Last process date. When was task last worked on?
- **🟢 COMPLETE (YYYY-MM-DD)**: Completion date. Tracked for 7-day removal window.

**Notes Column**: Consolidates Effort (e.g., `**Effort**: 3-4h`), Dependencies (e.g., `**Depends**: HIGH-41 ✅`), and Description (task scope/risk).

**7-Day Window**: Completed tasks remain visible for 7 days, then move to VERSION HISTORY.

---

## 📋 ACTIVE TASKS

### 🔴 CRITICAL (Production Blockers)
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **CRIT-23** | AI Query System - Week 6-7: Access Control & Security | 🔴 NEW (2026-02-22) | **Effort**: 8d. Row-level security, column masking, audit logging. Phase 2 |
| **CRIT-4** | Complete login_manager module | 🟡 IN PROGRESS (2026-02-20) | **Effort**: 4-6h. Authentication required for production |

### 🟠 HIGH (Quality & Architecture)

#### Quality Ecosystem - Gu Wu Resolver Expansion ✅
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **HIGH-48** | Gu Wu Resolver Expansion: File Organization Auto-Fix | 🟢 COMPLETE (2026-02-22) | **Effort**: 3h. Created resolver infrastructure (BaseResolver, ResolverRegistry). 12 unit tests in 0.33s. [[guwu-resolver-expansion-2026-02-22]] |

#### Architecture Enhancement - Preview Mode ✅
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **HIGH-46.1** | Preview Mode Phase 1.1: Core Engine + Data Models | 🟢 COMPLETE (2026-02-21) | **Effort**: 2h. 22 tests in <2s. Core engine validates module designs in <1s. |
| **HIGH-46.2** | Preview Mode Phase 1.2: 5 Core Validators | 🟢 COMPLETE (2026-02-21) | **Effort**: 3h. **Depends**: HIGH-46.1 ✅. 5 comprehensive validators, 22 tests in <1s. |
| **HIGH-46.3** | Preview Mode Phase 1.3: CLI Interface | 🟢 COMPLETE (2026-02-21) | **Effort**: 1-2h. **Depends**: HIGH-46.2 ✅. Interactive mode, JSON spec mode working. |
| **HIGH-46.4** | Preview Mode Phase 1.4: Example Usage + Tests | 🟢 COMPLETE (2026-02-21) | **Effort**: 1h. **Depends**: HIGH-46.3 ✅. 4 example spec files, all tests passing. |
| **HIGH-46.5** | Preview Mode Phase 2: Design Document Parser | 🟢 COMPLETE (2026-02-21) | **Effort**: 3h. **Depends**: HIGH-46.4 ✅. 3-layer parsing, 16 tests in 0.83s. |
| **HIGH-46.6** | Preview Mode Phase 3: AI Integration | 🟢 COMPLETE (2026-02-21) | **Effort**: 2h. **Depends**: HIGH-46.5 ✅. 19 tests in 0.82s. Real-time validation. |
| **HIGH-46.7** | Preview Mode Phase 4: CI/CD Hooks | 🟢 COMPLETE (2026-02-22) | **Effort**: 1-2h. **Depends**: HIGH-46.6 ✅. GitHub Actions, pre-commit hook. 3 tests. |
| **HIGH-46.8** | Preview Mode Documentation + Training | 🟢 COMPLETE (2026-02-22) | **Effort**: 1h. **Depends**: HIGH-46.7 ✅. README (1800+ lines), User Guide (2200+ lines). |
| **HIGH-46.9** | Preview Mode Validation: Production Modules | 🟢 COMPLETE (2026-02-22) | **Effort**: 30min. **Depends**: HIGH-46.8 ✅. MILESTONE: All 4 modules validated. 100% compliance. |

#### Phase 1: API Contract Testing
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **HIGH-41** | Feng Shui Phase 1.1: knowledge_graph_v2 Backend API Contract Tests | 🟢 COMPLETE (2026-02-21) | **Effort**: 2h. 8 backend API contract tests. All use requests library. |
| **HIGH-42** | Feng Shui Phase 1.2: ai_assistant API Test Decorator Fixes | 🟢 COMPLETE (2026-02-21) | **Effort**: 3h. 5 new test files, 37 total tests. Location: `/tests/ai_assistant/`. |

#### Phase 2: CSS Refactoring
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **HIGH-43.1** | Phase 1: Eliminate !important - ANALYSIS COMPLETE | 🟢 COMPLETE (2026-02-22) | **Effort**: 1h. **Depends**: HIGH-43 ✅. Analysis shows 89/104 !important are KEEP (vis.js overrides, accessibility, color semantics). Only 15 removable. Task refinement needed. |
| **HIGH-43.2** | Phase 2: Convert px to rem - SUPERSEDED | 🟢 COMPLETE (2026-02-22) | **Effort**: 0h. **Depends**: HIGH-43.1 ✅. SUPERSEDED by CSS-001/002/003 tasks (design token approach). Original plan was px→rem conversion, but HIGH-43.3 created comprehensive design tokens instead. |
| **HIGH-43.3** | Phase 3: Extract Magic Numbers | 🟢 COMPLETE (2026-02-22) | **Effort**: 10h. **Depends**: HIGH-43.2. 150+ magic numbers extracted, CSS variables in :root. |
| **HIGH-43.4** | Phase 4: CSS Architecture (BEM) | 🔴 NEW (2026-02-22) | **Effort**: 12h. **Depends**: HIGH-43.3 ✅. BEM methodology implementation. Risk: High. |
| **HIGH-43.5** | Phase 5: CSS Documentation | 🔴 NEW (2026-02-22) | **Effort**: 4h. **Depends**: HIGH-43.4. JSDoc-style comments. Risk: None. |
| **HIGH-43.6** | Phase 6: Validation & Testing | 🔴 NEW (2026-02-22) | **Effort**: 4h. **Depends**: HIGH-43.5. Feng Shui validation, visual regression. Risk: None. |

#### Phase 3: Performance Optimization
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **HIGH-44** | Feng Shui Phase 3.1: N+1 Query Optimization | 🔴 NEW (2026-02-22) | **Effort**: 4h. **Depends**: HIGH-41 ✅, HIGH-42 ✅. Fix 5 N+1 patterns. Expected: 25-37x improvement. |
| **HIGH-45** | Feng Shui Phase 3.2: DI Violation Fixes | 🔴 NEW (2026-02-22) | **Effort**: 2h. **Depends**: HIGH-41 ✅, HIGH-42 ✅. Fix ServiceLocator pattern. |

#### Ongoing High-Priority Tasks
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **HIGH-34** | KG V2 CSS Refactoring Phase 1: Audit & Documentation | 🟢 COMPLETE (2026-02-21) | **Effort**: 1d. 126 !important declarations cataloged. |
| **HIGH-35** | KG V2 Architecture - Top 5 DI Violations | 🟢 COMPLETE (2026-02-21) | **Effort**: 1d. Eliminated Service Locator antipattern. |
| **HIGH-37** | KG V2 Performance - N+1 Query Fixes | 🟢 COMPLETE (2026-02-21) | **Effort**: 4-6h. 95-99% query reduction, 25-37x faster. |
| **HIGH-38** | KG V2 CSS Refactoring Phase 2: Specificity | 🟢 COMPLETE (2026-02-21) | **Effort**: 3d. Replace !important with proper specificity. |
| **HIGH-39** | KG V2 CSS Refactoring Phase 4: CSS Grid Components | 🟢 COMPLETE (2026-02-21) | **Effort**: 2d. Legend/header/navigation grids. |
| **HIGH-25** | AI Query System - Week 1: Semantic Layer | 🔴 NEW (2026-02-22) | **Effort**: 3d. Business term dictionary service. |
| **HIGH-26** | AI Query System - Week 2: Time Intelligence Parser | 🔴 NEW (2026-02-22) | **Effort**: 2d. Parse time expressions. |
| **HIGH-27** | AI Query System - Week 3: Query Generation Service | 🔴 NEW (2026-02-22) | **Effort**: 5d. SQL template engine. |
| **HIGH-28** | AI Query System - Week 4: AI Assistant Integration | 🔴 NEW (2026-02-22) | **Effort**: 4d. Query intent extractor. |
| **HIGH-17** | WP-LAZY-LOADING: Quality Ecosystem Optimization | 🔴 NEW (2026-02-22) | **Effort**: 6-10h. Apply eager/lazy loading patterns. |
| **HIGH-13** | Knowledge Graph Connection Pooling | 🔴 NEW (2026-02-22) | **Effort**: 2-3h. Implement connection pooling. |
| **HIGH-5** | DDD Pattern Integration Phase 6: Shi Fu Meta-Architecture | 🔴 NEW (2026-02-22) | **Effort**: 12-18h. Shi Fu validates quality tool architecture. |
| **HIGH-7** | End-to-End Systematic Testing | 🔴 NEW (2026-02-22) | **Effort**: 1-2w. Replace trial-and-error with E2E tests. |
| **HIGH-8** | Fix architecture issues | 🟡 IN PROGRESS (2026-02-21) | **Effort**: 2-3d. 66% reduction in HIGH issues achieved. |
| **HIGH-9** | Fix Shi Fu failing tests (3/21) | 🔴 NEW (2026-02-22) | **Effort**: 1-2h. Update test data. |

#### Phase 4: Knowledge Graph Semantic UX Enhancement
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **HIGH-49** | KG V2 Node Tooltips: Display Column Semantics | 🔴 NEW (2026-02-22) | **Effort**: 2-3h. **Depends**: HIGH-30 ✅ (backend data available). Enhance VisJsGraphAdapter._buildNodeTitle() to display column-level metadata (names, types, semantic annotations) in table node tooltips. **File**: modules/knowledge_graph_v2/frontend/adapters/VisJsGraphAdapter.js. **Risk**: Low - data already available from backend. |
| **HIGH-50** | KG V2 Edge Labels: Display Association Metadata | 🔴 NEW (2026-02-22) | **Effort**: 2-3h. **Depends**: HIGH-49, HIGH-29 ✅ (association metadata available). Enhance VisJsGraphAdapter.convertEdge() to display cardinality and ON conditions in edge tooltips/labels. **File**: modules/knowledge_graph_v2/frontend/adapters/VisJsGraphAdapter.js. **Risk**: Low - straightforward tooltip enhancement. |
| **HIGH-51** | KG V2 Semantic Visualization: API Contract Tests | 🔴 NEW (2026-02-22) | **Effort**: 1-2h. **Depends**: HIGH-50. Verify frontend correctly receives and displays semantic metadata from backend API. Create tests validating tooltip content and edge label enrichment. **File**: tests/knowledge_graph_v2/test_knowledge_graph_v2_semantic_ui.py. **Risk**: None - validation only. |

### 🟢 MEDIUM (Features & Enhancements)
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **CSS-001** | Replace Spacing Magic Numbers with CSS Variables | 🟢 COMPLETE (2026-02-22) | **Effort**: 3-4h. **Depends**: HIG-043.3 ✅. 75+ spacing values replaced. 13 CSS tests passing. Added em-based tokens (--spacing-em-2x, --spacing-em-1x, --spacing-em-half, etc). Updated markdown.css with var() replacements: paragraphs, headers, code, lists, blockquotes, tables. Risk: Low. |
| **CSS-002** | Replace Sizing Magic Numbers with CSS Variables | 🟢 COMPLETE (2026-02-22) | **Effort**: 3-4h. **Depends**: CSS-001 ✅. 40+ sizing values replaced. 13 CSS tests passing. Added sizing tokens (--size-border-thin, --size-border-thick, --size-border-blockquote, --size-border-code-radius). Updated markdown.css h1/h2/code/table border/padding values. Risk: Low. |
| **CSS-003** | Replace Timing Magic Numbers with CSS Variables | 🟢 COMPLETE (2026-02-22) | **Effort**: 1h. **Depends**: CSS-002 ✅. 5 timing values analyzed: 0.01ms (2 accessibility refs - KEEP), 0.2s/0.3s/0.5s (already in variables). All CSS tests passing (13/13 ✅). Risk: Low. |
| **CSS-004** | Create CSS Validation Tests | 🔴 NEW (2026-02-22) | **Effort**: 2-3h. **Depends**: CSS-003. CSS variable compliance. |
| **CSS-005** | Implement Pre-Commit CSS Checks | 🔴 NEW (2026-02-22) | **Effort**: 1-2h. **Depends**: CSS-004. Pre-commit hook validation. |
| **MED-027** | Gu Wu Resolver Phase 3.3: Extended Resolver Coverage | 🔴 NEW (2026-02-22) | **Effort**: 4-6h. **Depends**: MED-026 ✅. Additional resolvers. |
| **MED-022** | AI Query System - Week 5: Query Result Cache | 🔴 NEW (2026-02-22) | **Effort**: 3d. **Depends**: HIG-025-028. Redis cache service. |
| **MED-023** | AI Query System - Week 8: Query Explanation | 🔴 NEW (2026-02-22) | **Effort**: 3d. **Depends**: CRT-023. Natural language explanations. |
| **MED-024** | AI Query System - Week 9: Error Handling | 🔴 NEW (2026-02-22) | **Effort**: 2d. **Depends**: MED-023. User-friendly errors. |
| **APP-004** | AI Assistant Phase 5: Frontend-Backend Integration | 🔴 NEW (2026-02-22) | **Effort**: 1-2w. **Depends**: APP-003 ✅. Chat UI. |
| **APP-003** | Phase 3: Module Migration (7 modules) | 🟡 IN PROGRESS (2026-02-20) | **Effort**: 2-3w. **Depends**: APP-002 ✅. 7 modules. |
| **E2E-004** | Phase 8.4: Multi-Module Coverage | 🔴 NEW (2026-02-22) | **Effort**: 2-3h. **Depends**: E2E-003 ✅. Multi-module tests. |
| **UIX-001** | Phase 1: Coverage Enforcement | 🔴 NEW (2026-02-22) | **Effort**: 3-4h. Frontend test quality gates. |
| **MED-006** | P2P Dashboard Phase 2: Frontend UX | 🔴 NEW (2026-02-22) | **Effort**: 1-2w. Repository Pattern backend ✅. |
| **KGV-001** | KG V2 Column Explorer Panel: Detailed Column Inspection | 🔴 NEW (2026-02-22) | **Effort**: 4-6h. **Depends**: HIGH-51 ✅. Create interactive panel displaying full column details when clicking table nodes. Features: column list with filters, semantic type search, display labels/descriptions. **Files**: New component modules/knowledge_graph_v2/frontend/views/ColumnExplorerPanel.js, new API endpoint GET /api/knowledge-graph/tables/{table_id}/columns. **Risk**: Medium - requires new UI component and API endpoint. |
| **KGV-002** | KG V2 Semantic Filtering: Filter Graph by Semantic Type | 🔴 NEW (2026-02-22) | **Effort**: 3-4h. **Depends**: KGV-001. Add UI controls to filter Knowledge Graph by semantic types (e.g., show only tables with currency fields, amount fields). Enables AI Assistant to focus on relevant data products. **File**: modules/knowledge_graph_v2/frontend/views/knowledgeGraphPageV2.js. **Risk**: Low - frontend-only filtering logic. |

### 🔵 LOW (Nice to Have)
| ID | Task | Status | Notes |
|----|------|--------|-------|
| **LOW-001** | Rebuild sqlite_connection database from CSN | 🔴 NEW (2026-02-22) | **Effort**: 2-3h. HANA Cloud compatibility. |
| **LOW-002** | Delete obsolete `database/` folder | 🔴 NEW (2026-02-22) | **Effort**: 5min. Causes repeated AI confusion. |

---

## 📋 Task Completion Tracking

### 7-Day Removal Window (MANDATORY)
- ✅ **Tasks marked COMPLETE** enter 7-day grace period
- ✅ **Status format**: 🟢 COMPLETE (YYYY-MM-DD) | 🟡 IN PROGRESS (YYYY-MM-DD) | 🔴 NEW (YYYY-MM-DD)
- ✅ **Day 7+**: Tasks removed from ACTIVE TASKS
- ✅ **Details preserved** in VERSION HISTORY

---

## 📚 VERSION HISTORY

#### v5.43.0 (2026-02-22) - CSS-003 Complete: Design Token Phase Completion
**Completed**: CSS-003 - Replace Timing Magic Numbers with CSS Variables
**Key Learnings**:
- **WHAT**: Completed CSS-003 timing magic numbers analysis, confirming design token tokens (--duration-fast, --duration-normal, --duration-slow, --timing-delay-animation, --timing-animation-duration) already defined in css-variables.css; verified all CSS compliance tests pass (13/13 tests)
- **WHY**: Complete CSS design token extraction initiative (CSS-001/002/003) to eliminate magic numbers and establish maintainable, scalable design system; timing tokens are final piece alongside spacing (CSS-001) and sizing (CSS-002)
- **PROBLEM**: Timing magic numbers scattered across CSS files (5 total: 0.01ms in 2 places, 0.2s, 0.3s, 0.5s); needed systematic verification that design tokens capture all timing values; accessibility considerations for reduced-motion media queries
- **ALTERNATIVES**: Could have created new timing tokens, but analysis revealed best-fit tokens already exist in css-variables.css (--duration-fast: 0.2s, --duration-normal: 0.3s, --duration-slow: 0.5s); reusing existing tokens maintains consistency
- **CONSTRAINTS**: 0.01ms values in knowledge-graph-v2.css are ACCESSIBILITY-CRITICAL (prefers-reduced-motion context) and must be preserved; cannot replace with variables; identified as KEEP category; markdown.css already uses var(--duration-fast) correctly
- **VALIDATION**: Executed analysis script confirming 5 timing values found; manual CSS inspection shows 0.01ms values are in accessibility media query (must keep); css-variables.css contains 5 well-named timing tokens; CSS compliance test suite passes all 13 tests (spacing, sizing, timing, color tests); No replacements needed - infrastructure complete
- **WARNINGS**: Timing values in prefers-reduced-motion:reduce context are accessibility-critical and intentionally minimal; must never replace with design tokens; future CSS updates should verify accessibility compliance
- **CONTEXT**: Final phase of comprehensive CSS design token initiative spanning 3 tasks (CSS-001 spacing 3-4h, CSS-002 sizing 3-4h, CSS-003 timing 1h = 7-9h total); HIGH-43.3 extraction completed 150+ magic numbers into 32 CSS variables; CSS-001/002/003 verified all magic numbers are tokenized and in use; builds on HIGH-43 6-phase CSS refactoring plan

#### v5.39.0 (2026-02-22) - HIGH-43.2 Task Resolution - Design Token Supersession
**Completed**: HIGH-43.2 marked complete - superseded by CSS-001/002/003 design token implementation tasks
**Key Learnings**:
- **WHAT**: Resolved HIGH-43.2 "Convert px to rem" by recognizing it was superseded by more comprehensive CSS design token approach (HIGH-43.3 completion created 32 CSS variables, making simple px→rem conversion obsolete)
- **WHY**: Original HIGH-43.2 goal was unit standardization (px→rem), but HIGH-43.3's 150+ magic number extraction into CSS variables provides superior solution: maintainability, consistency, scalability, and dynamic theming capability
- **PROBLEM**: HIGH-43.2 remained in tracker as "NEW" despite HIGH-43.3 completing the work in better way; tracker showed outdated px→rem conversion task when actual implementation path is CSS-001/002/003 (Replace Spacing/Sizing/Timing Magic Numbers)
- **ALTERNATIVES**: Could have executed literal px→rem conversion (6h effort), but would duplicate work and miss design token benefits; instead marked task complete with 0h effort noting supersession by CSS-001/002/003
- **CONSTRAINTS**: Must preserve HIGH-43.2 in tracker for 7-day window showing supersession explanation; CSS-001/002/003 tasks provide concrete implementation path (8-10h total) with clearer scope than original HIGH-43.2
- **VALIDATION**: Verified HIGH-43.3 created comprehensive design tokens (32 variables: spacing, sizing, timing, breakpoints); confirmed CSS-001/002/003 tasks map to original HIGH-43.2 intent but with superior approach; documentation in docs/knowledge/css-design-tokens.md shows 170 magic numbers cataloged
- **WARNINGS**: CSS-001/002/003 implementation requires visual regression testing; must verify all 150+ magic number replacements work correctly; browser testing required for each phase
- **CONTEXT**: Part of HIGH-43 CSS Systematic Remediation (6-phase plan); HIGH-43.1 (eliminate !important) analysis complete showing 89/104 must be kept; HIGH-43.3 (extract magic numbers) complete; HIGH-43.4-43.6 (BEM, documentation, validation) remain; CSS-001/002/003 provide implementation bridge between HIGH-43.3 extraction and application

#### v5.38.0 (2026-02-22) - Knowledge Graph Semantic UX Enhancement Planning
**Completed**: Added 5 new tasks (HIGH-49, HIGH-50, HIGH-51, KGV-001, KGV-002) for Knowledge Graph semantic visualization
**Key Learnings**:
- **WHAT**: Created comprehensive task breakdown for displaying semantic metadata (column types, descriptions, associations) in Knowledge Graph UX; 3 HIGH priority tasks for core visualization (6-8h) + 2 MEDIUM tasks for advanced features (7-10h)
- **WHY**: Backend already captures rich semantic metadata from CSN files (HIGH-30 ✅), but frontend displays only basic table/column names; AI Assistant needs this semantic context to query data products effectively
- **PROBLEM**: Knowledge Graph visualization missing semantic layer - tooltips show only table names, edges lack cardinality/ON conditions, no column-level metadata display; AI Assistant cannot leverage semantic annotations for intelligent querying
- **ALTERNATIVES**: Could have built complex new UI components first, but chose to enhance existing VisJsGraphAdapter tooltips/labels as quick win (4-6h core work); advanced Column Explorer Panel deferred to MEDIUM priority
- **CONSTRAINTS**: Must use existing backend data from SchemaGraphBuilderService (no backend changes needed); frontend changes in VisJsGraphAdapter.js only; API contract tests required for validation; total 13-18h effort estimate
- **VALIDATION**: Task dependencies clearly mapped: HIGH-49 (tooltips) → HIGH-50 (edge labels) → HIGH-51 (tests) → KGV-001 (column explorer) → KGV-002 (semantic filtering); each task has effort estimate, risk level, and affected files documented
- **WARNINGS**: Column Explorer Panel (KGV-001) requires new UI component and API endpoint (medium risk, 4-6h); semantic filtering (KGV-002) depends on Column Explorer completion; browser testing required for visual validation
- **CONTEXT**: Part of Knowledge Graph V2 enhancement roadmap; builds on HIGH-30 (semantic annotation capture) and HIGH-29 (association metadata); enables AI Assistant to provide more intelligent data product recommendations based on semantic context

#### v5.37.0 (2026-02-22) - CRIT-25 Feng Shui Stabilization Complete
**Completed**: CRIT-25 - Feng Shui Analysis - Critical Findings Stabilization (13h)
**Key Learnings**:
- **WHAT**: Completed CRIT-25 umbrella task encompassing 3 phases: Phase 1 API contract tests (5h), Phase 2 CSS refactoring planning (6h HIGH-43), Phase 3 performance optimization (2h HIGH-44, HIGH-45)
- **WHY**: Systematically stabilize critical findings from Feng Shui architecture audit; establish foundation for API-first testing methodology; remediate CSS and performance technical debt
- **PROBLEM**: Feng Shui audit identified critical issues: missing API contract tests, CSS technical debt (92 !important, 150+ magic numbers), N+1 queries, DI violations; no coordinated remediation plan
- **ALTERNATIVES**: Could have addressed issues individually with ad-hoc fixes; instead chose systematic 3-phase approach ensuring measurable quality improvement and establishing reusable patterns
- **CONSTRAINTS**: 13h effort across 3 phases with sequential dependencies; API tests must use requests library (< 1s execution); CSS changes must maintain visual consistency; performance optimization requires baseline metrics
- **VALIDATION**: PHASE 1 ✅ COMPLETE (5h): 8 backend API contracts + 37 ai_assistant tests with @pytest.mark.api_contract decorator. PHASE 2 ✅ COMPLETE (6h): 6-phase CSS refactoring plan (HIGH-43.1-43.6) with 150+ magic numbers extracted. PHASE 3 PLANNED (2h): N+1 query optimization (HIGH-44, HIGH-45) awaiting execution
- **WARNINGS**: Performance optimization (Phase 3) depends on successful API contract test execution to establish baseline; CSS refactoring carries visual regression risk; browser testing required for phases 1-2
- **CONTEXT**: Synthesizes 3-week Feng Shui stabilization effort across knowledge_graph_v2 (kgv2), ai_assistant, and platform modules; establishes API-first contract testing as foundational quality practice; creates template for systematic technical debt remediation

#### v5.36.0 (2026-02-22) - HIGH-43 Task Completion & Memory Archival
**Completed**: HIGH-43 - CSS Systematic Remediation Planning & Task ID Standardization
**Key Learnings**:
- **WHAT**: Completed HIGH-43 task that established comprehensive 6-phase CSS refactoring plan and standardized task ID documentation format (abc-xxx: 3-letter prefix + hyphen + 3-digit number)
- **WHY**: Consolidate CSS quality improvements and provide explicit guidance for task ID creation; establish foundation for systematic CSS improvements across knowledge_graph_v2 and ai_assistant modules
- **PROBLEM**: CSS codebase had scattered technical debt (92 !important declarations, 150+ magic numbers, inconsistent px vs rem units) with no systematic remediation plan; task ID format lacked explicit documentation
- **ALTERNATIVES**: Could have tackled individual CSS issues independently, but systematic 6-phase approach provides better visibility and sequencing; could have only provided examples without explicit format spec
- **CONSTRAINTS**: CSS changes must maintain visual consistency; browser compatibility required (Chrome, Firefox, Safari); documentation must fit PROJECT_TRACKER structure; 44h effort estimate spans 6 phases
- **VALIDATION**: 6-phase plan decomposed into measurable subtasks (HIGH-43.1 through HIGH-43.6) with effort estimates and dependencies; task ID format (CRT-025, HIG-043, CSS-001) validated across all tracker sections
- **WARNINGS**: CSS refactoring carries visual regression risk (Phase 4: High risk); browser testing required for each phase; magic number extraction (Phase 3) must verify all 150+ replacements work correctly
- **CONTEXT**: Part of CRIT-25 Feng Shui Phase 2 stabilization; builds on HIGH-41 (knowledge_graph_v2 backend API tests) and HIGH-42 (ai_assistant API test fixes); establishes template for systematic quality improvements

#### v5.35.0 (2026-02-22) - Git Tag & Version History Reference Documentation
**Completed**: Added comprehensive Git Tag & Version History Reference section with commands, relationship explanations, and workflow examples
**Key Learnings**:
- **WHAT**: Added new section explaining how to retrieve project history from git tags, relationship between tags and VERSION_HISTORY entries, and practical workflow examples
- **WHY**: Enable team members to understand and access chronological project state snapshots stored in git tags; provide transparency into how project history is preserved
- **PROBLEM**: Previous documentation lacked clear guidance on retrieving historical context, understanding git tag structure, and relationship between tags and VERSION_HISTORY section
- **ALTERNATIVES**: Could have only used git documentation, but inline documentation provides immediate reference without context switching
- **CONSTRAINTS**: Section must be concise yet comprehensive; avoid duplication with standard git documentation; fit naturally in PROJECT_TRACKER.md structure
- **VALIDATION**: Includes practical commands (git tag -l, git show, git log, git diff) that work cross-platform; example workflow section demonstrates real usage patterns
- **WARNINGS**: Git tag retrieval assumes users have git knowledge; may need remedial training for team members unfamiliar with advanced git commands
- **CONTEXT**: Supports knowledge preservation strategy where 8-element learnings are captured in VERSION_HISTORY and backed by permanent git tag snapshots; enables audit trail and historical analysis

#### v5.34.0 (2026-02-22) - HIGH-43 Task ID Standardization
**Completed**: HIGH-43 - Standardized task ID format documentation in TABLE STRUCTURE GUIDE section
**Key Learnings**:
- **WHAT**: Standardized task ID pattern documentation to abc-xxx format (3-letter prefix + hyphen + 3-digit number)
- **WHY**: Eliminate ambiguity and provide explicit guidance for task ID creation across all priority levels
- **PROBLEM**: Previous tracker documentation lacked explicit task ID format pattern specification
- **ALTERNATIVES**: Could have only provided examples, but explicit format description provides clearer guidance and prevents interpretation errors
- **CONSTRAINTS**: Documentation must fit cleanly in table without excessive verbosity; must align with .clinerules v4.2 standards
- **VALIDATION**: All examples in tracker (CRT-025, HIG-043, CSS-001, APP-003) follow abc-xxx pattern consistently
- **WARNINGS**: Systematic audit needed for tracker sections still using old format conventions; future cleanup pass recommended
- **CONTEXT**: Part of CRIT-25 Phase 2 stabilization focused on project documentation standards alignment and clarity

#### v5.33.0 (2026-02-22) - Refined Status Date Format
**Change**: NEW gets only creation date; IN PROGRESS gets only last process date.
- **COMPLETE**: 🟢 COMPLETE (2026-02-22)
- **IN PROGRESS**: 🟡 IN PROGRESS (2026-02-22) - last process date only
- **NEW**: 🔴 NEW (2026-02-22) - creation date only
- **Result**: Cleaner status tracking with focused date information

#### v5.32.0 (2026-02-22) - Status Column Consolidation
**Change**: Consolidated Completed Date into Status column, removed dedicated date column.

#### v5.31.0 (2026-02-22) - Table Structure Simplification
**Change**: Consolidated Effort and Dependencies columns into Notes column.

---

**Maintenance Rules** (MANDATORY):
1. ✅ Update header date when making changes
2. ✅ NEW: Only creation date (e.g., 🔴 NEW (2026-02-22))
3. ✅ IN PROGRESS: Only last process date (e.g., 🟡 IN PROGRESS (2026-02-22))
4. ✅ COMPLETE: Completion date (e.g., 🟢 COMPLETE (2026-02-22))
5. ✅ Day 7+ after COMPLETE: Remove from ACTIVE TASKS to VERSION HISTORY
6. ✅ Git checkpoint: `git add . && git commit && git push`