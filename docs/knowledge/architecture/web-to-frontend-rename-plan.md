# Web to Frontend Rename & Archive Cleanup

**Created**: 2026-01-25 22:31
**Purpose**: Rename web/ → frontend/ and remove all archives
**Status**: Plan Ready for Execution

---

## 🎯 Objectives

1. Rename `web/` → `frontend/`
2. Keep only `frontend/current/` (active frontend)
3. Delete ALL archive folders and obsolete files
4. Update all documentation references

---

## 📊 Scope Analysis

### What Will Be Renamed

**Directory Structure**:
```
BEFORE:
web/
├── current/              # Active frontend ✅
│   ├── app.html
│   └── js/
└── archive/              # Delete

AFTER:
frontend/                 # Renamed from web/
├── app.html             # Moved from current/
├── js/                  # Moved from current/
├── css/                 # Moved from current/
├── tests/               # Moved from current/
└── docs/                # Moved from current/
```

**Decision**: Flatten structure (remove `current/` subdirectory)

**Rationale**:
- No more `web/archive/` → no need for `current/`
- Simpler path: `frontend/app.html` vs `web/current/app.html`
- Standard naming: `backend/`, `frontend/` (parallel)

---

### What Will Be DELETED

**⚠️ WARNING: Permanent Deletion**

#### 1. All Archive Folders

**Root Archives**:
```
archive/
├── 2026-01-22-pre-flask-refactoring/     # DELETE
├── 2026-01-25-old-flask-backend/         # DELETE (just created!)
└── 2026-01-25-sapui5-frontend/           # DELETE (just created!)
```

**Web Archives**:
```
web/archive/                               # DELETE (entire folder)
└── [multiple old versions]
```

**Docs Archives**:
```
docs/archive/                              # DELETE
└── [old planning docs]
```

**Web/Current/Docs Archives**:
```
web/current/docs/archive/                  # DELETE
├── features-2026-01-25/                   # DELETE (just created!)
├── migration-2026-01-25/                  # DELETE (just created!)
└── REFACTORING_PROGRESS.md                # DELETE
```

**Data Products Archives**:
```
data-products/archive/                     # DELETE
└── [full multi-language CSN files]
```

#### 2. SQL Archives

```
sql/archive/                               # DELETE
└── [old SQL versions]
```

**Total to Delete**: ~60+ files across 7 archive locations

---

## 🔒 Safety Assessment

### What's Safe to Delete?

**YES - Safe to delete**:
- ✅ All archives (we have Git history)
- ✅ Old flask-backend (archived 30 min ago, in Git)
- ✅ Old SAPUI5 frontend (archived 30 min ago, in Git)
- ✅ Feature implementation docs (archived 30 min ago, in Git)
- ✅ Data product full versions (English-only is enough)

**Git is our backup**: Every file has complete history

### What If We Need Something?

**Git Commands**:
```bash
# Find deleted file
git log --all --full-history -- "archive/file.py"

# Restore from specific commit
git show <commit>:archive/file.py > file.py

# Or checkout entire commit
git checkout <commit> -- archive/
```

**Safety Net**: Git has EVERYTHING ✅

---

## 📋 Execution Plan

### Step 1: Create New Frontend Structure (15 min)

```bash
# Create temporary location
mkdir frontend-temp

# Copy web/current/* to frontend-temp/
xcopy web\current\* frontend-temp\ /E /I /Y

# Move frontend-temp to frontend
move frontend-temp frontend
```

### Step 2: Delete Archives (5 min)

```bash
# Root archives
rmdir /S /Q archive

# Web archives  
rmdir /S /Q web\archive

# Docs archives
rmdir /S /Q docs\archive

# Data products archives
rmdir /S /Q data-products\archive

# SQL archives
rmdir /S /Q sql\archive

# Web/current/docs archive
rmdir /S /Q web\current\docs\archive
```

### Step 3: Delete Old Web Folder (2 min)

```bash
# After frontend/ is created and verified
rmdir /S /Q web
```

### Step 4: Update Documentation (30 min)

