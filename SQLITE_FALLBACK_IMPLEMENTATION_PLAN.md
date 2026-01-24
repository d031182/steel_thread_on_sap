# SQLite Fallback Database Implementation Plan

**Feature**: SQLite Fallback for Offline Development/Demo
**Date**: 2026-01-24
**Status**: Planning

---

## 🎯 Objective

Create a SQLite fallback database system that:
1. Mirrors HANA data product table structures exactly
2. Follows CSN specifications precisely
3. Provides offline development capability
4. Enables demos without HANA connection
5. Integrates seamlessly with existing UI

---

## 📋 Requirements

### Core Requirements:
1. ✅ SQLite tables must match HANA table structures exactly
2. ✅ All field names, types, and constraints from CSN
3. ✅ Sample data (5-10 realistic records per table)
4. ✅ "Load from SQLite" button in UI
5. ✅ Automatic fallback: Try HANA → If fail → Use SQLite
6. ✅ Visual indicator showing data source (HANA vs SQLite)

### Starting Point:
- **Data Product**: Purchase Order (`sap.s4.dataProduct.PurchaseOrder.v1`)
- **CSN File**: `data-products/sap-s4com-PurchaseOrder-v1.en.json`
- **Main Entities**: 
  - `PurchaseOrder` (header)
  - `PurchaseOrderItem` (line items)
  - `PurchaseOrderScheduleLine` (delivery schedules)
  - `PurchaseOrderAccountAssignment` (account assignments)

---

## 🏗️ Architecture

### Database Structure:
```
backend/
  └── database/
      ├── p2p_fallback.db           # SQLite database file
      ├── schema/
      │   ├── purchase_order.sql    # PO schema from CSN
      │   ├── supplier.sql          # Future: Supplier
      │   └── ...                   # Future: Other products
      └── sample_data/
          ├── purchase_order_data.sql  # Sample PO records
          └── ...
```

### Backend API:
```python
# New endpoint
GET /api/data-products/sqlite/<product>

# Returns same format as HANA endpoint:
{
  "success": true,
  "source": "sqlite",
  "data": [ ... ],
  "rowCount": 10,
  "executionTime": 5.2
}
```

### Frontend Integration:
```javascript
// Automatic fallback logic
async loadData(product) {
  try {
    // Try HANA first
    return await loadFromHANA(product);
  } catch (error) {
    // Fallback to SQLite
    return await loadFromSQLite(product);
  }
}
```

---

## 📊 Phase 1: PurchaseOrder Schema Creation

### Step 1.1: Parse CSN Structure (30 min)

**From CSN file extract:**
- Main entity: `PurchaseOrder`
- Key field: `PurchaseOrder` (String, length 10)
- All 50+ fields with types and constraints

**CSN Field Mappings**:
```javascript
CSN Type          → SQLite Type
─────────────────────────────────
cds.String        → TEXT
cds.Decimal       → REAL
cds.Date          → TEXT (ISO format)
cds.Timestamp     → TEXT (ISO format)
cds.Boolean       → INTEGER (0/1)
```

### Step 1.2: Create SQLite Schema (1 hour)

**File**: `backend/database/schema/purchase_order.sql`

```sql
-- PurchaseOrder Header
CREATE TABLE PurchaseOrder (
    -- Key
    PurchaseOrder TEXT PRIMARY KEY,
    
    -- Document Information
    PurchaseOrderType TEXT,
    PurchaseOrderSubtype TEXT,
    PurchaseOrderDate TEXT,
    CreationDate TEXT,
    CreatedByUser TEXT,
    
    -- Organizational Data
    CompanyCode TEXT,
    PurchasingOrganization TEXT,
    PurchasingGroup TEXT,
    
    -- Partner Information
    Supplier TEXT,
    SupplierRespSalesPersonName TEXT,
    SupplierPhoneNumber TEXT,
    
    -- Payment Terms
    PaymentTerms TEXT,
    CashDiscount1Days INTEGER,
    CashDiscount1Percent REAL,
    CashDiscount2Days INTEGER,
    CashDiscount2Percent REAL,
    NetPaymentDays INTEGER,
    
    -- Currency & Pricing
    DocumentCurrency TEXT,
    ExchangeRate REAL,
    ExchangeRateIsFixed INTEGER,
    
    -- Incoterms
    IncotermsClassification TEXT,
    IncotermsVersion TEXT,
    IncotermsLocation1 TEXT,
    IncotermsLocation2 TEXT,
    
    -- Status
    ReleaseIsNotCompleted INTEGER,
    PurchasingCompletenessStatus INTEGER,
    PurchasingProcessingStatus TEXT,
    PurgReleaseSequenceStatus TEXT,
    
    -- Dates
    ValidityStartDate TEXT,
    ValidityEndDate TEXT,
    LastChangeDateTime TEXT,
    
    -- Additional Fields
    Language TEXT,
    CorrespncExternalReference TEXT,
    CorrespncInternalReference TEXT,
    PurchasingDocumentDeletionCode TEXT,
    
    -- ... (all 50+ fields from CSN)
);

-- PurchaseOrderItem
CREATE TABLE PurchaseOrderItem (
    -- Keys
    PurchaseOrder TEXT,
    PurchaseOrderItem TEXT,
    
    -- Material
    Material TEXT,
    MaterialGroup TEXT,
    MaterialType TEXT,
    PurchaseOrderItemText TEXT,
    
    -- Quantities
    OrderQuantity REAL,
    PurchaseOrderQuantityUnit TEXT,
    BaseUnit TEXT,
    
    -- Pricing
    NetPriceAmount REAL,
    NetAmount REAL,
    NetPriceQuantity REAL,
    OrderPriceUnit TEXT,
    
    -- Organizational
    CompanyCode TEXT,
    Plant TEXT,
    StorageLocation TEXT,
    
    -- Status & Control
    PurchaseOrderItemCategory TEXT,
    IsCompletelyDelivered INTEGER,
    IsFinallyInvoiced INTEGER,
    InvoiceIsExpected INTEGER,
    GoodsReceiptIsExpected INTEGER,
    
    -- ... (all fields from CSN)
    
    PRIMARY KEY (PurchaseOrder, PurchaseOrderItem),
    FOREIGN KEY (PurchaseOrder) REFERENCES PurchaseOrder(PurchaseOrder)
);
```

