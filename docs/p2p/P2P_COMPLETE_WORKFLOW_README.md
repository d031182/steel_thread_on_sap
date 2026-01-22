# Complete End-to-End Procure-to-Pay (P2P) Workflow Database

## Overview

This database provides a complete, consistent end-to-end Procure-to-Pay workflow implementation with **22 tables** and **8 views** based on SAP S/4HANA CSN (Core Schema Notation) definitions. It includes all major entities from the P2P process: Supplier, Purchase Order, Service Entry Sheet, Supplier Invoice, Payment Terms, and Journal Entry (Financial Accounting).

## Based on SAP CSN Files

This database schema is derived from the following SAP S/4HANA CSN definition files (English-only versions):
- `sap-s4com-Supplier-v1.en.json`
- `sap-s4com-PurchaseOrder-v1.en.json`
- `sap-s4com-ServiceEntrySheet-v1.en.json`
- `sap-s4com-SupplierInvoice-v1.en.json`
- `sap-s4com-PaymentTerms-v1.en.json`
- `sap-s4com-JournalEntryHeader-v1.en.json`

## Quick Start

```bash
# Create the database
sqlite3 p2p_complete.db < p2p_complete_workflow_sqlite.sql

# Open and query
sqlite3 p2p_complete.db

# Example query - View complete P2P tracking
SELECT * FROM vw_CompleteP2PTracking;
```

## Complete P2P Workflow

```
┌─────────────────┐
│  1. SUPPLIER    │
│   Master Data   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 2. PURCHASE     │
│     ORDER       │ ←── Payment Terms (Master Data)
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌─────────┐ ┌──────────────┐
│ 3a.     │ │ 3b. SERVICE  │
│ GOODS   │ │ ENTRY SHEET  │
│ RECEIPT │ │              │
└────┬────┘ └──────┬───────┘
     │             │
     └──────┬──────┘
            ↓
    ┌───────────────┐
    │ 4. SUPPLIER   │
    │    INVOICE    │
    └───────┬───────┘
            │
            ↓
    ┌───────────────┐
    │ 5. JOURNAL    │
    │    ENTRY      │ ← Financial Posting (KR - Vendor Invoice)
    │  (FI Posting) │   Dr. Expense/Inventory, Dr. Tax
    └───────┬───────┘   Cr. Accounts Payable
            │
            ↓
    ┌───────────────┐
    │  6. PAYMENT   │
    │   PROCESSING  │
    └───────┬───────┘
            │
            ↓
    ┌───────────────┐
    │ 7. JOURNAL    │
    │    ENTRY      │ ← Payment Clearing (KZ - Vendor Payment)
    │  (Clearing)   │   Dr. Accounts Payable
    └───────────────┘   Cr. Bank/Cash
```

## Database Structure

### 1. Master Data Tables (9 tables)

#### Suppliers
Complete supplier/vendor information including:
- Contact details (address, phone, email)
- Financial information (currency, payment terms, tax numbers)
- Banking information (IBAN, SWIFT, account details)
- Status controls (active, blocked, blocking reasons)

#### Payment Terms
Payment terms master data:
- Cash discount terms (days and percentages)
- Net payment days
- Partial payment options

#### Company Codes
Legal entities with:
- Country and currency
- Tax jurisdiction
- Address information

#### Plants
Physical locations/delivery addresses:
- Linked to company codes
- Address and postal information

#### Cost Centers
Cost accounting objects:
- Linked to company codes
- Responsible persons

#### Materials
Product master data:
- Material types (RAW, SEMI, FINISHED, TRADING)
- Material groups and pricing

#### Services
Service master data:
- Service categories
- Standard pricing and units of measure

### 2. Purchase Order Tables (3 tables)

#### PurchaseOrders
Header-level information:
- Supplier and company code
- Payment and delivery terms (Incoterms)
- Document statuses (PO status, release status)
- Total amounts (net, tax, gross)

