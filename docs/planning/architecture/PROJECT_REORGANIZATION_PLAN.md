# Project Reorganization Plan

**Date**: January 21, 2026, 9:50 PM  
**Purpose**: Clean up project structure, archive old files, keep only current/useful files

---

## Current State Analysis

**Total Files**: 75+ files in root directory
**Problem**: Cluttered, hard to navigate, multiple old versions

**Goal**: Clean, organized structure with clear categories

---

## Proposed New Structure

```
p2p_mcp/
│
├── 📂 docs/                          # All documentation
│   ├── 📂 hana-cloud/               # HANA Cloud documentation
│   ├── 📂 fiori/                    # Fiori design documentation
│   ├── 📂 p2p/                      # P2P project documentation
│   └── 📂 archive/                  # Old/deprecated docs
│
├── 📂 sql/                          # SQL scripts
│   ├── 📂 hana/                     # HANA Cloud SQL scripts
│   ├── 📂 sqlite/                   # SQLite database scripts
│   └── 📂 archive/                  # Old SQL versions
│
├── 📂 web/                          # Web applications
│   ├── 📂 current/                  # Current/recommended versions
│   └── 📂 archive/                  # Old versions
│
├── 📂 data-products/                # CSN data product files
│   ├── *.en.json                   # English-only (keep)
│   └── archive/                     # Full versions (archive)
│
├── 📂 scripts/                      # PowerShell scripts
│
└── README.md                        # Main project README
```

---

## File Categorization

### ✅ KEEP - Current/Essential Files (32 files)

#### **Main Documentation (7 files)**
1. `PROJECT_TRACKER_REFACTORED.md` ⭐ PRIMARY TRACKER
2. `README.md` (to be created - main project overview)

#### **HANA Cloud Documentation (8 files)**
3. `HANA_CLOUD_LEARNING_ROADMAP.md`
4. `HANA_CLOUD_GETTING_STARTED_SUMMARY.md`
5. `HANA_CLOUD_ADMINISTRATION_GUIDE_SUMMARY.md`
6. `HANA_CLOUD_FIRST_USER_SETUP.md`
7. `HANA_CLOUD_PRIVILEGES_GUIDE.md`
8. `HOW_TO_ACCESS_HANA_DATABASE_EXPLORER.md`
9. `HANA_SQL_SCRIPTS_README.md`
10. `SAP_HANA_CLOUD_OFFICIAL_SYNTAX_PERPLEXITY.md`

#### **HANA Cloud SQL Scripts - Current (3 files)**
11. `hana_create_p2p_user_SPECIFIC_GRANTS.sql` ⭐ BDC-COMPATIBLE
12. `hana_verify_user_setup.sql`
13. `hana_cleanup_user.sql`

#### **P2P Database (2 files)**
14. `p2p_complete_workflow_sqlite.sql` ⭐ COMPLETE DATABASE
15. `P2P_COMPLETE_WORKFLOW_README.md`

#### **Web Applications - Current (1 file)**
16. `p2p-data-products-ui5-fiori.html` ⭐ FINAL VERSION

#### **Data Products - English Only (6 files)**
17. `sap-s4com-Supplier-v1.en.json`
18. `sap-s4com-PurchaseOrder-v1.en.json`
19. `sap-s4com-ServiceEntrySheet-v1.en.json`
20. `sap-s4com-SupplierInvoice-v1.en.json`
21. `sap-s4com-PaymentTerms-v1.en.json`
22. `sap-s4com-JournalEntryHeader-v1.en.json`

#### **PowerShell Scripts (2 files)**
23. `analyze-csn-entities.ps1`
24. `Get-DataProductEntities.ps1`

#### **Analysis Documents (3 files)**
25. `CSN_ENTITY_MAPPING_ANALYSIS.md`
26. `sap_data_products_csn_analysis.md`
27. `SAPUI5_MIGRATION_GUIDE.md`

