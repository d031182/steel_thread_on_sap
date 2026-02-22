# Knowledge Vault Index

**Last Updated**: 2026-02-22 (2:52 AM)  
**Total Documents**: 68 (Reorganized into module-based structure)  
**Status**: Active ✅

---

## 📁 New Organization (2026-02-22)

The knowledge vault has been reorganized from a flat structure into **module-based subdirectories**:

```
docs/knowledge/
├── modules/
│   ├── ai-assistant/        # 21 docs - AI Assistant implementation details
│   ├── knowledge-graph/     # 11 docs - Knowledge Graph architecture & features
│   ├── data-products/       # 1 doc  - Data Products refactoring
│   └── logger/              # 3 docs - Logging system
├── quality-ecosystem/       # Quality tools documentation (Feng Shui, Gu Wu, Shi Fu)
└── [root-level docs]        # Cross-cutting architecture, standards, guides
```

**Benefits**:
- ✅ Easier navigation by module
- ✅ Clearer module boundaries
- ✅ Better maintenance and discovery
- ✅ Supports wikilink paths (e.g., `[[modules/ai-assistant/file-name]]`)

---

## 📚 Quick Navigation

### 🎯 Most Important (Start Here)
- [[Module Federation Standard]] - ⭐ Official module architecture (v1.0)
- [[Module Isolation Enforcement Standard]] - ⭐ Zero cross-module dependencies (v1.0)
- [[Gu Wu API Contract Testing Foundation]] - ⭐ Core testing methodology
- [[API First Contract Testing Methodology]] - Complete testing guide
- [[Feng Shui Preview Mode Design]] - ⭐ Proactive architecture validation
- [[Feng Shui Preview Mode Validation Results]] - ⭐ All 4 modules passed (29.2% confidence) (NEW)
- [[HIGH-46.6 Preview Mode AI Integration]] - ⭐ AI-powered module spec generation
- [[HIGH-46.7 Preview Mode CI/CD Integration]] - ⭐ GitHub Actions & pre-commit hooks
- [Quality Ecosystem Hub](quality-ecosystem/README.md) - ⭐ Feng Shui, Gu Wu, Shi Fu

### 🧩 Components
- [[Groq API Reference]] - Comprehensive Groq API guide
- [[Pydantic AI Framework]] - Type-safe AI agents
- [[Pydantic AI SAP AI Core Integration]] - ✅ Pydantic AI + SAP AI Core (WORKING!)
- [[AI Assistant Phase 4 Advanced Features]] - Latest features
- [[Knowledge Graph v2 Phase 2 Complete]] - Services layer
- [[P2P Dashboard Design]] - P2P dashboard with KPIs
- [[Chat UI Sticky Input Best Practices]] - Chat interface UX standards

### 🏗️ Architecture
- [[Configuration-Based Dependency Injection]] - DI standard
- [[Repository Pattern Modular Architecture]] - Industry standard DDD
- [[Cosmic Python Patterns]] - Complete DDD library
- [[Frontend Modular Architecture Proposal]] - Micro-frontend strategy
- [[App v2 Modular Architecture Plan]] - App redesign

### 📋 Guidelines
- [[SAP Fiori Design Standards]] - Fiori principles
- [[Testing Standards]] - 5-layer pyramid
- [[Feng Shui Pre-Commit Hook Documentation]] - Quality gates
- [[Module Quality Gate]] - Validation tool

### 📊 Requirements & Guides
- [[BDC AI Core Integration Requirements]] - SAP BDC integration
- [[Pytest Windows Setup Guide]] - Windows pytest config

---

## 📖 Full Document List

### 📁 Organized by Module (NEW Structure)

