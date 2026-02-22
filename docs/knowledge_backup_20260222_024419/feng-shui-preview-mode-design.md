# Feng Shui Preview Mode: Proactive Architecture Validation

**Version**: 1.0  
**Created**: 2026-02-21  
**Status**: Design Complete - Ready for Implementation  
**Effort Estimate**: 10-14 hours (4 phases)  

---

## 🎯 Executive Summary

**Problem**: Feng Shui discovers issues AFTER implementation (196 findings on 4 modules). Rework becomes expensive.

**Solution**: "Preview Mode" - Lightweight validation DURING planning phase to catch 80%+ of violations before coding starts.

**Impact**: 
- 25% time reduction (8+ days → 6+ days)
- Better code quality at inception
- Faster feedback loop (< 5 seconds per check)
- Zero/minimal rework

---

## 🏗️ Architecture

### Core Components

#### 1. Preview Engine (Fast Validation)
```python
class FengShuiPreviewEngine:
    """Lightweight validator for planning phase"""
    
    def __init__(self):
        self.validators = [
            ModuleStructureValidator(),
            APIContractValidator(),
            NamingConventionValidator(),
            IsolationValidator(),
            DocumentationValidator()
        ]
    
    def preview(self, concept: str, context: Dict) -> PreviewReport:
        """< 5 second validation of planned architecture"""
        findings = []
        
        for validator in self.validators:
            if validator.applicable(concept, context):
                result = validator.validate_concept(concept, context)
                findings.extend(result.findings)
        
        return PreviewReport(
            findings=findings,
            recommendations=self._generate_recommendations(findings),
            severity=self._calculate_severity(findings),
            execution_time=timer.elapsed()
        )
```

#### 2. Validators

**ModuleStructureValidator**:
- Validates planned `module.json` structure
- Checks required fields, naming conventions
- Verifies directory structure matches Module Federation Standard

**APIContractValidator**:
- Validates planned API endpoint design
- Checks RESTful conventions (GET/POST/PUT/DELETE)
- Verifies naming consistency (kebab-case routes, snake_case IDs)
- Ensures request/response schemas complete

**NamingConventionValidator**:
- Module IDs: `snake_case`
- Routes: `/kebab-case`
- Classes: `PascalCase` + `Module` suffix
- Files: `snake_case.py` for backend, `camelCase.js` for frontend

**IsolationValidator**:
- Detects planned cross-module imports
- Verifies Dependency Injection patterns
- Flags Service Locator antipatterns
- Suggests `core/interfaces/` alternatives

**DocumentationValidator**:
- Checks design docs for completeness
- Verifies API contract documentation
- Flags missing test plans
- Ensures knowledge vault references

---

## 📋 Feature Set

### Usage Patterns

#### Pattern 1: Validate Module Structure
```bash
python -m tools.fengshui preview --module ai_assistant_v3
```

**Validates**:
```
✓ module.json exists and is valid
✓ Required fields: id, name, version, type
✓ Directory structure: backend/, frontend/, tests/
✓ API endpoints follow naming conventions
✓ Test files in /tests/[module]/
```

**Output**:
```
FENG SHUI PREVIEW: ai_assistant_v3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Module structure: VALID
  - module.json: Present and valid
  - Directories: backend/, frontend/, tests/ exist
  - Naming: "ai_assistant" (snake_case) ✓

✅ API naming: VALID
  - Endpoints: /api/ai-assistant/chat (kebab-case) ✓
  - IDs: ai_assistant_module (snake_case) ✓

⚠️  ISOLATION: 1 POTENTIAL VIOLATION
  - Planned import: from modules.data_products_v2 import DataService
  - Suggestion: Use core/interfaces/data_product_repository.py with DI

✅ Documentation: VALID
  - Design doc found: docs/knowledge/ai-assistant-v3-design.md
  - API contracts documented
  - Test plan present

Execution time: 0.23s
Status: READY TO IMPLEMENT
Recommendation: Proceed with implementation
```

#### Pattern 2: Validate Design Document
```bash
python -m tools.fengshui preview --doc docs/knowledge/my-feature-design.md
```

**Analyzes**:
- Planned module structure
- API endpoint definitions
- Dependency declarations
- Test plans