#### **Reference Guides (5 files)**
28. `SNOWFLAKE_DATABASE_CREATION_GUIDE.md`
29. `SNOWFLAKE_STAGE_CREATION_GUIDE.md`
30. `SAP_FIORI_DESIGN_GUIDELINES.md`
31. `SAP_FIORI_ENHANCED_GUIDELINES.md`
32. `PYTHON_MIGRATION_PLAN.md`

---

### 🗄️ ARCHIVE - Old Versions (25 files)

#### **Old HANA SQL Scripts (10 files)** → `sql/archive/`
- `hana_create_dev_user.sql` (v1 - had errors)
- `hana_create_dev_user_simple.sql` (v2 - had syntax error)
- `hana_create_dev_user_final.sql` (v3 - superseded by SPECIFIC_GRANTS)
- `hana_create_p2p_user.sql` (v1 - had errors)
- `hana_create_p2p_user_simple.sql` (v2 - had syntax error)
- `hana_create_p2p_user_final.sql` (v3 - superseded by SPECIFIC_GRANTS)
- `hana_create_p2p_user_WORKING.sql` (v4 - superseded)
- `hana_create_p2p_user_MINIMAL.sql` (v5 - superseded)
- `hana_create_p2p_user_CORRECT.sql` (v6 - superseded)
- `hana_check_connection.sql` (keep this actually - utility)

#### **Old Web Applications (10 files)** → `web/archive/`
- `p2p-viewer.html` (v1 - basic)
- `p2p-viewer-fiori.html` (v2)
- `p2p-viewer-fiori-updated.html` (v3)
- `p2p-viewer-ui5.html` (v4)
- `p2p-viewer-ui5-fiori.html` (v5)
- `p2p-viewer-ui5-sapfiori.html` (v6)
- `p2p-viewer-v2-full-compliance.html` (v7)
- `p2p-data-products-viewer.html` (alternate)
- `p2p-data-products-fiori-compliant.html` (alternate)
- `p2p-data-products-ui5-compliant.html` (alternate)

#### **Old Database Scripts (1 file)** → `sql/archive/`
- `p2p_supplier_invoice_sqlite.sql` (simplified version)
- `p2p_supplier_invoice_db.sql` (non-sqlite)

#### **Old Documentation (4 files)** → `docs/archive/`
- `SupplierInvoice-Extraction-Tracker.md` (original tracker)
- `PROJECT_SUMMARY.md` (superseded by PROJECT_TRACKER)
- `P2P_DATABASE_README.md` (superseded by P2P_COMPLETE_WORKFLOW_README)
- `HANA_CLOUD_SETUP_ISSUE_RESOLVED.md` (troubleshooting history)
- `SAP_HANA_CLOUD_OFFICIAL_SYNTAX.md` (superseded by PERPLEXITY version)

---

### ❌ REMOVE - Unnecessary/Duplicate (6 files)

#### **Data Products - Full Versions (6 files)** - Superseded by .en.json
- `sap-s4com-Supplier-v1.json` (remove - have .en.json)
- `sap-s4com-PurchaseOrder-v1.json` (remove - have .en.json)
- `sap-s4com-ServiceEntrySheet-v1.json` (remove - have .en.json)
- `sap-s4com-SupplierInvoice-v1.json` (remove - have .en.json)
- `sap-s4com-PaymentTerms-v1.json` (remove - have .en.json)
- `sap-s4com-JournalEntryHeader-v1.json` (remove - have .en.json)

**Exception**: Keep `sap-s4com-SupplierInvoice-v1.en-complete.json` (special complete version)

#### **Old Tracking/Status Files** → Can consolidate or remove
- `P2P_DATA_PRODUCTS_CHANGELOG.md` (merge into tracker)
- `P2P_VIEWER_V2_CHANGELOG.md` (merge into tracker)
- `FIORI_SCRAPING_TRACKER.md` (historical)
- `SUPPLIER_INVOICE_VALIDATION_REPORT.md` (historical)