#### PurchaseOrderItems
Line item details:
- Item categories (STANDARD, SERVICE, CONSIGNMENT, etc.)
- Material or service references
- Quantities and pricing
- Account assignment (cost center, GL account)
- Delivery tolerances

#### PurchaseOrderHistory
Document flow tracking:
- Transaction types (GR, IR, SES)
- Reference documents
- Quantities and dates

### 3. Goods Receipt Tables (2 tables)

#### GoodsReceipts
Material receipt documents:
- Reference to purchase orders
- Posting and document dates
- Movement types

#### GoodsReceiptItems
Receipt line items:
- PO and material references
- Quantities received
- Quality inspection status
- Valuation amounts

### 4. Service Entry Sheet Tables (2 tables)

#### ServiceEntrySheets
Service confirmation documents:
- Reference to purchase orders
- Service performer information
- Acceptance status and dates

#### ServiceEntrySheetItems
Service line items:
- Service descriptions
- Quantities and performance dates
- Pricing and account assignment
- Acceptance status per item

### 5. Supplier Invoice Tables (2 tables)

#### SupplierInvoices
Invoice header information:
- Supplier and PO references
- Invoice dates and numbers
- Payment terms and due dates
- Amounts (gross, net, tax)
- Status (invoice status, payment status)
- Blocking/hold information with reasons
- Payment run information

#### SupplierInvoiceItems
Invoice line items:
- Complete references (PO, GR, SES)
- Material/service details
- Quantities and pricing
- Variance indicators (price, quantity, date)
- Variance amounts

### 6. Payment Tables (2 tables)

#### PaymentRuns
Batch payment processing:
- Payment run date and method
- Status (proposed, executed, cancelled)
- Total amounts

#### InvoicePayments
Individual invoice payments:
- Payment amounts and dates
- Payment methods and references
- Bank account details
- Payment status tracking

### 7. Journal Entry Tables (2 tables)

#### JournalEntries
Accounting document header (Financial Accounting postings):
- Company code, fiscal year, accounting document (compound key)
- Document types (KR = Vendor Invoice, KZ = Vendor Payment, SA = GL Document)
- Reference to source documents (Invoice ID, Payment ID)
- Multi-currency support with exchange rates
- Document status and reversal tracking
- Complete audit trail

#### JournalEntryItems
GL account line items (double-entry bookkeeping):
- GL account postings with debit/credit indicators (S = Debit/Soll, H = Credit/Haben)
- Amount tracking in transaction and company code currencies
- Cost center and profit center assignments
- Supplier/customer linkages for sub-ledger reconciliation
- Clearing information for payment matching
- Tax tracking per line item
- Purchase order, material, and plant references

## Pre-built Views

### vw_CompleteP2PTracking
Complete end-to-end tracking from PO to Payment:
- Purchase order details
- Goods receipt or service entry information
- Invoice details with status
- Payment information
- All in one comprehensive view

### vw_OutstandingInvoices
All unpaid invoices with:
- Payment due dates
- Days overdue calculation
- Blocking status and reasons
- Payment terms information

### vw_InvoiceVariances
Invoices with discrepancies:
- Price variances
- Quantity variances
- Variance amounts
- Blocking reasons

### vw_SupplierPerformance
Supplier metrics and KPIs:
- Total invoices and amounts
- Blocked invoices count
- Average processing days
- Paid vs unpaid status

### vw_ServiceEntrySheetStatus
Service entry sheet tracking:
- Acceptance status
- Document status
- Service descriptions and quantities

### vw_PurchaseOrderStatus
Purchase order summary:
- PO status and release status
- Item counts and quantities
- Received and invoiced quantities

### vw_PaymentTermsUsage
Payment terms utilization:
- Times used
- Total invoice amounts
- Discounts taken and amounts

### vw_FinancialPostings
Journal entries with source document tracking:
- Accounting documents (KR = Invoice, KZ = Payment, SA = GL Posting)
- Source document references (Invoice ID, Payment ID)
- Supplier information
- Multi-currency with exchange rates
- Debit/credit totals per document
- Complete audit trail

## Sample Data