**Files to Update** (10+ files):

1. ✅ `README.md` - Update all web/ → frontend/ references
2. ✅ `web/current/README.md` → `frontend/README.md`
3. ✅ `backend/README.md` - Update paths
4. ✅ `backend/app.py` - Update any hardcoded paths
5. ✅ `server.py` - Update comments/docs if needed
6. ✅ `.gitignore` - Update patterns if needed
7. ✅ `docs/knowledge/` - Update wikilinks
8. ✅ `PROJECT_TRACKER.md` - Note the rename
9. ✅ All `.clinerules` - Update path references
10. ✅ Search for remaining `web/` references

### Step 5: Commit & Tag (5 min)

```bash
git add -A
git commit -m "Major restructuring: Rename web/ → frontend/, delete all archives"
git tag -a v3.0-restructured
git push origin main --tags
```

---

## ⏱️ Time Estimate

- **Step 1**: Create frontend/ (15 min)
- **Step 2**: Delete archives (5 min)
- **Step 3**: Delete web/ (2 min)
- **Step 4**: Update docs (30 min)
- **Step 5**: Commit & push (5 min)

**Total**: ~60 minutes (1 hour)

---

## 🎯 Before/After Comparison

### Before

```
steel_thread_on_sap/
├── backend/
├── web/
│   ├── current/          # Active
│   └── archive/          # Old versions
├── archive/              # Root archives
│   ├── 2026-01-25-old-flask-backend/
│   └── 2026-01-25-sapui5-frontend/
├── docs/archive/
├── data-products/archive/
└── sql/archive/
```

### After

```
steel_thread_on_sap/
├── backend/              # Flask API ⭐
├── frontend/             # SPA ⭐ (renamed from web/current/)
├── docs/                 # Documentation (no archive/)
├── data-products/        # CSN files (no archive/)
├── sql/                  # Scripts (no archive/)
└── modules/              # Feature modules
```

**Cleaner**: No archives, clear naming, simpler structure

---

## 🚨 Risk Assessment

**Risks**:
- ⚠️ **HIGH**: Deleting 60+ archive files (permanent)
- ⚠️ **MEDIUM**: Path updates may miss some references
- ⚠️ **LOW**: Rename may break hardcoded paths

**Mitigation**:
- ✅ Git has complete history (can restore anything)
- ✅ Comprehensive search before commit
- ✅ Test application after rename
- ✅ Can revert commit if issues found

**Recommendation**: 
1. Execute rename first (Step 1-3)
2. Test application works
3. THEN update documentation (Step 4)
4. Commit & push (Step 5)

---

## ✅ Success Criteria

After execution:

- [ ] `frontend/` exists (contains web/current/ contents)
- [ ] `web/` folder deleted
- [ ] All `archive/` folders deleted
- [ ] Application runs: `python server.py`
- [ ] Frontend loads: `frontend/app.html`
- [ ] All documentation updated (no web/ references)
- [ ] No broken links
- [ ] Committed and pushed

---

## 📝 Documentation Impact

**Will Update**:
- Root `README.md`
- `frontend/README.md` (was web/current/README.md)
- `backend/README.md`
- `.clinerules`
- Knowledge vault docs with [[wikilinks]]

**Will Create**:
- This analysis document (already created!)

---

## 🔗 Related Documentation

- [[Project Cleanup Analysis]] - Phases 1-4
- [[Frontend Strategy Analysis]] - Why we kept vanilla JS
- [[Flask Frontend Backend Structure]] - Why separation is correct

---

**Ready to Execute**: Awaiting user confirmation to proceed

**Recommendation**: Execute in 5 steps above with testing between each step

</result>
<task_progress>
- [x] Phases 1-4: Cleanup Complete ✅
- [ ] Phase 5: Major Restructuring (NEW)
  - [ ] Create plan (web/ → frontend/, delete archives)
  - [ ] Execute rename
  - [ ] Delete archives
  - [ ] Update documentation
  - [ ] Test & commit
</task_progress>
</attempt_completion>