#### **Fiori Documentation** - Keep curated set
- Keep: `SAP_FIORI_DESIGN_GUIDELINES.md`, `SAP_FIORI_ENHANCED_GUIDELINES.md`
- Archive: `FIORI_DESIGN_SCRAPING_REPORT.md`, `FIORI_SCRAPING_COVERAGE_ANALYSIS.md`, `FIORI_DESIGN_EXTENDED_GUIDELINES.md`
- Remove: `SAP_FIORI_COMPLIANCE_AUDIT.md`, `SAP_FIORI_GUIDELINES_APPLICATION_AUDIT.md` (outdated)

---

## Reorganization Actions

### **Phase 1: Create Directory Structure**

```powershell
# Create main directories
New-Item -Path "docs" -ItemType Directory
New-Item -Path "docs/hana-cloud" -ItemType Directory
New-Item -Path "docs/fiori" -ItemType Directory
New-Item -Path "docs/p2p" -ItemType Directory
New-Item -Path "docs/archive" -ItemType Directory

New-Item -Path "sql" -ItemType Directory
New-Item -Path "sql/hana" -ItemType Directory
New-Item -Path "sql/sqlite" -ItemType Directory
New-Item -Path "sql/archive" -ItemType Directory

New-Item -Path "web" -ItemType Directory
New-Item -Path "web/current" -ItemType Directory
New-Item -Path "web/archive" -ItemType Directory

New-Item -Path "data-products" -ItemType Directory
New-Item -Path "data-products/archive" -ItemType Directory

New-Item -Path "scripts" -ItemType Directory
```

### **Phase 2: Move Current Files to Organized Locations**

```powershell
# HANA Cloud Documentation
Move-Item "HANA_CLOUD_*.md" "docs/hana-cloud/"
Move-Item "HOW_TO_ACCESS_*.md" "docs/hana-cloud/"
Move-Item "SAP_HANA_*.md" "docs/hana-cloud/"

# P2P Documentation
Move-Item "P2P_COMPLETE_WORKFLOW_README.md" "docs/p2p/"
Move-Item "CSN_ENTITY_MAPPING_ANALYSIS.md" "docs/p2p/"
Move-Item "sap_data_products_csn_analysis.md" "docs/p2p/"

# Fiori Documentation
Move-Item "SAP_FIORI_DESIGN_GUIDELINES.md" "docs/fiori/"
Move-Item "SAP_FIORI_ENHANCED_GUIDELINES.md" "docs/fiori/"
Move-Item "SAPUI5_MIGRATION_GUIDE.md" "docs/fiori/"

# Other Documentation
Move-Item "SNOWFLAKE_*.md" "docs/"
Move-Item "PYTHON_MIGRATION_PLAN.md" "docs/"

# HANA SQL Scripts - Current
Move-Item "hana_create_p2p_user_SPECIFIC_GRANTS.sql" "sql/hana/"
Move-Item "hana_verify_user_setup.sql" "sql/hana/"
Move-Item "hana_cleanup_user.sql" "sql/hana/"
Move-Item "hana_check_connection.sql" "sql/hana/"
Move-Item "HANA_SQL_SCRIPTS_README.md" "sql/hana/"

# SQLite Database Scripts
Move-Item "p2p_complete_workflow_sqlite.sql" "sql/sqlite/"

# PowerShell Scripts
Move-Item "*.ps1" "scripts/"

# Web Applications - Current
Move-Item "p2p-data-products-ui5-fiori.html" "web/current/"
Move-Item "p2p-data-products-master-detail.html" "web/current/"

# Data Products - English Only
Move-Item "*-v1.en.json" "data-products/"
```

### **Phase 3: Archive Old Files**

