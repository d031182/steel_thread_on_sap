# Table Structure Endpoint - Implementation Plan

**Feature**: Table Structure Endpoint for Data Products  
**Version**: 1.0  
**Date**: 2026-01-23  
**Status**: Planning → Implementation

---

## Overview

Add a REST API endpoint to retrieve detailed table structure information from HANA Cloud data product tables. This enables the frontend "Table Structure" button to display column details, data types, and metadata.

---

## Requirements

### User Requirements

1. ✅ User clicks "Table Structure" button on data product detail page
2. ✅ System queries HANA to get column information
3. ✅ Display column name, type, length, nullable, position, description
4. ✅ Handle errors gracefully (invalid schema/table, connection issues)
5. ✅ Log all operations for troubleshooting

### Technical Requirements

1. ✅ Query `SYS.TABLE_COLUMNS` system view
2. ✅ Validate schema name (must start with `_SAP_DATAPRODUCT`)
3. ✅ Validate table name (alphanumeric + underscore/dot/hyphen)
4. ✅ Return JSON with column metadata
5. ✅ Handle HANA connection errors
6. ✅ Log query execution time and results

---

## Architecture

### API Layer

**Endpoint**: `GET /api/data-products/<schema_name>/<table_name>/structure`

**Method**: `get_table_structure(schema_name, table_name)`

**Location**: `backend/app.py`

**Dependencies**:
- HANAConnection class (existing)
- Flask framework (existing)
- Python logging (existing)

### Response Format

```json
{
  "success": true,
  "schemaName": "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_abc123",
  "tableName": "Supplier",
  "columnCount": 120,
  "columns": [
    {
      "name": "Supplier",
      "position": 1,
      "dataType": "NVARCHAR",
      "length": 10,
      "scale": null,
      "nullable": false,
      "defaultValue": null,
      "comment": "Account Number of Supplier"
    }
  ]
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "message": "Invalid schema name",
    "code": "INVALID_INPUT"
  }
}
```

---

## Implementation Plan

### Phase 1: Test Development (1 hour)

**Test File**: `tests/tableStructureAPI.test.js`

**Test Cases**:
1. ✅ Test valid schema and table name
2. ✅ Test invalid schema name (not starting with `_SAP_DATAPRODUCT`)
3. ✅ Test invalid table name (special characters)
4. ✅ Test HANA connection not configured
5. ✅ Test table not found (empty result)
6. ✅ Test SQL execution error
7. ✅ Test column metadata parsing
8. ✅ Test response format validation

**Mock Strategy**:
- Mock HANA connection
- Mock system view query results
- Test without actual HANA connection

### Phase 2: API Implementation (1 hour)

**Steps**:
1. ✅ Add endpoint decorator and route
2. ✅ Implement input validation (schema, table)
3. ✅ Check HANA connection availability
4. ✅ Build parameterized SQL query
5. ✅ Execute query with HANAConnection
6. ✅ Parse and format results
7. ✅ Add comprehensive error handling
8. ✅ Add logging at each step

**Logging Points**:
- Request received (schema, table)
- Validation results
- SQL query execution start
- Query results (row count, execution time)
- Error conditions
- Response sent

### Phase 3: Integration Testing (30 minutes)

**Steps**:
1. ✅ Start Flask server
2. ✅ Test with actual HANA connection
3. ✅ Verify response format
4. ✅ Test error scenarios
5. ✅ Check logs for completeness

### Phase 4: Documentation (30 minutes)

**Updates**:
1. ✅ Update `PROJECT_TRACKER.md` with feature entry
2. ✅ Add API documentation to `backend/README.md`
3. ✅ Document testing results
4. ✅ Note any issues or limitations

---

## SQL Query

```sql
SELECT 
    COLUMN_NAME,
    POSITION,
    DATA_TYPE_NAME,
    LENGTH,
    SCALE,
    IS_NULLABLE,
    DEFAULT_VALUE,
    COMMENTS
FROM SYS.TABLE_COLUMNS
WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
ORDER BY POSITION
```

**Parameters**:
- Schema name (validated)
- Table name (validated)

---

## Validation Rules

### Schema Name Validation

**Rule**: Must start with `_SAP_DATAPRODUCT`

**Regex**: `^_SAP_DATAPRODUCT`

**Examples**:
- ✅ `_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_abc123`
- ❌ `PUBLIC`
- ❌ `P2P_SCHEMA`

### Table Name Validation

**Rule**: Alphanumeric + underscore/dot/hyphen only

**Regex**: `^[a-zA-Z0-9_.-]+$`

