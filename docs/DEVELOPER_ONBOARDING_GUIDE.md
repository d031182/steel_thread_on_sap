# Developer Onboarding Guide

**Project**: P2P Data Products Application  
**Purpose**: Complete guide for new developers (AI and human)  
**Version**: 1.0  
**Last Updated**: January 24, 2026

---

## 🎯 Welcome!

This guide will get you from **zero to productive** in the P2P Data Products project. Whether you're an AI assistant or human developer, this is your starting point.

**Estimated Time**: 2-3 hours to read, 1 day to become productive

---

## 📚 Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Project Overview](#project-overview)
3. [Documentation Map](#documentation-map)
4. [Architecture](#architecture)
5. [Development Workflow](#development-workflow)
6. [Module System](#module-system)
7. [Fiori/UI5 Development](#fioriui5-development)
8. [Testing Standards](#testing-standards)
9. [Git Workflow](#git-workflow)
10. [Common Tasks](#common-tasks)
11. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For AI Assistants ⭐ CRITICAL

**MANDATORY: Start EVERY session with these 4 steps:**

#### Step 1: Check Knowledge Graph FIRST
```xml
<use_mcp_tool>
  <server_name>github.com/modelcontextprotocol/servers/tree/main/src/memory</server_name>
  <tool_name>search_nodes</tool_name>
  <arguments>{"query": "[topic you're working on]"}</arguments>
</use_mcp_tool>
```
**Why**: Avoid re-investigating topics we've already researched (saves 1-2 hours)

#### Step 2: Read Development Guidelines
- **File**: `.clinerules`
- **Contains**: 
  - Mandatory development standards (7 rules)
  - API-first approach
  - Testing requirements
  - Fiori compliance
  - Git workflow
  - JavaScript vs XML preferences
- **Time**: 15 minutes to read thoroughly
- **Critical**: Contains enforcement policies

#### Step 3: Check Project Tracker
- **File**: `PROJECT_TRACKER.md`
- **Shows**: 
  - Complete project history
  - What's been done
  - Current status
  - Proven patterns
- **Time**: 5-10 minutes to scan
- **Use**: Learn from past work, avoid repetition

#### Step 4: Reference Fiori Documentation
- **Directory**: `docs/fiori/`
- **Start with**: `docs/fiori/README.md`
- **Contains**:
  - SAP Fiori design guidelines (11,000 words)
  - SAPUI5 API reference (10 controls)
  - Implementation checklists
  - Code examples
- **Time**: Reference as needed

**FAILURE TO FOLLOW THESE STEPS**:
- ❌ Results in wasted time re-investigating known topics
- ❌ Violates mandatory development guidelines
- ❌ Creates duplicate work
- ❌ May skip required testing/documentation

### For Human Developers

**Day 1: Setup (2-3 hours)**

1. **Clone Repository**
   ```bash
   git clone https://github.com/d031182/steel_thread_on_sap.git
   cd steel_thread_on_sap
   ```

2. **Read Core Documents** (1 hour)
   - This file (DEVELOPER_ONBOARDING_GUIDE.md)
   - `.clinerules` - Development standards
   - `README.md` - Project overview
   - `PROJECT_TRACKER.md` - Recent activity

3. **Set Up Environment** (30 min)
   ```bash
   # Python environment
   cd backend
   pip install -r requirements.txt
   
   # Test core infrastructure
   cd ../core/backend
   python test_core_infrastructure.py
   ```

4. **Browse Documentation** (30 min)
   - `docs/fiori/` - Fiori/UI5 guidelines
   - `docs/hana-cloud/` - HANA integration
   - `docs/p2p/` - Business context

5. **Run Application** (30 min)
   ```bash
   # Start Flask backend
   cd backend
   python app.py
   
   # Open browser
   # http://localhost:5000
   ```

---

## Project Overview

### What We're Building

**P2P Data Products Application** - Enterprise SAP Fiori application for Procure-to-Pay data management on SAP HANA Cloud.

### Business Context

**Procure-to-Pay (P2P)**: End-to-end business process from purchasing goods/services to making payments.

**Key Entities**:
- Purchase Orders (PO)
- Service Entry Sheets (SES)
- Supplier Invoices
- Suppliers
- Payment Terms
- Journal Entries

**Use Cases**:
- View and query P2P data products
- Execute SQL on HANA Cloud
- Validate data consistency
- Manage application features
- Monitor application logs

### Key Features

| Feature | Status | Description |
|---------|--------|-------------|
| Data Products | ✅ Module | View P2P data products from HANA |
| HANA Connection | ✅ Module | Connect to SAP HANA Cloud |
| SQL Execution | ✅ Module | Execute queries with formatting |
| Feature Manager | ✅ Module | Toggle features dynamically |
| Application Logging | ✅ Module | Persistent SQLite logging |
| Debug Mode | ✅ Module | Enhanced debugging UI |
| CSN Validation | ⏳ Module | Validate CSN against HANA |
| API Playground | ⏳ Module | Universal API tester |

### Technology Stack

**Backend**:
- **Language**: Python 3.x
- **Framework**: Flask (web server)
- **Database**: SQLite (logging), SAP HANA Cloud (data)
- **Libraries**: hdbcli (HANA), requests

**Frontend**:
- **Framework**: SAP UI5 / OpenUI5
- **Approach**: Pure JavaScript (NOT XML views)
- **Theme**: SAP Horizon
- **Style**: Fiori Design Guidelines

**Infrastructure**:
- **Architecture**: Modular (plug-and-play modules)
- **Version Control**: Git + GitHub
- **Testing**: Python unit tests (Node.js environment)
- **Scripts**: PowerShell

---

## Documentation Map

### Essential Reading (Must Read)

| Document | Purpose | Time | Priority |
|----------|---------|------|----------|
| `.clinerules` | Development standards | 15 min | ⭐⭐⭐⭐⭐ |
| `PROJECT_TRACKER.md` | Project history | 10 min | ⭐⭐⭐⭐⭐ |
| `docs/fiori/README.md` | Fiori/UI5 navigation | 10 min | ⭐⭐⭐⭐⭐ |
| `core/README.md` | Core infrastructure | 10 min | ⭐⭐⭐⭐ |
| This document | Onboarding guide | 2 hours | ⭐⭐⭐⭐⭐ |

### Reference Documentation (As Needed)

**Fiori/UI5**:
- `docs/fiori/FIORI_DESIGN_SCRAPING_REPORT.md` - 11,000-word complete guide
- `docs/fiori/SAPUI5_API_QUICK_REFERENCE.md` - API reference for 10 controls
- `docs/fiori/SAP_FIORI_DESIGN_GUIDELINES.md` - Core principles

**HANA Cloud**:
- `docs/hana-cloud/HANA_CLOUD_GETTING_STARTED_SUMMARY.md` - Getting started
- `docs/hana-cloud/DATA_PRODUCT_SUPPORT_IN_HANA_CLOUD.md` - Data products
- `docs/hana-cloud/HANA_CLOUD_PRIVILEGES_GUIDE.md` - Permissions

**P2P Business**:
- `docs/p2p/P2P_COMPLETE_WORKFLOW_README.md` - Business process
- `docs/p2p/P2P_DATA_PRODUCTS_GAP_ANALYSIS.md` - Data coverage

**Architecture**:
- `docs/planning/architecture/MODULAR_APPLICATION_ARCHITECTURE_PLAN.md`
- `docs/planning/architecture/FUTURE_PROOF_MODULE_ARCHITECTURE.md`

### Module-Specific Documentation

Each module has its own README:
- `modules/feature-manager/README.md`
- `modules/api-playground/README.md`
- `modules/application_logging/` (docs inside)
- etc.

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Browser)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │         SAP UI5 Application                      │   │
│  │  • Pure JavaScript (no XML views)                │   │
│  │  • SAP Horizon theme                             │   │
│  │  • Fiori design patterns                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│                 Backend (Flask Server)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Core Infrastructure                    │   │
│  │  • Module Registry (auto-discovery)              │   │
│  │  • Path Resolver (environment-agnostic)          │   │
│  │  • Configuration Management                      │   │
│  └──────────────────────────────────────────────────┘   │
│                          ↓                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │               Plug-in Modules                     │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐    │   │
│  │  │ Feature   │  │   API     │  │ App       │    │   │
│  │  │ Manager   │  │ Playground│  │ Logging   │    │   │
│  │  └───────────┘  └───────────┘  └───────────┘    │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐    │   │
│  │  │   Data    │  │   HANA    │  │   SQL     │    │   │
│  │  │ Products  │  │Connection │  │ Execution │    │   │
│  │  └───────────┘  └───────────┘  └───────────┘    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓ HDBCLI
┌─────────────────────────────────────────────────────────┐
│              SAP HANA Cloud Database                     │
│  • P2P Data Products (CSN-based views)                   │
│  • Business Data Context (BDC)                           │
│  • SQL query execution                                   │
└─────────────────────────────────────────────────────────┘
```

### Module Architecture ⭐

**Core Principle**: Plug-and-play modular system

**How It Works**:
1. Each module lives in `modules/[module-name]/`
2. Each module has a `module.json` configuration file
3. Core infrastructure auto-discovers all modules
4. Modules register their APIs automatically
5. Add/remove modules by adding/removing folders

**Module Structure**:
```
modules/[module-name]/
├── module.json          # Configuration & metadata
├── README.md           # Module documentation
├── backend/            # Python backend code
│   ├── __init__.py
│   └── api.py         # Flask routes
├── frontend/           # UI5 frontend code (optional)
│   ├── view.xml
│   └── controller.js
├── templates/          # HTML templates (optional)
├── docs/               # Module-specific docs
└── tests/              # Module tests
```

**Benefits**:
- ✅ Zero coupling between modules
- ✅ Independent development
- ✅ Easy to add/remove features
- ✅ Self-documenting (module.json)
- ✅ Testable in isolation

---

## Development Workflow

### 7 Mandatory Requirements ⭐ CRITICAL

Every feature MUST follow ALL 7 requirements:

1. ✅ **API-First** - Business logic before UI
2. ✅ **Testable Without UI** - Node.js unit tests
3. ✅ **Fiori Compliant** - SAP UI5 + Horizon theme
4. ✅ **Documented** - Dedicated feature documentation file
5. ✅ **Logged** - Application logging for AI troubleshooting
6. ✅ **Version Controlled** - Git commits with clear messages
7. ✅ **Tracker Updated** - PROJECT_TRACKER.md entry

**NO EXCEPTIONS**: These aren't optional. See `.clinerules` for enforcement policy.

### Feature Development Checklist

```
Phase 1: Planning (1-2 hours)
- [ ] Check knowledge graph for existing work
- [ ] Read relevant documentation
- [ ] Design API architecture
- [ ] Plan UI components
- [ ] Create implementation plan document
- [ ] Estimate time (include tests + docs!)

Phase 2: API Development (2-4 hours)
- [ ] Create API file in module's backend/
- [ ] Implement business logic (zero UI dependencies)
- [ ] Add JSDoc comments
- [ ] Use dependency injection
- [ ] Handle errors properly

Phase 3: Testing (1-2 hours)
- [ ] Create test file in tests/
- [ ] Write unit tests (100% method coverage)
- [ ] Test success + error scenarios
- [ ] Run in Node.js (not browser!)
- [ ] Verify all tests pass

Phase 4: UI Integration (2-4 hours)
- [ ] Select SAP UI5 controls
- [ ] Follow Fiori spacing system
- [ ] Use Horizon theme
- [ ] Wire APIs to UI
- [ ] Test responsive design

Phase 5: Documentation (1 hour)
- [ ] Create feature documentation file
- [ ] Update PROJECT_TRACKER.md
- [ ] Update memory tracker
- [ ] Update README if needed

Phase 6: Verification (30 min)
- [ ] Run all tests
- [ ] Test in browser
- [ ] Verify Fiori compliance
- [ ] User acceptance testing
```

**Total Time**: 8-14 hours per feature

---

## Module System

### Core Infrastructure

**Location**: `core/backend/`

**Components**:
1. **Module Registry** (`module_registry.py`)
   - Auto-discovers modules from `modules/` directory
   - Reads `module.json` from each module
   - Provides query API (get_all, get_by_category, etc.)
   - <10ms discovery time

2. **Path Resolver** (`path_resolver.py`)
   - Environment-agnostic path management
   - Configurable via `core/config/paths.json`
   - Absolute path resolution

**Usage**:
```python
from core.backend.module_registry import ModuleRegistry
from core.backend.path_resolver import PathResolver

# Initialize
registry = ModuleRegistry()
resolver = PathResolver()

# Get all modules
modules = registry.get_all_modules()
# {'feature-manager': {...}, 'api-playground': {...}}

# Get modules directory path
modules_dir = resolver.get('modules_dir')
```

### Creating a New Module

**Step 1: Create Directory Structure**
```bash
mkdir -p modules/my-feature/{backend,frontend,templates,docs,tests}
```

**Step 2: Create module.json**
```json
{
  "name": "my-feature",
  "displayName": "My Feature",
  "version": "1.0.0",
  "description": "What this module does",
  "category": "Business Logic",
  "author": "Your Name",
  "enabled": true,
  "requiresHana": false,
  "permissions": ["read", "write"],
  "structure": {
    "backend": "backend",
    "frontend": "frontend",
    "tests": "tests"
  }
}
```

**Step 3: Create Backend API**
```python
# modules/my-feature/backend/api.py
from flask import Blueprint, jsonify

bp = Blueprint('my_feature', __name__, url_prefix='/api/my-feature')

@bp.route('/', methods=['GET'])
def get_items():
    """Get all items"""
    return jsonify({
        'success': True,
        'items': []
    })

# Export blueprint for auto-registration
__all__ = ['bp']
```

**Step 4: Create Tests**
```python
# modules/my-feature/tests/test_api.py
def test_get_items():
    # Test implementation
    pass
```

**Step 5: Document**
```markdown
# modules/my-feature/README.md
```

**That's it!** The module is now auto-discovered and available.

---

## Fiori/UI5 Development

### CRITICAL: JavaScript vs XML ⭐

**We PREFER pure JavaScript over XML views**

**Why JavaScript**:
- ✅ Much easier to debug (Browser DevTools work perfectly)
- ✅ Console.log, breakpoints, step-through debugging
- ✅ Can see actual object instances and properties
- ✅ More reliable, works immediately
- ❌ XML is opaque and "ugly" to debug

**Pattern**:
```javascript
// ✅ GOOD: Pure JavaScript
var oPage = new sap.m.Page({
    title: "My Page",
    content: [
        new sap.m.Button({
            text: "Click Me",
            press: function() {
                console.log("Clicked!"); // Easy to debug!
            }
        })
    ]
});
oPage.placeAt("content");

// ❌ AVOID: XML views (unless user requests)
// Harder to debug, less visible
```

### Fiori Compliance Checklist

**Every UI component must**:
- [ ] Use SAP UI5 controls (not custom HTML/CSS)
- [ ] Use SAP Horizon theme
- [ ] Follow Fiori spacing system
- [ ] Support responsive design (S/M/L/XL)
- [ ] Use standard Fiori patterns
- [ ] Be accessible (keyboard, screen reader)

### Quick Reference by Component Type

| Need | Use | Reference |
|------|-----|-----------|
| Page layout | `sap.m.Page` | SAPUI5_API_QUICK_REFERENCE.md |
| Table | `sap.m.Table` + growing mode | FIORI_DESIGN_SCRAPING_REPORT.md §3 |
| Form | `sap.m.VBox` + validation | FIORI_DESIGN_SCRAPING_REPORT.md §2 |
| Tabs | `sap.m.IconTabBar` | SAPUI5_API_QUICK_REFERENCE.md |
| Messages | `sap.m.MessageStrip` | FIORI_DESIGN_SCRAPING_REPORT.md §4 |
| Input | `sap.m.Input` + value states | SAPUI5_API_QUICK_REFERENCE.md |

### Debugging SAP UI5 Issues

**Problem**: Content not visible, white space, narrow panel

**Solution Approach** (Proven Pattern):

1. **Start Simple**
   ```javascript
   // Just title + one control
   var oPage = new sap.m.Page({
       title: "Test",
       content: [new sap.m.Text({text: "Hello"})]
   });
   ```

2. **Add API Call**
   ```javascript
   fetch("/api/data")
       .then(r => r.json())
       .then(data => console.log("Got:", data));
   ```

3. **Add Controls Incrementally**
   - One list → works? ✅
   - Add switches → works? ✅
   - Add categories → works? ✅
   - Add IconTabBar → works? ✅

4. **If Issues**: Check console.log, verify:
   - Is API returning data?
   - Is data structure correct?
   - Are controls rendering?
   - Is page height set correctly?

**Key Learning**: Simple JavaScript version works immediately. Build complexity incrementally.

---

## Testing Standards

### Requirements

**Every API must have**:
- ✅ Unit tests in Node.js (not browser)
- ✅ 100% method coverage
- ✅ Success + error scenarios tested
- ✅ Mock dependencies for isolation
- ✅ Tests run in <5 seconds

### Test File Structure

```javascript
/**
 * Unit Tests for [Feature] API
 * 
 * Run with: node tests/[feature]API.test.js
 */

class TestRunner {
    constructor() {
        this.passed = 0;
        this.failed = 0;
    }
    
    async test(name, fn) {
        try {
            await fn();
            this.passed++;
            console.log(`✅ ${name}`);
        } catch (error) {
            this.failed++;
            console.error(`❌ ${name}`);
            console.error(`   ${error.message}`);
        }
    }
    
    async run() {
        // Tests here
        await this.test("Test 1", async () => {
            // Test implementation
        });
        
        // Summary
        console.log(`\n${this.passed}/${this.passed + this.failed} tests passing`);
        return this.failed === 0;
    }
}

// Execute
const runner = new TestRunner();
runner.run().then(success => {
    process.exit(success ? 0 : 1);
});
```

### Current Test Status

- ✅ Core Infrastructure: 19/19 tests passing (100%)
- ✅ HANA Connection API: 10/10 tests passing
- ✅ SQL Execution API: 15/15 tests passing
- ✅ Result Formatter API: 15/15 tests passing
- ✅ **Total**: 59/59 tests passing (100%)

---

## Git Workflow

### Daily Workflow

**Morning**:
```bash
git checkout main
git pull origin main
git status
```

**During Development**:
```bash
# After completing a logical change
git status
git add <files>
git commit -m "[Category] Clear message"
```

**End of Day** (User decides when):
```bash
# User will push when ready
git push origin main
```

### Commit Message Format

```
[Category] Brief description (max 72 chars)

Optional detailed explanation:
- What was changed
- Why it was changed
- Impact of the change
```

**Categories**:
- `[Feature]` - New functionality
- `[Fix]` - Bug fixes
- `[Refactor]` - Code improvements
- `[Docs]` - Documentation
- `[Test]` - Tests
- `[Config]` - Configuration
- `[Chore]` - Maintenance

**Example**:
```bash
git commit -m "[Feature] Add feature manager enhanced UI

- Created configurator_enhanced.html with IconTabBar
- Added statistics panel and Export/Import buttons
- Pure JavaScript SAP UI5 (no XML)
- All features working (minor console error documented)"
```

### AI Assistant Git Policy ⭐ IMPORTANT

**AI CAN**:
- ✅ `git add` - Stage files
- ✅ `git commit` - Commit changes
- ✅ `git tag` - Create tags

**AI CANNOT**:
- ❌ `git push` - Push to GitHub
- ❌ Any remote operations

**Why**: User maintains full control over what goes to GitHub

**Exception**: AI can push ONLY when user explicitly says "push to git" or "push to GitHub"

### Git Tagging

**Create tags for**:
- ✅ Major feature completion
- ✅ Before risky refactoring
- ✅ Production milestones (v1.0, v2.0)
- ✅ End of development phase

**Format**:
```bash
git tag -a v0.10-feature-name -m "Version 0.10 - Feature description
- Achievement 1
- Achievement 2"
```

**Current Version**: v0.9-folder-reorganization

---

## Common Tasks

### Task 1: Add a New Feature

**Time**: 8-14 hours

1. **Check knowledge graph** - Has this been researched before?
2. **Read `.clinerules`** - Understand requirements
3. **Create module** - Follow module structure
4. **Implement API** - Zero UI dependencies
5. **Write tests** - 100% coverage in Node.js
6. **Build UI** - Pure JavaScript SAP UI5
7. **Document** - Create feature doc + update tracker
8. **Commit** - Clear commit messages
9. **Get user approval** - Present completion

### Task 2: Debug an Issue

**Time**: 30 minutes - 2 hours

1. **Check application logs** ⭐ ALWAYS FIRST
   - Click "Logs" button in app (top right)
   - Look for ERROR and WARNING entries
   - Analyze sequence of events

2. **Identify root cause**
   - Use log context to understand what failed
   - Check error codes (HANA error codes documented)
   - Trace request flow

3. **Fix issue**
   - Make minimal changes
   - Test thoroughly
   - Document solution

4. **Prevent recurrence**
   - Add tests for the bug
   - Update documentation
   - Add logging if needed

### Task 3: Update Documentation

**Time**: 30 minutes - 2 hours

1. **Identify what needs documenting**
   - New feature?
   - Changed behavior?
   - Better explanation needed?

2. **Choose correct location**
   - Feature docs: `docs/planning/features/`
   - Architecture: `docs/planning/architecture/`
   - Fiori/UI5: `docs/fiori/`
   - HANA: `docs/hana-cloud/`
   - P2P business: `docs/p2p/`

3. **Use consistent format**
   - Markdown (.md files)
   - Clear headings
   - Code examples
   - Version information

4. **Update index**
   - Update README in directory
   - Add to quick navigation
   - Update .clinerules if needed

5. **Commit**
   ```bash
   git add docs/
   git commit -m "[Docs] Document [topic]"
   ```

### Task 4: Run the Application

**Development Mode**:
```bash
# Terminal 1: Start Flask backend
cd backend
python app.py
# Runs on http://localhost:5000

# Terminal 2: Watch for changes (optional)
# If you have auto-reload
```

**Access Application**:
- Main app: http://localhost:5000
- Feature Manager: http://localhost:5000/feature-manager-enhanced
- API Playground: http://localhost:5000/api-playground

### Task 5: Connect to HANA Cloud

**Prerequisites**:
1. SAP BTP account with HANA Cloud instance
2. IP address added to HANA allowlist
3. User credentials with data product privileges

**Steps**:
1. Get connection details from SAP BTP Cockpit
2. Update `default-env.json` (git-ignored, not committed!)
3. Test connection:
   ```python
   from modules.hana_connection.backend import api
   result = api.test_connection()
   ```

**Common Issues**:
- Connection refused → IP not in allowlist
- Authentication failed → Wrong credentials
- No privileges → Need SELECT on BDC views

**Reference**: `docs/hana-cloud/` directory

---

## Troubleshooting

### Common Issues

#### Issue: "Tests are failing"

**Solution**:
1. Check if running in Node.js (not browser)
2. Verify mock dependencies are set up
3. Check API has zero UI dependencies
4. Run tests individually to isolate issue

#### Issue: "UI not displaying content"

**Solution**:
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify API is returning data (console.log)
4. Start with simple version, add complexity incrementally
5. Ensure page height is set (html, body, #content { height: 100% })

#### Issue: "HANA connection not working"

**Solution**:
1. Check application logs (Logs button)
2. Look for HANA error codes
3. Common fixes:
   - Error -10709: IP not in allowlist
   - Error 258: Invalid credentials
   - Error 259: Table/view not found
4. Reference: `docs/hana-cloud/TROUBLESHOOTING.md`

#### Issue: "Module not being discovered"

**Solution**:
1. Verify `module.json` exists in module root
2. Check JSON is valid (no syntax errors)
3. Ensure `enabled: true` in module.json
4. Run registry test: `python core/backend/test_core_infrastructure.py`

---

## Resources

### Documentation Locations

```
docs/
├── fiori/                  # Fiori/UI5 guidelines ⭐
│   ├── README.md          # Navigation guide
│   ├── FIORI_DESIGN_SCRAPING_REPORT.md  # 11K words
│   └── SAPUI5_API_QUICK_REFERENCE.md    # API ref
├── hana-cloud/            # HANA Cloud guides
│   ├── HANA_CLOUD_GETTING_STARTED_SUMMARY.md
│   └── DATA_PRODUCT_SUPPORT_IN_HANA_CLOUD.md
├── p2p/                   # Business context
│   └── P2P_COMPLETE_WORKFLOW_README.md
└── planning/              # Architecture & plans
    ├── architecture/
    └── features/
```

### External Resources

- **SAP Fiori Design**: https://experience.sap.com/fiori-design-web/
- **SAPUI5 SDK**: https://sapui5.hana.ondemand.com/sdk/
- **SAP HANA Cloud Docs**: https://help.sap.com/docs/hana-cloud
- **SAP Community**: https://community.sap.com/

### Getting Help

**For AI Assistants**:
1. Check knowledge graph (MCP memory)
2. Search existing documentation
3. Check PROJECT_TRACKER.md for similar work
4. Check application logs for issues

**For Human Developers**:
1. Read relevant documentation
2. Check PROJECT_TRACKER.md for examples
3. Ask project owner
4. Consult SAP Community

---

## Development Standards Summary

### Code Quality
- ✅ Clean, readable code
- ✅ JSDoc comments on public methods
- ✅ Proper error handling
- ✅ No console.log in production
- ✅ Files < 1000 lines (split if larger)

### Performance
- ✅ API methods < 100ms response
- ✅ Test execution < 5 seconds total
- ✅ UI interactions < 300ms
- ✅ No memory leaks

### Security
- ✅ Input validation
- ✅ XSS prevention
- ✅ No hardcoded credentials
- ✅ Secure storage practices

---

## Success Criteria

A feature is complete when:

- [x] Planning document created
- [x] APIs implemented (zero UI dependencies)
- [x] Tests written (100% method coverage)
- [x] All tests passing in Node.js
- [x] UI integrated (Fiori compliant)
- [x] Documentation complete
- [x] PROJECT_TRACKER updated
- [x] Memory tracker updated
- [x] User approved

**Minimum to Merge/Deploy**:
1. All tests passing (100%)
2. API-first proven (works in Node.js)
3. Fiori compliant (uses UI5 controls)
4. Documented (dedicated file + tracker)
5. User approved

---

## Key Learnings

### From Project Experience

**API-First Works** ✅:
- Version 2.2: 40/40 tests passing without browser
- APIs work in browser, Node.js, CLI, servers
- Clear separation enables better testing

**Pure JavaScript Better for Debugging** ✅:
- Browser DevTools: console.log, breakpoints, inspection
- XML views: opaque, hard to debug
- Developer quote: XML is "ugly" to debug

**Incremental Complexity** ✅:
- Start simple → test → add complexity → test
- Complex attempts are OK, but pivot if debugging takes too long
- Simple versions work immediately

**Knowledge Graph Saves Time** ✅:
- Checking memory first avoids re-research
- 90 minutes saved per session
- Build on previous work

---

## Next Steps

### Your First Day

**Hour 1: Reading**
- [ ] Read this document completely
- [ ] Scan `.clinerules`
- [ ] Browse `PROJECT_TRACKER.md`

**Hour 2: Setup**
- [ ] Clone repository
- [ ] Install dependencies
- [ ] Run core infrastructure tests
- [ ] Start Flask application

**Hour 3: Explore**
- [ ] Browse existing modules
- [ ] Read module documentation
- [ ] Test existing features in browser
- [ ] Understand module structure

**Hour 4-8: First Task**
- [ ] Pick a simple task (or get assigned one)
- [ ] Follow development workflow
- [ ] Create your first module or feature
- [ ] Get feedback from project owner

### Becoming Productive

**Week 1**: Learn project structure, standards, patterns  
**Week 2**: Implement first feature with guidance  
**Week 3**: Independent module development  
**Week 4**: Help others, improve documentation

---

## 🎉 Welcome to the Team!

You now have everything you need to be productive in the P2P Data Products project.

**Remember**:
1. ✅ Check knowledge graph FIRST (AI) or read docs (human)
2. ✅ Follow ALL 7 mandatory requirements
3. ✅ Pure JavaScript for UI5 (easier debugging!)
4. ✅ Test in Node.js (100% coverage)
5. ✅ Document everything
6. ✅ Use application logs for troubleshooting
7. ✅ Commit frequently with clear messages

**Questions?**
- Check `PROJECT_TRACKER.md` for examples
- Reference documentation in `docs/`
- Ask project owner

---

**Status**: ✅ **ONBOARDING GUIDE COMPLETE**

**Version**: 1.0

**Last Updated**: January 24, 2026

---

*Happy Coding!* 🚀