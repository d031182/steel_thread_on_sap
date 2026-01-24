# Project Structure Refactoring Plan

**Date**: 2026-01-23
**Objective**: Refactor to standard best practice structure for Flask + SAP UI5 application

---

## Current Structure Issues

1. **Duplicate frontend locations**: `frontend/`, `web/current/`, `web/current/webapp/`
2. **Unclear separation**: Mixed static files and application code
3. **Non-standard naming**: `web/current` instead of standard `frontend` or `static`
4. **Archived content**: `web/archive` cluttering main structure

---

## Target Structure (Industry Best Practice)

```
steel_thread_on_sap/
│
├── backend/                      # Flask backend application
│   ├── app.py                   # Main Flask app
│   ├── requirements.txt         # Python dependencies
│   ├── config.py               # Configuration management (new)
│   ├── models/                 # Database models (future)
│   ├── routes/                 # API routes (future modular structure)
│   └── tests/                  # Backend tests (future)
│
├── frontend/                     # SAP UI5 frontend application
│   ├── index.html              # Main entry point
│   ├── manifest.json           # UI5 app descriptor (if needed)
│   ├── Component.js            # UI5 component (if needed)
│   ├── controller/             # UI5 controllers
│   ├── view/                   # UI5 views
│   ├── model/                  # UI5 models
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript modules
│   │   ├── api/               # Business logic APIs
│   │   ├── services/          # Service layer
│   │   └── utils/             # Utilities (clientErrorLogger, etc.)
│   └── i18n/                   # Internationalization
│
├── tests/                       # Integration tests
│   ├── backend/                # Backend API tests
│   └── frontend/               # Frontend unit tests
│
├── docs/                        # Documentation
│   ├── api/                    # API documentation
│   ├── setup/                  # Setup guides
│   └── architecture/           # Architecture docs
│
├── data-products/              # Data product definitions
├── sql/                        # SQL scripts
├── scripts/                    # Utility scripts
├── logs/                       # Application logs (runtime)
├── archive/                    # Archived versions (moved from web/)
│
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
├── package.json                # Node.js dependencies (if any)
├── requirements.txt            # Python dependencies (root level)
└── .env.example               # Environment template
```

---

## Migration Steps

### Phase 1: Prepare Archive (Safe Backup)
1. ✅ Move `web/archive/` to `archive/web-historical/`
2. ✅ Move `frontend/` (unused) to `archive/frontend-original/`

### Phase 2: Consolidate Frontend
1. ✅ Copy `web/current/` content to new `frontend/`
2. ✅ Clean up duplicate files
3. ✅ Remove nested `webapp/` structure (flatten if redundant)
4. ✅ Organize into standard subdirectories

### Phase 3: Update Backend
1. ✅ Update Flask `static_folder` path to point to `frontend/`
2. ✅ Test all routes work correctly
3. ✅ Update any hardcoded paths

### Phase 4: Clean Up
1. ✅ Remove old `web/` directory
2. ✅ Update documentation files
3. ✅ Update `.gitignore` if needed

### Phase 5: Verify & Test
1. ✅ Run backend: `python backend/app.py`
2. ✅ Test frontend loads at http://localhost:5000
3. ✅ Test all APIs work
4. ✅ Test client error logging
5. ✅ Run unit tests

### Phase 6: Documentation
1. ✅ Update README.md with new structure
2. ✅ Update PROJECT_TRACKER.md
3. ✅ Create ARCHITECTURE.md documenting structure

---

## Benefits of New Structure

### 1. **Industry Standard**
- Follows Python/Flask best practices
- Matches SAP UI5 project conventions
- Clear separation of concerns

### 2. **Scalability**
- Easy to add new routes in `backend/routes/`
- Modular frontend structure
- Room for growth

### 3. **Maintainability**
- Clear where to find things
- Standard naming conventions
- Self-documenting structure

### 4. **Developer Experience**
- New developers understand structure immediately
- IDE tools work better with standard layout
- CI/CD pipelines expect this structure

### 5. **Testing**
- Clear location for tests
- Separate backend/frontend tests
- Easy integration testing

---

## File Mappings

### Frontend Migration
```
web/current/index.html              → frontend/index.html
web/current/js/api/                 → frontend/js/api/
web/current/js/services/            → frontend/js/services/
web/current/js/utils/               → frontend/js/utils/
web/current/css/                    → frontend/css/
web/current/docs/                   → docs/frontend/
web/current/tests/                  → tests/frontend/
web/current/webapp/                 → (merge or remove if duplicate)
```

### Backend Updates
```
backend/app.py                      → Update static_folder path
backend/README.md                   → Update instructions
```

### Archive Migration
```
web/archive/                        → archive/web-historical/
frontend/ (unused)                  → archive/frontend-original/
```

---

## Risk Mitigation

1. **Git Safety**: Create checkpoint tag before starting
2. **Backup**: Archive old structure in `archive/`
3. **Incremental**: Test after each phase
4. **Rollback**: Keep old structure until verified
5. **Documentation**: Update all docs immediately

---

## Post-Refactoring Tasks

1. ✅ Update all documentation references
2. ✅ Update PROJECT_TRACKER.md
3. ✅ Test complete workflow end-to-end
4. ✅ Git commit with clear message
5. ✅ Create git tag: `v2.4-structure-refactored`
6. ✅ Update onboarding docs

---

## Timeline Estimate

- Phase 1: 10 minutes (Archive)
- Phase 2: 20 minutes (Consolidate)
- Phase 3: 10 minutes (Update Backend)
- Phase 4: 10 minutes (Clean Up)
- Phase 5: 15 minutes (Testing)
- Phase 6: 15 minutes (Documentation)

**Total**: ~80 minutes

---

## Success Criteria

✅ Application runs without errors
✅ All APIs functional
✅ Frontend loads correctly
✅ Client error logging works
✅ Tests pass
✅ Structure follows best practices
✅ Documentation updated
✅ Git history preserved

---

## Next Steps

1. Get user approval for this plan
2. Create git checkpoint tag
3. Execute phases sequentially
4. Test after each phase
5. Update documentation
6. Commit and push

---

**Status**: 📋 PLANNED - Awaiting user approval to proceed