**Examples**:
- ✅ `Supplier`
- ✅ `Purchase_Order`
- ✅ `Payment.Terms`
- ❌ `DROP TABLE;--`
- ❌ `'; DELETE FROM`

---

## Error Handling

### Error Scenarios

| Scenario | HTTP Code | Error Code | Message |
|----------|-----------|------------|---------|
| Invalid schema | 400 | INVALID_INPUT | Invalid schema name |
| Invalid table | 400 | INVALID_INPUT | Invalid table name |
| No HANA connection | 500 | NOT_CONFIGURED | HANA connection not configured |
| SQL error | 500 | SERVER_ERROR | Failed to retrieve table structure |
| Table not found | 200 | - | Returns empty columns array |

### Logging Strategy

**Log Levels**:
- `INFO`: Normal operations (request received, query executed)
- `WARNING`: Validation failures, suspicious input
- `ERROR`: HANA errors, SQL failures, unexpected issues

**Log Format**:
```
INFO: Retrieved structure for <schema>.<table>: <N> columns
WARNING: Invalid schema name requested: <schema>
ERROR: Failed to get table structure: <error details>
```

---

## Testing Strategy

### Unit Tests (Node.js)

**Framework**: Pure Node.js (no browser required)

**Approach**:
1. Mock HANAConnection class
2. Mock query results
3. Test all code paths
4. Verify error handling
5. Check response formats

**Coverage Target**: 100% of method

### Integration Tests (Manual)

**Test Data Products**:
1. Supplier (known to work)
2. Purchase Order (if installed)
3. Non-existent table (error case)

**Test Scenarios**:
1. Valid request → Success with columns
2. Invalid schema → 400 error
3. Invalid table name → 400 error
4. Table not found → 200 with empty columns
5. HANA down → 500 error

---

## Dependencies

### Existing

- ✅ `backend/app.py` - Flask application
- ✅ `HANAConnection` class - Database connection
- ✅ `SYS.TABLE_COLUMNS` view - HANA system view
- ✅ Python `logging` module

### New

- ✅ Test file: `tests/tableStructureAPI.test.js`
- ✅ Documentation updates
- ✅ PROJECT_TRACKER entry

---

## Success Criteria

### Feature Complete When:

- [x] Planning document created ✅ (this file)
- [ ] Tests written with 100% method coverage
- [ ] All tests passing in Node.js
- [ ] API implemented with zero UI dependencies
- [ ] Comprehensive logging added
- [ ] Integration tested with real HANA
- [ ] PROJECT_TRACKER updated
- [ ] User can click "Table Structure" button and see columns
- [ ] Error scenarios handled gracefully

---

## Risks & Mitigation

### Risk 1: HANA Connection Issues

**Impact**: Endpoint fails when IP not in allowlist

**Mitigation**: 
- Clear error messages
- Suggest checking IP allowlist
- Log connection attempts

### Risk 2: Large Tables

**Impact**: Query might be slow for tables with 100+ columns

**Mitigation**:
- Query already sorted by POSITION (fast)
- System view is indexed
- No data returned, only metadata

### Risk 3: Schema Name Changes

**Impact**: Validation might break if BDC changes naming

**Mitigation**:
- Document validation rules
- Easy to update regex if needed
- Log validation failures

---

## Future Enhancements

### Phase 2 (Optional)

1. **CSN Comparison**: Compare HANA structure with CSN schema
2. **Column Search**: Filter columns by name/type
3. **Primary Key Indicator**: Highlight key columns
4. **Foreign Key Info**: Show relationships
5. **Caching**: Cache structure for performance

---

## Timeline

**Total Estimated Time**: 3 hours

| Phase | Duration | Status |
|-------|----------|--------|
| Planning | 30 min | ✅ Complete |
| Test Development | 1 hour | ⏳ Next |
| API Implementation | 1 hour | Pending |
| Integration Testing | 30 min | Pending |
| Documentation | 30 min | Pending |

---

## Files to Modify

1. ✅ `TABLE_STRUCTURE_ENDPOINT_PLAN.md` - This planning doc (created)
2. ⏳ `tests/tableStructureAPI.test.js` - Unit tests (to create)
3. ⏳ `backend/app.py` - API endpoint (to modify)
4. ⏳ `PROJECT_TRACKER.md` - Feature documentation (to update)
5. ⏳ `backend/README.md` - API docs (to update)

---

## Status

**Current Phase**: Planning Complete ✅  
**Next Step**: Write tests first (TDD approach)  
**Blockers**: None  
**Notes**: Ready to proceed with test-driven development

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-23 14:51  
**Author**: AI Assistant (following development guidelines)
