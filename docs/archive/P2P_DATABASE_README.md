# P2P Supplier Invoice Database

This directory contains SQL database schemas for the Procure-to-Pay (P2P) Supplier Invoice workflow.

## Available Files

### 1. `p2p_supplier_invoice_db.sql`
**Standard SQL version** - Compatible with:
- MySQL
- PostgreSQL
- SQL Server
- Most enterprise databases

Uses standard SQL syntax with:
- VARCHAR data types
- DECIMAL for currency
- BOOLEAN for flags
- Standard date/time functions

### 2. `p2p_supplier_invoice_sqlite.sql`
**SQLite-specific version** - Optimized for:
- SQLite databases
- Local development
- Testing and demos
- Embedded applications

Uses SQLite-specific features:
- TEXT data types
- REAL for numbers
- INTEGER for booleans (0/1)
- SQLite date functions (julianday, date, datetime)

## Quick Start

### Using SQLite (Recommended for Testing)

```bash
# 1. Install SQLite (if not already installed)
# Windows: Download from https://www.sqlite.org/download.html
# Mac: brew install sqlite3
# Linux: sudo apt-get install sqlite3

# 2. Create and populate the database
sqlite3 p2p_invoice.db < p2p_supplier_invoice_sqlite.sql

# 3. Open the database
sqlite3 p2p_invoice.db

# 4. Run some queries
SELECT * FROM vw_OutstandingInvoices;
SELECT * FROM vw_InvoiceVariances;
```

### Using MySQL

```bash
# 1. Create database
mysql -u root -p -e "CREATE DATABASE p2p_invoice;"

# 2. Import schema and data
mysql -u root -p p2p_invoice < p2p_supplier_invoice_db.sql

# 3. Connect and query
mysql -u root -p p2p_invoice
```

### Using PostgreSQL

```bash
# 1. Create database
createdb p2p_invoice

# 2. Import schema and data
psql p2p_invoice < p2p_supplier_invoice_db.sql

# 3. Connect and query
psql p2p_invoice
```

## Database Structure

### Master Data Tables
- `Suppliers` - Vendor information
- `CompanyCodes` - Legal entities
- `Plants` - Physical locations
- `Materials` - Products/items

### Procurement Tables
- `PurchaseOrders` - Purchase order headers
- `PurchaseOrderItems` - PO line items
- `GoodsReceipts` - Material receipt documents
- `GoodsReceiptItems` - GR line items

### Invoice Tables (Main Focus)
- `SupplierInvoices` - Invoice headers
- `SupplierInvoiceItems` - Invoice line items
- `InvoicePayments` - Payment records

### Pre-built Views
- `vw_OutstandingInvoices` - All unpaid invoices
- `vw_InvoiceVariances` - Invoices with variances
- `vw_POtoInvoiceTracking` - Complete P2P tracking
- `vw_SupplierPerformance` - Supplier metrics

## Sample Data

The database includes 7 sample invoices covering various scenarios:

| Invoice ID | Scenario | Status | Notes |
|------------|----------|--------|-------|
| INV-001 | Normal PO invoice | PAID | Fully processed and paid |
| INV-002 | Normal PO invoice | POSTED | Awaiting payment |
| INV-003 | Service invoice | POSTED | Non-material PO |
| INV-004 | Price variance | HELD | Blocked for review (price mismatch) |
| INV-005 | Quantity variance | HELD | Blocked for review (qty mismatch) |
| INV-006 | Non-PO invoice | PARKED | Awaiting approval |
| INV-007 | Credit memo | POSTED | Return/adjustment |

## Example Queries

### 1. View All Outstanding Invoices
```sql
SELECT * FROM vw_OutstandingInvoices 
ORDER BY PaymentDueDate;
```

### 2. Find Invoices with Variances
```sql
SELECT * FROM vw_InvoiceVariances 
WHERE BlockingReason IS NOT NULL;
```

### 3. Track a Specific PO Through P2P Cycle
```sql
SELECT * FROM vw_POtoInvoiceTracking 
WHERE PurchaseOrderID = 'PO-2024001';
```

### 4. Supplier Performance Analysis
```sql
SELECT * FROM vw_SupplierPerformance 
ORDER BY TotalInvoiceAmount DESC;
```

