# SQLite Test Database - Fallback Data Source

## Purpose

This SQLite database serves as a **fallback data source** when the HANA Cloud connection is unavailable or not configured. It provides dummy test data to enable development, testing, and demonstration of the application even without access to HANA Cloud.

## Use Cases

### 1. **Development Without HANA**
- Developers can work on the application without needing HANA Cloud credentials
- Test UI components and workflows locally
- Debug application logic with realistic data

### 2. **HANA Connection Issues**
- When HANA Cloud is temporarily unavailable
- Network connectivity problems
- Credential/authentication issues
- Database maintenance windows

### 3. **Demonstrations & Training**
- Demo the application without exposing production data
- Training sessions for new developers
- Customer presentations without live system access

### 4. **Automated Testing**
- CI/CD pipelines can run tests without HANA dependency
- Consistent test data across environments
- Faster test execution (local SQLite vs remote HANA)

## Database Contents

The `p2p_complete_workflow_sqlite.sql` file contains a complete Procure-to-Pay (P2P) workflow with:

### Master Data
- **5 Suppliers** - Global Steel, Premium Electronics, Logistics Services, Pacific Components, Industrial Maintenance
- **3 Company Codes** - USA (1000), Europe (2000), Asia Pacific (3000)
- **4 Plants** - San Francisco, New York, Berlin, Singapore
- **4 Cost Centers** - Production, Maintenance, Logistics
- **4 Payment Terms** - NET30, NET60, 2/10NET30, 3/15NET45
- **7 Materials** - Steel plates, aluminum, electronic components, sensors, etc.
- **5 Services** - Maintenance, logistics, consulting, installation

### Transaction Data
- **4 Purchase Orders** - Materials and services orders
- **2 Goods Receipts** - Material deliveries
- **2 Service Entry Sheets** - Service confirmations
- **5 Supplier Invoices** - Various statuses (PAID, POSTED, HELD, PARKED)
- **1 Payment** - With payment run
- **5 Journal Entries** - Financial accounting postings

### Test Scenarios
1. ✅ **Complete Material Flow**: PO → GR → Invoice → Payment (PAID)
2. ⏳ **Service Flow**: PO → SES → Invoice (awaiting payment)
3. ⚠️ **Price Variance**: Invoice with price difference (HELD/BLOCKED)
4. 🌍 **International**: Multi-currency transaction with exchange rates
5. 📝 **Non-PO Invoice**: Invoice without purchase order (PARKED)

### Useful Views
- `vw_CompleteP2PTracking` - End-to-end document flow tracking
- `vw_OutstandingInvoices` - Unpaid invoices with aging
- `vw_InvoiceVariances` - Blocked invoices with variance details
- `vw_SupplierPerformance` - Supplier metrics and KPIs
- `vw_ServiceEntrySheetStatus` - Service acceptance tracking
- `vw_PurchaseOrderStatus` - PO completion status
- `vw_PaymentTermsUsage` - Payment terms utilization
- `vw_FinancialPostings` - Journal entries with source documents

## How to Use

### 1. Create the Database

```bash
# Navigate to sql/sqlite directory
cd sql/sqlite

# Create SQLite database
sqlite3 p2p_test.db < p2p_complete_workflow_sqlite.sql
```

### 2. Query the Database

```bash
# Open SQLite CLI
sqlite3 p2p_test.db

# Example queries:
sqlite> SELECT * FROM Suppliers;
sqlite> SELECT * FROM vw_CompleteP2PTracking;
sqlite> SELECT * FROM vw_OutstandingInvoices;
```

### 3. Connect from Application

```python
# Python example (Flask backend)
import sqlite3

# When HANA is unavailable, fall back to SQLite
try:
    hana_conn = connect_to_hana()
except Exception:
    sqlite_conn = sqlite3.connect('sql/sqlite/p2p_test.db')
    # Use sqlite_conn for queries
```

```javascript
// Node.js example
const sqlite3 = require('sqlite3').verbose();

// When HANA connection fails
const db = new sqlite3.Database('sql/sqlite/p2p_test.db');

db.all('SELECT * FROM Suppliers', [], (err, rows) => {
  if (err) throw err;
  console.log(rows);
});
```

