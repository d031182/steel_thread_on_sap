# CSN Viewer Feature - Implementation Plan

**Feature**: View CSN Definition Button in Data Product Detail Dialog  
**Version**: 1.0  
**Date**: January 23, 2026, 10:49 PM  
**Status**: Planning Complete → Ready for Implementation

---

## 📋 Compliance Checklist

- [ ] 1. API-First Approach - CSN API methods with zero UI dependencies
- [ ] 2. Testability Without UI - Unit tests running in Node.js
- [ ] 3. SAP Fiori Design Guidelines - Use only SAP UI5 controls
- [ ] 4. Feature Documentation - This document + API docs
- [ ] 5. Application Logging - Log CSN retrieval and display
- [ ] 6. Version Control with Git - Clear commits for each phase
- [ ] 7. Project Tracker Updates - Update PROJECT_TRACKER.md when complete

---

## 🎯 Overview

### User Story

**As a** developer working with SAP data products  
**I want** to view the CSN (Core Schema Notation) definition of a data product  
**So that** I can understand the complete schema including entities, fields, types, and relationships

### Business Value

- **Schema Understanding**: View authoritative data product definitions
- **Development Aid**: Reference field names, types, constraints when writing queries
- **Documentation**: Built-in schema reference without external docs
- **Quality**: Ensure queries match actual schema structure

---

## 📐 Requirements

### Functional Requirements

1. **View CSN Button**
   - Display in data product detail dialog header actions
   - Icon: sap-icon://document-text
   - Label: "View CSN"
   - Enabled for all data products with available CSN

2. **CSN Viewer Dialog**
   - Display formatted CSN definition (not raw JSON)
   - Show all entities in the data product
   - Display fields with metadata (type, length, key, nullable)
   - Show annotations (@EndUserText.quickInfo)
   - Collapsible sections for each entity
   - Search/filter capability

3. **Actions**
   - Copy CSN to clipboard (formatted JSON)
   - Download CSN as JSON file
   - Close dialog

4. **Error Handling**
   - Handle CSN not available
   - Handle API failures
   - Show helpful error messages

### Non-Functional Requirements

1. **Performance**: CSN loads in < 2 seconds
2. **Usability**: Clear, readable format (not raw JSON dump)
3. **Accessibility**: Keyboard navigation, screen reader support
4. **Responsive**: Works on desktop and tablet
5. **Logging**: Log all CSN retrievals for troubleshooting

---

## 🏗️ Architecture

### API Layer

**File**: `web/current/js/api/dataProductsAPI.js`

**New Methods**:

```javascript
/**
 * Get CSN definition for a data product
 * @param {string} schemaName - Data product schema name
 * @returns {Promise<Object>} CSN definition result
 */
async getCSNDefinition(schemaName) {
    const url = `${this.baseUrl}/data-products/${schemaName}/csn`;
    const response = await fetch(url);
    return await response.json();
}

/**
 * Parse CSN and extract entity information
 * @param {Object} csn - CSN definition object
 * @returns {Array<Object>} Array of entity info
 */
parseCSNEntities(csn) {
    if (!csn?.definitions) return [];
    
    const entities = [];
    for (const [entityName, entityDef] of Object.entries(csn.definitions)) {
        if (entityDef.elements) {
            entities.push({
                name: entityName,
                elements: entityDef.elements,
                fieldCount: Object.keys(entityDef.elements).length
            });
        }
    }
    return entities;
}

/**
 * Format CSN field for display
 * @param {string} fieldName - Field name
 * @param {Object} fieldDef - Field definition
 * @returns {Object} Formatted field info
 */
formatCSNField(fieldName, fieldDef) {
    return {
        name: fieldName,
        type: fieldDef.type || 'unknown',
        length: fieldDef.length || null,
        scale: fieldDef.scale || null,
        precision: fieldDef.precision || null,
        key: fieldDef.key === true,
        nullable: !fieldDef.notNull,
        description: fieldDef['@EndUserText.quickInfo'] || 
                    fieldDef['@EndUserText.label'] || '',
        annotations: this._extractAnnotations(fieldDef)
    };
}

/**
 * Extract all annotations from field definition
 * @private
 */
_extractAnnotations(fieldDef) {
    const annotations = {};
    for (const [key, value] of Object.entries(fieldDef)) {
        if (key.startsWith('@')) {
            annotations[key] = value;
        }
    }
    return annotations;
}
```