#### AI Assistant Module
- [[modules/ai-assistant/ai-assistant-v2-pydantic-implementation|AI Assistant v2 Pydantic Implementation]]
- [[modules/ai-assistant/ai-assistant-phase-2-implementation|AI Assistant Phase 2 Implementation]]
- [[modules/ai-assistant/ai-assistant-phase-3-conversation-enhancement|AI Assistant Phase 3 Conversation Enhancement]]
- [[modules/ai-assistant/ai-assistant-phase-4-advanced-features|AI Assistant Phase 4 Advanced Features]]
- [[modules/ai-assistant/ai-assistant-litellm-integration|AI Assistant LiteLLM Integration]] - ⭐ LiteLLM provider integration
- [[modules/ai-assistant/ai-assistant-database-abstraction-analysis|AI Assistant Database Abstraction Analysis]]
- [[modules/ai-assistant/ai-assistant-hana-datasource-issue|AI Assistant HANA DataSource Issue]]
- [[modules/ai-assistant/ai-assistant-hana-datasource-solution|AI Assistant HANA DataSource Solution]]
- [[modules/ai-assistant/ai-assistant-hana-direct-query-limitations|AI Assistant HANA Direct Query Limitations]]
- [[modules/ai-assistant/ai-assistant-hana-fix-summary|AI Assistant HANA Fix Summary]]
- [[modules/ai-assistant/ai-assistant-hana-table-name-fix|AI Assistant HANA Table Name Fix]]
- [[modules/ai-assistant/ai-assistant-implementation-status-2026-02-21|AI Assistant Implementation Status]]
- [[modules/ai-assistant/ai-assistant-module-isolation-audit|AI Assistant Module Isolation Audit]]
- [[modules/ai-assistant/ai-assistant-repository-pattern-implementation-guide|AI Assistant Repository Pattern Guide]]
- [[modules/ai-assistant/ai-assistant-shell-overlay-implementation|AI Assistant Shell Overlay Implementation]]
- [[modules/ai-assistant/ai-assistant-sql-service-hana-issue|AI Assistant SQL Service HANA Issue]]
- [[modules/ai-assistant/ai-assistant-ux-design|AI Assistant UX Design]]
- [[modules/ai-assistant/ai-assistant-ux-gap-analysis|AI Assistant UX Gap Analysis]]
- [[modules/ai-assistant/ai-assistant-reality-check-2026-02-15|AI Assistant Reality Check 2026-02-15]]
- [[modules/ai-assistant/pydantic-ai-sap-ai-core-integration|Pydantic AI SAP AI Core Integration]]
- [[modules/ai-assistant/sap-ai-core-pydantic-ai-integration|SAP AI Core Pydantic AI Integration]]

#### Knowledge Graph Module
- [[modules/knowledge-graph/knowledge-graph-v2-architecture-proposal|Knowledge Graph v2 Architecture Proposal]]
- [[modules/knowledge-graph/knowledge-graph-v2-api-design|Knowledge Graph v2 API Design]]
- [[modules/knowledge-graph/knowledge-graph-v2-services-design|Knowledge Graph v2 Services Design]]
- [[modules/knowledge-graph/knowledge-graph-v2-phase-2-complete|Knowledge Graph v2 Phase 2 Complete]]
- [[modules/knowledge-graph/knowledge-graph-v2-phase-5-frontend-architecture|Knowledge Graph v2 Phase 5 Frontend Architecture]]
- [[modules/knowledge-graph/knowledge-graph-v2-feng-shui-audit-2026-02-21|Knowledge Graph v2 Feng Shui Audit 2026-02-21]] - ⚠️ 168 findings
- [[modules/knowledge-graph/knowledge-graph-10k-benchmark-results|Knowledge Graph 10K Benchmark Results]]
- [[modules/knowledge-graph/knowledge-graph-cache-debugging-lessons|Knowledge Graph Cache Debugging Lessons]]
- [[modules/knowledge-graph/knowledge-graph-semantic-enhancement-implementation-plan|Knowledge Graph Semantic Enhancement Plan]] - 4-phase roadmap
- [[modules/knowledge-graph/knowledge-graph-csn-semantic-completeness-analysis|Knowledge Graph CSN Semantic Completeness Analysis]]
- [[modules/knowledge-graph/knowledge-graph-ai-assistant-requirements|Knowledge Graph AI Assistant Requirements]]

#### Data Products Module
- [[modules/data-products/data-products-v2-di-refactoring-proposal|Data Products v2 DI Refactoring Proposal]]

#### Logger Module
- [[modules/logger/dual-mode-logging-system|Dual-Mode Logging System]]
- [[modules/logger/log-viewer-overlay-implementation|Log Viewer Overlay Implementation]]
- [[modules/logger/logger-to-log-module-rename|Logger to Log Module Rename]]

