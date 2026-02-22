# P2P Workflow Architecture

**Type**: Architecture  
**Category**: Business Process  
**Created**: 2026-01-19  
**Updated**: 2026-01-25  
**Status**: Active

## Overview

Complete end-to-end Procure-to-Pay (P2P) workflow architecture based on SAP S/4HANA business processes. Defines the data model, process flows, and integration points for P2P operations from supplier management through payment processing.

## Related Documentation

- [[Data Products in HANA Cloud]] - Data product consumption approach
- [[CSN HANA Cloud Solution]] - CSN data access for schema definitions
- [[HANA Connection Module]] - Database connectivity for P2P data
- [[Modular Architecture]] - Module structure for P2P components

## P2P Process Flow

```
┌─────────────────┐
│  1. SUPPLIER    │  Master Data
│   Management    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 2. PURCHASE     │  ←── Payment Terms
│     ORDER       │
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
    │ 4. SUPPLIER   │  Three-Way Match
    │    INVOICE    │  (PO + GR/SES + Invoice)
    └───────┬───────┘
            │
            ↓
    ┌───────────────┐
    │ 5. JOURNAL    │  FI Posting (KR)
    │    ENTRY      │  Dr. Expense | Cr. AP
    └───────┬───────┘
            │
            ↓
    ┌───────────────┐
    │  6. PAYMENT   │  Payment Processing
    │   PROCESSING  │
    └───────┬───────┘
            │
            ↓
    ┌───────────────┐
    │ 7. JOURNAL    │  Payment Clearing (KZ)
    │    ENTRY      │  Dr. AP | Cr. Bank
    └───────────────┘
```

## Data Model

### Entity Groups

**1. Master Data** (9 entities)
- Suppliers (vendor master)
- Payment Terms (discount terms)
- Company Codes (legal entities)
- Plants (locations)
- Cost Centers (cost accounting)
- Materials (product master)
- Services (service master)
- GL Accounts (chart of accounts)
- Tax Codes (tax master)

**2. Purchase Orders** (3 entities)
- PurchaseOrders (header)
- PurchaseOrderItems (line items)
- PurchaseOrderHistory (document flow)

**3. Goods Receipts** (2 entities)
- GoodsReceipts (header)
- GoodsReceiptItems (line items)

**4. Service Entry Sheets** (2 entities)
- ServiceEntrySheets (header)
- ServiceEntrySheetItems (line items)

**5. Supplier Invoices** (2 entities)
- SupplierInvoices (header)
- SupplierInvoiceItems (line items)

**6. Payments** (2 entities)
- PaymentRuns (batch processing)
- InvoicePayments (individual payments)

**7. Financial Postings** (2 entities)
- JournalEntries (accounting document)
- JournalEntryItems (GL line items)

**Total**: 22 tables, 8 views

## Business Process Scenarios

### Scenario 1: Standard Material Procurement

**Flow**: PO → GR → Invoice → Payment

**Steps**:
1. Create Purchase Order for materials
2. Receive goods (Goods Receipt)
3. Supplier sends invoice
4. System performs three-way match (PO, GR, Invoice)
5. Post invoice if match successful
6. Execute payment per payment terms

**Key Tables**:
- PurchaseOrders, PurchaseOrderItems
- GoodsReceipts, GoodsReceiptItems
- SupplierInvoices, SupplierInvoiceItems
- JournalEntries (KR posting)
- InvoicePayments
- JournalEntries (KZ clearing)

### Scenario 2: Service Procurement

**Flow**: PO → SES → Invoice → Payment

**Steps**:
1. Create Purchase Order for services
2. Service performed by vendor
3. Create Service Entry Sheet (SES)
4. Manager acceptance workflow
5. Supplier sends invoice
6. Three-way match (PO, SES, Invoice)
7. Post invoice
8. Execute payment