### Backend Layer

**File**: `backend/app.py`

**Existing Endpoint** (already implemented):
```python
@app.route('/api/data-products/<schema_name>/csn', methods=['GET'])
def get_data_product_csn(schema_name):
    """
    Get CSN definition for a data product
    Currently loads from local files
    Future: Integrate with BDC MCP for live retrieval
    """
    # Implementation exists - loads from data-products/ folder
```

**Enhancement Needed**: Add better error handling and logging

### UI Layer

**File**: `web/current/index.html`

**Location**: Data product detail dialog (`openProductDetailDialog` function)

**New Button** (in header actions):
```javascript
new sap.m.Button({
    text: "View CSN",
    icon: "sap-icon://document-text",
    type: "Transparent",
    press: async function() {
        await showCSNViewer(oProduct);
    }
})
```

**New Dialog** (`showCSNViewer` function):
```javascript
async function showCSNViewer(product) {
    // 1. Fetch CSN from API
    // 2. Parse entities and fields
    // 3. Create ObjectPageLayout dialog
    // 4. Display formatted CSN with sections
    // 5. Add copy/download actions
}
```

---

## 📅 Implementation Phases

### Phase 1: Planning (✅ Complete)
**Duration**: 15 minutes  
**Deliverables**:
- [x] This implementation plan document
- [x] Compliance checklist
- [x] Time estimates

### Phase 2: API Enhancement (45 minutes)
**Tasks**:
- [ ] Add `getCSNDefinition()` to dataProductsAPI.js
- [ ] Add `parseCSNEntities()` helper
- [ ] Add `formatCSNField()` helper
- [ ] Add JSDoc comments
- [ ] Test API methods

**Deliverables**:
- New API methods in dataProductsAPI.js
- Enhanced backend error handling
- API test results

### Phase 3: UI Integration (1 hour)
**Tasks**:
- [ ] Add "View CSN" button to detail dialog
- [ ] Create `showCSNViewer()` function
- [ ] Design CSN display using SAP UI5 controls
- [ ] Implement entity sections (collapsible)
- [ ] Add field table with metadata
- [ ] Add copy to clipboard action
- [ ] Add download JSON action

**UI Controls Used**:
- sap.m.Dialog (main container)
- sap.uxap.ObjectPageLayout (for sections)
- sap.m.Panel (for collapsible entities)
- sap.m.Table (for field list)
- sap.m.Button (actions)
- sap.m.MessageStrip (info messages)

**Deliverables**:
- Fully functional CSN viewer
- SAP Fiori compliant UI
- Responsive design

### Phase 4: Testing (30 minutes)
**Tasks**:
- [ ] Create tests/csnViewerAPI.test.js
- [ ] Test getCSNDefinition() method
- [ ] Test parseCSNEntities() method
- [ ] Test formatCSNField() method
- [ ] Test error scenarios
- [ ] Run all tests (target: 10/10 passing)

**Deliverables**:
- Unit test file
- 100% method coverage
- All tests passing

### Phase 5: Documentation (20 minutes)
**Tasks**:
- [ ] Add feature section to this document
- [ ] Update PROJECT_TRACKER.md
- [ ] Add usage examples
- [ ] Document keyboard shortcuts

**Deliverables**:
- Updated documentation
- Tracker entry
- Usage guide

### Phase 6: Verification (20 minutes)
**Tasks**:
- [ ] Test in browser (all 6 data products)
- [ ] Verify copy/download functionality
- [ ] Check responsive behavior
- [ ] Verify Fiori compliance
- [ ] Final git commits