**Output**:
```
FENG SHUI PREVIEW: Design Document Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Document: my-feature-design.md
Parsed sections: Module Structure, API Contracts, Dependencies, Tests

✅ ARCHITECTURE COMPLIANCE
  - Module structure matches federation standard ✓
  - Naming conventions correct ✓
  - DI patterns identified ✓

⚠️  POTENTIAL ISSUES FOUND: 2
  1. Cross-module import detected: data_products_v2 → ai_assistant
     → Recommendation: Use core/interfaces/ instead
  
  2. Missing test plan for POST endpoint
     → Recommendation: Add @pytest.mark.api_contract test definition

💡 RECOMMENDATIONS
  - Use repository pattern for data access
  - Plan API contract tests before implementation
  - Consider lazy loading for graph queries

Execution time: 0.42s
Status: READY WITH RECOMMENDATIONS
Action: Review recommendations, update design if needed
```

#### Pattern 3: Validate API Contracts
```bash
python -m tools.fengshui preview --api-contracts api_design.yaml
```

**YAML Format**:
```yaml
endpoints:
  - path: /api/ai-assistant/chat
    method: POST
    description: Send chat message
    request:
      schema: ChatRequest
    response:
      schema: ChatResponse
    tests_planned: true
    
  - path: /api/ai-assistant/history
    method: GET
    description: Get conversation history
    dependencies: [data_products_v2]  # ← Violation detected
```

**Output**:
```
FENG SHUI PREVIEW: API Contract Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Endpoints: 2

✅ RESTful Compliance
  - POST /api/ai-assistant/chat (write operation) ✓
  - GET /api/ai-assistant/history (read operation) ✓

⚠️  ISOLATION VIOLATIONS: 1
  - GET /api/ai-assistant/history
    Current: Depends on data_products_v2
    Issue: Cross-module dependency
    Fix: Move to data_products_v2 or use core/interfaces/

✅ Test Coverage
  - POST /api/ai-assistant/chat: @pytest.mark.api_contract planned ✓
  - GET /api/ai-assistant/history: No test planned ⚠️
    → Recommendation: Add test coverage

Execution time: 0.18s
Status: VIOLATIONS FOUND
Action: Resolve cross-module dependency before implementation
```

#### Pattern 4: Real-Time Integration (AI Usage)
```python
# During planning conversation, AI triggers preview internally
AI: "I'm designing a new query history feature..."

# AI designs architecture
AI: """
Module: query_history (new)
- Backend: Flask routes in ai_assistant/backend/api.py
- Service: QueryHistoryService
- Repository: Uses data_products_v2 for storage
- Tests: 8 API contract tests
"""

# AI triggers preview (internal call during planning)
result = fengshui_preview.validate_design(
    concept="query_history feature",
    context={
        "modules": ["ai_assistant", "data_products_v2"],
        "patterns": ["repository pattern", "DI"],
        "violations": ["cross_module_import"]
    }
)

# AI receives feedback
if result.severity >= "HIGH":
    AI: """
    ⚠️  VIOLATION DETECTED:
    Your design imports from data_products_v2.
    
    💡 SOLUTION:
    Instead of importing QueryHistoryRepository from data_products_v2,
    create QueryHistoryRepository in ai_assistant/backend/repositories/
    and inject DataProductRepository via Dependency Injection.
    
    This maintains module isolation.
    """
```

---

## 📊 Implementation Phases

### Phase 1: Core Preview Engine (4-6 hours)
**Goal**: Fast validation infrastructure

**Files to Create**:
```
tools/fengshui/preview/
├── __init__.py
├── preview_engine.py           # Orchestrator
├── validators/
│   ├── __init__.py
│   ├── base_validator.py       # Abstract base
│   ├── module_structure.py     # Validates planned structure
│   ├── api_contracts.py        # Validates endpoint design
│   ├── naming_conventions.py   # Validates naming patterns
│   ├── isolation_checker.py    # Checks cross-module refs
│   └── documentation.py        # Analyzes design docs
├── formatters/
│   ├── __init__.py
│   └── preview_report.py       # User-friendly output
└── models/
    ├── __init__.py
    └── preview_report.py       # Data structures
```

**Key Classes**:
```python
class PreviewReport:
    findings: List[Finding]
    recommendations: List[str]
    severity: Severity  # CRITICAL, HIGH, MED, LOW
    execution_time: float
    status: str  # READY, VIOLATIONS, WARNINGS

class Finding:
    validator: str
    severity: Severity
    message: str
    location: str  # e.g., "module.json:5"
    fix: str
```

