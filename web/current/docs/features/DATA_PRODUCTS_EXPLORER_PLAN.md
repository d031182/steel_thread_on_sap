# Data Products Explorer Feature Plan

## Overview

Add a new section to the application dedicated to exploring, listing, and consuming real data products from the connected HANA Cloud instance.

## Key Differences from Existing Features

### Current Features
1. **Data Products Catalog** (existing)
   - Shows hardcoded P2P data products (Supplier, PO, Invoice, etc.)
   - Sample data is static/mock data
   - CSN definitions from local JSON files

2. **HANA Connection** (existing)
   - Manages HANA instance connections
   - SQL Console for custom queries
   - Shows CLI commands (can't execute in browser)

### New Feature: Data Products Explorer
3. **Data Products Explorer** (NEW)
   - **Lists ACTUAL data product schemas** from your HANA instance
   - **Queries REAL data** from `_SAP_DATAPRODUCT_*` schemas
   - **Discovers installed products** automatically
   - **Browses tables and columns** dynamically
   - **Executes queries** using backend connection

## Feature Design

### Navigation Structure

```
Shell Bar Navigation:
├── 📦 Data Products (existing - mock data)
├── 🔌 HANA Connection (existing - SQL console)
└── 🗄️ Data Products Explorer (NEW - real data)
```

### UI Components

#### 1. Data Products Explorer Page

**Left Panel: Installed Data Products**
```
┌─────────────────────────────┐
│ Installed Data Products (27)│
├─────────────────────────────┤
│ 🔍 Search: [___________]    │
├─────────────────────────────┤
│ ✓ Supplier                  │
│   📊 4 tables               │
│   🕐 2025-11-04             │
├─────────────────────────────┤
│   Customer                  │
│   📊 3 tables               │
│   🕐 2025-11-04             │
├─────────────────────────────┤
│   Product                   │
│   📊 2 tables               │
│   🕐 2025-11-07             │
└─────────────────────────────┘
```

**Right Panel: Data Product Details**
```
┌──────────────────────────────────────────┐
│ Supplier Data Product                    │
│ Schema: _SAP_DATAPRODUCT_..._v1_...     │
├──────────────────────────────────────────┤
│ 📋 Tables (4)                            │
│                                          │
│ ┌─ Supplier ─────────────────┐          │
│ │ 120 columns | 1,234 rows   │          │
│ │ [View Structure] [Query]   │          │
│ └────────────────────────────┘          │
│                                          │
│ ┌─ SupplierCompanyCode ─────┐          │
│ │ 25 columns | 2,456 rows    │          │
│ │ [View Structure] [Query]   │          │
│ └────────────────────────────┘          │
└──────────────────────────────────────────┘
```

#### 2. Table Explorer View

```
┌────────────────────────────────────────────┐
│ Table: Supplier                            │
│ Schema: _SAP_DATAPRODUCT_..._Supplier_v1_...│
├────────────────────────────────────────────┤
│ Structure | Data | Query                  │
├────────────────────────────────────────────┤
│ 📊 Table Structure (120 columns)          │
│                                            │
│ Column Name          Type        Nullable │
│ ────────────────────────────────────────  │
│ Supplier            NVARCHAR(10)    No    │
│ SupplierName        NVARCHAR(80)    No    │
│ Country             NCHAR(3)        Yes   │
│ ...                                        │
│                                            │
│ [⬇️ View Top 100 Rows]                    │
└────────────────────────────────────────────┘
```

#### 3. Data View

```
┌────────────────────────────────────────────┐
│ Supplier Data (showing 100 of 1,234)      │
├────────────────────────────────────────────┤
│ Supplier | SupplierName    | Country | ... │
│──────────────────────────────────────────  │
│ 0001026704| Small Victory... | US     | ...│
│ 0001026511| Small Victory... | US     | ...│
│ ...                                        │
│                                            │
│ [◀ Previous] Page 1 of 13 [Next ▶]       │
│ [📥 Export CSV]                            │
└────────────────────────────────────────────┘
```

## Technical Implementation

### Backend API Endpoints

```javascript
// New endpoints in server.js

// 1. List all data product schemas
app.get('/api/data-products', async (req, res) => {
  const query = `
    SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME 
    FROM SYS.SCHEMAS 
    WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
    ORDER BY CREATE_TIME DESC
  `;
  // Execute and return results
});

// 2. Get tables in a data product
app.get('/api/data-products/:schemaName/tables', async (req, res) => {
  const query = `
    SELECT TABLE_NAME, TABLE_TYPE, RECORD_COUNT 
    FROM SYS.TABLES 
    WHERE SCHEMA_NAME = '${req.params.schemaName}'
    ORDER BY TABLE_NAME
  `;
  // Execute and return results
});

// 3. Get table structure
app.get('/api/data-products/:schemaName/:tableName/structure', async (req, res) => {
  const query = `
    SELECT 
      COLUMN_NAME, 
      DATA_TYPE_NAME, 
      LENGTH, 
      IS_NULLABLE,
      DEFAULT_VALUE,
      POSITION
    FROM SYS.TABLE_COLUMNS 
    WHERE SCHEMA_NAME = '${req.params.schemaName}'
      AND TABLE_NAME = '${req.params.tableName}'
    ORDER BY POSITION
  `;
  // Execute and return results
});

// 4. Query table data
app.post('/api/data-products/:schemaName/:tableName/query', async (req, res) => {
  const { limit = 100, offset = 0, columns = '*', where = '' } = req.body;
  
  const query = `
    SELECT ${columns} 
    FROM "${req.params.schemaName}"."${req.params.tableName}"
    ${where ? 'WHERE ' + where : ''}
    LIMIT ${limit} OFFSET ${offset}
  `;
  // Execute and return results
});
```

### Frontend Components

```javascript
// New file: web/current/js/api/dataProductsAPI.js

export class DataProductsAPI {
  constructor(baseURL = 'http://localhost:3000') {
    this.baseURL = baseURL;
  }

  async listDataProducts() {
    // Call /api/data-products
    // Parse and return schema list
  }

  async getTables(schemaName) {
    // Call /api/data-products/:schemaName/tables
    // Return table list
  }

  async getTableStructure(schemaName, tableName) {
    // Call /api/data-products/:schemaName/:tableName/structure
    // Return column definitions
  }

  async queryTable(schemaName, tableName, options = {}) {
    // Call /api/data-products/:schemaName/:tableName/query
    // Return data rows
  }

  async getDataProductMetadata(schemaName) {
    // Parse schema name to extract product info
    // Return: { name, version, uuid, namespace }
  }
}
```

## Implementation Steps

### Phase 1: Backend Setup
- [x] Backend already exists (web/current/backend/)
- [ ] Add 4 new API endpoints for data products
- [ ] Test endpoints with Postman/curl
- [ ] Add error handling and validation

### Phase 2: Frontend API
- [ ] Create `dataProductsAPI.js`
- [ ] Implement API client methods
- [ ] Add caching for performance
- [ ] Write unit tests

### Phase 3: UI Components
- [ ] Add new nav item "Data Products Explorer"
- [ ] Create explorer page layout (2-column)
- [ ] Build data product list component
- [ ] Build table list component
- [ ] Build table structure viewer
- [ ] Build data grid component

### Phase 4: Integration
- [ ] Connect UI to API
- [ ] Add loading states
- [ ] Add error handling
- [ ] Add pagination
- [ ] Add search/filter

### Phase 5: Polish
- [ ] Add export functionality
- [ ] Add query builder
- [ ] Add column sorting
- [ ] Add data type icons
- [ ] Performance optimization

## User Workflows

### Workflow 1: Discover Installed Data Products
1. User clicks "Data Products Explorer" in nav
2. Page loads list of 27 installed data products
3. User sees: name, table count, install date
4. User can search/filter the list

### Workflow 2: Explore Supplier Data Product
1. User clicks "Supplier" in list
2. Right panel shows 4 tables
3. User clicks "Supplier" table
4. Shows table structure (120 columns)
5. User clicks "View Top 100 Rows"
6. Shows real supplier data from HANA

### Workflow 3: Query Specific Data
1. User navigates to a table
2. Clicks "Query" button
3. Simple query builder appears:
   - Select columns (multi-select)
   - Add WHERE conditions
   - Set LIMIT
4. Clicks "Execute"
5. Results displayed in grid

### Workflow 4: Export Data
1. User viewing data
2. Clicks "Export CSV"
3. Downloads current view as CSV

## Benefits

### vs Current "Data Products" Section
- **Real data** instead of mock data
- **Discovers** what's actually installed
- **Dynamic** - no hardcoding needed
- **Accurate** - reflects current HANA state

### vs "HANA Connection" Section
- **User-friendly** - no SQL knowledge required
- **Guided** - structured exploration
- **Safe** - no accidental DELETE/UPDATE
- **Purpose-built** - designed for data product exploration

## Sample Queries Generated

The system will generate safe, read-only queries like:

```sql
-- List all data products
SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME 
FROM SYS.SCHEMAS 
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%';

-- Get Supplier tables
SELECT TABLE_NAME, RECORD_COUNT 
FROM SYS.TABLES 
WHERE SCHEMA_NAME = '_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_...';

-- View Supplier data
SELECT TOP 100 
  Supplier, 
  SupplierName, 
  Country, 
  BPAddrCityName, 
  CreationDate
FROM "_SAP_DATAPRODUCT_..._Supplier_v1_..."."_SAP_DATAPRODUCT_..._supplier.Supplier"
ORDER BY CreationDate DESC;
```

## Security Considerations

1. **Read-Only Access**
   - Only SELECT queries allowed
   - No INSERT/UPDATE/DELETE
   - Backend validates query type

2. **SQL Injection Prevention**
   - Parameterized queries
   - Schema/table name validation
   - No direct SQL from user

3. **Authentication**
   - Uses P2P_DEV_USER credentials
   - Connection pooling for performance
   - Timeout handling

## Next Steps

1. **Approve this plan** ✓
2. **Implement Phase 1** - Backend endpoints
3. **Test with your 27 data products**
4. **Implement Phases 2-3** - Frontend
5. **Polish and refine** - Phase 4-5

## Questions to Clarify

1. **Priority**: Is this high priority for your project?
2. **Scope**: Should we start with read-only, or add query builder too?
3. **Export**: CSV export important? Excel? JSON?
4. **Filters**: Basic filtering enough, or need advanced?
5. **Performance**: Expect to query large tables (>1M rows)?

---

**Status**: Planning Complete - Ready for Implementation  
**Created**: January 22, 2026, 2:51 AM  
**Next**: Await approval to begin Phase 1
