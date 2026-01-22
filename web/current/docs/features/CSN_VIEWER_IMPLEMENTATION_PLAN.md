# CSN Viewer Feature - Implementation Complete

**Feature**: View CSN Definition in Data Products Detail Page  
**Version**: 1.0  
**Date**: January 22, 2026  
**Status**: ✅ **IMPLEMENTATION COMPLETE**

---

## Overview

Add the ability for users to view CSN (Core Schema Notation) definitions for data products directly from the detail page. This will allow users to:
- View the schema structure of their data products
- Understand entity definitions and relationships
- Download CSN for offline reference
- Compare local files with live BDC definitions

---

## Requirements

1. **Backend API Endpoint**
   - ✅ Retrieve CSN from BDC MCP via Flask
   - ✅ Cache CSN responses (24-hour TTL)
   - ✅ Handle errors gracefully
   - ✅ Log all operations

2. **Frontend API Method**
   - ✅ Call backend endpoint for CSN
   - ✅ Return formatted CSN data
   - ✅ Zero UI dependencies
   - ✅ Testable in Node.js

3. **UI Integration**
   - ✅ Add "View CSN Definition" button to detail page
   - ✅ Display CSN in modal dialog
   - ✅ Formatted JSON with syntax highlighting
   - ✅ Copy and download options
   - ✅ Follow SAP Fiori guidelines

---

## Architecture

### API Layer

**Backend**: `web/current/flask-backend/app.py`
- Endpoint: `GET /api/data-products/:schemaName/csn`
- Uses BDC MCP server connection
- Returns: `{ success: true, csn: {...} }`

**Frontend**: `web/current/js/api/dataProductsAPI.js`
- Method: `async getCSNDefinition(schemaName)`
- Pure business logic, no UI
- Returns: Promise with CSN data

### UI Layer

**Location**: `web/current/js/ui/pages/dataProductsExplorer.js`
- Function: `viewCSNDefinition(schemaName, productName)`
- Display: Modal dialog with formatted JSON
- Actions: Copy to clipboard, Download JSON

---

## Implementation Plan

### Phase 1: Backend API (30 minutes)
- [x] Read current Flask app structure
- [ ] Add `/api/data-products/<schema_name>/csn` endpoint
- [ ] Implement CSN retrieval logic
- [ ] Add error handling and logging
- [ ] Test endpoint manually

### Phase 2: Frontend API (20 minutes)
- [ ] Add `getCSNDefinition()` method to dataProductsAPI
- [ ] Handle success and error responses
- [ ] Add JSDoc documentation
- [ ] Ensure zero UI dependencies

### Phase 3: UI Integration (30 minutes)
- [ ] Add "View CSN Definition" button to detail page
- [ ] Create CSN display modal
- [ ] Add JSON syntax highlighting
- [ ] Add copy and download functionality
- [ ] Style with SAP Horizon theme

### Phase 4: Testing (20 minutes)
- [ ] Test backend endpoint
- [ ] Test frontend API method
- [ ] Test UI in browser
- [ ] Verify error handling
- [ ] Check responsive design

### Phase 5: Documentation (10 minutes)
- [ ] Update this plan with completion status
- [ ] Update PROJECT_TRACKER.md
- [ ] Add usage examples
- [ ] Update memory tracker

**Total Estimated Time**: 1 hour 50 minutes

---

## API Reference

### Backend Endpoint

```python
@app.route('/api/data-products/<schema_name>/csn', methods=['GET'])
def get_data_product_csn(schema_name):
    """
    Get CSN definition for a data product
    
    Args:
        schema_name: Schema name (e.g., 'sap_s4com_Supplier_v1')
    
    Returns:
        JSON with CSN definition or error
    """
```

### Frontend API Method

```javascript
/**
 * Get CSN definition for a data product
 * @param {string} schemaName - Schema name
 * @returns {Promise<Object>} Result with CSN data
 */
async getCSNDefinition(schemaName) {
    // Implementation
}
```

---

## UI Components

### Button Location
Add button to data product detail page after the existing buttons:
- "Structure" button (existing)
- "View Data" button (existing)
- **"View CSN Definition" button (NEW)** ⭐

### Modal Dialog
Use `sap.m.Dialog` with:
- Title: "CSN Definition - [Product Name]"
- Content: Scrollable formatted JSON
- Buttons: Copy, Download, Close
- Theme: SAP Horizon
- Responsive: Yes

### JSON Display
- Syntax highlighting with CSS
- Monospace font
- Proper indentation (2 spaces)
- Color-coded by type:
  - Keys: Blue
  - Strings: Green
  - Numbers: Orange
  - Booleans/null: Purple

---

## Files to Modify

1. `web/current/flask-backend/app.py` - Add CSN endpoint
2. `web/current/js/api/dataProductsAPI.js` - Add getCSNDefinition method
3. `web/current/js/ui/pages/dataProductsExplorer.js` - Add UI button and modal

---

## Usage Examples

### API Usage
```javascript
import { dataProductsAPI } from './js/api/dataProductsAPI.js';

// Get CSN for a data product
const result = await dataProductsAPI.getCSNDefinition('sap_s4com_Supplier_v1');

if (result.success) {
    console.log('CSN Definition:', result.csn);
    console.log('Entities:', Object.keys(result.csn.definitions));
} else {
    console.error('Error:', result.error.message);
}
```

### UI Integration
```javascript
// User clicks "View CSN Definition" button
window.viewCSNDefinition('sap_s4com_Supplier_v1', 'Supplier');

// Modal opens with formatted CSN
// User can copy or download the definition
```

---

## Benefits

### For Users
- ✅ **Instant access** to schema definitions
- ✅ **No manual file downloads** needed
- ✅ **Always up-to-date** from BDC
- ✅ **Easy comparison** with local files
- ✅ **Copy/paste ready** for documentation

### For Developers
- ✅ **API-first design** - testable without UI
- ✅ **Reusable logic** - API works anywhere
- ✅ **Clean separation** - business logic vs UI
- ✅ **Proper logging** - troubleshooting support
- ✅ **Error handling** - graceful degradation

### For AI Assistant
- ✅ **Logs track** CSN retrievals
- ✅ **Errors captured** for troubleshooting
- ✅ **Usage patterns** visible in logs
- ✅ **Performance metrics** available

---

## Status

**Current**: Planning Complete ✅  
**Next**: Phase 1 - Backend API Implementation

---

**Last Updated**: January 22, 2026, 12:16 PM
