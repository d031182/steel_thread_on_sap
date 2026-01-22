# Development Guidelines & Best Practices

**Project**: P2P Data Products Application  
**Purpose**: Standards and rules for feature development  
**Version**: 1.0  
**Last Updated**: January 22, 2026

---

## 🎯 Core Development Principles

This document defines the mandatory standards and best practices for developing new features and capabilities in the P2P Data Products application.

---

## 1. API-First Approach ⭐ MANDATORY

### Principle
**Always implement business logic as APIs before building UI**

### Requirements

**✅ DO:**
- Design and implement APIs with zero UI dependencies
- Create pure business logic that works in any environment (browser, Node.js, CLI)
- Use dependency injection for external dependencies (storage, network, etc.)
- Return data structures, not DOM elements or UI components
- Make all API methods async (Promise-based)
- Document APIs with JSDoc comments

**❌ DON'T:**
- Mix business logic with UI code
- Use `document`, `window`, or browser-specific APIs in business logic
- Hard-code UI frameworks in API layer
- Assume browser environment in core logic

### Example - Correct API-First Pattern

```javascript
/**
 * SQL Execution API - Pure business logic
 * @class
 */
export class SQLExecutionAPI {
    /**
     * @param {StorageService} storageService - Injected dependency
     * @param {HanaConnectionAPI} connectionAPI - Injected dependency
     */
    constructor(storageService, connectionAPI) {
        this.storage = storageService;
        this.connectionAPI = connectionAPI;
    }

    /**
     * Execute SQL query
     * @param {string} instanceId - Instance identifier
     * @param {string} sql - SQL statement
     * @param {Object} options - Execution options
     * @returns {Promise<Object>} Query result
     */
    async executeQuery(instanceId, sql, options = {}) {
        // Pure business logic - no UI coupling
        const result = await this._execute(instanceId, sql, options);
        await this.saveQueryHistory(result);
        return result;
    }
}

// Later: UI consumes the API
import { sqlExecutionAPI } from './js/api/sqlExecutionAPI.js';

button.addEventListener('click', async () => {
    const result = await sqlExecutionAPI.executeQuery(id, sql);
    displayResults(result); // UI layer handles display
});
```

### Benefits Proven
- ✅ **Version 2.2**: 40/40 tests passing without any browser
- ✅ **Reusability**: APIs work in browser, Node.js, CLI tools, servers
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Quality**: 100% test coverage achieved

---

## 2. Testability Without UI ⭐ MANDATORY

### Principle
**All new services and capabilities must be testable in Node.js without any UI**

### Requirements

**Test Suite Standards:**
- ✅ Every API must have unit tests
- ✅ Tests must run in Node.js (not browser)
- ✅ Achieve 100% method coverage
- ✅ Test both success and error scenarios
- ✅ Use mock dependencies for isolation
- ✅ Tests must run in < 5 seconds

**Test File Structure:**
```javascript
/**
 * Unit Tests for [Feature Name] API
 * 
 * Run with: node tests/[feature]API.test.js
 */

import { FeatureAPI } from '../js/api/featureAPI.js';

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
    
    // Helper methods...
}

// Run tests
const runner = new TestRunner();
runner.run().then(success => {
    process.exit(success ? 0 : 1);
});
```

**Mock Dependencies:**
```javascript
// Create mock storage for testing
class MockStorage {
    constructor() {
        this.data = new Map();
    }
    
    async save(key, value) {
        this.data.set(key, value);
        return true;
    }
    
    async load(key) {
        return this.data.get(key);
    }
}

// Inject mock in tests
const mockStorage = new MockStorage();
const api = new FeatureAPI(mockStorage);
```

### Test Coverage Requirements

| Component | Minimum Tests | Status |
|-----------|--------------|--------|
| Each API method | 1 test | Required |
| Error scenarios | 1 per error type | Required |
| Edge cases | As needed | Recommended |
| Integration | Optional | Nice to have |

### Current Test Status
- ✅ HANA Connection API: 10/10 tests passing
- ✅ SQL Execution API: 15/15 tests passing
- ✅ Result Formatter API: 15/15 tests passing
- ✅ **Total**: 40/40 tests (100% pass rate)

---

