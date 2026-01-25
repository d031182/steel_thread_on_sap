# CSN Investigation Findings

**Type**: Component Investigation  
**Status**: Concluded  
**Investigation Date**: 2026-01-23/24  
**Created**: 2026-01-25

## Overview

Complete investigation of CSN (Core Schema Notation) data access for SAP Data Products, including multiple approaches evaluated and the final solution adopted.

## Related Documentation

- [[CSN HANA Cloud Solution]] - Adopted solution (native HANA table access)
- [[HANA Connection Module]] - Provides connection for CSN queries
- [[Modular Architecture]] - Pattern for future CSN module

## Investigation Summary

### Problem Statement

How to access CSN (Core Schema Notation) definitions for SAP Data Products to understand table structures, field types, and relationships?

### Approaches Evaluated

#### Option 1: SAP Discovery API (Rejected)
- **Method**: HTTP access to Discovery API URLs
- **CSN Source**: `https://canary.discovery.api.sap/...`
- **Result**: ❌ Network/authentication blocked in corporate environment
- **Limitation**: Direct HTTP requests fail with connection errors

#### Option 2: BDC MCP Server (Evaluated)
- **Method**: Use BDC MCP tools (`availableDataProducts`, `csnSchema`)
- **Advantage**: Works around network restrictions
- **Limitation**: Requires MCP client integration
- **Status**: Viable but more complex

#### Option 3: Native HANA Table (✅ Adopted)
- **Method**: Query CSN directly from HANA Cloud internal table
- **Table**: `_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN`
- **Advantage**: Zero external dependencies, pure SQL
- **Status**: ✅ **PRODUCTION SOLUTION**

### Final Solution

See [[CSN HANA Cloud Solution]] for complete implementation details.

**Key Benefits**:
- ✅ No external API dependencies
- ✅ Fast local database queries
- ✅ Works in BTP without network config
- ✅ Real-time synchronized data
- ✅ Simple SQL-based access

## CSN Viewer Feature

### Status: Investigated, Not Implemented

**Investigation Findings**:
- Backend endpoint designed (`/api/data-products/<schema>/csn`)
- CSN URL mapping created (`backend/csn_urls.py`)
- Network access limitations discovered
- Frontend integration planned but not executed

**Recommendation**:
- Use native HANA table approach instead
- Query `_SAP_DATAPRODUCT_DELTA_CSN` directly
- Parse JSON from `CSN_JSON` column
- No external API calls needed

### Implementation Artifacts (Historical)

**Files Created During Investigation**:
- `backend/csn_urls.py` - ORD ID to URL mapping (10 P2P products)
- Endpoint design for `/api/data-products/<schema>/csn`
- MCP integration approaches documented

**Status**: Investigation complete, native HANA approach adopted instead

## Technical Details

### CSN Structure

Core Schema Notation defines:
- **Entities**: Data product tables
- **Elements**: Table fields/columns
- **Types**: Data types (cds.String, cds.Decimal, etc.)
- **Annotations**: Metadata and constraints
- **Associations**: Relationships between entities

### ORD ID Format

`namespace:resourceType:productName:version`

**Examples**:
- `sap.s4com:apiResource:Supplier:v1`
- `sap.s4com:apiResource:PurchaseOrder:v1`

### CSN in HANA Cloud

**Table Structure**:
```sql
_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN
├── REMOTE_SOURCE_NAME (NVARCHAR, 255) - Product identifier
└── CSN_JSON (NCLOB, 2GB) - Complete CSN as JSON
```

**Query Example**:
```sql
SELECT CSN_JSON 
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
WHERE REMOTE_SOURCE_NAME LIKE '%PurchaseOrder%';
```

## Lessons Learned

### Network Access Realities
1. Corporate networks often block external APIs
2. Discovery API URLs not accessible via direct HTTP
3. BTP to external APIs may require network configuration
4. **Solution**: Use internal HANA tables when available

### API Design Considerations
1. MCP provides workarounds for network restrictions
2. Native database access is most reliable
3. External API dependencies create fragility
4. **Principle**: Prefer local data over remote APIs

### Investigation Value
1. ✅ Discovered optimal solution (HANA table)
2. ✅ Documented alternative approaches
3. ✅ Identified network limitations early
4. ✅ Saved future implementation time

## Current Status

### Implemented ✅
- CSN data accessible via HANA native tables
- SQL-based query approach working
- Zero external dependencies
- Production-ready solution

### Not Implemented ❌
- CSN Viewer UI component (not needed)
- Discovery API integration (blocked)
- MCP-based CSN fetching (unnecessary)

### Rationale
Native HANA table access provides everything needed:
- Complete CSN definitions
- Fast performance
- Reliable availability
- Simple implementation

## Future Considerations

### If CSN Viewer Needed

**Approach**: Query HANA table directly
```python
@app.route('/api/data-products/<product>/csn')
def get_csn(product):
    sql = """
    SELECT CSN_JSON 
    FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
    WHERE REMOTE_SOURCE_NAME LIKE ?
    """
    result = hana_connection.query(sql, (f'%{product}%',))
    csn = json.loads(result['CSN_JSON'])
    return jsonify({'success': True, 'csn': csn})
```

**No external APIs needed!**

## References

- Investigation documents: `csn-investigation-archive/` (historical)
- Implementation: [[CSN HANA Cloud Solution]]
- Backend: `backend/app.py` CSN endpoint
- Documentation: `docs/hana-cloud/CHECK_HANA_BDC_CAPABILITIES.md`

## Status

✅ **INVESTIGATION COMPLETE** - Solution adopted and documented