### Components (20)
- [[Groq API Reference]], [[Groq Documentation Overview]], [[Pydantic AI Framework]]
- [[Gu Wu API Contract Testing Foundation]], [[API First Contract Testing Methodology]]
- [[CSN Investigation Findings]], [[HANA Connection Module]], [[HANA Connection UI]]
- [[HANA Cloud Setup]], [[HANA Cloud Integration Summary]], [[SAP HANA Graph Engines Comparison]]
- [[SQLite Graph Fallback Solutions]], [[P2P Dashboard Design]], [[P2P Database Creation Workflow]]
- [[App v2 Modular Architecture Plan]], [[Module Categorization Analysis]]
- [[Gu Wu Phase 8 Architecture-Aware E2E Testing]], [[Feng Shui Code Review Agent]]
- [[Frontend Modular Architecture Proposal]]
- [[Eager vs Lazy Loading Best Practices]]
- [[Module Federation Architecture Proposal]]
- [[HIGH-31 Advanced Graph Queries Implementation]] - Phase 3: Analytics API (7 endpoints)
- [[HIGH-46.5 Preview Mode Parser Implementation]] - ⭐ Validation engine (650+ lines, 17 tests)
- [[HIGH-46.6 Preview Mode AI Integration]] - ⭐ AI-powered module spec generation
- [[Feng Shui Preview Mode Validation Results]] - ⭐ 4/4 modules passed (< 1ms validation) (NEW)
- [[HIGH-43 CSS Systematic Remediation Plan]] - 🎨 CSS refactoring roadmap (96 HIGH findings)

### Architecture (30)
- [[Module Federation Standard]] ⭐
- [[Module Isolation Enforcement Standard]] ⭐
- [[Global Context State Management Patterns]] - ⭐ Pub/Sub, Redux, Context API (industry standards)
- [Quality Ecosystem](quality-ecosystem/) - Feng Shui, Gu Wu, Shi Fu docs
- [[Configuration-Based Dependency Injection]], [[Repository Pattern Modular Architecture]]
- [[AI Assistant Repository Pattern Implementation Guide]] - ⚠️ CRITICAL fix ready to execute
- [[Feng Shui Repository Pattern Guide]], [[Cosmic Python Patterns]]
- [[DDD Patterns Quality Ecosystem Integration]], [[Shi Fu Meta-Architecture Intelligence]]
- [[DataSource Architecture Refactoring Proposal]], [[Knowledge Graph v2 Architecture Proposal]]
- [[Knowledge Graph v2 API Design]], [[Knowledge Graph v2 Services Design]]
- [[Agentic Workflow Patterns]], [[CSN HANA Cloud Solution]]
- [[Infrastructure vs Feature Modules]], [[Modular Architecture]], [[Modular Architecture Evolution]]
- [[Modular Architecture Implementation]], [[GoF Design Patterns Analysis]], [[GoF Design Patterns Guide]]
- [[Gu Wu Phase 3 AI Capabilities]], [[Gu Wu Phase 4 Pattern Integration]]
- [[Gu Wu Phase 4 Complete Implementation]], [[Gu Wu Phase 6 Reflection]], [[Gu Wu Phase 7 Intelligence]]
- [[Feng Shui Agentic Enhancement Plan]], [[Feng Shui Phase 4.15 Implementation Plan]]
- [[Feng Shui Phase 4-17 Complete]], [[Shi Fu Master Teacher Design]]
- [[InputListItem Control Decision]], [[Data Products in HANA Cloud]], [[P2P Workflow Architecture]]

### Guidelines (16)
- [[SAP UI5 Common Pitfalls]], [[Frontend Modular Architecture Proposal]]
- [[SAP Fiori Design Standards]], [[Testing Standards]], [[Comprehensive Testing Strategy]]
- [[Automated UI Testing]], [[Module Error Handling Pattern]], [[Module Quality Gate]]
- [[Systematic Debugging Strategy]], [[Graph Visualization Strategy]]
- [[Feng Shui Phase 5 File Organization]], [[Feng Shui Separation of Concerns]]
- [[Feng Shui vs Gu Wu Separation]], [[Feng Shui GoF Pattern Checks]]
- [[Feng Shui Pre-Commit Hook Documentation]], [[Log Integration Proposal]]
- [[Dual-Mode Logging System]], [[Log Viewer Overlay Implementation]], [[Log Dependency Injection Pattern]]

### Requirements (1)
- [[BDC AI Core Integration Requirements]]

### Guides (1)
- [[Pytest Windows Setup Guide]]

---

## 🔍 How to Use

**For AI**:
1. Check knowledge graph FIRST (`search_nodes`)
2. Browse categories above for relevant docs
3. Click [[links]] to read full documents
4. Use quality-ecosystem/ hub for tool docs

**For Developers**:
1. Start with "Most Important" section
2. Navigate via [[wikilinks]]
3. Check quality-ecosystem/ for tools
4. Review guidelines before coding

