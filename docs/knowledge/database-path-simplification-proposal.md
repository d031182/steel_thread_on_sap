# Database Path Simplification Proposal

**Date**: 2026-02-23  
**Status**: PROPOSED  
**Priority**: MEDIUM (Technical Debt)

## Problem Statement

The current `core/services/database_path_resolvers.py` (400+ lines) is **over-engineered** and creates unnecessary complexity:

### Issues

1. **Redundant Configuration**: Database paths are defined in TWO places:
   - `module.json` (single source of truth)
   - `database_path_resolvers.py` (manual mapping that can drift)

2. **Strategy Pattern Overkill**: 5 different resolver strategies for a simple path lookup
   - `ModuleOwnedPathResolver`
   - `SharedPathResolver`
   - `ConfigurablePathResolver`
   - `TemporaryPathResolver`
   - Factory class

3. **Error-Prone**: Manual mapping can get out of sync with module.json
   ```python
   DATABASE_NAMES = {
       'knowledge_graph_v2': 'p2p_graph.db',
       'data_products_v2': 'p2p_data.db',
       # What if module.json changes? This won't know!
   }
   ```

4. **Limited Usage**: Only used in 3 files (`server.py`, 2 rebuild scripts)

## Proposed Solution

**Replace with Convention-over-Configuration**: Read paths directly from `module.json`

### New Implementation (20 lines vs 400+)

```python
"""
Database Path Utilities

Simple convention-over-configuration approach: read paths from module.json
"""
import json
import os
from pathlib import Path
from typing import Optional

def get_module_database_path(module_name: str) -> str:
    """
    Get database path from module's module.json.
    
    Args:
        module_name: Module name (e.g., 'data_products_v2')
        
    Returns:
        Database path from module.json
        
    Raises:
        FileNotFoundError: If module.json doesn't exist
        KeyError: If database.path not in module.json
    """
    module_json_path = Path(f"modules/{module_name}/module.json")
    
    with open(module_json_path, 'r', encoding='utf-8') as f:
        module_config = json.load(f)
    
    db_path = module_config['database']['path']
    
    # Ensure directory exists
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    return db_path

def resolve_database_path(database_name: str) -> str:
    """
    Resolve database path by name (backward compatibility).
    
    Args:
        database_name: Database name ('p2p_data', 'p2p_graph', 'logs')
        
    Returns:
        Database path
    """
    # Simple mapping (for backward compatibility with scripts)
    name_to_module = {
        'p2p_data': 'data_products_v2',
        'p2p_graph': 'knowledge_graph_v2',
        'logs': 'logger'
    }
    
    module_name = name_to_module.get(database_name, database_name)
    return get_module_database_path(module_name)
```

## Benefits

1. **Single Source of Truth**: Database paths only in `module.json`
2. **Self-Documenting**: Path is in module configuration
3. **Less Code**: 20 lines vs 400+ lines
4. **Type-Safe**: No string mapping to maintain
5. **Automatic**: Module changes automatically reflected

## Migration Plan

### Phase 1: Create Simplified Version
- [x] Document proposal
- [ ] Create `core/services/database_utils.py` (new simplified version)
- [ ] Add unit tests

### Phase 2: Update Consumers
- [ ] Update `server.py`
- [ ] Update rebuild scripts

### Phase 3: Cleanup
- [ ] Delete `core/services/database_path_resolvers.py` (400+ lines)
- [ ] Delete `core/services/database_path_resolver_factory.py`
- [ ] Delete `core/interfaces/database_path_resolver.py`
- [ ] Archive related tests

## Backward Compatibility

The `resolve_database_path()` function provides backward compatibility for existing scripts that use:
```python
from core.services.database_path_resolvers import resolve_database_path
```

They can simply change to:
```python
from core.services.database_utils import resolve_database_path
```

## Risk Assessment

**Risk**: LOW
- Only 3 files use the current resolvers
- Simple find/replace migration
- Tests cover the change

**Effort**: 1-2 hours

## Related Documents

- [[Module Federation Standard]] - Defines module.json structure
- `modules/*/module.json` - Contains database paths

---

**Recommendation**: Proceed with simplification. The Strategy Pattern adds no value here - it's a simple path lookup that should read from module.json convention.