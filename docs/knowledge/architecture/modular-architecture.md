# Modular Architecture

**Type**: Architecture  
**Decision Date**: 2026-01-24  
**Status**: Adopted  
**Created**: 2026-01-25

## Overview

The project uses a modular architecture where all backend services live in self-contained modules under `modules/[module-name]/backend/`.

## Context

Previously, the project used a centralized `backend/services/` directory which became tightly coupled and hard to maintain. We needed a more scalable, plug-and-play architecture.

## Decision

**Adopted Structure**:
```
modules/[module-name]/
├── module.json          # Configuration (required)
├── backend/            # Python backend services
│   ├── __init__.py     # Clean exports
│   └── service.py      # Business logic
├── frontend/           # UI5 frontend (optional)
├── tests/              # Module tests
└── docs/               # Module docs (optional)
```

## Benefits

- ✅ **Self-contained** - Each module is independent
- ✅ **Plug-and-play** - Add/remove by folder
- ✅ **Feature flags** - Toggle via feature_flags.json
- ✅ **Auto-discovery** - Core infrastructure finds modules
- ✅ **Clean imports** - `from modules.my_module.backend import Service`

## Related Components

- [[HANA Connection Module]] - First module following this pattern
- [[Data Products Module]] - Migrated to modular structure
- [[Feature Manager Module]] - Implements feature toggling

## Related Architecture

- [[API First Approach]] - Modules implement API-first pattern
- [[Testing Strategy]] - Each module has own tests

## Related Guidelines

- [[Development Guidelines]] - Documents modular architecture
- [[Git Workflow]] - Version control for modules

## Implementation

### Legacy Pattern (Obsolete)
```
backend/
└── services/              ← Tightly coupled
    ├── service1.py
    └── service2.py
```

### Current Pattern
```
modules/
├── hana_connection/
│   ├── backend/
│   │   └── hana_connection_service.py
│   └── tests/
├── data_products/
│   ├── backend/
│   │   └── sqlite_data_products_service.py
│   └── tests/
└── feature-manager/
    ├── backend/
    │   └── api.py
    └── tests/
```

## Migration

Completed 2026-01-24:
- Migrated HANA Connection to modules/
- Migrated Data Products to modules/
- Removed backend/services/ directory
- Updated all imports in backend/app.py

## Status

✅ **ADOPTED** - All new services must follow modular architecture

## References

- Core infrastructure: `core/README.md`
- Development guidelines: `.clinerules`
- Migration summary: PROJECT_TRACKER.md (v0.9)