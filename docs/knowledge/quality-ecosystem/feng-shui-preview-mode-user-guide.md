# Feng Shui Preview Mode: User Guide

**Version**: 1.0  
**Created**: 2026-02-22  
**Status**: Production Ready ✅  
**Related**: [[quality-ecosystem/feng-shui-preview-mode-design]], [[implementation-tasks/high-46.5-preview-mode-parser-implementation]], [[implementation-tasks/high-46.6-preview-mode-ai-integration]], [[implementation-tasks/high-46.7-preview-mode-cicd-integration]]

---

## 🎯 What is Preview Mode?

**Preview Mode** is Feng Shui's proactive architecture validation tool that **catches violations during planning** - before any code is written.

### The Problem
Traditional development workflow:
```
Design → Implement → Test → Find Issues → Rework
                                    ↑
                              Expensive (2+ days)
```

### The Solution
Preview Mode workflow:
```
Design → Validate → Fix Design → Implement → Test
           ↑
    Fast (<1s), Cheap (design changes)
```

### Key Benefits
- ⚡ **80%+ violations caught** before coding starts
- 🚀 **< 1 second** validation time
- 💰 **25% time savings** (eliminate rework cycles)
- ✅ **Zero technical debt** from architecture violations

---

## 🚀 Getting Started

### Installation
Preview Mode is included in Feng Shui. No additional installation needed.

```bash
# Verify installation
python -m tools.fengshui.preview --help
```

### Basic Usage

#### 1. Interactive Mode (Recommended for New Modules)

```bash
python -m tools.fengshui.preview
```

You'll be prompted for:
- **Module ID**: `my_new_module` (snake_case)
- **Route**: `/my-new-module` (kebab-case)
- **Factory Name**: `MyNewModuleModule` (PascalCase + Module)
- **Files**: `module.json`, `README.md`
- **Directories**: `backend`, `frontend`, `tests`
- **Backend API**: `/api/my-new-module`
- **Dependencies**: `logger` (optional)

#### 2. Validate Existing Module

```bash
python -m tools.fengshui.preview --module ai_assistant
```

This automatically parses:
- `modules/ai_assistant/module.json`
- `modules/ai_assistant/README.md`

#### 3. Validate Multiple Modules

```bash
python -m tools.fengshui.preview --module ai_assistant --module logger --module data_products_v2
```

---

## 📋 What Gets Validated?

### 1. Naming Conventions ✅

**Module IDs** must be `snake_case`:
```
✅ ai_assistant
✅ data_products_v2
❌ aiAssistant
❌ AIAssistant
```

**Routes** must be `/kebab-case`:
```
✅ /ai-assistant
✅ /data-products
❌ /ai_assistant
❌ /AIAssistant
```

**Factory Names** must be `PascalCase` + `Module`:
```
✅ AIAssistantModule
✅ DataProductsV2Module
❌ AIAssistant
❌ ai_assistant_module
```

**Backend APIs** must be `/api/kebab-case`:
```
✅ /api/ai-assistant
✅ /api/data-products
❌ /api/ai_assistant
```

### 2. Module Structure ✅

**Required Files** (CRITICAL if missing):
- `module.json` - Module metadata
- `README.md` - Module documentation

**Required Directories** (CRITICAL if missing):
- `backend/` - Server-side code
- `frontend/` - Client-side code
- `tests/` - Test files

**Recommended Structure** (HIGH warning if missing):
```
backend/
├── api.py              # Flask Blueprint
├── services/           # Business logic
└── repositories/       # Data access

frontend/
├── module.js           # Factory
├── adapters/           # API client
└── views/              # UI components
```

### 3. Module Isolation 🔴 CRITICAL

**The Golden Rule**: Modules MUST NOT import from other modules directly.

**Violations** (CRITICAL severity):
```python
❌ from modules.data_products_v2 import DataService
❌ from modules.ai_assistant.backend.services import AgentService
```

**Correct Pattern** (Use Dependency Injection):
```python
✅ from core.interfaces.data_product_repository import IDataProductRepository

class MyService:
    def __init__(self, data_repo: IDataProductRepository):
        self.data_repo = data_repo  # Injected
```

**Why This Matters**:
- Cross-module imports create tight coupling
- Changes in one module break another
- Testing becomes impossible (circular dependencies)
- Violates [[Module Federation Standard]]

### 4. Dependency Declaration ⚠️

Dependencies in `module.json` should be **minimal and justified**.

**Good Dependencies** (Infrastructure):
```json
{
  "dependencies": ["logger"]  // ✅ OK - logging is infrastructure
}
```