The database includes complete sample data demonstrating:

### 5 Suppliers
- 3 material suppliers
- 2 service providers
- Complete contact and banking information

### 4 Payment Terms
- NET30, NET60, 2/10NET30, 3/15NET45

### 4 Purchase Orders
1. Material PO (steel plate)
2. Service PO (equipment maintenance)
3. Mixed material PO (electronics)
4. International service PO (logistics)

### 2 Goods Receipts
- Full receipt for PO-2024001
- Partial receipt for PO-2024003

### 2 Service Entry Sheets
- Partial service completion (40 of 80 hours)
- Full service completion (international shipment)

### 5 Supplier Invoices
1. **INV-2024001**: Material invoice (PAID) - with GR reference
2. **INV-2024002**: Service invoice (POSTED) - with SES reference
3. **INV-2024003**: Material invoice (HELD) - price variance
4. **INV-2024004**: Service invoice (POSTED) - with SES reference
5. **INV-2024005**: Non-PO invoice (PARKED) - awaiting approval

### 1 Payment Run & Payment
- Payment run executed on 2024-03-20
- Payment for INV-2024001 (ACH, cleared)

### 5 Journal Entries (Financial Accounting Postings)
1. **5000000001** (KR): Invoice posting for INV-2024001 - Material purchase
   - Dr. GR/IR Clearing 5000 | Dr. Tax Input 250 | Cr. AP 5250
2. **5000000002** (KZ): Payment clearing for INV-2024001
   - Dr. Accounts Payable 5250 | Cr. Bank 5250
3. **5000000003** (KR): Invoice posting for INV-2024002 - Service purchase
   - Dr. Services Expense 5000 | Dr. Tax Input 250 | Cr. AP 5250
4. **5000000004** (KR): Invoice posting for INV-2024003 - With price variance
   - Dr. Inventory 13500 | Dr. Tax 676 | Dr. Price Variance 200 | Cr. AP 15488
5. **5000000005** (KR): Invoice posting for INV-2024004 - Multi-currency
   - Dr. Logistics Expense 2550 | Dr. Tax 128 | Cr. AP 2678 (USD→SGD @ 1.35)

## Key Features

### Complete Document Flow
✅ Purchase Order → Goods Receipt → Invoice → Payment  
✅ Purchase Order → Service Entry Sheet → Invoice → Payment  
✅ Non-PO Invoices (directly to invoice)

### Three-Way Matching
- Purchase Order quantities and prices
- Goods Receipt/Service Entry quantities
- Invoice quantities and prices
- Automated variance detection

### Variance Management
- Price variance detection and blocking
- Quantity variance detection
- Variance amount calculation
- Blocking reason tracking

### Payment Management
- Payment terms with discount options
- Payment due date calculation
- Cash discount tracking
- Payment run processing
- Multiple payment methods

### Service Procurement
- Service Entry Sheet acceptance workflow
- Service performer tracking
- Performance date recording
- Account assignment to cost centers

### Multi-Currency Support
- Currency per transaction
- Exchange rate tracking
- Multi-national operations (USD, EUR, SGD)

### Complete Audit Trail
- Created by/date for all documents
- Posted by/date for finalized documents
- Last changed by/date tracking
- Document status history

## Example Queries

### 1. Complete P2P Cycle for a Specific PO
```sql
SELECT * FROM vw_CompleteP2PTracking 
WHERE PurchaseOrderID = 'PO-2024001';
```

### 2. Outstanding Invoices Due This Week
```sql
SELECT * FROM vw_OutstandingInvoices 
WHERE julianday(PaymentDueDate) BETWEEN julianday('now') AND julianday('now', '+7 days')
ORDER BY PaymentDueDate;
```

### 3. Invoices Blocked for Variances
```sql
SELECT * FROM vw_InvoiceVariances 
WHERE BlockingReason IS NOT NULL
ORDER BY InvoiceDate DESC;
```

### 4. Supplier Performance Report
```sql
SELECT * FROM vw_SupplierPerformance 
ORDER BY TotalInvoiceAmount DESC;
```