**Deliverables**:
- Verified working feature
- Clean git history
- Production-ready code

---

## 🎨 UI Design (SAP Fiori Compliant)

### CSN Viewer Dialog Layout

```
┌─────────────────────────────────────────────────────────┐
│ CSN Definition: Supplier                          [X]   │
├─────────────────────────────────────────────────────────┤
│ [Copy] [Download JSON] [Close]                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ℹ️ Core Schema Notation (CSN) - 4 entities, 120 fields  │
│                                                          │
│ 📦 supplier.Supplier (120 fields) ▼                     │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Field Name          Type      Length  Key  Desc    │ │
│ │ Supplier            String    10      🔑   Account  │ │
│ │ SupplierName        String    80      -    Name    │ │
│ │ Country             String    3       -    Country │ │
│ │ ...                                                 │ │
│ └────────────────────────────────────────────────────┘ │
│                                                          │
│ 📦 supplier.SupplierCompanyCode (25 fields) ▼           │
│ ┌────────────────────────────────────────────────────┐ │
│ │ [Collapsed]                                         │ │
│ └────────────────────────────────────────────────────┘ │
│                                                          │
│ 📦 supplier.SupplierPurchasingOrg (30 fields) ▼         │
│ 📦 supplier.SupplierWithHoldingTax (15 fields) ▼        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Color Scheme (SAP Horizon)

- Entity headers: Primary Blue (#0070f2)
- Key fields: Success Green (#107e3e) 
- Regular fields: Default text
- Annotations: Gray text (#6a6d70)
- Panels: Transparent background

---

## 📊 Expected Metrics

### Code Additions

```
dataProductsAPI.js:    ~100 lines (3 new methods)
index.html:            ~200 lines (showCSNViewer function)
csnViewerAPI.test.js:  ~250 lines (10 unit tests)
CSN_VIEWER_PLAN.md:    This document
PROJECT_TRACKER.md:    ~50 lines (feature entry)
```

### Test Coverage

```
Target: 10 unit tests, 100% method coverage
Methods to test:
- getCSNDefinition() (3 tests)
- parseCSNEntities() (3 tests)
- formatCSNField() (3 tests)
- Error scenarios (1 test)
```

---

## 🚀 Expected Outcome

After implementation, users will be able to:

1. ✅ Click data product in main table
2. ✅ See detail dialog open
3. ✅ Click "View CSN" button in header
4. ✅ See formatted CSN definition dialog
5. ✅ Browse entities and fields
6. ✅ Copy CSN to clipboard
7. ✅ Download CSN as JSON file
8. ✅ Close and return to detail dialog

---

## ⚠️ Dependencies & Prerequisites

### Already Available ✅
- Backend API endpoint: `/api/data-products/<schema>/csn`
- Local CSN files: 6 data products in `data-products/`
- SAP UI5 framework loaded
- dataProductsAPI.js exists
- Flask backend running

### Will Create
- CSN parsing and formatting methods
- CSN viewer UI components
- Unit tests for new methods
- Feature documentation

---

## 📝 Acceptance Criteria

Feature is complete when:

- [x] Planning document created (this file)
- [ ] API methods implemented with zero UI dependencies
- [ ] 10 unit tests written and passing (100%)
- [ ] "View CSN" button added to detail dialog
- [ ] CSN viewer dialog displays formatted CSN
- [ ] Copy and download functionality working
- [ ] All 6 data products tested
- [ ] Documentation complete
- [ ] PROJECT_TRACKER.md updated
- [ ] Git commits with proper messages
- [ ] User acceptance confirmed

---

## 🎓 Technical Design

### CSN Structure Example

```json
{
  "meta": {},
  "definitions": {
    "supplier.Supplier": {
      "kind": "entity",
      "elements": {
        "Supplier": {
          "@EndUserText.quickInfo": "Account Number of Supplier",
          "key": true,
          "type": "cds.String",
          "length": 10
        },
        "SupplierName": {
          "@EndUserText.quickInfo": "Name of Supplier",
          "type": "cds.String",
          "length": 80
        }
      }
    }
  }
}
```

### UI Component Hierarchy

```
sap.m.Dialog
└── sap.uxap.ObjectPageLayout
    ├── ObjectPageHeader (title, actions)
    ├── headerContent (metadata)
    └── sections (entities)
        └── ObjectPageSection (per entity)
            └── ObjectPageSubSection
                └── sap.m.Panel
                    └── sap.m.Table (fields)
                        ├── Column: Field Name
                        ├── Column: Type
                        ├── Column: Length
                        ├── Column: Key
                        └── Column: Description