**Warning Dependencies** (Business Logic):
```json
{
  "dependencies": ["data_products_v2"]  // ⚠️ Consider DI instead
}
```

**Why This Matters**:
- Each dependency increases coupling
- Makes module harder to test/reuse
- Suggests architectural issue

---

## 📊 Understanding Results

### Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FENG SHUI PREVIEW VALIDATION RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Naming conventions validated
✓ Module structure validated
✗ Module isolation validated

FINDINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[CRITICAL] Cross-module import detected
Location: Dependencies declaration
Message: Direct dependency on 'data_products_v2' may cause tight coupling
Recommendation: Use core/interfaces/ with Dependency Injection instead

[HIGH] Missing recommended directory
Location: Module structure
Message: Directory 'backend/services/' not found
Recommendation: Add services layer for business logic

Status: VIOLATIONS FOUND ❌
Next Steps: Review CRITICAL findings and update design before implementation
```

### Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| **CRITICAL** | Architecture violation | **MUST FIX** before implementation |
| **HIGH** | Quality issue | **SHOULD FIX** before implementation |
| **MEDIUM** | Improvement opportunity | Can proceed, but consider fixing |
| **LOW** | Suggestion | Optional enhancement |

### Exit Codes

| Code | Meaning | CI/CD Action |
|------|---------|--------------|
| `0` | ✅ All passed | Proceed to implementation |
| `1` | ⚠️ Warnings | Proceed with caution |
| `2` | ❌ CRITICAL/HIGH | Block until fixed |
| `3` | 🔥 Engine error | Check logs |

---

## 🔧 Advanced Usage

### JSON Spec Mode

Create a `module_spec.json` file:

```json
{
  "module_id": "my_module",
  "route": "/my-module",
  "factory_name": "MyModuleModule",
  "files": ["module.json", "README.md"],
  "directories": ["backend", "frontend", "tests"],
  "backend_api": "/api/my-module",
  "dependencies": ["logger"],
  "description": "My module description"
}
```

Then validate:

```bash
python -m tools.fengshui.preview --spec module_spec.json
```

### JSON Output (for CI/CD)

```bash
python -m tools.fengshui.preview --module ai_assistant --json
```

Output:
```json
{
  "module_id": "ai_assistant",
  "status": "VIOLATIONS_FOUND",
  "findings": [
    {
      "severity": "CRITICAL",
      "validator": "IsolationValidator",
      "message": "Cross-module import detected",
      "location": "Dependencies declaration",
      "recommendation": "Use core/interfaces/ with Dependency Injection"
    }
  ],
  "exit_code": 2
}
```

### Confidence Levels

When validating existing modules, Preview Mode shows **confidence levels**:

```
⚠️ Confidence: 42.9% (3/7 sources parsed)
- ✓ module.json found
- ✓ README.md found
- ✓ backend/ directory found
- ✗ API endpoints (not documented)
- ✗ Test structure (not found)
```

**What This Means**:
- **> 70%**: High confidence (reliable validation)
- **40-70%**: Medium confidence (some info missing)
- **< 40%**: Low confidence (add more documentation)

**How to Improve**:
- Add missing files (`module.json`, `README.md`)
- Document API endpoints in README
- Create test files structure

---

## 🎓 Workflow Integration

### Step-by-Step: Adding a New Feature

#### Phase 1: Design (Planning)

1. **Write Design Doc**
   ```markdown
   # Feature: User Authentication
   
   ## Module Structure
   - ID: `auth_service`
   - Route: `/auth-service`
   - Factory: `AuthServiceModule`
   
   ## API Endpoints
   - POST /api/auth-service/login
   - POST /api/auth-service/logout
   - GET /api/auth-service/verify
   
   ## Dependencies
   - logger (for audit logging)
   ```

2. **Validate Design** ⭐ NEW STEP
   ```bash
   python -m tools.fengshui.preview --module auth_service
   ```

3. **Fix Any Violations**
   - CRITICAL → Must fix
   - HIGH → Should fix
   - MEDIUM/LOW → Consider fixing

#### Phase 2: Implementation

4. **Write API Contract Tests**
   ```python
   @pytest.mark.api_contract
   def test_login_endpoint():
       response = requests.post(url, json=credentials)
       assert response.status_code == 200
   ```

5. **Implement APIs**
   - Backend: Flask routes
   - Frontend: Metadata endpoint

6. **Test APIs**
   ```bash
   pytest tests/auth_service/ -v -m api_contract
   ```

7. **Build UX** (only after APIs stable)

### Integration with Existing Workflow

Preview Mode fits into the **API-First Development** workflow:

```
1. Design API Contracts
2. ⭐ Validate with Preview Mode (NEW)
3. Write API Contract Tests
4. Implement APIs
5. Test APIs via requests (<1s)
6. Verify APIs Stable
7. Build UX
```

---

## 🔗 CI/CD Integration

### Pre-commit Hook

**Setup**:
```bash
cp scripts/pre-commit-preview.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**What It Does**:
- Validates modified modules before commit
- Blocks commit if CRITICAL/HIGH violations
- Shows clear error messages