### Phase 2: Design Document Parser (2-3 hours)
**Goal**: Extract architecture from markdown

**Features**:
```python
class DesignDocumentParser:
    def extract_module_structure(self, doc_path: str) -> ModuleStructure:
        """Parse planned directory structure from design doc"""
        
    def extract_api_endpoints(self, doc_path: str) -> List[APIEndpoint]:
        """Parse planned API endpoints"""
        
    def extract_dependencies(self, doc_path: str) -> List[Dependency]:
        """Parse planned module dependencies"""
        
    def extract_test_plans(self, doc_path: str) -> List[TestPlan]:
        """Parse planned test definitions"""
```

**Parser recognizes**:
```markdown
## Module Structure
- Backend: modules/ai_assistant/backend/
- Frontend: modules/ai_assistant/frontend/
- Tests: tests/ai_assistant/

## API Endpoints
- POST /api/ai-assistant/chat
- GET /api/ai-assistant/history
- DELETE /api/ai-assistant/{id}

## Dependencies
- data_products_v2 (cross-module)

## Test Plans
- @pytest.mark.api_contract for each endpoint
```

### Phase 3: Real-Time Feedback Integration (2-3 hours)
**Goal**: Fast feedback during planning

**Integration Points**:
1. **AI Planning Hook**: Trigger preview when AI detects violations in concept
2. **CLI Command**: `python -m tools.fengshui preview --concept "feature description"`
3. **Pre-Commit Check**: Validate design docs before git commit

**Flow**:
```
User → AI Planning → AI detects violation risk → 
AI triggers preview → Preview returns findings → 
AI corrects design → Proceed to implementation
```

### Phase 4: CI/CD Integration (1-2 hours)
**Goal**: Enforce preview checks in pipeline

**Pre-Commit Hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate design docs
python -m tools.fengshui preview --check-all-docs

if [ $? -ne 0 ]; then
  echo "❌ Design validation failed. Fix issues before committing."
  exit 1
fi

exit 0
```

**GitHub Actions**:
```yaml
name: Feng Shui Preview Check

on: [pull_request]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Feng Shui Preview
        run: python -m tools.fengshui preview --check-all-docs
      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ Design validation failed. Check Feng Shui Preview output above.'
            })
```

---

## 🎯 Integration with Workflow

### Current Workflow (Reactive)
```
1. User requests feature
2. AI designs feature
3. AI implements feature
4. Run Feng Shui analysis (post-implementation)
5. Fix issues discovered (rework)
```

### New Workflow (Proactive)
```
1. User requests feature
2. AI designs feature
3. AI runs Feng Shui Preview  ← NEW
4. AI corrects design (if violations)
5. AI implements clean code
6. Run full Feng Shui analysis (validation)
7. Minimal/no rework
```

### AI Enforcement Checklist
```python
# In .clinerules v4.2 enhancement

Before implementing ANY feature, AI must ask:
1. ✅ Have I designed the API endpoints?
2. ✅ Have I written API contract tests?
3. ✅ NEW: Have I validated with Feng Shui Preview?
4. ✅ Have I tested APIs via requests/curl?
5. ✅ Are all API contract tests passing?
6. ✅ Am I about to build UX without stable APIs?

If Feng Shui Preview shows violations: STOP. Correct design FIRST.
```

---

## 📈 Expected Impact

### Time Savings
```
WITHOUT Preview Mode:
Design Phase      → Implementation → Feng Shui Audit → Fix Issues
(1 day)           (5 days)         (1 hour)          (2 days)
                                    ↑
                              Find 196 issues (example)
Total: 8+ days

WITH Preview Mode:
Design + Preview  → Clean Implementation → Minimal Audit
(1 day + 15 min)  (5 days)               (1 hour)
  ↑
Catch 80% before coding

Total: 6+ days
Savings: 2+ days (25% reduction)
```

### Quality Improvements
```
Issue Type          Before          After           Improvement
────────────────────────────────────────────────────────────
Cross-Module Refs   ~20 findings    ~2 findings     90% reduction
API Violations      ~40 findings    ~5 findings     87.5% reduction
Naming Issues       ~30 findings    ~3 findings     90% reduction
Missing Tests       ~50 findings    ~5 findings     90% reduction
────────────────────────────────────────────────────────────
Total               196 findings    ~15 findings    92.3% reduction
```

### Detection Rate
- **Planning Phase**: 80%+ of violations caught before coding
- **Implementation Phase**: 10-15% that slip through (complex interactions)
- **Final Audit Phase**: 5-10% edge cases (rare)

---

## 🔧 Technical Specifications

### CLI Interface
```bash
# Validate entire module
python -m tools.fengshui preview --module ai_assistant