## 3. SAP Fiori Design Guidelines ⭐ MANDATORY

### Principle
**All UI must follow official SAP Fiori design guidelines**

### Requirements

**Framework:**
- ✅ Use SAP UI5 / OpenUI5 framework
- ✅ Use official SAP UI5 controls (sap.m, sap.f, sap.ui.layout)
- ✅ Use SAP Horizon theme (`sap_horizon`)
- ❌ DO NOT create custom HTML/CSS components when UI5 controls exist

**Design Principles (SAP Fiori 5):**
1. **Role-Based** - Clear purpose and user roles
2. **Responsive** - Mobile, tablet, desktop support
3. **Simple** - Minimal cognitive load
4. **Coherent** - Consistent patterns
5. **Delightful** - Professional appearance

**Spacing System:**
```javascript
// Use official SAP UI5 spacing classes
sapUiContentPadding      // 1rem (16px) - Content areas
sapUiSmallMargin         // 0.5rem (8px) - Small gaps
sapUiMediumMargin        // 1rem (16px) - Medium gaps
sapUiLargeMargin         // 2rem (32px) - Large gaps
sapUiTinyMargin          // 0.25rem (4px) - Fine adjustments
sapUiResponsiveMargin    // Responsive margins
```

**Color Palette:**
```javascript
// SAP Horizon theme colors
Primary Blue:   #0070f2
Success Green:  #107e3e
Error Red:      #b00
Warning Orange: #e9730c
Shell Dark:     #354a5f
Background:     #f5f6f7
```

**Component Selection:**
- Tables: `sap.m.Table` or `sap.ui.table.Table`
- Forms: `sap.ui.layout.form.Form`
- Navigation: `sap.m.IconTabBar`
- Headers: `sap.f.ShellBar`
- Dialogs: `sap.m.Dialog`
- Lists: `sap.m.List`

**Reference Documentation:**
- Main Guide: https://experience.sap.com/fiori-design-web/
- UI5 Controls: https://sapui5.hana.ondemand.com/
- Design Guidelines: `docs/fiori/SAP_FIORI_DESIGN_GUIDELINES.md`

### Quality Checklist
- [ ] Uses SAP UI5 framework
- [ ] Uses Horizon theme
- [ ] Uses standard controls only
- [ ] Follows spacing system
- [ ] Responsive design tested
- [ ] Accessible (keyboard, screen reader)
- [ ] No custom HTML/CSS (unless necessary)

---

## 4. Feature Documentation ⭐ MANDATORY

### Principle
**Each new feature must have comprehensive documentation in a dedicated file**

### Requirements

**Documentation File Structure:**

```markdown
# [Feature Name] - Implementation Guide

**Feature**: [Name]
**Version**: 1.0
**Date**: [Date]
**Status**: [Planning / In Progress / Complete]

---

## Overview

Brief description of the feature and its purpose.

## Requirements

What the feature must accomplish:
1. Requirement 1
2. Requirement 2
3. ...

## Architecture

### API Layer
- API file: `js/api/[feature]API.js`
- Methods: [list methods]
- Dependencies: [list dependencies]

### Service Layer (if needed)
- Service files
- Utilities

### UI Layer
- UI components
- Fiori controls used
- Integration points

## Implementation Plan

**Phase 1: API Development** (X hours)
- [ ] Task 1
- [ ] Task 2
- [ ] ...

**Phase 2: Testing** (X hours)
- [ ] Task 1
- [ ] Task 2

**Phase 3: UI Integration** (X hours)
- [ ] Task 1
- [ ] Task 2

## API Reference

### Method: methodName()
**Purpose**: What it does
**Parameters**: List parameters
**Returns**: Return type and structure
**Example**:
```javascript
const result = await api.methodName(params);
```

## Test Coverage

- [ ] Unit tests created
- [ ] Tests passing: X/X
- [ ] Coverage: 100%

## UI Components

List of UI5 controls used and their purpose.

## Files Created

1. `path/to/file1.js` - Description
2. `path/to/file2.js` - Description
3. ...

## Usage Examples

### Basic Usage
```javascript
// Code example
```

### Advanced Usage
```javascript
// Code example
```

## Status

Current status and next steps.
```