**Example**:
```bash
$ git commit -m "Add feature"

Running Feng Shui Preview...
[CRITICAL] Module isolation violation in auth_service
❌ Commit blocked. Fix violations first.
```

### GitHub Actions

See `.github/workflows/preview-validation.yml` for automated PR validation.

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found"

**Symptom**:
```
Error: Module 'my_module' not found in modules/
```

**Solution**:
Ensure directory exists: `modules/my_module/`

### Issue: "Invalid module.json"

**Symptom**:
```
Error: Invalid JSON in modules/my_module/module.json
```

**Solution**:
```bash
# Validate JSON syntax
python -m json.tool modules/my_module/module.json
```

### Issue: "Low confidence warning"

**Symptom**:
```
⚠️ Confidence: 28.6% (2/7 sources parsed)
```

**Solution**:
- Add `module.json` with complete metadata
- Add `README.md` with structure documentation
- Document API endpoints
- Create test file structure

### Issue: "False positive on isolation"

**Symptom**:
```
[CRITICAL] Cross-module import detected
Dependencies: ["data_products_v2"]
```

**Why It's Flagged**:
Direct module dependencies often indicate tight coupling.

**Solutions**:
1. **Use Dependency Injection** (preferred):
   ```python
   # Define interface in core/interfaces/
   from core.interfaces.data_product_repository import IDataProductRepository
   ```

2. **Justify in Design Doc**:
   ```markdown
   ## Dependencies
   - data_products_v2: Required for [specific reason]
     Using DI pattern via core/interfaces/
   ```

---

## 💡 Best Practices

### 1. Validate Early
Run Preview Mode during **initial design phase**, not after implementation starts.

### 2. Fix CRITICAL Violations Immediately
Don't proceed to implementation with CRITICAL findings.

### 3. Document Decisions
Update `README.md` with:
- Module structure
- API endpoints
- Design decisions
- Dependency justifications

### 4. Use Pre-commit Hooks
Automate validation to prevent violations from being committed.

### 5. Integrate with Planning
Make Preview Mode part of your **standard planning workflow**.

---

## 📚 Related Documentation

### Core Standards
- **[[Module Federation Standard]]** - Official module architecture
- **[[Module Isolation Enforcement Standard]]** - Isolation rules
- **[[Gu Wu API Contract Testing Foundation]]** - Testing methodology
- **[[API-First Contract Testing Methodology]]** - Complete development guide

### Implementation Details
- **[[quality-ecosystem/feng-shui-preview-mode-design]]** - Original design document
- **[[implementation-tasks/high-46.5-preview-mode-parser-implementation]]** - Document parser technical details
- **[[implementation-tasks/high-46.6-preview-mode-ai-integration]]** - AI integration hooks
- **[[implementation-tasks/high-46.7-preview-mode-cicd-integration]]** - CI/CD setup guide

### Quality Tools
- **Feng Shui** - Full architecture analysis
- **Gu Wu** - API contract testing
- **Shi Fu** - Ecosystem health monitoring

---

## 🎯 Success Metrics

### Time Savings
- **Without Preview Mode**: 8+ days (design → implement → audit → rework)
- **With Preview Mode**: 6+ days (design → validate → implement)
- **Savings**: 2+ days (25% reduction)

### Quality Improvements
- **Planning Phase**: 80%+ violations caught (low fix cost)
- **Implementation Phase**: 10-15% slip through (medium fix cost)
- **Post-Merge Phase**: 5-10% edge cases (high fix cost)

### Developer Experience
- **Instant Feedback**: < 1 second validation
- **Clear Guidance**: Actionable recommendations with examples
- **Confidence**: Design validated before coding starts

---

## 🚀 Next Steps

1. **Try it now**: `python -m tools.fengshui.preview`
2. **Validate existing module**: `python -m tools.fengshui.preview --module ai_assistant`
3. **Set up pre-commit hook**: Copy from `scripts/pre-commit-preview.py`
4. **Read design doc**: [[quality-ecosystem/feng-shui-preview-mode-design]]
5. **Check technical README**: `tools/fengshui/preview/README.md`

---

**Questions?** See [[quality-ecosystem/feng-shui-preview-mode-design]] or the technical README at `tools/fengshui/preview/README.md`