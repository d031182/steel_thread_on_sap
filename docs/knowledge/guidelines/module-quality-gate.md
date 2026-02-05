# Module Quality Gate

**Purpose**: THE SINGLE validation tool - all modules must pass before deployment  
**Location**: `tools/fengshui/module_quality_gate.py`  
**Related**: [[Modular Architecture]], [[Module Error Handling Pattern]]

---

## Overview

The Module Quality Gate is **THE authoritative validation tool** for all modules. Every module MUST pass all checks before going live.

### Key Principle

**One validation tool to rule them all** - No redundant check scripts allowed.

---

## Usage

```bash
# Check a specific module (THE authoritative validation)
python tools/fengshui/module_quality_gate.py <module_name>

# Example
python tools/fengshui/module_quality_gate.py knowledge_graph
```

### Exit Codes

- **0** = PASSED - Module ready for deployment
- **1** = FAILED - Module has errors, fix before deployment

---

## Checks Performed

### Critical (ERROR-level)
- ✅ module.json exists and is valid JSON
- ✅ Backend blueprint properly configured (if backend/ exists)
- ✅ Blueprint exported in backend/__init__.py
- ✅ No DI violations (no direct .connection, .service access)
- ✅ Module registered in app.py (if has backend)

### Recommended (WARNING-level)
- ⚠️ README.md exists with documentation
- ⚠️ Comprehensive module.json metadata
- ⚠️ Integration documentation provided

---

## Integration

**MANDATORY**: Run before ANY module goes live:

1. **Pre-commit hook** (recommended)
2. **CI/CD pipeline step** (required)
3. **Manual check before PR** (minimum)

### Rule

**Module MUST exit 0 (PASSED) before deployment**

---

## Architecture Decision

**Why one quality gate?**

1. **Single source of truth** - No confusion about which validation to run
2. **Consistency** - All modules validated the same way
3. **Maintainability** - One tool to update, not many
4. **No redundancy** - Eliminated check_module_blueprints.py (was duplicate)

**History**:
- **Previous**: Multiple check scripts scattered across codebase
- **2026-01-30**: Consolidated to single quality gate
- **Current**: This is THE validation tool

---

## See Also

- [[Modular Architecture]] - Module structure standards
- [[Module Error Handling Pattern]] - Error handling in modules
- `.clinerules` - Development standards requiring quality gate