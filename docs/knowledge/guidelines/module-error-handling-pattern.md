# Module Error Handling Pattern

**Category:** Guidelines  
**Status:** Production Standard  
**Created:** 2026-01-29  
**Last Updated:** 2026-01-29

## Overview

Industry-standard error handling pattern for module loading in Flask applications. Implements **try-catch-log-reraise** principle to provide full error visibility while maintaining graceful degradation.

## Problem Statement

### Anti-Pattern: Silent Failures ❌

```python
try:
    from modules.something import api
    app.register_blueprint(api)
except Exception as e:
    logger.warning(f"Module not loaded: {e}")
    # Silently continues - error details lost!
```

**Problems:**
- Error details hidden in vague log messages
- No stack trace for debugging
- Wasted hours hunting for root cause
- False sense of success (app runs but broken)

### What We Need ✅

1. **Log full error details** (type, message, stack trace)
2. **Don't hide the error** (propagate it OR document it)
3. **Provide debugging context** (import path, expected blueprint name)
4. **Startup diagnostics** (summary of what loaded/failed)

## Solution: Centralized ModuleLoader

Located: `core/backend/module_loader.py`

### Key Features

1. **Try-Catch-Log-Reraise Pattern**
   ```python
   try:
       # Attempt operation
       module = __import__(import_path, fromlist=[blueprint_name])
   except Exception as e:
       # Log with FULL details
       logger.error(f"Import error: {type(e).__name__}: {e}", exc_info=True)
       # Then re-raise (don't hide it!)
       raise
   ```

2. **Critical vs Non-Critical Modules**
   - `is_critical=True`: Raises exception, stops app
   - `is_critical=False`: Logs warning, app continues

3. **Detailed Error Messages**
   - Error type: `ImportError`, `AttributeError`, etc.
   - Error message: Specific details
   - Stack trace: Full traceback for debugging
   - Context: Module name, import path, blueprint name

4. **Startup Diagnostics**
   ```
   ============================================================
   MODULE LOADING SUMMARY
   ============================================================
   Total modules: 6
   ✓ Loaded: 5
   ⚠ Failed: 1
     - Knowledge Graph: ImportError: No module named 'vis'
   ============================================================
   ```

## Usage

### In app.py

```python
from core.backend.module_loader import ModuleLoader

# Create loader
module_loader = ModuleLoader(app)

# Load modules
module_loader.load_blueprint(
    "Data Products",                    # Human-readable name
    "modules.data_products.backend",    # Import path
    "data_products_api",                # Blueprint variable name
    "/api/data-products",               # API endpoint
    is_critical=False                   # Graceful degradation
)

# Log summary at startup
module_loader.log_startup_summary()
```

### Error Handling Flow

```
1. Attempt Import
   ↓
2. Import Fails
   ↓
3. Catch Exception
   ↓
4. Log Full Details (type, message, stack trace)
   ↓
5. Check is_critical
   ↓
6a. Critical=True → Raise ModuleLoadError (app stops)
6b. Critical=False → Log warning (app continues)
```

## Industry Standards Implemented

### 1. Python Logging Best Practices

- Use `logger.error()` with `exc_info=True` for stack traces
- Include error type: `{type(e).__name__}`
- Provide context: module name, operation details

### 2. Fail-Fast Principle

- Critical components stop execution immediately
- Non-critical components degrade gracefully
- Clear distinction between essential and optional

### 3. Observability

- Startup diagnostics show system health
- Error logs provide debugging context
- Tracking of loaded/failed modules
- Summary statistics available

### 4. Flask Blueprint Patterns

- Consistent registration flow
- Error handling at blueprint level
- Application continues with partial functionality

### 5. Defensive Programming

- Validate inputs (module name, import path)
- Catch specific exceptions (ImportError, AttributeError)
- Provide actionable error messages

## Examples

### Example 1: Non-Critical Module Fails

**Scenario**: Optional API Playground fails to load

**Log Output:**
```
ERROR:core.backend.module_loader:Import error for API Playground: ImportError: No module named 'swagger'
Traceback (most recent call last):
  File "core/backend/module_loader.py", line 75, in load_blueprint
    module = __import__(import_path, fromlist=[blueprint_name])
ImportError: No module named 'swagger'
WARNING:core.backend.module_loader:⚠ API Playground not loaded - application will continue without it

============================================================
MODULE LOADING SUMMARY
============================================================
Total modules: 6
✓ Loaded: 5
⚠ Failed: 1
  - API Playground: ImportError: No module named 'swagger'
============================================================
```

**Result**: Application starts, other modules work, user can use app

### Example 2: Critical Module Fails

**Scenario**: Essential logging module fails

```python
module_loader.load_blueprint(
    "Logging Service",
    "modules.log_manager.backend",
    "logging_api",
    "/api/logs",
    is_critical=True  # App cannot run without logging
)
```