### Example Documentation Files
- ✅ `SQL_EXECUTION_ENHANCEMENT_PLAN.md` - Planning document
- ✅ `SQL_EXECUTION_API_SUMMARY.md` - Complete summary
- ✅ `HANA_CONNECTION_IMPLEMENTATION_SUMMARY.md` - API summary

### Documentation Locations
- **Planning**: Project root or `docs/` folder
- **API Docs**: Embedded JSDoc comments
- **User Guides**: `docs/` folder
- **Reference**: `README.md` or dedicated guides

---

## 5. Application Logging ⭐ MANDATORY

### Principle
**Use application logging for troubleshooting, workflow understanding, and issue resolution**

### Purpose of Application Logging

The application logging system serves three critical purposes:

#### 1. **Troubleshooting Tool**
- ✅ Identify issues when they occur
- ✅ Understand the sequence of events leading to problems
- ✅ Debug production issues without code changes
- ✅ Monitor system health in real-time

#### 2. **Workflow Understanding**
- ✅ Log essential activities to track application flow
- ✅ Document key decision points and data transformations
- ✅ Show timing and performance metrics
- ✅ Trace requests through the system

#### 3. **AI Assistant Tool** ⭐ PRIMARY PURPOSE
- ✅ **The log is PRIMARILY for the AI assistant to consume**
- ✅ AI uses logs to understand what's happening in the application
- ✅ AI analyzes logs to identify root causes of issues
- ✅ AI references logs when helping developers resolve problems
- ✅ Logs enable AI to provide accurate, context-aware assistance

### What to Log

**Essential Activities** ✅:
```python
# Backend (Flask)
logger.info("Loaded 5 data products from HANA")
logger.info("Query executed successfully: 100 rows, 1644.97ms")
logger.warning("Limiting to first 10 of 120 columns for table SalesOrder")
logger.error("Failed to connect to HANA: Connection timeout")
```

**DO Log:**
- ✅ API endpoint calls (method, path, user)
- ✅ Database queries (SQL, execution time, row count)
- ✅ External service calls (URL, response time, status)
- ✅ Business logic decisions (why path A vs path B)
- ✅ Error conditions (what failed, why, context)
- ✅ Performance metrics (execution times, counts)
- ✅ Configuration changes (what changed, who, when)
- ✅ Authentication/authorization events
- ✅ Data transformations (input → process → output)

**DON'T Log:**
- ❌ Sensitive data (passwords, tokens, PII)
- ❌ Full request/response payloads (too verbose)
- ❌ Every single line of code execution
- ❌ Redundant information
- ❌ Debug statements in production

### Log Levels

Use appropriate log levels:

```python
# INFO - Normal operations, key milestones
logger.info("Processing order #12345")
logger.info("Email sent successfully to user@example.com")

# WARNING - Something unexpected but not critical
logger.warning("Cache miss for key 'product_123', fetching from database")
logger.warning("API rate limit approaching: 950/1000 requests")

# ERROR - Something failed but application continues
logger.error("Failed to send email: SMTP connection refused")
logger.error("Database query timeout after 30 seconds")

# CRITICAL - Severe issue requiring immediate attention
logger.critical("Database connection pool exhausted")
logger.critical("Out of memory error")
```

### Log Format Standards

**Backend (Python):**
```python
# Include context in every log entry
logger.info(f"Query executed successfully: {row_count} rows, {execution_time:.2f}ms")
logger.warning(f"Limiting to first {limit} of {total} columns for table {table_name}")
logger.error(f"Failed to connect to {host}:{port}: {error_message}")
```

**Frontend (JavaScript):**
```javascript
// Use console for development, API logging for production
console.log(`[DataProductsAPI] Fetched ${count} products`);
console.warn(`[SQLExecutionAPI] Query took ${time}ms (slow)`);
console.error(`[HanaConnectionAPI] Connection failed:`, error);
```

### AI Assistant Usage

**How AI Uses Logs:**

1. **Diagnosing Issues:**
   ```
   User: "The query is failing"
   
   AI: *Checks application logs*
       → Sees: "ERROR: Query timeout after 30 seconds"
       → Identifies: Database performance issue
       → Suggests: Optimize query or increase timeout
   ```

