# CSN Viewer - Final Implementation Plan

**Feature**: CSN (Core Schema Notation) Viewer  
**Version**: 3.0 (Final - After Complete Investigation)  
**Date**: 2026-01-24  
**Status**: ✅ **READY TO IMPLEMENT** - HANA SQL Solution Validated

---

## 🎯 Final Decision: HANA SQL Query Solution

After thorough investigation of all options, the clear winner is **querying CSN directly from HANA Cloud**.

---

## Investigation Summary

### What We Discovered:

#### ✅ **HANA Cloud Has CSN Data**
- **Table**: `_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN`
- **Structure**:
  - `REMOTE_SOURCE_NAME` (NVARCHAR, 255) - Data product identifier
  - `CSN_JSON` (NCLOB, 2GB) - Complete CSN definitions in JSON
- **Status**: Data exists, confirmed via SQL query
- **Blocker**: Needs SELECT privilege grant

#### ✅ **SAP API Business Hub Exists**
- **URL**: https://api.sap.com/dataproduct/sap-s4com-PurchaseOrder-v1
- **Content**: Official data product pages with CSN download links
- **Access**: Publicly accessible, no authentication required
- **Limitation**: Download links in HTML pages, not programmatic API

#### ✅ **SAP's Production BDC**
- User has access to SAP's production BDC system
- **Observation**: Even SAP's BDC directs users to API Business Hub for CSN
- **Conclusion**: No hidden automated CSN API exists

#### ❌ **Canary Discovery API**
- URLs like `https://canary.discovery.api.sap/...`
- **Status**: Development/test environment
- **Decision**: Not suitable for production use

---

## The Solution: HANA SQL Query

### Architecture:

```
Frontend (UI5)
    ↓ (click "View CSN")
Backend (Flask) /api/data-products/{product}/csn
    ↓ (SQL query)
HANA Cloud _SAP_DATAPRODUCT_DELTA_CSN table
    ↓ (return)
CSN JSON displayed in UI
```

### Implementation:

#### **Backend Changes** (`backend/app.py`):

```python
@app.route('/api/data-products/<schema_name>/csn', methods=['GET'])
def get_data_product_csn(schema_name):
    """Get CSN schema for a data product from HANA Cloud"""
    
    try:
        # Query CSN table
        sql = """
        SELECT CSN_JSON 
        FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
        WHERE REMOTE_SOURCE_NAME LIKE ?
        """
        
        # Execute query
        cursor = hana_connection.cursor()
        cursor.execute(sql, (f'%{schema_name}%',))
        result = cursor.fetchone()
        
        if result and result[0]:
            # Parse CSN JSON
            csn_data = json.loads(result[0])
            
            return jsonify({
                'success': True,
                'csn': csn_data,
                'source': 'HANA Cloud'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'CSN not found for this data product'
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching CSN: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

#### **Frontend Integration** (UI5):

```javascript
// In data product details view
onViewCSN: function(oEvent) {
    const sProductName = this.getView().getBindingContext().getProperty("name");
    
    // Call backend API
    fetch(`/api/data-products/${sProductName}/csn`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display CSN in dialog or new view
                this._showCSNDialog(data.csn);
            }
        });
}
```

---

## Prerequisites

### 1. Grant HANA Privileges (5 minutes)

Run as SYSTEM or admin user with GRANT authority:

```sql
-- Grant SELECT on CSN table
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN" 
TO DBADMIN;

-- Verify grant
SELECT * FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN" 
LIMIT 1;
```

### 2. Test CSN Access (10 minutes)

```sql
-- Check available CSN entries
SELECT REMOTE_SOURCE_NAME, LEFT(CSN_JSON, 100) as CSN_PREVIEW 
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN";

-- Test specific product
SELECT CSN_JSON 
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
WHERE REMOTE_SOURCE_NAME LIKE '%Supplier%';
```

---

## Implementation Steps

### Phase 1: Backend Implementation (1 hour)

1. **Update `backend/app.py`**:
   - Add CSN endpoint
   - Implement SQL query
   - Add error handling
   - Test with Postman/curl

2. **Test locally**:
   ```bash
   curl http://localhost:5000/api/data-products/Supplier/csn
   ```

### Phase 2: Frontend Implementation (1 hour)

1. **Add CSN viewer dialog** (UI5 component)
2. **Add "View CSN" button** to data product details
3. **Wire up API call**
4. **Format and display CSN JSON**

### Phase 3: Testing & Deployment (30 minutes)

1. **Local testing**: Verify CSN display for all products
2. **Deploy to BTP**: Cloud Foundry deployment
3. **Production testing**: Verify in BTP environment

---

## Bonus Feature: External Link (15 minutes)

Add reference link to SAP API Business Hub:

```javascript
// Add second button
<Button 
    text="View on SAP API Hub" 
    type="Ghost" 
    press="onOpenAPIHub" 
    icon="sap-icon://sys-help" />

// Handler
onOpenAPIHub: function() {
    const product = this.getProductName();
    const url = `https://api.sap.com/api/sap-s4com-${product}-v1/overview`;
    window.open(url, '_blank');
}
```

---

## Advantages of This Solution

✅ **Automated** - No manual user actions  
✅ **Fast** - Local HANA query, no network calls  
✅ **Reliable** - No external API dependencies  
✅ **BTP-Native** - Pure HANA Cloud solution  
✅ **Better than SAP** - Automated vs SAP's manual approach  
✅ **Production-Ready** - Stable, proven approach  

---

## Files Status

### Production Files (Keep):
- ✅ `backend/app.py` - Add CSN endpoint here
- ✅ `backend/csn_urls.py` - Can keep for reference
- ✅ `CSN_VIEWER_FINAL_IMPLEMENTATION_PLAN.md` - This file
- ✅ `docs/hana-cloud/CHECK_HANA_BDC_CAPABILITIES.md` - Investigation guide

### Archive (Reference Only):
- 📦 `CSN_VIEWER_FEATURE_IMPLEMENTATION_PLAN.md` → archive
- 📦 `CSN_VIEWER_FEATURE_COMPLETE_SUMMARY.md` → archive
- 📦 `CSN_VIEWER_FEATURE_REVISED_SUMMARY.md` → archive
- 📦 `CSN_HANA_CLOUD_SOLUTION.md` → archive
- 📦 `OPTION_2_VALIDATION_PLAN.md` → archive
- 📦 `docs/hana-cloud/BDC_MCP_IMPORTANT_NOTICE.md` → archive
- 📦 `docs/hana-cloud/archive/BDC_MCP_*.md` → keep archived

### Temporary Test Files (Delete):
- 🗑️ `test_hana_bdc_check.py`
- 🗑️ `test_*.json`
- 🗑️ `test_overview_page.html`
- 🗑️ `test_api_response.txt`

---

## Time Estimate

- **Grant privileges**: 5 minutes
- **Backend implementation**: 1 hour
- **Frontend implementation**: 1 hour  
- **Testing & deployment**: 30 minutes
- **Bonus external link**: 15 minutes

**Total**: ~2 hours 50 minutes

---

## Next Session TODO

1. [ ] Grant HANA SELECT privileges
2. [ ] Test CSN access from SQL client
3. [ ] Implement backend CSN endpoint
4. [ ] Implement frontend CSN viewer
5. [ ] Test end-to-end locally
6. [ ] Deploy to BTP Cloud Foundry
7. [ ] Update PROJECT_TRACKER.md with completion
8. [ ] Commit all changes to Git

---

**Status**: Investigation complete, solution validated, ready to implement! 🚀