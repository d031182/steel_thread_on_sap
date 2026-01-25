# CSN HANA Cloud Solution

**Type**: Architecture  
**Decision Date**: 2026-01-23  
**Status**: Adopted  
**Created**: 2026-01-25

## Overview

Solution for accessing Core Schema Notation (CSN) data for SAP Data Products by querying native HANA Cloud tables instead of external Discovery APIs.

## Context

Initially attempted to access CSN data via SAP Discovery API but encountered network/authentication issues. Investigation revealed that HANA Cloud already stores CSN data natively in internal tables.

## Decision

**Adopted Approach**: Query CSN directly from HANA table

**Table Used**:
```
_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN
```

**Structure**:
- `REMOTE_SOURCE_NAME` (NVARCHAR, 255) - Data product identifier
- `CSN_JSON` (NCLOB, 2GB) - Complete CSN definitions in JSON format

## Implementation

```python
@app.route('/api/data-products/<schema_name>/csn', methods=['GET'])
def get_data_product_csn(schema_name):
    sql = """
    SELECT CSN_JSON 
    FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
    WHERE REMOTE_SOURCE_NAME LIKE ?
    """
    
    result = conn.execute_query(sql, (f'%{schema_name}%',))
    
    if result['success'] and result['rows']:
        csn_json = result['rows'][0]['CSN_JSON']
        csn_data = json.loads(csn_json)
        return jsonify({'success': True, 'csn': csn_data})
```

## Advantages

- ✅ **Zero external dependencies** - Pure HANA SQL
- ✅ **Already in database** - No API calls needed
- ✅ **Fast performance** - Local database query
- ✅ **Works in BTP** - Just needs privilege grant
- ✅ **Real-time data** - Stays synchronized
- ✅ **No network issues** - Everything local to HANA

## Requirements

**Privilege Grant**:
```sql
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN" 
TO DBADMIN;
```

## Related Documentation

- [[HANA Connection Module]] - Provides connection to execute CSN queries
- [[Modular Architecture]] - CSN viewer would be a module
- Data Products Module - Uses CSN data for schema information (in modules/data_products/)

## Alternative Considered

**Discovery API Approach**: Use SAP Discovery API URLs
- ❌ Network/authentication issues in corporate environment
- ❌ External dependency
- ❌ Unknown if works from BTP
- ✅ Native HANA solution chosen instead

## Benefits

1. **Reliability** - No external API dependencies
2. **Performance** - Local database queries
3. **Simplicity** - Pure SQL, no HTTP complexity
4. **BTP Native** - Uses HANA Cloud native features
5. **Production-Proven** - Standard HANA table access

## Status

✅ **ADOPTED** - Solution validated, ready for implementation

## References

- Original investigation: csn-investigation-archive/
- HANA Cloud documentation
- Implementation: backend/app.py CSN endpoint