---

## 📊 Statistics

| Category | Count | Status |
|----------|-------|--------|
| Components | 20 | ✅ Active |
| Architecture | 30 | ✅ Active |
| Guidelines | 16 | ✅ Active |
| Requirements | 1 | ✅ Active |
| Guides | 1 | ✅ Active |
| **Total** | **68** | **✅ Maintained** |

---

## 🎉 Recent Updates (Last 5)

### 2026-02-22 (12:56 AM) - Feng Shui Preview Mode Validation Complete ✅
- [[Feng Shui Preview Mode Validation Results]] - All 4 production modules tested and passed
- **Results**: ai_assistant ✅, data_products_v2 ✅, logger ✅, knowledge_graph_v2 ✅
- Zero violations detected across all modules (Module Federation Standard v1.0 compliance)
- **Performance**: < 1ms per module (suitable for pre-commit hooks)
- **Insight**: 29.2% confidence score consistent → opportunity to enhance design documents
- Proven: Design-first validation catches issues 60-300x faster than runtime testing

### 2026-02-22 (12:36 AM) - HIGH-43 Created: CSS Systematic Remediation Plan 🎨
- [[HIGH-43 CSS Systematic Remediation Plan]] - Comprehensive 6-phase CSS refactoring roadmap
- Analyzed 96 HIGH Feng Shui findings (85 !important overrides, 11 color violations)
- **Phases**: SAP Fiori tokens → !important removal → WCAG compliance → theming → motion → docs
- Total effort: 6 hours. Target: Zero !important overrides, 100% WCAG compliant

### 2026-02-21 (11:48 PM) - HIGH-46.6 Complete: Feng Shui Preview AI Integration ✅
- [[HIGH-46.6 Preview Mode AI Integration]] - AI-powered module spec generation (650+ lines)
- GPT-4o integration for intelligent module scaffolding
- Natural language → complete module.json + file structure
- 19 comprehensive tests (0.82s execution time)
- Example integration with validation

### 2026-02-21 (12:05 PM) - HIGH-31 Complete: Knowledge Graph Phase 3 ✅
- [[HIGH-31 Advanced Graph Queries Implementation]] - 7 analytics endpoints (PageRank, Centrality, Communities, etc.)
- [[Knowledge Graph v2 Feng Shui Audit 2026-02-21]] - Comprehensive quality audit (168 findings)
- [[Knowledge Graph Semantic Enhancement Implementation Plan]] - 4-phase enhancement roadmap
- [[Knowledge Graph CSN Semantic Completeness Analysis]] - Semantic metadata analysis
- All 13 API contract tests passing; implementation doc + audit complete

### 2026-02-21 (Morning) - Knowledge Graph Semantic Enhancement ✅
- [[AI Assistant Implementation Status 2026-02-21]] - Module status analysis (backend ✅, frontend gaps)
- Semantic annotation extraction complete (CSN metadata integration)
- CSN association integration complete (136 explicit relationships)

### 2026-02-15 (4:50 PM) - AI Assistant Reality Check ⚠️
- [[AI Assistant Reality Check 2026-02-15]] - Module audit reveals 5 failing tests
- Documentation out of sync with implementation
- 60-70% complete vs "Phases 1-4 Complete ✅" claimed
- Action plan: Fix 5 critical issues (2-3 hours)

### 2026-02-15 (3:05 PM) - v5.0 Released ⭐
- ModuleFederationAgent complete (8th Feng Shui agent)
- Feng Shui README updated to v4.7
- Clean version baseline established

### 2026-02-14
- [[Eager vs Lazy Loading Best Practices]] - Industry standards
- [[Knowledge Graph 10K Benchmark Results]] - Performance data

### 2026-02-08
- [[Knowledge Graph v2 Phase 2 Complete]] - Services layer

### 2026-02-07
- [[Module Federation Architecture Proposal]] - BFF pattern
- [[Frontend Modular Architecture Proposal]] - Micro-frontend

**Full History**: See `docs/knowledge/CHANGELOG.md` (archived updates)

---

## 📁 Related Resources

- Root: `README.md` - Project overview
- Tracker: `PROJECT_TRACKER.md` - Current tasks
- Standards: `.clinerules` - Development rules
- Tools: `tools/fengshui/`, `tools/guwu/`, `tools/shifu/`

---

**Philosophy**: "Navigate quickly, read deeply, understand thoroughly"