**Key Tables**:
- PurchaseOrders, PurchaseOrderItems
- ServiceEntrySheets, ServiceEntrySheetItems
- SupplierInvoices, SupplierInvoiceItems
- JournalEntries, InvoicePayments

### Scenario 3: Variance Management

**Flow**: Invoice → Variance Detection → Block → Review → Approve/Reject

**Variance Types**:
- **Price Variance**: Invoice price ≠ PO price
- **Quantity Variance**: Invoice qty ≠ GR/SES qty
- **Date Variance**: Invoice date > tolerance

**Process**:
1. Invoice received with discrepancies
2. System calculates variance amounts
3. Invoice automatically blocked (HELD status)
4. AP team reviews variance
5. Decision: Approve variance OR Reject invoice
6. If approved: Release block and process

**Key Fields**:
- `SupplierInvoiceItems.PriceVarianceIndicator`
- `SupplierInvoiceItems.QuantityVarianceIndicator`
- `SupplierInvoiceItems.VarianceAmount`
- `SupplierInvoices.BlockingReason`
- `SupplierInvoices.InvoiceStatus` (HELD)

### Scenario 4: Early Payment Discount

**Flow**: Invoice → Discount Calculation → Early Payment → Discount Taken

**Payment Terms Example**: 2/10 NET 30
- 2% discount if paid within 10 days
- Net amount due in 30 days

**Process**:
1. Invoice posted with payment terms
2. System calculates:
   - Discount date (invoice date + 10 days)
   - Discount amount (gross * 2%)
   - Due date (invoice date + 30 days)
3. Payment run proposes payment before discount date
4. Execute payment with discount
5. System records discount taken

**Key Fields**:
- `PaymentTerms.CashDiscount1Percent`
- `PaymentTerms.CashDiscount1Days`
- `SupplierInvoices.CashDiscount1Date`
- `SupplierInvoices.CashDiscount1Amount`
- `InvoicePayments.DiscountAmount`

## Data Product Mapping

### P2P Data Products (from SAP BDC)

| Data Product | CSN File | Primary Entities | Status |
|--------------|----------|------------------|--------|
| **Supplier** | sap-s4com-Supplier-v1 | Supplier, SupplierCompany | ✅ Available |
| **Purchase Order** | sap-s4com-PurchaseOrder-v1 | PurchasingDocument, PurchasingDocumentItem | ✅ Available |
| **Service Entry Sheet** | sap-s4com-ServiceEntrySheet-v1 | ServiceEntrySheet, ServiceEntrySheetItem | ✅ Available |
| **Supplier Invoice** | sap-s4com-SupplierInvoice-v1 | SupplierInvoice, SupplierInvoiceItem | ✅ Available |
| **Payment Terms** | sap-s4com-PaymentTerms-v1 | PaymentTerms | ✅ Available |
| **Journal Entry** | sap-s4com-JournalEntryHeader-v1 | JournalEntry, JournalEntryItem | ✅ Available |

### CSN Access

**Method**: Query native HANA table (see [[CSN HANA Cloud Solution]])

```sql
SELECT CSN_JSON 
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
WHERE REMOTE_SOURCE_NAME LIKE '%PurchaseOrder%';
```

## Integration Points

### 1. HANA Cloud Connection

**Module**: [[HANA Connection Module]]

**Usage**:
```python
from modules.hana_connection.backend import HanaConnectionService

conn = HanaConnectionService()
result = conn.execute_query("SELECT * FROM SUPPLIER")
```

### 2. Data Products Module

**Location**: `modules/data_products/`

**Capabilities**:
- Browse available data products
- Query data product entities
- Parse CSN definitions
- Generate sample data

### 3. CSN Validation Module

**Location**: `modules/csn_validation/`

**Capabilities**:
- Validate CSN structure
- Compare CSN vs HANA schema
- Identify schema drift
- Generate migration scripts

## Pre-built Views

### vw_CompleteP2PTracking
Complete end-to-end tracking from PO to Payment
- All document references
- Status tracking
- Amount reconciliation