### 5. Overdue Invoices
```sql
SELECT 
    InvoiceID,
    SupplierName,
    GrossAmount,
    Currency,
    PaymentDueDate,
    DaysOverdue
FROM vw_OutstandingInvoices 
WHERE DaysOverdue > 0
ORDER BY DaysOverdue DESC;
```

### 6. Invoice Approval Workflow Status
```sql
SELECT 
    InvoiceStatus,
    COUNT(*) AS Count,
    SUM(GrossAmount) AS TotalAmount,
    Currency
FROM SupplierInvoices
GROUP BY InvoiceStatus, Currency
ORDER BY InvoiceStatus;
```

### 7. Three-Way Match Verification
```sql
SELECT 
    si.InvoiceID,
    si.SupplierInvoiceNumber,
    po.PurchaseOrderID,
    gr.GoodsReceiptID,
    po.TotalAmount AS POAmount,
    si.GrossAmount AS InvoiceAmount,
    (si.GrossAmount - po.TotalAmount) AS Variance
FROM SupplierInvoices si
JOIN PurchaseOrders po ON si.PurchaseOrderID = po.PurchaseOrderID
LEFT JOIN GoodsReceipts gr ON po.PurchaseOrderID = gr.PurchaseOrderID
WHERE si.PurchaseOrderID IS NOT NULL;
```

## P2P Workflow Stages

```
1. Purchase Requisition (not included in this simplified model)
   ↓
2. Purchase Order (PurchaseOrders table)
   ↓
3. Goods Receipt (GoodsReceipts table)
   ↓
4. Supplier Invoice (SupplierInvoices table) ← Main Focus
   ↓
5. Payment (InvoicePayments table)
```

## Invoice Statuses

- **PARKED**: Invoice entered but not yet posted (requires approval)
- **HELD**: Invoice blocked due to variances or other issues
- **POSTED**: Invoice posted to accounts payable (ready for payment)
- **PAID**: Invoice fully paid
- **CANCELLED**: Invoice cancelled/reversed

## Blocking Reasons

- **PRICE_VARIANCE**: Invoice price doesn't match PO price
- **QUANTITY_VARIANCE**: Invoice quantity doesn't match GR quantity
- **DATE_VARIANCE**: Date-related discrepancies
- **MANUAL**: Manually blocked by user
- **QUALITY**: Quality issues with received goods

## Key Features

✅ Complete P2P workflow coverage  
✅ Three-way matching (PO → GR → Invoice)  
✅ Variance detection and blocking  
✅ Multi-currency support  
✅ Payment tracking  
✅ Audit trail (CreatedBy, CreatedDate, PostedBy, PostedDate)  
✅ Service and material invoices  
✅ Credit memo support  
✅ Non-PO invoice handling  

## Database Diagram

```
Suppliers ──────┐
                │
CompanyCodes ───┼──→ PurchaseOrders ──→ PurchaseOrderItems
                │            │                    │
Plants ─────────┘            │                    │
                             ↓                    ↓
Materials ────────────→ GoodsReceipts ──→ GoodsReceiptItems
                             │                    │
                             ↓                    ↓
                      SupplierInvoices ──→ SupplierInvoiceItems
                             │
                             ↓
                      InvoicePayments
```

## Notes

- Foreign key constraints are enabled
- All monetary values use appropriate precision (2 decimal places)
- Dates are stored as TEXT in SQLite (ISO 8601 format: 'YYYY-MM-DD')
- Boolean values use INTEGER (1/0) in SQLite
- Sample data uses realistic business scenarios
- Views provide common business queries out-of-the-box

## Troubleshooting

### SQLite: "no such table" error
Make sure you're in the correct directory and the database file exists:
```bash
ls -l p2p_invoice.db
```

### Foreign key constraint errors
Ensure foreign keys are enabled:
```sql
PRAGMA foreign_keys = ON;
```

### Date comparison issues in SQLite
Use julianday() for date arithmetic:
```sql
SELECT julianday('now') - julianday(PaymentDueDate) AS DaysOverdue
FROM SupplierInvoices;
```

## Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- SAP P2P Process Documentation (if applicable)

## License

This is sample data for educational and testing purposes.
