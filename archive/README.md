# Archived v1 Components

This directory contains v1 components that have been archived.

## Archive Date
February 10, 2026

## Archived v1 Application

- **app_v1/** - Original Flask application (v1)
  - Archived from: `app/`
  - Status: Legacy implementation  
  - Reason: Migrated to modular v2 architecture

## Archived v1 Modules

All non-v2 modules have been moved to this archive:

- ai_assistant
- api_playground  
- csn_validation
- data_products (v1)
- debug_mode
- feature_manager
- hana_connection
- knowledge_graph (v1)
- log_manager
- login_manager
- p2p_dashboard
- sql_execution
- sqlite_connection

## Active v2 Implementation

The following v2 components remain active:
- **modules/data_products_v2/** - Active v2 module
- **modules/knowledge_graph_v2/** - Active v2 module  
- **app/** - Active v2 application (renamed from app_v2)

## Running the Application

To run the active v2 application:
```bash
python server.py
```

This will now start the v2 application from the `app/` directory.

## Purpose of Archive

These v1 components are kept for:
1. **Historical reference** - Understanding the v1 implementation
2. **Migration guidance** - Comparing v1 vs v2 approaches
3. **Future reference** - May need v1 patterns for specific cases

## Important Notes

⚠️ **Do NOT import from archived components** - Use v2 equivalents

✅ **Active application**: `app/` directory (v2 architecture)
✅ **Active modules**: `modules/` directory (v2 modules only)

---

**Last Updated**: February 10, 2026  
**Branch**: main  
**Decision**: Full migration to v2 architecture complete