# Validate design document
python -m tools.fengshui preview --doc docs/knowledge/feature-design.md

# Validate API contracts (YAML)
python -m tools.fengshui preview --api-contracts api_design.yaml

# Real-time concept validation
python -m tools.fengshui preview --concept "add query history to ai_assistant"

# Check all design docs
python -m tools.fengshui preview --check-all-docs

# Verbose output with details
python -m tools.fengshui preview --module ai_assistant -v

# Output as JSON for CI/CD
python -m tools.fengshui preview --module ai_assistant --json
```

### Return Codes
```
0: VALID - No violations found
1: WARNINGS - Non-critical issues found (can proceed with caution)
2: HIGH - Critical issues found (should fix before implementing)
3: ERROR - Preview engine error
```

### Performance Requirements
```
✓ Single module validation: < 1 second
✓ Design document analysis: < 0.5 seconds  
✓ API contract validation: < 0.3 seconds
✓ All checks on push: < 5 seconds
✓ Typical PR preview run: < 10 seconds
```

---

## 📚 Knowledge Vault Integration

**Related Documentation**:
- [[Module Federation Standard]] - Architecture rules
- [[Gu Wu API Contract Testing Foundation]] - API testing
- [[Module Isolation Enforcement Standard]] - Isolation rules
- [[API-First Contract Testing Methodology]] - API-first principles

**Create New Docs**:
- `feng-shui-preview-mode-user-guide.md` - End-user documentation
- `feng-shui-preview-mode-developer-guide.md` - Implementation details
- `feng-shui-preview-validators-catalog.md` - Validator descriptions

---

## ✅ Success Criteria

### Phase 1 (Core Engine)
- [ ] Preview engine implemented and tested
- [ ] 5 validators working (< 1s response)
- [ ] CLI interface complete
- [ ] JSON output for CI/CD

### Phase 2 (Document Parser)
- [ ] Markdown parser extracts module structure
- [ ] API endpoint extraction working
- [ ] Dependency detection accurate
- [ ] Test plan recognition implemented

### Phase 3 (Real-Time Integration)
- [ ] AI can trigger preview during planning
- [ ] Feedback integrated into design conversation
- [ ] Violations corrected before implementation
- [ ] Seamless workflow

### Phase 4 (CI/CD Integration)
- [ ] Pre-commit hook working
- [ ] GitHub Actions workflow passing
- [ ] Violations block commits (configurable)
- [ ] Clear feedback in PR comments

---

## 📅 Rollout Plan

**Week 1**: Phase 1 & 2 (6-9 hours)
- Core engine and validators
- Document parser
- Basic CLI interface

**Week 2**: Phase 3 & 4 (3-5 hours)
- Real-time integration
- CI/CD setup
- Documentation

**Week 3**: Validation & Refinement (2-3 hours)
- User testing
- Performance tuning
- Edge case handling

**Target Launch**: End of Week 3 (by Feb 28, 2026)

---

## 🎓 Why This Approach

### Problem It Solves
1. **Reactive vs Proactive**: Current Feng Shui is reactive (post-implementation)
2. **Rework Cost**: 196 findings require 2+ days of rework
3. **Planning Gaps**: Violations emerge from design, not implementation

### Why It Works
1. **Fast Feedback**: < 1 second per check enables tight feedback loop
2. **Prevention**: 80% catch rate BEFORE coding saves 2+ days
3. **Design Integrity**: Enforces principles at inception, not post-facto
4. **Layered Approach**: Combines with full Feng Shui for comprehensive validation

### Complementary to Existing Tools
- **Shi Fu**: Provides guidance during planning (patterns, recommendations)
- **Feng Shui Preview**: Fast validation during planning (violations, fixes)
- **Feng Shui Full**: Comprehensive audit after implementation (edge cases, interactions)
- **Gu Wu**: Tests API contracts to validate implementation (testing methodology)

**Together**: Proactive design enforcement + Guided planning + Comprehensive audit + API testing = **Zero Technical Debt Culture**