### vw_OutstandingInvoices
Unpaid invoices with due dates
- Payment due dates
- Days overdue
- Blocking status

### vw_InvoiceVariances
Invoices with discrepancies
- Price/quantity variances
- Variance amounts
- Blocking reasons

### vw_SupplierPerformance
Supplier metrics and KPIs
- Invoice counts and amounts
- Blocked invoice statistics
- Processing time averages

### vw_ServiceEntrySheetStatus
Service confirmation tracking
- Acceptance status
- Document flow

### vw_PurchaseOrderStatus
PO summary and progress
- Item counts
- Received quantities
- Invoiced quantities

### vw_PaymentTermsUsage
Payment terms analysis
- Usage frequency
- Total amounts
- Discount tracking

### vw_FinancialPostings
Journal entries with source tracking
- Document types (KR, KZ, SA)
- Debit/credit totals
- Multi-currency support

## Sample Data Scenarios

**Included scenarios demonstrate**:
- Material procurement (steel, electronics)
- Service procurement (maintenance, logistics)
- Price variance blocking
- Partial goods receipt
- Partial service entry
- Multi-currency operations (EUR, USD, SGD)
- Cash discount opportunities
- Payment clearing

## Query Examples

### Outstanding Invoices
```sql
SELECT * FROM vw_OutstandingInvoices 
WHERE PaymentDueDate <= date('now', '+7 days')
ORDER BY PaymentDueDate;
```

### Variance Analysis
```sql
SELECT * FROM vw_InvoiceVariances 
WHERE BlockingReason IS NOT NULL
ORDER BY VarianceAmount DESC;
```

### Supplier Performance
```sql
SELECT * FROM vw_SupplierPerformance 
ORDER BY TotalInvoiceAmount DESC;
```

### Cash Discount Opportunities
```sql
SELECT 
    InvoiceID,
    SupplierInvoiceNumber,
    GrossAmount,
    CashDiscount1Amount,
    CashDiscount1Date,
    CAST(julianday(CashDiscount1Date) - julianday('now') AS INTEGER) AS DaysRemaining
FROM SupplierInvoices
WHERE PaymentStatus = 'UNPAID'
    AND CashDiscount1Date >= date('now')
ORDER BY DaysRemaining;
```

## Implementation Files

### Database Scripts
- `scripts/sql/sqlite/p2p_complete_workflow_sqlite.sql` - Complete schema + data
- `scripts/sql/hana/users/create_p2p_data_product_user.sql` - User setup

### CSN Definitions
- `data-products/sap-s4com-Supplier-v1.en.json`
- `data-products/sap-s4com-PurchaseOrder-v1.en.json`
- `data-products/sap-s4com-ServiceEntrySheet-v1.en.json`
- `data-products/sap-s4com-SupplierInvoice-v1.en.json`
- `data-products/sap-s4com-PaymentTerms-v1.en.json`
- `data-products/sap-s4com-JournalEntryHeader-v1.en.json`

### Related Documentation
- Entity mapping: `docs/p2p/CSN_ENTITY_MAPPING_ANALYSIS.md`
- Gap analysis: `docs/p2p/P2P_DATA_PRODUCTS_GAP_ANALYSIS.md`
- CSN analysis: `docs/p2p/sap_data_products_csn_analysis.md`
- Web apps guide: `docs/p2p/P2P_WEB_APPLICATIONS_GUIDE.md`

## Status

✅ **ACTIVE ARCHITECTURE** - Production data model

**Used By**:
- Data Products module
- CSN Validation module
- P2P web application
- Development and testing

**Validated By**:
- SAP S/4HANA CSN definitions
- Business process analysis
- Sample data scenarios
- Query testing

## References

- Database schema: `scripts/sql/sqlite/p2p_complete_workflow_sqlite.sql`
- CSN files: `data-products/`
- Module: `modules/data_products/`
- Backend: [[HANA Connection Module]]