### Step 1.3: Add Sample Data (1 hour)

**File**: `backend/database/sample_data/purchase_order_data.sql`

```sql
-- Sample Purchase Orders
INSERT INTO PurchaseOrder VALUES
('4500000001', 'NB', 'T', '2024-01-15', '2024-01-15', 'JOHNDOE', 
 '1000', '1000', '001', 'VENDOR001', 'John Smith', '+1-555-0100',
 'Z001', 14, 2.0, 30, 1.0, 60, 'USD', 1.0, 0,
 'EXW', '2020', 'New York', '', 0, 0, '01', '',
 '2024-01-15', '2024-12-31', '2024-01-15T10:30:00Z',
 'EN', 'REF-001', 'INT-001', NULL),
 
('4500000002', 'NB', 'T', '2024-01-16', '2024-01-16', 'JANEDOE',
 '1000', '1000', '002', 'VENDOR002', 'Jane Wilson', '+1-555-0200',
 'Z002', 30, 0, 0, 0, 90, 'EUR', 1.1, 0,
 'FOB', '2020', 'Hamburg', '', 0, 0, '02', '',
 '2024-01-16', '2024-12-31', '2024-01-16T14:20:00Z',
 'EN', 'REF-002', 'INT-002', NULL);

-- Sample Purchase Order Items
INSERT INTO PurchaseOrderItem VALUES
('4500000001', '00010', 'MAT001', 'Z-RAW', 'ROH', 'Raw Material A',
 100.0, 'KG', 'KG', 50.00, 5000.00, 1.0, 'KG',
 '1000', 'PLANT01', 'LOC01', '0', 0, 0, 1, 1,
 -- ... more fields
),
('4500000001', '00020', 'MAT002', 'Z-RAW', 'ROH', 'Raw Material B',
 200.0, 'KG', 'KG', 30.00, 6000.00, 1.0, 'KG',
 '1000', 'PLANT01', 'LOC01', '0', 0, 0, 1, 1
);
```

---

## 🔧 Phase 2: Backend Implementation

### Step 2.1: Database Connection Module (30 min)

**File**: `backend/database/sqlite_connection.py`

```python
import sqlite3
import os
from typing import List, Dict, Any

class SQLiteConnection:
    """SQLite connection for fallback database"""
    
    def __init__(self, db_path='backend/database/p2p_fallback.db'):
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database if it doesn't exist"""
        if not os.path.exists(self.db_path):
            self._create_database()
    
    def _create_database(self):
        """Create database with schema and sample data"""
        # Run schema creation scripts
        # Run sample data scripts
        pass
    
    def query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
```

### Step 2.2: Backend API Endpoint (1 hour)

**File**: `backend/app.py` (add new endpoint)

