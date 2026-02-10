# Version Control Strategy - Preventing Archive Confusion

**Created:** January 23, 2026, 10:00 AM CET  
**Purpose:** Clear strategy to prevent version confusion during refactoring

---

## ⚠️ Problem Identified

During refactoring, archived versions were accidentally restored, creating confusion about which version is current. This happened because:

1. Multiple HTML files existed in the same directory
2. Archives were nested (archive inside archive)
3. No clear indicator of which file is "production"
4. `index.html` was restored from archives multiple times

---

## ✅ New Strategy

### 1. Single Source of Truth

**Production File:** `web/current/index.html`  
**Rule:** This file is ALWAYS the production version  
**Never:** Copy from archives back to `index.html` manually

### 2. Clear Archive Organization

**Structure:**
```
web/
├── current/
│   ├── index.html ⭐ (PRODUCTION - never touch directly)
│   ├── PRODUCTION_VERSION.md (documents what's in index.html)
│   │
│   ├── js/ (JavaScript APIs - current)
│   ├── css/ (Styles - current)
│   ├── tests/ (Tests - current)
│   │
│   └── archives/
│       ├── 2026-01-22-vanilla-js/
│       │   ├── index.html
│       │   └── README.md (why archived)
│       │
│       ├── 2026-01-22-ui5-incomplete/
│       │   ├── app-complete.html
│       │   └── README.md
│       │
│       └── 2026-01-23-sapui5-no-logging/
│           ├── index-ui5.html
│           └── README.md
│
└── archive/ (root level - old project structures)
```

### 3. Git is Primary Version Control

**Instead of manual archives, use Git:**

```bash
# Tag important versions
git tag -a v3.3-production -m "Production: SAPUI5 + HANA + Logging"
git push origin v3.3-production

# View history
git log --oneline

# Compare versions
git diff v3.2 v3.3

# Restore specific version (if needed)
git checkout v3.3-production -- web/current/index.html
```

### 4. Documentation as Source of Truth

**Files:**
1. `PRODUCTION_VERSION.md` - Describes current production
2. `VERSION_HISTORY.md` - Timeline of all versions
3. Each archive folder has `README.md` explaining why archived

---

## 🔧 Implementation Plan

### Phase 1: Clean Up Current Mess (Now)

1. ✅ Remove nested archives
2. ✅ Flatten archive structure
3. ✅ Date-based archive folders
4. ✅ Document production version

### Phase 2: Establish Process (Next)

1. Create `VERSION_HISTORY.md`
2. Add git tags for versions
3. Create restore scripts
4. Update documentation

### Phase 3: Prevent Future Issues

1. Add `.production` marker file
2. Create deployment script
3. Add pre-commit hooks
4. Document workflow

---

## 📋 Rules Going Forward

### ✅ DO:

1. **Use Git for versions:**
   ```bash
   git tag -a v3.4 -m "Description"
   git push origin v3.4
   ```

2. **Document in PRODUCTION_VERSION.md:**
   - What file is production
   - When it was set
   - What features it has

3. **Archive with purpose:**
   - Create folder: `archives/YYYY-MM-DD-reason/`
   - Add README.md explaining why
   - Never nest archives

4. **Test before promoting:**
   - Run all tests
   - Verify in browser
   - Check all features
   - Then copy to `index.html`

### ❌ DON'T:

1. **Never randomly restore from archives**
   - Always check PRODUCTION_VERSION.md first
   - Confirm with user before changing

2. **Never nest archives**
   - Flat structure only
   - One level: `archives/date-reason/`

3. **Never edit index.html directly**
   - Work in development files
   - Test thoroughly
   - Then promote to production

4. **Never delete archives without documenting**
   - Always keep README.md
   - Explain why archived

---

## 🎯 Quick Reference

### To Find Production Version:

1. Read `web/current/PRODUCTION_VERSION.md`
2. Check `web/current/index.html` (always production)
3. Review git tags: `git tag -l`

### To Archive a Version:

```bash
# 1. Create archive folder
New-Item -ItemType Directory -Path "web/current/archives/2026-01-23-reason"

# 2. Copy file
Copy-Item "web/current/old-file.html" "web/current/archives/2026-01-23-reason/"

# 3. Create README
echo "Archived because: [reason]" > web/current/archives/2026-01-23-reason/README.md

# 4. Commit
git add web/current/archives/2026-01-23-reason/
git commit -m "[Archive] Reason for archiving"
```

### To Restore a Version:

```bash
# Option 1: From Git (PREFERRED)
git checkout <tag-or-commit> -- web/current/index.html

# Option 2: From Archive (LAST RESORT)
# First: Check PRODUCTION_VERSION.md
# Then: Confirm with user
# Finally: Copy and document
Copy-Item "archives/date/file.html" "index.html"
# Update PRODUCTION_VERSION.md
# Commit changes
```

---

## 📊 Version History Template

**File:** `VERSION_HISTORY.md` (to be created)

```markdown
# Version History

## v3.3 - Current Production (2026-01-23)
- File: index.html (from p2p-fiori-proper.html)
- Features: SAPUI5 + HANA + Advanced Logging
- Git Tag: v3.3-production
- Tests: 72/72 passing
- Status: ✅ Production

## v3.2 - Archived (2026-01-22)
- File: app-complete.html
- Features: SAPUI5 + HANA (no logging)
- Reason: Missing logging system
- Location: archives/2026-01-22-no-logging/

## v3.1 - Archived (2026-01-22)
- File: index.html (vanilla JS)
- Features: Custom HTML + HANA
- Reason: Not using SAPUI5 framework
- Location: archives/2026-01-22-vanilla-js/
```

---

## 🚀 Next Steps

### Immediate (Today):

1. ✅ Create this strategy document
2. [ ] Flatten archive structure
3. [ ] Create VERSION_HISTORY.md
4. [ ] Add git tags for versions
5. [ ] Commit and document

### Short Term (This Week):

1. [ ] Create restore script
2. [ ] Add pre-commit hooks
3. [ ] Test rollback procedure
4. [ ] Update all documentation

### Long Term:

1. [ ] Automated deployment
2. [ ] CI/CD pipeline
3. [ ] Automated testing
4. [ ] Version badges in UI

---

## 🔍 Troubleshooting

### "Which version is production?"
→ Read `PRODUCTION_VERSION.md`

### "I can't find a feature"
→ Check `VERSION_HISTORY.md` for which version has it

### "Archive is nested"
→ Flatten it, update this document

### "Not sure if I should archive"
→ If it's not production and not in active development, archive it

---

## 📝 Checklist for Every Change

Before making any change to `index.html`:

- [ ] Read `PRODUCTION_VERSION.md`
- [ ] Confirm current version
- [ ] Test new version thoroughly
- [ ] Update `PRODUCTION_VERSION.md`
- [ ] Create git tag
- [ ] Archive old version (if needed)
- [ ] Update `VERSION_HISTORY.md`
- [ ] Commit with clear message
- [ ] Push to GitHub

---

**Status:** ✅ Strategy Defined  
**Next:** Implement Phase 2 (VERSION_HISTORY.md + git tags)  
**Goal:** Never lose track of versions again!