### 5. Service Entry Sheets Pending Acceptance
```sql
SELECT * FROM vw_ServiceEntrySheetStatus 
WHERE AcceptanceStatus = 'NOT_ACCEPTED'
ORDER BY DocumentDate;
```

### 6. PO Items Not Yet Fully Received
```sql
SELECT 
    poi.PurchaseOrderID,
    poi.ItemNumber,
    COALESCE(m.MaterialDescription, s.ServiceDescription) AS Item,
    poi.OrderQuantity,
    poi.QuantityReceived,
    (poi.OrderQuantity - poi.QuantityReceived) AS Outstanding
FROM PurchaseOrderItems poi
LEFT JOIN Materials m ON poi.MaterialID = m.MaterialID
LEFT JOIN Services s ON poi.ServiceID = s.ServiceID
WHERE poi.QuantityReceived < poi.OrderQuantity
AND poi.ItemStatus != 'CANCELLED';
```

### 7. Invoice Payment Status Summary
```sql
SELECT 
    InvoiceStatus,
    PaymentStatus,
    COUNT(*) AS Count,
    ROUND(SUM(GrossAmount), 2) AS TotalAmount,
    Currency
FROM SupplierInvoices
GROUP BY InvoiceStatus, PaymentStatus, Currency
ORDER BY InvoiceStatus, PaymentStatus;
```

### 8. Cash Discount Opportunities
```sql
SELECT 
    si.InvoiceID,
    si.SupplierInvoiceNumber,
    s.SupplierName,
    si.GrossAmount,
    si.Currency,
    si.CashDiscount1Date,
    si.CashDiscount1Amount,
    CAST(julianday(si.CashDiscount1Date) - julianday('now') AS INTEGER) AS DaysRemaining
FROM SupplierInvoices si
JOIN Suppliers s ON si.SupplierID = s.SupplierID
WHERE si.PaymentStatus = 'UNPAID'
    AND si.CashDiscount1Date IS NOT NULL
    AND si.CashDiscount1Date >= date('now')
ORDER BY DaysRemaining;
```

### 9. Document Flow History for a PO
```sql
SELECT 
    poh.PurchaseOrderID,
    poh.ItemNumber,
    poh.TransactionType,
    poh.ReferenceDocument,
    poh.Quantity,
    poh.PostingDate,
    CASE poh.TransactionType
        WHEN 'GR' THEN 'Goods Receipt'
        WHEN 'SES' THEN 'Service Entry'
        WHEN 'IR' THEN 'Invoice Receipt'
    END AS TransactionDescription
FROM PurchaseOrderHistory poh
WHERE poh.PurchaseOrderID = 'PO-2024001'
ORDER BY poh.PostingDate;
```

### 10. Supplier Banking Details
```sql
SELECT 
    SupplierID,
    SupplierName,
    IBAN,
    SWIFTCode,
    BankCountry,
    BankAccountNumber
FROM Suppliers
WHERE IsActive = 1
ORDER BY SupplierName;
```

## Entity Relationships

### Core Relationships
- `Suppliers` → `PurchaseOrders` (1:N)
- `PaymentTerms` → `PurchaseOrders` (1:N)
- `PaymentTerms` → `SupplierInvoices` (1:N)
- `PurchaseOrders` → `PurchaseOrderItems` (1:N)
- `PurchaseOrders` → `GoodsReceipts` (1:N)
- `PurchaseOrders` → `ServiceEntrySheets` (1:N)
- `PurchaseOrders` → `SupplierInvoices` (1:N)
- `GoodsReceipts` → `GoodsReceiptItems` (1:N)
- `ServiceEntrySheets` → `ServiceEntrySheetItems` (1:N)
- `SupplierInvoices` → `SupplierInvoiceItems` (1:N)
- `SupplierInvoices` → `InvoicePayments` (1:N)
- `PaymentRuns` → `InvoicePayments` (1:N)