**Log Output:**
```
ERROR:core.backend.module_loader:Import error for Logging Service: ImportError: No module named 'sqlite3'
Traceback (most recent call last):
  ...
ModuleLoadError: Failed to load module 'Logging Service': No module named 'sqlite3'
```

**Result**: Application stops with clear error, developer fixes immediately

### Example 3: All Modules Load Successfully

**Log Output:**
```
INFO:core.backend.module_loader:Loading Feature Manager from modules.feature_manager.backend...
INFO:core.backend.module_loader:✓ Feature Manager registered at /api/features
INFO:core.backend.module_loader:Loading Data Products from modules.data_products.backend...
INFO:core.backend.module_loader:✓ Data Products registered at /api/data-products
...

============================================================
MODULE LOADING SUMMARY
============================================================
Total modules: 6
✓ Loaded: 6
============================================================
```

**Result**: Clean startup, all features available

## Key Principles

### 1. Always Log Before Re-raising

```python
except Exception as e:
    logger.error(f"Error: {type(e).__name__}: {e}", exc_info=True)
    raise  # Don't hide the error!
```

**Why**: Logs persist for analysis, but error still visible

### 2. Provide Context in Error Messages

```python
error_msg = f"Import error for {module_name}: {type(e).__name__}: {e}"
```

**Why**: Developer knows exactly what failed and why

### 3. Use exc_info=True for Stack Traces

```python
logger.error(error_msg, exc_info=True)
```

**Why**: Stack trace shows exact line where failure occurred

### 4. Distinguish Critical vs Optional

```python
is_critical=True   # App cannot function without this
is_critical=False  # App works with reduced functionality
```

**Why**: Appropriate response to different failure types

### 5. Provide Startup Diagnostics

```python
module_loader.log_startup_summary()
```

**Why**: Developer sees system health immediately

## When to Use

### Use ModuleLoader When:
- ✅ Loading Flask blueprints
- ✅ Registering API modules
- ✅ Dynamic plugin loading
- ✅ Optional feature modules
- ✅ Any module that might fail to import

### Don't Use ModuleLoader For:
- ❌ Core Python imports (use normal import)
- ❌ Static dependencies (requirements.txt)
- ❌ Configuration files (use try-catch directly)

## Migration Guide

### Old Pattern

```python
try:
    from modules.something.backend import something_api
    app.register_blueprint(something_api)
    logger.info("Something API registered")
except Exception as e:
    logger.warning(f"WARNING: Something not registered: {e}")
```

### New Pattern

```python
module_loader.load_blueprint(
    "Something",
    "modules.something.backend",
    "something_api",
    "/api/something",
    is_critical=False
)
```

**Improvement**:
- Logs full error details automatically
- Consistent across all modules
- Startup summary included
- Less boilerplate code

## Testing

To test module loading errors:

1. **Simulate import failure**: Temporarily rename module folder
2. **Restart server**: Check logs for error details
3. **Verify**: App continues if `is_critical=False`
4. **Check summary**: Startup diagnostics show failure

Expected log output includes:
- Error type and message
- Full stack trace
- Module name and import path
- Startup summary with ✓/⚠ indicators

## Related Patterns

- [[Try-Catch-Log-Reraise Pattern]] - General error handling
- [[Graceful Degradation]] - Handling optional feature failures
- [[Fail-Fast Principle]] - Critical component handling
- [[Modular Architecture]] - Module system overview

## Lessons Learned

### From Knowledge Graph Bug

**Problem**: Connection error was silently logged but returned empty results
```python
try:
    if not self.conn:
        logger.error("No connection")
        return []  # Silent failure!
```

**Solution**: Log details, then re-raise
```python
try:
    if not self.conn:
        raise RuntimeError("No connection - check DataSource init")
except Exception as e:
    logger.error(f"{type(e).__name__}: {e}", exc_info=True)
    raise  # Don't hide it!
```

**Time Saved**: 90+ minutes of debugging

### User Feedback

> "Shouldn't catch this kind of errors, so that we don't need to search for it?"

**Answer**: Yes! Catch to log details, but re-raise to maintain visibility. Best of both worlds:
- ✅ Error details in logs for later analysis
- ✅ Error visible in console for immediate debugging
- ✅ No silent failures

## Future Enhancements

- [ ] Add health check endpoint showing module status
- [ ] Store module loading history in database
- [ ] Add API endpoint to retry failed modules
- [ ] Module dependency resolution
- [ ] Parallel module loading with dependency ordering

## References

- Python Logging: https://docs.python.org/3/library/logging.html
- Flask Blueprints: https://flask.palletsprojects.com/en/latest/blueprints/
- Fail-Fast: https://en.wikipedia.org/wiki/Fail-fast
- Graceful Degradation: https://en.wikipedia.org/wiki/Fault_tolerance

## Version History

### 1.0.0 (2026-01-29)
- Initial implementation
- ModuleLoader class created
- Integrated into app.py
- Documentation completed

## Author

P2P Development Team  
Based on user feedback and industry best practices