## Integration with Application

### Backend Configuration

The application should automatically detect and use SQLite when HANA is unavailable:

```python
# Flask app.py
def get_database_connection():
    """Get database connection with automatic fallback"""
    
    # Try HANA first
    if HANA_HOST and HANA_USER and HANA_PASSWORD:
        try:
            conn = connect_to_hana()
            logger.info("Connected to HANA Cloud")
            return conn
        except Exception as e:
            logger.warning(f"HANA connection failed: {e}")
    
    # Fall back to SQLite
    logger.info("Using SQLite fallback database")
    sqlite_path = 'sql/sqlite/p2p_test.db'
    
    if not os.path.exists(sqlite_path):
        logger.info("Creating SQLite database from schema")
        create_sqlite_database()
    
    return sqlite3.connect(sqlite_path)
```

### Frontend Indication

The UI should indicate when using fallback data:

```javascript
// Show banner when using SQLite
if (connection.type === 'sqlite') {
    MessageStrip.show({
        text: "Using test data (SQLite fallback). HANA Cloud unavailable.",
        type: "Warning",
        showIcon: true
    });
}
```

## Differences from HANA

### SQL Syntax
SQLite uses slightly different SQL syntax than HANA:

| Feature | HANA SQL | SQLite SQL |
|---------|----------|------------|
| String concat | `\|\|` | `\|\|` ✅ Same |
| Date functions | `CURRENT_DATE` | `date('now')` |
| DateTime | `CURRENT_TIMESTAMP` | `datetime('now')` |
| Auto-increment | `GENERATED BY DEFAULT AS IDENTITY` | `AUTOINCREMENT` |
| Schema names | `"SCHEMA"."TABLE"` | Just `TABLE` |

### Features Not Available
- ❌ Data products (SAP-specific)
- ❌ Complex HANA-specific functions
- ❌ Graph processing
- ❌ Spatial data
- ❌ Multi-tenancy

### Available Features
- ✅ Standard SQL queries (SELECT, INSERT, UPDATE, DELETE)
- ✅ Joins, subqueries, CTEs
- ✅ Transactions
- ✅ Views
- ✅ Indexes
- ✅ Foreign keys

## Maintenance

### Updating Test Data

To add or modify test data:

1. Edit `p2p_complete_workflow_sqlite.sql`
2. Recreate the database:
   ```bash
   rm p2p_test.db
   sqlite3 p2p_test.db < p2p_complete_workflow_sqlite.sql
   ```

### Adding New Scenarios

When adding new test scenarios:

1. Document the scenario purpose
2. Add realistic data
3. Include all related documents (PO → GR/SES → Invoice → Payment)
4. Update this README with the new scenario

## Best Practices

### DO ✅
- Use SQLite for development and testing
- Keep test data realistic and comprehensive
- Document any SQLite-specific SQL differences
- Test with both HANA and SQLite
- Use views for complex queries

### DON'T ❌
- Don't use SQLite for production
- Don't expect HANA-specific features
- Don't hard-code SQLite paths in application
- Don't commit actual production data
- Don't skip testing with real HANA

## Troubleshooting

### Database File Not Found
```bash
# Verify file exists
ls -la sql/sqlite/p2p_test.db

# If not, create it:
cd sql/sqlite
sqlite3 p2p_test.db < p2p_complete_workflow_sqlite.sql
```

### Permission Issues
```bash
# Make sure file is readable
chmod 644 p2p_test.db
```

### SQL Syntax Errors
- Check if query uses HANA-specific syntax
- Convert to SQLite-compatible SQL
- Test queries in SQLite CLI first

## See Also

- [HANA Cloud Setup Guide](../../docs/hana-cloud/HANA_CLOUD_FIRST_USER_SETUP.md)
- [SQL Script Validation](../../docs/hana-cloud/SQL_SCRIPT_VALIDATION.md)
- [Development Guidelines](../../DEVELOPMENT_GUIDELINES.md)
- [P2P Complete Workflow Guide](../../docs/p2p/P2P_COMPLETE_WORKFLOW_README.md)

---

**Remember**: SQLite is a **fallback** for development. Always test with real HANA Cloud before production deployment!