```powershell
# Old HANA SQL Scripts
Move-Item "hana_create_*_user.sql" "sql/archive/"  # v1-v6
Move-Item "hana_create_*_user_*.sql" "sql/archive/"  # WORKING, MINIMAL, etc.

# Old SQLite Scripts
Move-Item "p2p_supplier_invoice_*.sql" "sql/archive/"

# Old Web Applications
Move-Item "p2p-viewer*.html" "web/archive/"  # All old versions
Move-Item "p2p-data-products-viewer.html" "web/archive/"
Move-Item "p2p-data-products-fiori-compliant.html" "web/archive/"
Move-Item "p2p-data-products-ui5-compliant.html" "web/archive/"

# Old Documentation
Move-Item "SupplierInvoice-Extraction-Tracker.md" "docs/archive/"
Move-Item "PROJECT_SUMMARY.md" "docs/archive/"
Move-Item "P2P_DATABASE_README.md" "docs/archive/"
Move-Item "HANA_CLOUD_SETUP_ISSUE_RESOLVED.md" "docs/archive/"
Move-Item "SAP_HANA_CLOUD_OFFICIAL_SYNTAX.md" "docs/archive/"
Move-Item "P2P_DATA_PRODUCTS_CHANGELOG.md" "docs/archive/"
Move-Item "P2P_VIEWER_V2_CHANGELOG.md" "docs/archive/"
Move-Item "FIORI_*REPORT.md" "docs/archive/"
Move-Item "FIORI_*TRACKER.md" "docs/archive/"
Move-Item "FIORI_*COVERAGE*.md" "docs/archive/"
Move-Item "SAP_FIORI_COMPLIANCE_AUDIT.md" "docs/archive/"
Move-Item "SAP_FIORI_GUIDELINES_APPLICATION_AUDIT.md" "docs/archive/"

# Data Products - Full Versions
Move-Item "sap-s4com-*-v1.json" "data-products/archive/"  # Not .en.json
```

### **Phase 4: Remove Unnecessary Files**

```powershell
# Remove duplicate/unnecessary files
Remove-Item "cline-skills-docs.html"  # Not project-related
Remove-Item "hana_create_user_official.html"  # Temporary research file
```

---

## Final Structure (After Reorganization)

```
p2p_mcp/
│
├── 📂 docs/
│   ├── 📂 hana-cloud/
│   │   ├── HANA_CLOUD_LEARNING_ROADMAP.md ⭐
│   │   ├── HANA_CLOUD_GETTING_STARTED_SUMMARY.md ⭐
│   │   ├── HANA_CLOUD_ADMINISTRATION_GUIDE_SUMMARY.md ⭐
│   │   ├── HANA_CLOUD_FIRST_USER_SETUP.md
│   │   ├── HANA_CLOUD_PRIVILEGES_GUIDE.md
│   │   ├── HOW_TO_ACCESS_HANA_DATABASE_EXPLORER.md
│   │   └── SAP_HANA_CLOUD_OFFICIAL_SYNTAX_PERPLEXITY.md
│   │
│   ├── 📂 fiori/
│   │   ├── SAP_FIORI_DESIGN_GUIDELINES.md ⭐
│   │   ├── SAP_FIORI_ENHANCED_GUIDELINES.md
│   │   ├── SAP_FIORI_UX_PAGES_TO_SCRAPE.md
│   │   ├── FIORI_IMPLEMENTATION_STATUS.md
│   │   ├── FIORI_DESIGN_EXTENDED_GUIDELINES.md
│   │   └── SAPUI5_MIGRATION_GUIDE.md
│   │
│   ├── 📂 p2p/
│   │   ├── P2P_COMPLETE_WORKFLOW_README.md ⭐
│   │   ├── CSN_ENTITY_MAPPING_ANALYSIS.md
│   │   ├── sap_data_products_csn_analysis.md
│   │   └── P2P_DATA_PRODUCTS_GAP_ANALYSIS.md
│   │
│   ├── 📂 archive/ (old docs)
│   │
│   ├── SNOWFLAKE_DATABASE_CREATION_GUIDE.md
│   ├── SNOWFLAKE_STAGE_CREATION_GUIDE.md
│   └── PYTHON_MIGRATION_PLAN.md
│
├── 📂 sql/
│   ├── 📂 hana/
│   │   ├── hana_create_p2p_user_SPECIFIC_GRANTS.sql ⭐ USE THIS
│   │   ├── hana_verify_user_setup.sql
│   │   ├── hana_cleanup_user.sql
│   │   ├── hana_check_connection.sql
│   │   └── HANA_SQL_SCRIPTS_README.md
│   │
│   ├── 📂 sqlite/
│   │   └── p2p_complete_workflow_sqlite.sql ⭐ COMPLETE DB
│   │
│   └── 📂 archive/ (old SQL versions)
│
├── 📂 web/
│   ├── 📂 current/
│   │   ├── p2p-data-products-ui5-fiori.html ⭐ RECOMMENDED
│   │   └── p2p-data-products-master-detail.html (alternate)
│   │
│   └── 📂 archive/ (10+ old versions)
│
├── 📂 data-products/
│   ├── sap-s4com-Supplier-v1.en.json ⭐
│   ├── sap-s4com-PurchaseOrder-v1.en.json ⭐
│   ├── sap-s4com-ServiceEntrySheet-v1.en.json ⭐
│   ├── sap-s4com-SupplierInvoice-v1.en.json ⭐
│   ├── sap-s4com-SupplierInvoice-v1.en-complete.json
│   ├── sap-s4com-PaymentTerms-v1.en.json ⭐
│   ├── sap-s4com-JournalEntryHeader-v1.en.json ⭐
│   │
│   └── 📂 archive/ (full multi-language versions)
│
├── 📂 scripts/
│   ├── analyze-csn-entities.ps1
│   └── Get-DataProductEntities.ps1
│
├── PROJECT_TRACKER_REFACTORED.md ⭐ PRIMARY TRACKER
└── README.md ⭐ PROJECT OVERVIEW (to be created)
```