2. **Understanding Workflows:**
   ```
   User: "Why is the table limiting columns?"
   
   AI: *Checks application logs*
       → Sees: "WARNING: Limiting to first 10 of 120 columns"
       → Explains: Performance optimization for readability
       → Shows: Where limit is configured
   ```

3. **Root Cause Analysis:**
   ```
   User: "Data products aren't loading"
   
   AI: *Analyzes log sequence*
       → Sees: "INFO: Connecting to HANA..."
       → Sees: "ERROR: Connection refused"
       → Identifies: HANA server unavailable
       → Recommends: Check network, verify server status
   ```

### Implementation

**Backend Setup:**
```python
# Flask app.py
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory log storage for UI access
class MemoryLogHandler(logging.Handler):
    def __init__(self, max_logs=100):
        super().__init__()
        self.logs = []
        self.max_logs = max_logs
    
    def emit(self, record):
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': self.format(record)
        })
        # Keep only last max_logs
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

# Add handler
memory_handler = MemoryLogHandler(max_logs=100)
logger.addHandler(memory_handler)

# API endpoint for logs
@app.route('/api/logs')
def get_logs():
    return jsonify({
        'success': True,
        'logs': memory_handler.logs
    })
```

**Frontend Integration:**
```javascript
// Access logs via API
const logViewerAPI = new LogViewerAPI();
const result = await logViewerAPI.getLogs({ limit: 100 });
console.log('Application logs:', result.logs);
```

### Log Viewer UI

**Location**: Top-right "Logs" button in Fiori app

**Features**:
- ✅ Real-time log viewing
- ✅ Filter by level (INFO, WARNING, ERROR)
- ✅ Color-coded entries
- ✅ Timestamps
- ✅ Refresh capability
- ✅ Clear logs function

**Usage**:
```
1. Click "Logs" button (top right)
2. View application activity
3. Filter by log level if needed
4. Share logs with AI for troubleshooting
```

### Best Practices

**1. Be Specific:**
```python
# BAD
logger.info("Processing data")

# GOOD
logger.info(f"Processing 1,234 orders from 2024-01-01 to 2024-01-31")
```

**2. Include Context:**
```python
# BAD
logger.error("Query failed")

# GOOD
logger.error(f"Query failed for table '{table_name}': {error_details}")
```

**3. Log at Right Level:**
```python
# User successfully logged in → INFO
logger.info(f"User '{username}' logged in successfully")

# User login failed → WARNING (might be wrong password)
logger.warning(f"Failed login attempt for user '{username}'")

# Authentication system crashed → ERROR
logger.error(f"Authentication service unavailable: {error}")
```

**4. Use Structured Data:**
```python
# Include metrics
logger.info(f"API response: {status_code}, {response_time}ms, {bytes_sent} bytes")

# Include IDs for tracing
logger.info(f"Order #{order_id} processed by user #{user_id}")
```

### Benefits

**For Developers:**
- 🔍 Quick issue identification
- 📊 Performance insights
- 🐛 Faster debugging
- 📈 System health monitoring

**For AI Assistant:**
- 🤖 Accurate problem diagnosis
- 💡 Context-aware suggestions
- 🎯 Root cause identification
- 📚 Application behavior learning

**For Users:**
- ✅ Faster issue resolution
- 📱 Real-time system visibility
- 🛡️ Proactive problem detection
- 📞 Better support experience

---

## 6. Project Tracker Updates ⭐ MANDATORY

### Principle
**Always update PROJECT_TRACKER_REFACTORED.md when completing features**

### Purpose of Project Tracker

The `PROJECT_TRACKER_REFACTORED.md` serves as the **complete historical record** of all project work:

**Key Purposes:**
1. **Historical Documentation** - Complete timeline of all development work
2. **Knowledge Preservation** - Captures decisions, problems solved, and solutions
3. **Progress Tracking** - Shows evolution from initial concept to current state
4. **Onboarding Tool** - New developers can understand project history
5. **Reference Guide** - Find how previous features were implemented
6. **Decision Log** - Documents why choices were made
7. **Metrics Record** - Tracks development time, code changes, test coverage
8. **Success Stories** - Shows proven patterns and working examples