### Cross-Document References
- `SupplierInvoiceItems` → `PurchaseOrderItems` (N:1)
- `SupplierInvoiceItems` → `GoodsReceiptItems` (N:1)
- `SupplierInvoiceItems` → `ServiceEntrySheetItems` (N:1)

## Business Process Scenarios

### Scenario 1: Standard Material Procurement
1. Create Purchase Order for materials
2. Receive goods (Goods Receipt)
3. Supplier sends invoice
4. Three-way match (PO, GR, Invoice)
5. Post invoice
6. Execute payment

### Scenario 2: Service Procurement
1. Create Purchase Order for services
2. Service performed
3. Create Service Entry Sheet
4. Acceptance by manager
5. Supplier sends invoice
6. Three-way match (PO, SES, Invoice)
7. Post invoice
8. Execute payment

### Scenario 3: Variance Handling
1. Invoice received with price different from PO
2. System detects price variance
3. Invoice automatically blocked (HELD status)
4. AP team reviews variance
5. Either: Reject invoice OR Approve variance
6. If approved: Release block and process payment

### Scenario 4: Non-PO Invoice
1. Invoice received without PO reference
2. Create parked invoice
3. Route for approval
4. Once approved, post invoice
5. Execute payment

### Scenario 5: Early Payment Discount
1. Invoice posted with payment terms including discount
2. System calculates discount date and amount
3. Payment run proposes payment before discount date
4. Execute payment with discount
5. System records discount taken

## Technical Notes

### SQLite-Specific Features
- `TEXT` datatype for strings
- `REAL` datatype for numbers
- `INTEGER` datatype for booleans (1 = true, 0 = false)
- `julianday()` function for date calculations
- `AUTOINCREMENT` for PurchaseOrderHistory
- `PRAGMA foreign_keys = ON` for referential integrity

### Data Types
- Dates stored as TEXT in ISO 8601 format ('YYYY-MM-DD')
- Timestamps stored as TEXT ('YYYY-MM-DD HH:MM:SS')
- Currency amounts stored as REAL with 2 decimal precision
- IDs stored as TEXT for flexibility

### Constraints
- PRIMARY KEY constraints on all tables
- FOREIGN KEY constraints for referential integrity
- CHECK constraints for status values
- NOT NULL constraints for required fields
- DEFAULT values for common fields

## File Size & Performance
- Compact SQLite database
- Indexed foreign keys for performance
- Views pre-compiled for fast queries
- Sample data demonstrates all scenarios
- Suitable for demo, development, and testing

## Use Cases

### Development
- API development and testing
- Integration testing
- Data model understanding
- Query development

### Training
- P2P process education
- SAP concept demonstration
- SQL query practice
- Reporting development

### Prototyping
- Proof of concept development
- UI mockups with real data
- Business process simulation
- Integration pattern testing

## Differences from Simplified Database

This **complete workflow** database includes:

✅ **More comprehensive master data**:
- Full supplier details (banking, tax, contacts)
- Payment terms with discount structures
- Cost centers for account assignment
- Separate Materials and Services tables

✅ **Service Entry Sheet support**:
- Complete service procurement workflow
- Acceptance workflow
- Service performer tracking

✅ **Purchase Order History**:
- Document flow tracking
- Transaction type logging

✅ **Payment Run processing**:
- Batch payment management
- Payment proposal workflow

✅ **Enhanced invoice features**:
- Cash discount tracking
- Payment run linkage
- More detailed status fields

✅ **More realistic sample data**:
- Multi-currency transactions
- International operations
- Mixed scenarios (materials and services)

✅ **Additional views**:
- Service Entry Sheet status
- Payment terms utilization
- Purchase order status summary

## Compatibility

- **SQLite**: 3.x and above
- **Can be adapted to**:
  - MySQL
  - PostgreSQL
  - SQL Server
  - Oracle

## License

Sample database for educational and development purposes.

---

**Created**: January 19, 2026  
**Based on**: SAP S/4HANA CSN Definitions  
**Version**: 1.0  
**Database**: SQLite