```python
from database.sqlite_connection import SQLiteConnection

sqlite_db = SQLiteConnection()

@app.route('/api/data-products/sqlite/<product>')
def get_data_product_sqlite(product):
    """Get data product from SQLite fallback"""
    
    try:
        # Map product name to table
        table_mapping = {
            'PurchaseOrder': 'PurchaseOrder',
            'Supplier': 'Supplier',
            # ... more mappings
        }
        
        table_name = table_mapping.get(product)
        if not table_name:
            return jsonify({
                'success': False,
                'error': f'Unknown product: {product}'
            }), 404
        
        # Query SQLite
        start_time = time.time()
        sql = f'SELECT * FROM {table_name} LIMIT 100'
        results = sqlite_db.query(sql)
        execution_time = (time.time() - start_time) * 1000
        
        return jsonify({
            'success': True,
            'source': 'sqlite',
            'data': results,
            'rowCount': len(results),
            'executionTime': round(execution_time, 2)
        })
        
    except Exception as e:
        logger.error(f'SQLite query failed: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## 🎨 Phase 3: Frontend Integration

### Step 3.1: Update Data Products API (30 min)

**File**: `web/current/js/api/dataProductsAPI.js`

Add fallback logic:

```javascript
/**
 * Load data with automatic HANA/SQLite fallback
 */
async loadDataWithFallback(instanceId, product) {
    try {
        // Try HANA first
        const result = await this.loadData(instanceId, product);
        return {
            ...result,
            source: 'hana'
        };
    } catch (error) {
        console.warn(`[DataProductsAPI] HANA failed, trying SQLite...`);
        
        // Fallback to SQLite
        const response = await fetch(`/api/data-products/sqlite/${product}`);
        const data = await response.json();
        
        if (data.success) {
            return {
                ...data,
                source: 'sqlite'
            };
        }
        
        throw new Error('Both HANA and SQLite failed');
    }
}

/**
 * Load directly from SQLite
 */
async loadFromSQLite(product) {
    const response = await fetch(`/api/data-products/sqlite/${product}`);
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error);
    }
    
    return data;
}
```

### Step 3.2: UI Updates (1 hour)

**Add to Data Products view:**

```javascript
// Data source indicator
const sourceIcon = new sap.m.Label({
    text: data.source === 'sqlite' ? '📦 SQLite' : '☁️ HANA Cloud',
    design: data.source === 'sqlite' ? 'Information' : 'Success'
});

// Manual source selection buttons
const loadFromHanaBtn = new sap.m.Button({
    text: 'Load from HANA',
    icon: 'sap-icon-cloud',
    press: () => this.loadFromHANA(product)
});