**What Gets Tracked:**
- ✅ Feature implementations (new capabilities)
- ✅ Bug fixes (production issues resolved)
- ✅ Architecture changes (refactoring, migrations)
- ✅ Documentation updates (major docs created)
- ✅ Performance improvements (optimizations)
- ✅ Testing milestones (test coverage achievements)
- ✅ User feedback (requests and resolutions)

**Benefits:**
- **For AI Assistant**: Maintains context across sessions, learns from past work
- **For Developers**: Understand project evolution and proven patterns
- **For Users**: See what's been delivered and what's coming
- **For Maintenance**: Quick reference for how features work
- **For Quality**: Track that guidelines are being followed

### Requirements

**When to Update:**
- ✅ After completing planning phase
- ✅ After implementing APIs
- ✅ After completing tests
- ✅ After UI integration
- ✅ After final verification

**Version Entry Template:**

```markdown
### Version X.X - [Feature Name] (YYYY-MM-DD, HH:MM AM/PM)

**Objective**: Brief description of what was accomplished

**User Requirements**:
1. Requirement 1
2. Requirement 2
3. ...

**Work Performed**:

1. ✅ **[Task Category 1]**
   - Details
   - Metrics
   - Status

2. ✅ **[Task Category 2]**
   - Details
   - Metrics
   - Status

**[Feature] Capabilities**:

```javascript
// Code examples showing key features
```

**Architecture Benefits**:

Key improvements and patterns applied.

**Progress Metrics**:

| Metric | Value | Status |
|--------|-------|--------|
| Metric 1 | Value | Status |
| Metric 2 | Value | Status |

**Files Created**:
- ✅ `path/to/file1` - Description
- ✅ `path/to/file2` - Description

**Status**: ✅ **COMPLETED** - [Summary]

---
```

### Memory Tracker Updates

After completing a significant feature, also update the memory tracker:

```javascript
// Use MCP memory tool to store knowledge
<use_mcp_tool>
<server_name>github.com/modelcontextprotocol/servers/tree/main/src/memory</server_name>
<tool_name>create_entities</tool_name>
<arguments>
{
  "entities": [
    {
      "name": "Feature_Name",
      "entityType": "api_component",
      "observations": [
        "Key fact 1",
        "Key fact 2",
        "..."
      ]
    }
  ]
}
</arguments>
</use_mcp_tool>
```

---

## 📋 Feature Development Workflow

### Complete Workflow Checklist

**Phase 1: Planning** (1-2 hours)
- [ ] Understand user requirements
- [ ] Research existing patterns
- [ ] Design API architecture
- [ ] Plan UI components
- [ ] Create implementation plan document
- [ ] Estimate time and effort

**Phase 2: API Development** (2-4 hours)
- [ ] Create API file in `js/api/`
- [ ] Implement business logic methods
- [ ] Add JSDoc comments
- [ ] Use dependency injection
- [ ] Handle errors properly
- [ ] Ensure zero UI dependencies

**Phase 3: Testing** (1-2 hours)
- [ ] Create test file in `tests/`
- [ ] Write unit tests (100% method coverage)
- [ ] Test success scenarios
- [ ] Test error scenarios
- [ ] Run tests in Node.js
- [ ] Verify all tests pass

**Phase 4: UI Integration** (2-4 hours)
- [ ] Select appropriate SAP UI5 controls
- [ ] Follow Fiori spacing system
- [ ] Use Horizon theme
- [ ] Wire APIs to UI
- [ ] Test responsive design
- [ ] Verify accessibility

**Phase 5: Documentation** (1 hour)
- [ ] Create feature documentation file
- [ ] Update PROJECT_TRACKER_REFACTORED.md
- [ ] Update memory tracker
- [ ] Update README if needed
- [ ] Add usage examples

**Phase 6: Verification** (30 minutes)
- [ ] Run all tests
- [ ] Test in browser
- [ ] Verify Fiori compliance
- [ ] Check responsive design
- [ ] User acceptance testing

---

## 🎯 Quality Standards

### Code Quality
- ✅ Clean, readable code
- ✅ Consistent naming conventions
- ✅ Proper error handling
- ✅ No console.log in production code
- ✅ JSDoc comments on all public methods
- ✅ File size < 1000 lines (split if larger)