```

---

## 🔧 Implementation Details

### API Methods

**1. getCSNDefinition(schemaName)**

**Purpose**: Retrieve CSN from backend  
**Input**: Schema name (e.g., "sap_s4com_Supplier_v1")  
**Output**: 
```javascript
{
    success: true,
    source: 'local_file',
    schemaName: 'sap_s4com_Supplier_v1',
    ordId: 'sap.s4com:apiResource:Supplier:v1',
    csn: { /* CSN definition */ }
}
```

**2. parseCSNEntities(csn)**

**Purpose**: Extract entity list from CSN  
**Input**: CSN object  
**Output**:
```javascript
[
    {
        name: 'supplier.Supplier',
        elements: { /* field definitions */ },
        fieldCount: 120
    },
    {
        name: 'supplier.SupplierCompanyCode',
        elements: { /* field definitions */ },
        fieldCount: 25
    }
]
```

**3. formatCSNField(fieldName, fieldDef)**

**Purpose**: Format field for display  
**Input**: Field name and definition  
**Output**:
```javascript
{
    name: 'Supplier',
    type: 'cds.String',
    length: 10,
    key: true,
    nullable: false,
    description: 'Account Number of Supplier',
    annotations: {
        '@EndUserText.quickInfo': 'Account Number of Supplier'
    }
}
```

### UI Functions

**showCSNViewer(product)**

**Workflow**:
```
1. Show busy indicator
2. Call dataProductsAPI.getCSNDefinition(product.schemaName)
3. Parse CSN using parseCSNEntities()
4. Create dialog with ObjectPageLayout
5. Add entity sections (one per entity)
6. Populate field tables
7. Add action buttons (copy, download)
8. Open dialog
9. Hide busy indicator
```

---

## 🧪 Testing Strategy

### Unit Tests (tests/csnViewerAPI.test.js)

**Test Suite**: 10 tests, ~250 lines

**Tests**:

1. **getCSNDefinition() - Success**
   - Mock successful API response
   - Verify CSN object returned
   - Check all required fields present

2. **getCSNDefinition() - Not Found**
   - Mock 404 response
   - Verify error handling
   - Check error structure

3. **getCSNDefinition() - API Error**
   - Mock 500 response
   - Verify graceful failure
   - Check error message

4. **parseCSNEntities() - Valid CSN**
   - Input: Complete CSN with 4 entities
   - Verify: Returns 4 entity objects
   - Check: Field counts correct

5. **parseCSNEntities() - Empty CSN**
   - Input: Empty CSN object
   - Verify: Returns empty array
   - No errors thrown

6. **parseCSNEntities() - Invalid Input**
   - Input: null, undefined, malformed
   - Verify: Returns empty array
   - Graceful handling

7. **formatCSNField() - String Field**
   - Input: String field with length
   - Verify: All properties extracted
   - Check: Type, length, description

8. **formatCSNField() - Key Field**
   - Input: Primary key field
   - Verify: key=true
   - Check: Marked as key column

9. **formatCSNField() - Decimal Field**
   - Input: Decimal with precision/scale
   - Verify: Precision and scale extracted
   - Check: Proper formatting

10. **formatCSNField() - With Annotations**
    - Input: Field with multiple annotations
    - Verify: All annotations extracted
    - Check: Annotation object structure

---

## 📚 Usage Examples

### Example 1: View Supplier CSN

```
User Action:
1. Click "Supplier" in data products table
2. Detail dialog opens showing tables
3. Click "View CSN" button in header
4. CSN viewer dialog opens

