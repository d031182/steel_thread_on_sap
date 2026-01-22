# Web Application Documentation

**Last Updated:** January 22, 2026  
**Version:** 3.3

---

## Documentation Structure

```
docs/
├── features/      Feature implementation documentation
├── migration/     Migration and refactoring guides
└── archive/       Historical/obsolete documentation
```

---

## Features Documentation

**Location:** `features/`

### Core Features

1. **DATA_PRODUCTS_EXPLORER_PLAN.md** - Explorer feature planning
2. **DATA_PRODUCTS_EXPLORER_IMPLEMENTATION.md** - Implementation details
3. **EXPLORER_DETAIL_PAGE_ENHANCEMENT.md** - Detail page enhancements
4. **EXPLORER_DETAIL_PAGE_IMPLEMENTATION_COMPLETE.md** - Implementation summary

### Logging Features

5. **LOG_VIEWER_FEATURE_SUMMARY.md** - Log viewer overview
6. **ADVANCED_LOGGING_QUICKWINS_IMPLEMENTATION.md** - Quick wins implementation

### SQL Features

7. **SQL_CONSOLE_EXECUTION_FEATURE.md** - SQL console feature
8. **SQL_EXECUTION_API_SUMMARY.md** - API summary
9. **SQL_EXECUTION_ENHANCEMENT_PLAN.md** - Enhancement roadmap

### UI Features

10. **THEME_SWITCHING_FEATURE.md** - Theme switching implementation

---

## Migration Documentation

**Location:** `migration/`

1. **FLASK_REFACTORING_PLAN.md** - Flask migration planning
2. **SAPUI5_MIGRATION_PHASE1_COMPLETE.md** - SAPUI5 migration completion
3. **SAPUI5_MIGRATION_PLAN.md** - SAPUI5 migration planning

---

## Archive

**Location:** `archive/`

- **REFACTORING_PROGRESS.md** - Historical refactoring progress

---

## Quick Links

### Backend Documentation
- [Flask Backend README](../flask-backend/README.md)
- [Flask Backend Docs](../flask-backend/docs/)

### Frontend Documentation  
- [Frontend README](../README.md)
- [Application Features](../../../APPLICATION_FEATURES.md)

### Project Documentation
- [Project Tracker](../../../PROJECT_TRACKER.md)
- [Development Guidelines](../../../DEVELOPMENT_GUIDELINES.md)

---

## Documentation Standards

### When to Create New Docs

- New feature implementation
- Significant refactoring
- Architecture changes
- Migration activities

### File Naming Convention

- Use SCREAMING_SNAKE_CASE.md
- Be descriptive: `FEATURE_NAME_IMPLEMENTATION.md`
- Include status suffix: `_PLAN`, `_COMPLETE`, `_SUMMARY`

### Content Guidelines

1. **Start with metadata:** Date, version, status
2. **Provide overview:** What and why
3. **Include details:** How it works
4. **Show examples:** Code snippets, usage
5. **Link related docs:** Cross-references
6. **Keep updated:** Update dates and status

---

## Contributing

### Adding Documentation

1. Create file in appropriate subdirectory
2. Follow naming convention
3. Use standard structure
4. Update this README
5. Link from related docs

### Archiving Documentation

When docs become obsolete:
1. Move to `archive/`
2. Update this README
3. Add note in archive file explaining why

---

**Status:** ✅ Organized Structure  
**Last Reorganization:** January 22, 2026