### Performance Standards
- ✅ API methods < 100ms response time
- ✅ Test execution < 5 seconds total
- ✅ UI interactions < 300ms
- ✅ No memory leaks
- ✅ Efficient data structures

### Security Standards
- ✅ Input validation
- ✅ XSS prevention (escape HTML)
- ✅ No hardcoded credentials
- ✅ Secure storage practices
- ✅ Error messages don't leak sensitive info

---

## 📚 Reference Examples

### Proven Implementations

**Version 2.1 - HANA Connection API**
- ✅ Perfect API-first example
- ✅ 10/10 tests passing
- ✅ Zero UI dependencies
- ✅ Full JSDoc documentation
- 📄 See: `js/api/hanaConnectionAPI.js`

**Version 2.2 - SQL Execution APIs**
- ✅ Two APIs with clean separation
- ✅ 30/30 tests passing
- ✅ Complete feature documentation
- ✅ Comprehensive summary
- 📄 See: `SQL_EXECUTION_API_SUMMARY.md`

### Design Pattern Examples

**Dependency Injection:**
```javascript
constructor(storageService = new StorageService()) {
    this.storage = storageService; // Mockable!
}
```

**Promise-Based APIs:**
```javascript
async executeQuery(instanceId, sql) {
    return await this._execute(instanceId, sql);
}
```

**Error Handling:**
```javascript
try {
    const result = await api.execute();
    return { success: true, data: result };
} catch (error) {
    return {
        success: false,
        error: {
            message: error.message,
            code: 'ERROR_CODE',
            details: { /* additional info */ }
        }
    };
}
```

---

## ✅ Success Criteria

### Feature Completion Checklist

A feature is considered complete when:

- [x] **Planning document created** with architecture and plan
- [x] **APIs implemented** with zero UI dependencies
- [x] **Tests written** with 100% method coverage
- [x] **All tests passing** in Node.js environment
- [x] **UI integrated** following Fiori guidelines
- [x] **Documentation complete** in dedicated file
- [x] **PROJECT_TRACKER updated** with version entry
- [x] **Memory tracker updated** with key knowledge
- [x] **User acceptance** - Feature approved by user

### Minimum Requirements

**To merge/deploy a feature:**
1. ✅ All tests passing (100%)
2. ✅ API-first proven (works in Node.js)
3. ✅ Fiori compliant (uses UI5 controls)
4. ✅ Documented (dedicated file + tracker)
5. ✅ User approved (feedback incorporated)

---

## 🚀 Benefits of Following These Guidelines

### For Development
- **Faster iteration** - APIs tested independently
- **Better quality** - 100% test coverage standard
- **Easier debugging** - Clear separation of concerns
- **Reusable code** - APIs work everywhere

### For Maintenance
- **Clear history** - PROJECT_TRACKER documents everything
- **Easy onboarding** - Guidelines provide standards
- **Consistent patterns** - Follow proven examples
- **Reduced bugs** - Testing catches issues early

### For Users
- **Consistent UX** - Fiori guidelines ensure quality
- **Reliable features** - Thoroughly tested
- **Professional appearance** - SAP design standards
- **Better performance** - Quality standards enforced

---

## 📞 Support & Resources

### Documentation
- This file: `DEVELOPMENT_GUIDELINES.md`
- Project tracker: `PROJECT_TRACKER_REFACTORED.md`
- Fiori guidelines: `docs/fiori/SAP_FIORI_DESIGN_GUIDELINES.md`
- HANA Cloud guides: `docs/hana-cloud/`

### Examples
- API examples: `js/api/`
- Test examples: `tests/`
- Documentation examples: Root + `docs/`

### External Resources
- SAP Fiori Design: https://experience.sap.com/fiori-design-web/
- SAP UI5 SDK: https://sapui5.hana.ondemand.com/
- SAP HANA Cloud: https://help.sap.com/docs/hana-cloud

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-22 | Initial guidelines based on Version 2.1-2.2 learnings |

---

**Remember**: These guidelines exist to ensure quality, consistency, and maintainability. Following them makes development faster and more enjoyable! 🎉
