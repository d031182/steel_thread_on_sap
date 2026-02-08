# Gu Wu (顾武) Testing Framework

**Philosophy**: "Attending to martial affairs with discipline and continuous improvement"

---

## 🎯 Overview

Gu Wu is a self-healing, self-optimizing testing framework that integrates with Feng Shui for automated E2E test generation.

---

## 🔧 Feng Shui + Gu Wu Integration (Phase 8.3)

### Complete Pipeline

```
Feng Shui Multi-Agent Analysis
         ↓
    JSON Report
         ↓
Gu Wu Test Generator
         ↓
    pytest Tests
         ↓
    Execution
```

### CLI Usage

```bash
# Run complete pipeline (Feng Shui → Gu Wu → pytest)
python -m tools.guwu.feng_shui_integration <module_name>

# Example:
python -m tools.guwu.feng_shui_integration knowledge_graph_v2

# Generate tests without running them:
python -m tools.guwu.feng_shui_integration knowledge_graph_v2 --no-run
```

### What It Does

1. **Feng Shui Analysis**: Runs multi-agent orchestrator on module
2. **Report Generation**: Saves JSON report (`feng_shui_report_<module>.json`)
3. **Test Generation**: Creates pytest file (`tests/e2e/app_v2_modules/test_<module>.py`)
4. **Test Execution**: Runs generated tests (optional)

### Generated Test Structure

Each module gets 5 automated tests:

1. **test_scripts_accessible**: Verifies frontend scripts load via HTTP
2. **test_navigation_consistency**: Validates module.json navigation config
3. **test_interface_compliance**: Checks implementations match interfaces
4. **test_dynamic_loading_compatibility**: Ensures ES6 export compatibility
5. **test_sapui5_rendering_safety**: Validates SAPUI5 rendering patterns

---

## 📊 Benefits

| Metric | Before (Browser) | After (Gu Wu) | Improvement |
|--------|-----------------|---------------|-------------|
| **Speed** | 60-300 seconds | 1-5 seconds | **60-180x faster** |
| **Automation** | Manual clicks | Fully automated | 100% |
| **Repeatability** | Hard to reproduce | pytest rerun | Perfect |
| **CI/CD Ready** | No | Yes | ✅ |

---

## 🧪 Testing the Integration

```bash
# Run integration tests
pytest tests/unit/tools/guwu/test_feng_shui_integration.py -v

# Expected: 10 tests passing
```

---

## 📚 Architecture

- **Integration**: `tools/guwu/feng_shui_integration.py`
- **Base Generator**: `tools/guwu/generators/base_generator.py`
- **App V2 Generator**: `tools/guwu/generators/app_v2_test_generator.py`
- **Tests**: `tests/unit/tools/guwu/test_feng_shui_integration.py`

---

## 🚀 Next Steps

1. **Phase 8.4**: Extend to all 7 pending modules
2. **Phase 8.5**: Add intelligent test evolution (learns from failures)
3. **Phase 8.6**: Integrate into CI/CD pipeline

---

**Status**: ✅ Phase 8.3 COMPLETE (February 8, 2026)