const loadFromSqliteBtn = new sap.m.Button({
    text: 'Load from SQLite',
    icon: 'sap-icon-database',
    press: () => this.loadFromSQLite(product)
});
```

---

## 📝 Detailed Implementation Steps

### Phase 1: Schema Creation (2 hours)

**Task 1.1**: Parse PurchaseOrder CSN ✅ (DONE)
- [x] Read CSN file
- [x] Identify 4 main entities
- [x] Extract field definitions

**Task 1.2**: Generate SQLite Schema (1 hour)
- [ ] Create `backend/database/schema/purchase_order.sql`
- [ ] Map all CSN fields to SQLite types
- [ ] Add primary keys and foreign keys
- [ ] Add constraints (enum values, etc.)

**Task 1.3**: Create Sample Data (1 hour)
- [ ] Create `backend/database/sample_data/purchase_order_data.sql`
- [ ] Add 5 realistic PO headers
- [ ] Add 10-15 PO items
- [ ] Add schedule lines
- [ ] Ensure data relationships are correct

### Phase 2: Backend Development (2 hours)

**Task 2.1**: Database Connection Class (30 min)
- [ ] Create `backend/database/sqlite_connection.py`
- [ ] Implement connection pooling
- [ ] Add query method
- [ ] Add error handling

**Task 2.2**: Backend API Endpoint (1 hour)
- [ ] Add `/api/data-products/sqlite/<product>` endpoint
- [ ] Implement product → table mapping
- [ ] Add logging
- [ ] Return same format as HANA endpoint

**Task 2.3**: Database Initialization (30 min)
- [ ] Script to create database
- [ ] Script to load schema
- [ ] Script to load sample data
- [ ] Add to app startup

### Phase 3: Frontend Integration (2 hours)

**Task 3.1**: API Updates (30 min)
- [ ] Add `loadDataWithFallback()` method
- [ ] Add `loadFromSQLite()` method
- [ ] Update error handling

**Task 3.2**: UI Updates (1 hour)
- [ ] Add "Load from SQLite" button
- [ ] Add data source indicator badge
- [ ] Update button layout
- [ ] Add tooltips

**Task 3.3**: Automatic Fallback (30 min)
- [ ] Implement try-catch logic
- [ ] Show user-friendly messages
- [ ] Log fallback events

### Phase 4: Testing (1 hour)

**Task 4.1**: Unit Tests
- [ ] Test SQLite connection
- [ ] Test schema creation
- [ ] Test data queries
- [ ] Test error handling

**Task 4.2**: Integration Tests
- [ ] Test HANA → SQLite fallback
- [ ] Test manual SQLite load
- [ ] Test data display
- [ ] Test source indicator

**Task 4.3**: User Testing
- [ ] Disconnect from HANA
- [ ] Verify automatic fallback
- [ ] Verify manual SQLite load
- [ ] Verify data accuracy

### Phase 5: Documentation (30 min)

**Task 5.1**: Update Documentation
- [ ] Update PROJECT_TRACKER.md
- [ ] Create SQLite usage guide
- [ ] Document schema mapping process
- [ ] Add troubleshooting section

---

## 📊 PurchaseOrder CSN Analysis

### Main Entity: `PurchaseOrder`

**Key Fields**:
- `PurchaseOrder` (String, 10) - PRIMARY KEY

**Categories** (50+ fields total):
1. **Document Info** (8 fields): Type, Subtype, Date, Created, Language
2. **Organizational** (4 fields): CompanyCode, PurchasingOrg, Group
3. **Supplier** (6 fields): Supplier, Address, Phone, Contact
4. **Payment** (7 fields): Terms, Discounts, Net Days
5. **Currency** (3 fields): Currency, ExchangeRate, IsFixed
6. **Incoterms** (5 fields): Classification, Version, Locations
7. **Status** (6 fields): Release, Completeness, Processing
8. **Dates** (4 fields): Validity, LastChange
9. **Additional** (15+ fields): References, Tax, Down Payment, etc.

### Related Entities:

**PurchaseOrderItem** (30+ fields):
- Keys: PurchaseOrder + PurchaseOrderItem
- Material, quantities, pricing, delivery

**PurchaseOrderScheduleLine** (40+ fields):
- Keys: PurchaseOrder + Item + ScheduleLine
- Delivery schedules, dates, quantities

**PurchaseOrderAccountAssignment** (35+ fields):
- Keys: PurchaseOrder + Item + AccountAssignmentNumber
- Cost centers, GL accounts, projects

---

## 🎯 Success Criteria

### Schema Accuracy:
- ✅ All CSN fields represented
- ✅ Correct SQLite data types
- ✅ Primary keys and foreign keys
- ✅ Constraints for enum values

### Data Quality:
- ✅ 5+ realistic PO records
- ✅ Proper relationships (header → items)
- ✅ Valid enum values
- ✅ Realistic business data

### Functionality:
- ✅ Backend endpoint works
- ✅ Automatic fallback works
- ✅ Manual SQLite load works
- ✅ Data displays correctly in UI
- ✅ Source indicator visible

### User Experience:
- ✅ Seamless fallback (no user action needed)
- ✅ Clear indication of data source
- ✅ Manual control available
- ✅ Performance acceptable (<100ms)

---

## 📈 Timeline Estimate

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Parse CSN | 30 min | ✅ Done |
| 1 | Create schema | 1 hour | Pending |
| 1 | Sample data | 1 hour | Pending |
| 2 | Connection class | 30 min | Pending |
| 2 | Backend endpoint | 1 hour | Pending |
| 2 | Initialize DB | 30 min | Pending |
| 3 | API updates | 30 min | Pending |
| 3 | UI updates | 1 hour | Pending |
| 3 | Fallback logic | 30 min | Pending |
| 4 | Testing | 1 hour | Pending |
| 5 | Documentation | 30 min | Pending |
| **TOTAL** | | **8 hours** | |

---

## 🚀 Next Steps

### Immediate Actions:
1. **Create SQLite schema** from CSN fields
2. **Generate sample data** (realistic PO records)
3. **Implement backend** endpoint
4. **Update frontend** with fallback logic
5. **Test thoroughly**

### Future Enhancements:
- Add more data products (Supplier, ServiceEntrySheet, etc.)
- Import tool (CSV → SQLite)
- Export tool (SQLite → CSV)
- Schema sync tool (CSN → SQLite)
- Data refresh mechanism

---

## 💡 Benefits

### For Development:
- ✅ Work offline without HANA connection
- ✅ Faster iteration (no network latency)
- ✅ No credential management
- ✅ Consistent test data

### For Demo:
- ✅ Always works (no network issues)
- ✅ Consistent demo data
- ✅ No HANA dependency
- ✅ Professional fallback

### For Testing:
- ✅ Reliable test data
- ✅ Fast test execution
- ✅ Easy to reset/refresh
- ✅ Version controlled (SQL scripts)

---

## 📞 Questions for User

1. **Scope**: Start with PurchaseOrder only, or include all P2P products?
2. **Data Volume**: 5-10 records enough, or need more?
3. **Relationships**: Include related entities (Items, ScheduleLines)?
4. **Timeline**: Implement today (8 hours), or split across multiple sessions?

---

**Status**: ✅ **PLAN COMPLETE** - Ready to implement
**Next**: User approval to proceed with implementation