---

## Benefits of Reorganization

### ✅ **Clarity**
- Clear separation of concerns
- Easy to find files by category
- Logical grouping

### ✅ **Maintainability**
- Current files easily identifiable
- Old versions preserved but separate
- Clean root directory

### ✅ **Professionalism**
- Enterprise-grade organization
- Easy onboarding for new team members
- Clear project structure

### ✅ **Efficiency**
- Faster navigation
- Less confusion
- Better IDE performance

---

## Files to Keep in Root (Minimal)

1. `PROJECT_TRACKER_REFACTORED.md` - Main project tracker
2. `README.md` - Project overview (to be created)
3. `.gitignore` (if using Git)
4. `package.json` (if Node.js project)

**Everything else organized in subdirectories**

---

## Execution Plan

### **Step 1**: Create directory structure
### **Step 2**: Move current files to organized locations
### **Step 3**: Archive old versions
### **Step 4**: Remove unnecessary files
### **Step 5**: Create new README.md
### **Step 6**: Update PROJECT_TRACKER with reorganization
### **Step 7**: Verify all files accessible
### **Step 8**: Update any path references

---

## Post-Reorganization File Count

**Before**: 75+ files in root  
**After**: 
- Root: 2-3 files
- docs/: ~30 files (organized in subdirectories)
- sql/: ~15 files (organized in subdirectories)
- web/: ~12 files (organized in subdirectories)
- data-products/: ~13 files (organized)
- scripts/: 2 files

**Total**: Same files, but **organized** for clarity

---

## Recommendation

**Execute reorganization in phases**:
1. ✅ Create directory structure
2. ✅ Move KEEP files first
3. ✅ Archive old versions
4. ✅ Remove duplicates
5. ✅ Create README.md
6. ✅ Update tracker

**Time Required**: ~30 minutes

**Risk**: Low (all files preserved in archive directories)

**Benefit**: Significant improvement in project organization

---

**Status**: 📋 **PLAN READY - Awaiting Approval**  
**Last Updated**: January 21, 2026, 9:50 PM