Result:
- Shows 4 entities
- Main entity: supplier.Supplier (120 fields)
- Fields displayed with types, lengths, keys
- Descriptions from @EndUserText annotations
```

### Example 2: Copy CSN Definition

```
User Action:
1. Open CSN viewer for any product
2. Click "Copy to Clipboard" button

Result:
- Complete CSN copied as formatted JSON
- Toast: "CSN copied to clipboard"
- Can paste into any editor
```

### Example 3: Download CSN File

```
User Action:
1. Open CSN viewer
2. Click "Download JSON" button

Result:
- File downloads: supplier-csn-2026-01-23.json
- Contains complete CSN definition
- Ready for offline use
```

---

## 🔄 Workflow Integration

### Current Flow (Before Enhancement)

```
1. User clicks data product
2. Detail dialog opens
3. Shows tables with Structure/View Data buttons
4. [END]
```

### Enhanced Flow (After Implementation)

```
1. User clicks data product
2. Detail dialog opens
3. Header shows: Refresh | View CSN | Settings
   └─ NEW: View CSN button
4. Click "View CSN"
5. CSN viewer dialog opens
   - Shows all entities
   - Displays all fields with metadata
   - Copy/Download actions available
6. User can copy or download CSN
7. Close viewer, return to detail dialog
```

---

## 🎯 Success Metrics

### Quantitative

- **API Response Time**: < 500ms for local CSN
- **Dialog Open Time**: < 1 second
- **Test Coverage**: 100% (10/10 tests)
- **Code Quality**: No linter errors
- **Fiori Compliance**: 100% (SAP UI5 controls only)

### Qualitative

- **Usability**: Users find CSN easily
- **Readability**: CSN format is clear and understandable
- **Reliability**: No errors when viewing any data product
- **Maintainability**: Code follows existing patterns

---

## 🚨 Risk Assessment

### Low Risk ✅
- Backend API already exists and works
- Local CSN files available for all products
- Similar UI patterns already implemented (table structure viewer)
- Clear requirements and design

### Mitigation Strategies

**Risk**: CSN file not available for a product  
**Mitigation**: Show helpful error with link to BDC integration guide

**Risk**: Large CSN causes browser slowdown  
**Mitigation**: Limit initial display to 50 fields, add "Show All" button

**Risk**: User doesn't understand CSN format  
**Mitigation**: Add explanatory text and field descriptions

---

## 📖 Reference Materials

### Existing Implementations

**Similar Feature**: Table Structure Viewer
- File: `web/current/index.html` (showTableStructure function)
- Pattern: Fetch data → Parse → Create dialog → Display table
- Can reuse: Dialog structure, table layout, error handling

**CSN Documentation**:
- `docs/hana-cloud/BDC_MCP_CSN_RETRIEVAL_GUIDE.md` (complete guide)
- Backend endpoint: `backend/app.py` (lines 380-450)

### SAP UI5 Resources

- ObjectPageLayout: https://sapui5.hana.ondemand.com/#/api/sap.uxap.ObjectPageLayout
- Dialog: https://sapui5.hana.ondemand.com/#/api/sap.m.Dialog
- Panel: https://sapui5.hana.ondemand.com/#/api/sap.m.Panel
- Table: https://sapui5.hana.ondemand.com/#/api/sap.m.Table

---

## ✅ Ready to Implement

This plan ensures:
- ✅ Full compliance with development guidelines
- ✅ Clear roadmap for implementation
- ✅ Testable architecture
- ✅ SAP Fiori compliant UI
- ✅ Comprehensive documentation

**Next Step**: Begin Phase 2 (API Enhancement)

---

**Status**: ✅ PLANNING COMPLETE - Ready for implementation  
**Estimated Time**: 2.5 hours (full compliance)  
**Started**: January 23, 2026, 10:49 PM  
**Target Completion**: January 23, 2026, ~1:20 AM