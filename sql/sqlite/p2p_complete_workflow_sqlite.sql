-- ============================================================================
-- Complete End-to-End Procure-to-Pay (P2P) Workflow Database - SQLite Version
-- ============================================================================
-- Based on SAP S/4HANA CSN definitions for:
-- - Supplier
-- - Purchase Order
-- - Service Entry Sheet
-- - Supplier Invoice
-- - Payment Terms
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- 1. MASTER DATA - Suppliers & Payment Terms
-- ============================================================================

-- Suppliers (Vendors) - Master Data
CREATE TABLE Suppliers (
    SupplierID TEXT PRIMARY KEY,
    SupplierName TEXT NOT NULL,
    SupplierType TEXT CHECK(SupplierType IN ('Material', 'Service', 'Both')),
    
    -- Contact Information
    StreetName TEXT,
    CityName TEXT,
    PostalCode TEXT,
    Country TEXT,
    Region TEXT,
    PhoneNumber TEXT,
    EmailAddress TEXT,
    
    -- Financial Information
    Currency TEXT DEFAULT 'USD',
    PaymentTermsCode TEXT,
    TaxNumber TEXT,
    VATRegistrationNumber TEXT,
    
    -- Banking Information
    BankCountry TEXT,
    BankNumber TEXT,
    BankAccountNumber TEXT,
    IBAN TEXT,
    SWIFTCode TEXT,
    
    -- Status and Controls
    IsActive INTEGER DEFAULT 1,
    IsBlocked INTEGER DEFAULT 0,
    BlockingReason TEXT,
    
    -- Audit
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (date('now')),
    LastChangedBy TEXT,
    LastChangedDate TEXT
);

-- Payment Terms Master Data
CREATE TABLE PaymentTerms (
    PaymentTermsCode TEXT PRIMARY KEY,
    PaymentTermsName TEXT NOT NULL,
    PaymentTermsDescription TEXT,
    
    -- Discount Terms
    CashDiscount1Days INTEGER,
    CashDiscount1Percent REAL,
    CashDiscount2Days INTEGER,
    CashDiscount2Percent REAL,
    
    -- Due Date Calculation
    NetPaymentDays INTEGER NOT NULL,
    
    -- Additional Terms
    PartialPaymentAllowed INTEGER DEFAULT 0,
    
    IsActive INTEGER DEFAULT 1
);

-- Company Codes (Legal Entities)
CREATE TABLE CompanyCodes (
    CompanyCode TEXT PRIMARY KEY,
    CompanyName TEXT NOT NULL,
    Country TEXT,
    Currency TEXT,
    TaxJurisdiction TEXT,
    Address TEXT,
    City TEXT
);

-- Plants (Physical Locations / Delivery Addresses)
CREATE TABLE Plants (
    PlantID TEXT PRIMARY KEY,
    PlantName TEXT NOT NULL,
    CompanyCode TEXT NOT NULL,
    Address TEXT,
    City TEXT,
    PostalCode TEXT,
    Country TEXT,
    Region TEXT,
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Cost Centers
CREATE TABLE CostCenters (
    CostCenter TEXT PRIMARY KEY,
    CostCenterName TEXT NOT NULL,
    CompanyCode TEXT NOT NULL,
    ControllingArea TEXT,
    ResponsiblePerson TEXT,
    IsActive INTEGER DEFAULT 1,
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Materials / Products
CREATE TABLE Materials (
    MaterialID TEXT PRIMARY KEY,
    MaterialDescription TEXT NOT NULL,
    MaterialType TEXT CHECK(MaterialType IN ('RAW', 'SEMI', 'FINISHED', 'TRADING')),
    MaterialGroup TEXT,
    BaseUnitOfMeasure TEXT,
    StandardPrice REAL,
    IsActive INTEGER DEFAULT 1
);

-- Services
CREATE TABLE Services (
    ServiceID TEXT PRIMARY KEY,
    ServiceDescription TEXT NOT NULL,
    ServiceCategory TEXT,
    UnitOfMeasure TEXT,
    StandardPrice REAL,
    IsActive INTEGER DEFAULT 1
);

-- ============================================================================
-- 2. PURCHASE ORDER (Goods & Services)
-- ============================================================================

-- Purchase Order Header
CREATE TABLE PurchaseOrders (
    PurchaseOrderID TEXT PRIMARY KEY,
    CompanyCode TEXT NOT NULL,
    
    -- Supplier Information
    SupplierID TEXT NOT NULL,
    
    -- Document Information
    DocumentDate TEXT NOT NULL,
    PurchaseOrderType TEXT, -- 'Standard', 'Subcontracting', 'Consignment', 'Service'
    PurchasingGroup TEXT,
    PurchasingOrganization TEXT,
    
    -- Payment & Delivery Terms
    PaymentTermsCode TEXT,
    IncotermsClassification TEXT,
    IncotermsLocation TEXT,
    
    -- Amounts
    Currency TEXT DEFAULT 'USD',
    TotalNetAmount REAL,
    TotalTaxAmount REAL,
    TotalGrossAmount REAL,
    
    -- Status
    POStatus TEXT CHECK(POStatus IN ('OPEN', 'PARTIALLY_RECEIVED', 'PARTIALLY_INVOICED', 'FULLY_RECEIVED', 'FULLY_INVOICED', 'CLOSED', 'CANCELLED')),
    ReleaseStatus TEXT, -- 'NOT_RELEASED', 'RELEASED', 'REJECTED'
    
    -- Dates
    RequestedDeliveryDate TEXT,
    
    -- References
    PurchaseRequisition TEXT,
    
    -- Audit
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (datetime('now')),
    LastChangedBy TEXT,
    LastChangedDate TEXT,
    
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode),
    FOREIGN KEY (PaymentTermsCode) REFERENCES PaymentTerms(PaymentTermsCode)
);

-- Purchase Order Items
CREATE TABLE PurchaseOrderItems (
    PurchaseOrderID TEXT,
    ItemNumber INTEGER,
    
    -- Item Type
    ItemCategory TEXT CHECK(ItemCategory IN ('STANDARD', 'CONSIGNMENT', 'SUBCONTRACTING', 'SERVICE', 'LIMIT', 'TEXT')),
    
    -- Material/Service Reference
    MaterialID TEXT,
    ServiceID TEXT,
    ShortText TEXT,
    
    -- Plant & Location
    PlantID TEXT,
    StorageLocation TEXT,
    
    -- Account Assignment
    AccountAssignmentCategory TEXT, -- 'K' = Cost Center, 'A' = Asset, 'P' = Project, etc.
    CostCenter TEXT,
    GLAccount TEXT,
    
    -- Quantities
    OrderQuantity REAL NOT NULL,
    UnitOfMeasure TEXT,
    QuantityReceived REAL DEFAULT 0,
    QuantityInvoiced REAL DEFAULT 0,
    
    -- Pricing
    NetPriceAmount REAL NOT NULL,
    PriceUnit REAL DEFAULT 1,
    TaxCode TEXT,
    TaxAmount REAL,
    NetAmount REAL,
    
    -- Delivery
    DeliveryDate TEXT,
    
    -- Status
    ItemStatus TEXT CHECK(ItemStatus IN ('OPEN', 'PARTIALLY_RECEIVED', 'FULLY_RECEIVED', 'CANCELLED')),
    DeletionIndicator INTEGER DEFAULT 0,
    
    -- Tolerances
    OverdeliveryTolerancePercent REAL DEFAULT 10.0,
    UnderdeliveryTolerancePercent REAL DEFAULT 10.0,
    UnlimitedOverdelivery INTEGER DEFAULT 0,
    
    PRIMARY KEY (PurchaseOrderID, ItemNumber),
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID),
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID),
    FOREIGN KEY (CostCenter) REFERENCES CostCenters(CostCenter)
);

-- Purchase Order History (for tracking document flow)
CREATE TABLE PurchaseOrderHistory (
    HistoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    PurchaseOrderID TEXT NOT NULL,
    ItemNumber INTEGER NOT NULL,
    
    -- Transaction Type
    TransactionType TEXT, -- 'GR' = Goods Receipt, 'IR' = Invoice Receipt, 'SES' = Service Entry
    
    -- Reference Document
    ReferenceDocument TEXT,
    ReferenceDocumentItem INTEGER,
    
    -- Quantities
    Quantity REAL,
    
    -- Transaction Date
    PostingDate TEXT,
    
    FOREIGN KEY (PurchaseOrderID, ItemNumber) REFERENCES PurchaseOrderItems(PurchaseOrderID, ItemNumber)
);

-- ============================================================================
-- 3. GOODS RECEIPT (For Materials)
-- ============================================================================

-- Goods Receipt Header
CREATE TABLE GoodsReceipts (
    GoodsReceiptID TEXT PRIMARY KEY,
    
    -- Reference
    PurchaseOrderID TEXT,
    
    -- Document Information
    DocumentDate TEXT NOT NULL,
    PostingDate TEXT NOT NULL,
    CompanyCode TEXT NOT NULL,
    PlantID TEXT,
    
    -- Movement Type
    MovementType TEXT, -- '101' = GR for PO, '102' = GR Reversal, etc.
    
    -- Status
    DocumentStatus TEXT CHECK(DocumentStatus IN ('POSTED', 'CANCELLED')),
    
    -- Audit
    PostedBy TEXT,
    PostedDate TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID)
);

-- Goods Receipt Items
CREATE TABLE GoodsReceiptItems (
    GoodsReceiptID TEXT,
    ItemNumber INTEGER,
    
    -- Reference
    PurchaseOrderID TEXT NOT NULL,
    POItemNumber INTEGER NOT NULL,
    
    -- Material
    MaterialID TEXT,
    MaterialDescription TEXT,
    
    -- Quantities
    QuantityReceived REAL NOT NULL,
    UnitOfMeasure TEXT,
    
    -- Location
    PlantID TEXT,
    StorageLocation TEXT,
    
    -- Valuation
    AmountInLocalCurrency REAL,
    
    -- Quality
    QualityInspectionRequired INTEGER DEFAULT 0,
    QualityInspectionStatus TEXT,
    
    PRIMARY KEY (GoodsReceiptID, ItemNumber),
    FOREIGN KEY (GoodsReceiptID) REFERENCES GoodsReceipts(GoodsReceiptID),
    FOREIGN KEY (PurchaseOrderID, POItemNumber) REFERENCES PurchaseOrderItems(PurchaseOrderID, ItemNumber),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID)
);

-- ============================================================================
-- 4. SERVICE ENTRY SHEET (For Services)
-- ============================================================================

-- Service Entry Sheet Header
CREATE TABLE ServiceEntrySheets (
    ServiceEntrySheetID TEXT PRIMARY KEY,
    
    -- Reference
    PurchaseOrderID TEXT NOT NULL,
    
    -- Document Information
    DocumentDate TEXT NOT NULL,
    CompanyCode TEXT NOT NULL,
    
    -- Service Performer
    ServicePerformer TEXT,
    ServicePerformerContactPerson TEXT,
    
    -- Acceptance
    AcceptanceStatus TEXT CHECK(AcceptanceStatus IN ('NOT_ACCEPTED', 'ACCEPTED', 'REJECTED')),
    AcceptedBy TEXT,
    AcceptanceDate TEXT,
    
    -- Status
    DocumentStatus TEXT CHECK(DocumentStatus IN ('DRAFT', 'POSTED', 'CANCELLED')),
    
    -- Amounts
    Currency TEXT,
    TotalNetAmount REAL,
    
    -- Audit
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (datetime('now')),
    PostedBy TEXT,
    PostedDate TEXT,
    
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Service Entry Sheet Items
CREATE TABLE ServiceEntrySheetItems (
    ServiceEntrySheetID TEXT,
    ItemNumber INTEGER,
    
    -- Reference
    PurchaseOrderID TEXT NOT NULL,
    POItemNumber INTEGER NOT NULL,
    
    -- Service
    ServiceID TEXT,
    ServiceDescription TEXT,
    ShortText TEXT,
    
    -- Quantities & Performance
    Quantity REAL NOT NULL,
    UnitOfMeasure TEXT,
    ServicePerformanceDate TEXT,
    
    -- Pricing
    NetPriceAmount REAL,
    NetAmount REAL,
    
    -- Account Assignment
    CostCenter TEXT,
    GLAccount TEXT,
    
    -- Acceptance
    AcceptanceStatus TEXT,
    
    PRIMARY KEY (ServiceEntrySheetID, ItemNumber),
    FOREIGN KEY (ServiceEntrySheetID) REFERENCES ServiceEntrySheets(ServiceEntrySheetID),
    FOREIGN KEY (PurchaseOrderID, POItemNumber) REFERENCES PurchaseOrderItems(PurchaseOrderID, ItemNumber),
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID),
    FOREIGN KEY (CostCenter) REFERENCES CostCenters(CostCenter)
);

-- ============================================================================
-- 5. SUPPLIER INVOICE
-- ============================================================================

-- Supplier Invoice Header
CREATE TABLE SupplierInvoices (
    InvoiceID TEXT PRIMARY KEY,
    FiscalYear TEXT NOT NULL,
    CompanyCode TEXT NOT NULL,
    
    -- Supplier
    SupplierID TEXT NOT NULL,
    
    -- Document Dates
    InvoiceDate TEXT NOT NULL,
    PostingDate TEXT NOT NULL,
    DocumentDate TEXT,
    
    -- Reference Information
    SupplierInvoiceNumber TEXT NOT NULL, -- Supplier's own invoice number
    PurchaseOrderID TEXT, -- Can be NULL for non-PO invoices
    
    -- Invoice Type
    InvoiceDocumentType TEXT, -- 'INVOICE', 'CREDIT_MEMO', 'DEBIT_MEMO'
    IsInvoice INTEGER DEFAULT 1, -- 1 = Invoice, 0 = Credit Memo
    InvoiceOrigin TEXT, -- 'MANUAL', 'EDI', 'OCR', 'ERS', 'EVALUATED_RECEIPT_SETTLEMENT'
    
    -- Payment Terms
    PaymentTermsCode TEXT,
    PaymentMethod TEXT,
    PaymentDueDate TEXT,
    CashDiscount1Amount REAL,
    CashDiscount1Date TEXT,
    CashDiscount2Amount REAL,
    CashDiscount2Date TEXT,
    
    -- Amounts
    Currency TEXT DEFAULT 'USD',
    GrossAmount REAL NOT NULL,
    NetAmount REAL,
    TaxAmount REAL,
    CashDiscountAmount REAL,
    WithholdingTaxAmount REAL,
    
    -- Status and Processing
    InvoiceStatus TEXT CHECK(InvoiceStatus IN ('PARKED', 'HELD', 'POSTED', 'PAID', 'PARTIALLY_PAID', 'CANCELLED')),
    PaymentStatus TEXT CHECK(PaymentStatus IN ('UNPAID', 'PARTIALLY_PAID', 'FULLY_PAID')),
    
    -- Blocking/Hold Reasons
    IsBlocked INTEGER DEFAULT 0,
    BlockingReason TEXT, -- 'PRICE_VARIANCE', 'QUANTITY_VARIANCE', 'DATE_VARIANCE', 'MANUAL', 'QUALITY', 'AMOUNT'
    
    -- Payment Information
    PaymentReference TEXT,
    PaymentRunDate TEXT,
    
    -- Audit Fields
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (datetime('now')),
    PostedBy TEXT,
    PostedDate TEXT,
    LastChangedBy TEXT,
    LastChangedDate TEXT,
    
    -- Foreign Keys
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode),
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID),
    FOREIGN KEY (PaymentTermsCode) REFERENCES PaymentTerms(PaymentTermsCode)
);

-- Supplier Invoice Items
CREATE TABLE SupplierInvoiceItems (
    InvoiceID TEXT,
    ItemNumber INTEGER,
    
    -- Reference Documents
    PurchaseOrderID TEXT,
    POItemNumber INTEGER,
    GoodsReceiptID TEXT,
    GRItemNumber INTEGER,
    ServiceEntrySheetID TEXT,
    SESItemNumber INTEGER,
    
    -- Material/Service Details
    MaterialID TEXT,
    ServiceID TEXT,
    MaterialDescription TEXT,
    
    -- Plant & Account Assignment
    PlantID TEXT,
    CostCenter TEXT,
    GLAccount TEXT,
    
    -- Quantities and Amounts
    Quantity REAL,
    UnitOfMeasure TEXT,
    UnitPrice REAL,
    NetAmount REAL NOT NULL,
    TaxCode TEXT,
    TaxAmount REAL,
    TotalAmount REAL,
    
    -- Variance Indicators
    HasPriceVariance INTEGER DEFAULT 0,
    HasQuantityVariance INTEGER DEFAULT 0,
    HasDateVariance INTEGER DEFAULT 0,
    HasAmountVariance INTEGER DEFAULT 0,
    
    -- Variance Amounts
    PriceVarianceAmount REAL DEFAULT 0,
    QuantityVarianceAmount REAL DEFAULT 0,
    
    -- Item Text
    ItemText TEXT,
    
    PRIMARY KEY (InvoiceID, ItemNumber),
    FOREIGN KEY (InvoiceID) REFERENCES SupplierInvoices(InvoiceID),
    FOREIGN KEY (PurchaseOrderID, POItemNumber) REFERENCES PurchaseOrderItems(PurchaseOrderID, ItemNumber),
    FOREIGN KEY (GoodsReceiptID, GRItemNumber) REFERENCES GoodsReceiptItems(GoodsReceiptID, ItemNumber),
    FOREIGN KEY (ServiceEntrySheetID, SESItemNumber) REFERENCES ServiceEntrySheetItems(ServiceEntrySheetID, ItemNumber),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID),
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID),
    FOREIGN KEY (CostCenter) REFERENCES CostCenters(CostCenter)
);

-- ============================================================================
-- 6. PAYMENT PROCESSING
-- ============================================================================

-- Payment Runs
CREATE TABLE PaymentRuns (
    PaymentRunID TEXT PRIMARY KEY,
    CompanyCode TEXT NOT NULL,
    PaymentRunDate TEXT NOT NULL,
    PaymentMethod TEXT, -- 'WIRE', 'CHECK', 'ACH', 'CARD'
    Status TEXT CHECK(Status IN ('PROPOSED', 'EXECUTED', 'CANCELLED')),
    TotalAmount REAL,
    Currency TEXT,
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Invoice Payments
CREATE TABLE InvoicePayments (
    PaymentID TEXT PRIMARY KEY,
    InvoiceID TEXT NOT NULL,
    PaymentRunID TEXT,
    
    -- Payment Details
    PaymentDate TEXT NOT NULL,
    PaymentAmount REAL NOT NULL,
    PaymentMethod TEXT,
    PaymentReference TEXT,
    
    -- Currency
    Currency TEXT,
    ExchangeRate REAL DEFAULT 1.0,
    
    -- Bank Details
    PayingCompanyBankAccount TEXT,
    BeneficiaryBankAccount TEXT,
    
    -- Status
    PaymentStatus TEXT CHECK(PaymentStatus IN ('PROPOSED', 'SENT', 'CLEARED', 'FAILED', 'CANCELLED')),
    
    -- Audit
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (InvoiceID) REFERENCES SupplierInvoices(InvoiceID),
    FOREIGN KEY (PaymentRunID) REFERENCES PaymentRuns(PaymentRunID)
);

-- ============================================================================
-- 7. JOURNAL ENTRIES (Financial Accounting Postings)
-- ============================================================================

-- Journal Entry Header (Accounting Document)
CREATE TABLE JournalEntries (
    CompanyCode TEXT,
    FiscalYear TEXT,
    AccountingDocument TEXT,
    
    -- Document Information
    AccountingDocumentType TEXT, -- 'KR' = Vendor Invoice, 'KZ' = Vendor Payment, 'SA' = GL Account Document
    DocumentDate TEXT NOT NULL,
    PostingDate TEXT NOT NULL,
    FiscalPeriod TEXT,
    
    -- Reference
    DocumentReferenceID TEXT, -- Link to source document (Invoice ID, Payment ID, etc.)
    ReferenceDocumentType TEXT, -- 'INVOICE', 'PAYMENT', 'MANUAL'
    AccountingDocumentHeaderText TEXT,
    
    -- Currency
    TransactionCurrency TEXT DEFAULT 'USD',
    CompanyCodeCurrency TEXT DEFAULT 'USD',
    ExchangeRate REAL DEFAULT 1.0,
    
    -- Status
    AccountingDocumentCategory TEXT, -- 'NORMAL', 'REVERSAL', 'ACCRUAL'
    IsReversal INTEGER DEFAULT 0,
    ReverseDocument TEXT,
    ReversalReason TEXT,
    
    -- Audit
    AccountingDocCreatedByUser TEXT,
    AccountingDocumentCreationDate TEXT DEFAULT (date('now')),
    CreationTime TEXT DEFAULT (time('now')),
    LastChangeDate TEXT,
    
    PRIMARY KEY (CompanyCode, FiscalYear, AccountingDocument),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Journal Entry Items (GL Account Line Items)
CREATE TABLE JournalEntryItems (
    CompanyCode TEXT,
    FiscalYear TEXT,
    AccountingDocument TEXT,
    AccountingDocumentItem INTEGER,
    
    -- GL Account
    GLAccount TEXT NOT NULL,
    GLAccountName TEXT,
    
    -- Amounts (in Transaction Currency)
    AmountInTransactionCurrency REAL NOT NULL,
    DebitCreditCode TEXT CHECK(DebitCreditCode IN ('S', 'H')), -- S = Debit (Soll), H = Credit (Haben)
    
    -- Amounts (in Company Code Currency)
    AmountInCompanyCodeCurrency REAL,
    
    -- Currency
    TransactionCurrency TEXT,
    ExchangeRate REAL DEFAULT 1.0,
    
    -- Cost Assignment
    CostCenter TEXT,
    ProfitCenter TEXT,
    
    -- Partner Information
    Supplier TEXT,
    Customer TEXT,
    
    -- Reference
    AssignmentReference TEXT, -- Link to source item (Invoice Item, Payment, etc.)
    DocumentItemText TEXT,
    
    -- Clearing
    ClearingDate TEXT,
    ClearingAccountingDocument TEXT,
    
    -- Tax
    TaxCode TEXT,
    TaxAmount REAL,
    
    -- Additional Assignment
    PurchaseOrder TEXT,
    PurchaseOrderItem INTEGER,
    MaterialID TEXT,
    PlantID TEXT,
    
    PRIMARY KEY (CompanyCode, FiscalYear, AccountingDocument, AccountingDocumentItem),
    FOREIGN KEY (CompanyCode, FiscalYear, AccountingDocument) REFERENCES JournalEntries(CompanyCode, FiscalYear, AccountingDocument),
    FOREIGN KEY (Supplier) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (CostCenter) REFERENCES CostCenters(CostCenter),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID)
);

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Company Codes
INSERT INTO CompanyCodes VALUES
('1000', 'ACME Corporation USA', 'US', 'USD', 'US-CA', '100 Market Street', 'San Francisco'),
('2000', 'ACME Europe GmbH', 'DE', 'EUR', 'DE', 'Hauptstraße 50', 'Berlin'),
('3000', 'ACME Asia Pacific', 'SG', 'SGD', 'SG', '88 Marina Bay', 'Singapore');

-- Plants
INSERT INTO Plants VALUES
('1001', 'San Francisco Manufacturing', '1000', '123 Factory Road', 'San Francisco', '94102', 'US', 'CA'),
('1002', 'New York Distribution Center', '1000', '456 Warehouse Blvd', 'New York', '10001', 'US', 'NY'),
('2001', 'Berlin Production Facility', '2000', 'Industriestraße 10', 'Berlin', '10115', 'DE', 'BE'),
('3001', 'Singapore Logistics Hub', '3000', '88 Cargo Way', 'Singapore', '018956', 'SG', 'SG');

-- Cost Centers
INSERT INTO CostCenters VALUES
('CC-1001', 'Production - SF', '1000', 'CTRL-1000', 'John Doe', 1),
('CC-1002', 'Maintenance - SF', '1000', 'CTRL-1000', 'Jane Smith', 1),
('CC-2001', 'Production - Berlin', '2000', 'CTRL-2000', 'Hans Mueller', 1),
('CC-3001', 'Logistics - SG', '3000', 'CTRL-3000', 'Li Wei', 1);

-- Payment Terms
INSERT INTO PaymentTerms VALUES
('NET30', 'Net 30 Days', 'Payment due within 30 days', NULL, NULL, NULL, NULL, 30, 0, 1),
('NET60', 'Net 60 Days', 'Payment due within 60 days', NULL, NULL, NULL, NULL, 60, 0, 1),
('2/10NET30', '2% 10 Days Net 30', '2% discount if paid within 10 days, net 30 days', 10, 2.0, NULL, NULL, 30, 0, 1),
('3/15NET45', '3% 15 Days Net 45', '3% discount if paid within 15 days, net 45 days', 15, 3.0, NULL, NULL, 45, 0, 1);

-- Suppliers
INSERT INTO Suppliers VALUES
('SUP-001', 'Global Steel Supply Inc', 'Material', '100 Industry Ave', 'Pittsburgh', '15222', 'US', 'PA', '+1-412-555-0100', 'orders@globalsteel.com', 'USD', 'NET30', 'US-123456789', 'US-VAT-123456', 'US', '021000021', '1234567890', 'US12345678901234567890', 'CHASUS33', 1, 0, NULL, 'BUYER-001', '2023-01-15', NULL, NULL),
('SUP-002', 'Premium Electronics GmbH', 'Material', 'Elektronikstraße 25', 'Munich', '80331', 'DE', 'BY', '+49-89-555-0200', 'sales@premiumelec.de', 'EUR', '2/10NET30', 'DE-987654321', 'DE-VAT-987654', 'DE', '70050000', '9876543210', 'DE89370400440532013000', 'COBADEFF', 1, 0, NULL, 'BUYER-002', '2023-02-10', NULL, NULL),
('SUP-003', 'Logistics Services Ltd', 'Service', '500 Transport Way', 'Chicago', '60601', 'US', 'IL', '+1-312-555-0300', 'billing@logservices.com', 'USD', 'NET60', 'US-555666777', 'US-VAT-555666', 'US', '071000013', '5556667777', 'US55566677778899001122', 'BOFAUS3N', 1, 0, NULL, 'BUYER-001', '2023-03-05', NULL, NULL),
('SUP-004', 'Pacific Components Co', 'Material', '12 Industrial Park', 'Singapore', '628763', 'SG', 'SG', '+65-6789-1234', 'orders@pacificcomp.sg', 'SGD', 'NET30', 'SG-201234567M', 'SG-GST-201234567M', 'SG', 'DBSSSGSG', '1234567890', 'SG12345678901234567890', 'DBSSSGSG', 1, 0, NULL, 'BUYER-003', '2023-04-20', NULL, NULL),
('SUP-005', 'Industrial Maintenance Services', 'Service', '789 Service Road', 'San Francisco', '94103', 'US', 'CA', '+1-415-555-0500', 'service@indmaint.com', 'USD', 'NET30', 'US-888999000', 'US-VAT-888999', 'US', '121000248', '8889990000', 'US88899900001111223344', 'WFBIUS6S', 1, 0, NULL, 'BUYER-001', '2023-05-15', NULL, NULL);

-- Materials
INSERT INTO Materials VALUES
('MAT-1001', 'Steel Plate 10mm Grade A36', 'RAW', 'STEEL', 'KG', 2.50, 1),
('MAT-1002', 'Aluminum Extrusion 50x50mm', 'RAW', 'METAL', 'M', 8.75, 1),
('MAT-1003', 'Electronic Control Unit ECU-2000', 'SEMI', 'ELEC', 'EA', 450.00, 1),
('MAT-1004', 'Hydraulic Pump HP-500', 'SEMI', 'HYDR', 'EA', 1250.00, 1),
('MAT-1005', 'Industrial Bearing 6205-2RS', 'RAW', 'MECH', 'EA', 12.50, 1),
('MAT-1006', 'Power Supply Unit 24V 10A', 'SEMI', 'ELEC', 'EA', 85.00, 1),
('MAT-1007', 'Sensor Module SM-300', 'SEMI', 'ELEC', 'EA', 175.00, 1);

-- Services
INSERT INTO Services VALUES
('SRV-2001', 'Equipment Maintenance - Monthly', 'MAINTENANCE', 'HR', 125.00, 1),
('SRV-2002', 'Logistics Transportation - Domestic', 'LOGISTICS', 'KM', 2.50, 1),
('SRV-2003', 'Logistics Transportation - International', 'LOGISTICS', 'SHIPMENT', 850.00, 1),
('SRV-2004', 'Technical Consulting - Engineering', 'CONSULTING', 'HR', 175.00, 1),
('SRV-2005', 'Equipment Installation', 'INSTALLATION', 'EA', 500.00, 1);

-- ============================================================================
-- SAMPLE DATA - Purchase Orders (Materials & Services)
-- ============================================================================

-- PO 1: Material Purchase Order
INSERT INTO PurchaseOrders VALUES
('PO-2024001', '1000', 'SUP-001', '2024-01-10', 'Standard', 'PG-001', 'POrg-1000', 'NET30', 'EXW', 'San Francisco', 'USD', 5000.00, 250.00, 5250.00, 'FULLY_RECEIVED', 'RELEASED', '2024-02-15', NULL, 'BUYER-001', '2024-01-10 09:00:00', NULL, NULL);

INSERT INTO PurchaseOrderItems VALUES
('PO-2024001', 10, 'STANDARD', 'MAT-1001', NULL, 'Steel Plate for Production', '1001', 'SL01', 'K', 'CC-1001', '400000', 2000, 'KG', 0, 0, 2.50, 1, 'S1', 250.00, 5000.00, '2024-02-15', 'OPEN', 0, 10.0, 10.0, 0);

-- PO 2: Service Purchase Order
INSERT INTO PurchaseOrders VALUES
('PO-2024002', '1000', 'SUP-005', '2024-01-15', 'Service', 'PG-001', 'POrg-1000', 'NET30', 'EXW', 'San Francisco', 'USD', 10000.00, 500.00, 10500.00, 'OPEN', 'RELEASED', '2024-02-28', NULL, 'BUYER-001', '2024-01-15 10:30:00', NULL, NULL);

INSERT INTO PurchaseOrderItems VALUES
('PO-2024002', 10, 'SERVICE', NULL, 'SRV-2001', 'Monthly Equipment Maintenance - Q1 2024', '1001', NULL, 'K', 'CC-1002', '420000', 80, 'HR', 0, 0, 125.00, 1, 'S1', 500.00, 10000.00, '2024-02-28', 'OPEN', 0, 0, 0, 0);

-- PO 3: Mixed Material Purchase Order
INSERT INTO PurchaseOrders VALUES
('PO-2024003', '2000', 'SUP-002', '2024-01-20', 'Standard', 'PG-002', 'POrg-2000', '2/10NET30', 'FOB', 'Berlin', 'EUR', 14750.00, 738.00, 15488.00, 'PARTIALLY_RECEIVED', 'RELEASED', '2024-03-01', NULL, 'BUYER-002', '2024-01-20 11:00:00', NULL, NULL);

INSERT INTO PurchaseOrderItems VALUES
('PO-2024003', 10, 'STANDARD', 'MAT-1003', NULL, 'Electronic Control Units', '2001', 'SL01', 'K', 'CC-2001', '410000', 20, 'EA', 0, 0, 450.00, 1, 'S1', 450.00, 9000.00, '2024-03-01', 'OPEN', 0, 5.0, 5.0, 0),
('PO-2024003', 20, 'STANDARD', 'MAT-1006', NULL, 'Power Supply Units', '2001', 'SL01', 'K', 'CC-2001', '410000', 50, 'EA', 0, 0, 85.00, 1, 'S1', 213.00, 4250.00, '2024-03-01', 'OPEN', 0, 10.0, 10.0, 0),
('PO-2024003', 30, 'STANDARD', 'MAT-1007', NULL, 'Sensor Modules', '2001', 'SL01', 'K', 'CC-2001', '410000', 10, 'EA', 0, 0, 175.00, 1, 'S1', 88.00, 1750.00, '2024-03-01', 'OPEN', 0, 10.0, 10.0, 0);

-- PO 4: International Service PO
INSERT INTO PurchaseOrders VALUES
('PO-2024004', '3000', 'SUP-003', '2024-01-25', 'Service', 'PG-003', 'POrg-3000', 'NET60', 'FOB', 'Chicago', 'USD', 2550.00, 128.00, 2678.00, 'OPEN', 'RELEASED', '2024-03-15', NULL, 'BUYER-003', '2024-01-25 14:00:00', NULL, NULL);

INSERT INTO PurchaseOrderItems VALUES
('PO-2024004', 10, 'SERVICE', NULL, 'SRV-2003', 'International Shipment - Container', '3001', NULL, 'K', 'CC-3001', '430000', 3, 'SHIPMENT', 0, 0, 850.00, 1, 'S1', 128.00, 2550.00, '2024-03-15', 'OPEN', 0, 0, 0, 0);

-- ============================================================================
-- SAMPLE DATA - Goods Receipts (for Material POs)
-- ============================================================================

-- GR for PO-2024001
INSERT INTO GoodsReceipts VALUES
('GR-2024001', 'PO-2024001', '2024-02-16', '2024-02-16', '1000', '1001', '101', 'POSTED', 'warehouse.sf', '2024-02-16 14:30:00');

INSERT INTO GoodsReceiptItems VALUES
('GR-2024001', 1, 'PO-2024001', 10, 'MAT-1001', 'Steel Plate 10mm Grade A36', 2000, 'KG', '1001', 'SL01', 5000.00, 0, NULL);

-- Update PO History
INSERT INTO PurchaseOrderHistory (PurchaseOrderID, ItemNumber, TransactionType, ReferenceDocument, ReferenceDocumentItem, Quantity, PostingDate) VALUES
('PO-2024001', 10, 'GR', 'GR-2024001', 1, 2000, '2024-02-16');

-- GR for PO-2024003 (partial)
INSERT INTO GoodsReceipts VALUES
('GR-2024002', 'PO-2024003', '2024-03-02', '2024-03-02', '2000', '2001', '101', 'POSTED', 'warehouse.berlin', '2024-03-02 10:15:00');

INSERT INTO GoodsReceiptItems VALUES
('GR-2024002', 1, 'PO-2024003', 10, 'MAT-1003', 'Electronic Control Unit ECU-2000', 20, 'EA', '2001', 'SL01', 9000.00, 0, NULL),
('GR-2024002', 2, 'PO-2024003', 20, 'MAT-1006', 'Power Supply Unit 24V 10A', 30, 'EA', '2001', 'SL01', 2550.00, 0, NULL);

-- Update PO History
INSERT INTO PurchaseOrderHistory (PurchaseOrderID, ItemNumber, TransactionType, ReferenceDocument, ReferenceDocumentItem, Quantity, PostingDate) VALUES
('PO-2024003', 10, 'GR', 'GR-2024002', 1, 20, '2024-03-02'),
('PO-2024003', 20, 'GR', 'GR-2024002', 2, 30, '2024-03-02');

-- ============================================================================
-- SAMPLE DATA - Service Entry Sheets (for Service POs)
-- ============================================================================

-- SES for PO-2024002 (partial - 40 hours performed out of 80 ordered)
INSERT INTO ServiceEntrySheets VALUES
('SES-2024001', 'PO-2024002', '2024-02-20', '1000', 'TechServ Inc', 'Mike Johnson', 'ACCEPTED', 'MAINT-MGR-001', '2024-02-21', 'POSTED', 'USD', 5000.00, 'TECHNICIAN-001', '2024-02-20 16:00:00', 'MAINT-MGR-001', '2024-02-21 09:00:00');

INSERT INTO ServiceEntrySheetItems VALUES
('SES-2024001', 1, 'PO-2024002', 10, 'SRV-2001', 'Equipment Maintenance - Monthly', 'January 2024 Maintenance', 40, 'HR', '2024-02-20', 125.00, 5000.00, 'CC-1002', '420000', 'ACCEPTED');

-- Update PO History
INSERT INTO PurchaseOrderHistory (PurchaseOrderID, ItemNumber, TransactionType, ReferenceDocument, ReferenceDocumentItem, Quantity, PostingDate) VALUES
('PO-2024002', 10, 'SES', 'SES-2024001', 1, 40, '2024-02-20');

-- SES for PO-2024004 (full shipment completed)
INSERT INTO ServiceEntrySheets VALUES
('SES-2024002', 'PO-2024004', '2024-03-18', '3000', 'Logistics Services Ltd', 'Sarah Chen', 'ACCEPTED', 'LOG-MGR-001', '2024-03-19', 'POSTED', 'USD', 2550.00, 'LOG-COORD-001', '2024-03-18 11:30:00', 'LOG-MGR-001', '2024-03-19 08:00:00');

INSERT INTO ServiceEntrySheetItems VALUES
('SES-2024002', 1, 'PO-2024004', 10, 'SRV-2003', 'Logistics Transportation - International', '3 Container Shipment to Singapore', 3, 'SHIPMENT', '2024-03-18', 850.00, 2550.00, 'CC-3001', '430000', 'ACCEPTED');

-- Update PO History
INSERT INTO PurchaseOrderHistory (PurchaseOrderID, ItemNumber, TransactionType, ReferenceDocument, ReferenceDocumentItem, Quantity, PostingDate) VALUES
('PO-2024004', 10, 'SES', 'SES-2024002', 1, 3, '2024-03-18');

-- ============================================================================
-- SAMPLE DATA - Supplier Invoices (with complete references)
-- ============================================================================

-- Invoice 1: Material Invoice matching PO and GR (POSTED and PAID)
INSERT INTO SupplierInvoices VALUES (
    'INV-2024001', '2024', '1000', 'SUP-001',
    '2024-02-18', '2024-02-20', '2024-02-18',
    'GSS-2024-0156', 'PO-2024001',
    'INVOICE', 1, 'EDI',
    'NET30', 'ACH', '2024-03-22', NULL, NULL, NULL, NULL,
    'USD', 5250.00, 5000.00, 250.00, 0.00, 0.00,
    'PAID', 'FULLY_PAID',
    0, NULL,
    'ACH-2024-03-20-001', '2024-03-20',
    'ap.clerk', '2024-02-20 10:30:00', 'ap.manager', '2024-02-20 14:15:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-2024001', 1, 'PO-2024001', 10, 'GR-2024001', 1, NULL, NULL, 'MAT-1001', NULL, 'Steel Plate 10mm Grade A36', '1001', 'CC-1001', '400000', 2000, 'KG', 2.50, 5000.00, 'S1', 250.00, 5250.00, 0, 0, 0, 0, 0.00, 0.00, NULL);

-- Update PO History
INSERT INTO PurchaseOrderHistory (PurchaseOrderID, ItemNumber, TransactionType, ReferenceDocument, ReferenceDocumentItem, Quantity, PostingDate) VALUES
('PO-2024001', 10, 'IR', 'INV-2024001', 1, 2000, '2024-02-20');

-- Invoice 2: Service Invoice matching PO and SES (POSTED, awaiting payment)
INSERT INTO SupplierInvoices VALUES (
    'INV-2024002', '2024', '1000', 'SUP-005',
    '2024-02-22', '2024-02-25', '2024-02-22',
    'IMS-2024-089', 'PO-2024002',
    'INVOICE', 1, 'MANUAL',
    'NET30', 'CHECK', '2024-03-27', 100.00, '2024-03-05', NULL, NULL,
    'USD', 5250.00, 5000.00, 250.00, 0.00, 0.00,
    'POSTED', 'UNPAID',
    0, NULL,
    NULL, NULL,
    'ap.clerk', '2024-02-25 13:20:00', 'ap.manager', '2024-02-25 15:00:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-2024002', 1, 'PO-2024002', 10, NULL, NULL, 'SES-2024001', 1, NULL, 'SRV-2001', 'Equipment Maintenance - Monthly', '1001', 'CC-1002', '420000', 40, 'HR', 125.00, 5000.00, 'S1', 250.00, 5250.00, 0, 0, 0, 0, 0.00, 0.00, 'January 2024 maintenance services completed');

-- Update PO History
INSERT INTO PurchaseOrderHistory (PurchaseOrderID, ItemNumber, TransactionType, ReferenceDocument, ReferenceDocumentItem, Quantity, PostingDate) VALUES
('PO-2024002', 10, 'IR', 'INV-2024002', 1, 40, '2024-02-25');

-- Invoice 3: Material Invoice with Price Variance (HELD)
INSERT INTO SupplierInvoices VALUES (
    'INV-2024003', '2024', '2000', 'SUP-002',
    '2024-03-05', '2024-03-08', '2024-03-05',
    'PE-2024-445', 'PO-2024003',
    'INVOICE', 1, 'EDI',
    '2/10NET30', 'WIRE', '2024-04-07', 294.00, '2024-03-18', NULL, NULL,
    'EUR', 15488.00, 14750.00, 738.00, 0.00, 0.00,
    'HELD', 'UNPAID',
    1, 'PRICE_VARIANCE',
    NULL, NULL,
    'ap.berlin', '2024-03-08 09:15:00', NULL, NULL, NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-2024003', 1, 'PO-2024003', 10, 'GR-2024002', 1, NULL, NULL, 'MAT-1003', NULL, 'Electronic Control Unit ECU-2000', '2001', 'CC-2001', '410000', 20, 'EA', 460.00, 9200.00, 'S1', 460.00, 9660.00, 1, 0, 0, 0, 200.00, 0.00, 'Price increase from 450 to 460 EUR'),
('INV-2024003', 2, 'PO-2024003', 20, 'GR-2024002', 2, NULL, NULL, 'MAT-1006', NULL, 'Power Supply Unit 24V 10A', '2001', 'CC-2001', '410000', 30, 'EA', 85.00, 2550.00, 'S1', 128.00, 2678.00, 0, 0, 0, 0, 0.00, 0.00, NULL);

-- Update PO History
INSERT INTO PurchaseOrderHistory (PurchaseOrderID, ItemNumber, TransactionType, ReferenceDocument, ReferenceDocumentItem, Quantity, PostingDate) VALUES
('PO-2024003', 10, 'IR', 'INV-2024003', 1, 20, '2024-03-08'),
('PO-2024003', 20, 'IR', 'INV-2024003', 2, 30, '2024-03-08');

-- Invoice 4: Service Invoice matching PO and SES (POSTED, awaiting payment)
INSERT INTO SupplierInvoices VALUES (
    'INV-2024004', '2024', '3000', 'SUP-003',
    '2024-03-20', '2024-03-22', '2024-03-20',
    'LOG-2024-778', 'PO-2024004',
    'INVOICE', 1, 'EDI',
    'NET60', 'WIRE', '2024-05-21', NULL, NULL, NULL, NULL,
    'USD', 2678.00, 2550.00, 128.00, 0.00, 0.00,
    'POSTED', 'UNPAID',
    0, NULL,
    NULL, NULL,
    'ap.singapore', '2024-03-22 11:00:00', 'ap.singapore.mgr', '2024-03-22 13:30:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-2024004', 1, 'PO-2024004', 10, NULL, NULL, 'SES-2024002', 1, NULL, 'SRV-2003', 'Logistics Transportation - International', '3001', 'CC-3001', '430000', 3, 'SHIPMENT', 850.00, 2550.00, 'S1', 128.00, 2678.00, 0, 0, 0, 0, 0.00, 0.00, 'Container shipment completed');

-- Update PO History
INSERT INTO PurchaseOrderHistory (PurchaseOrderID, ItemNumber, TransactionType, ReferenceDocument, ReferenceDocumentItem, Quantity, PostingDate) VALUES
('PO-2024004', 10, 'IR', 'INV-2024004', 1, 3, '2024-03-22');

-- Invoice 5: Non-PO Invoice (PARKED, awaiting approval)
INSERT INTO SupplierInvoices VALUES (
    'INV-2024005', '2024', '1000', 'SUP-003',
    '2024-03-25', '2024-03-27', '2024-03-25',
    'LOG-2024-890', NULL,
    'INVOICE', 1, 'MANUAL',
    'NET60', 'CHECK', '2024-05-26', NULL, NULL, NULL, NULL,
    'USD', 1575.00, 1500.00, 75.00, 0.00, 0.00,
    'PARKED', 'UNPAID',
    0, NULL,
    NULL, NULL,
    'ap.clerk', '2024-03-27 14:00:00', NULL, NULL, NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-2024005', 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'SRV-2002', 'Emergency logistics service - unplanned', '1001', 'CC-1001', '400000', 600, 'KM', 2.50, 1500.00, 'S1', 75.00, 1575.00, 0, 0, 0, 0, 0.00, 0.00, 'Unplanned emergency delivery service');

-- ============================================================================
-- SAMPLE DATA - Payments
-- ============================================================================

-- Payment Run 1
INSERT INTO PaymentRuns VALUES
('PAYRUN-2024001', '1000', '2024-03-20', 'ACH', 'EXECUTED', 5250.00, 'USD', 'payment.system', '2024-03-20 02:00:00');

-- Payment for INV-2024001
INSERT INTO InvoicePayments VALUES
('PAY-2024001', 'INV-2024001', 'PAYRUN-2024001', '2024-03-20', 5250.00, 'ACH', 'ACH-2024-03-20-001', 'USD', 1.0, 'BANK-ACC-1000', 'BANK-ACC-SUP001', 'CLEARED', 'payment.system', '2024-03-20 02:00:00');

-- ============================================================================
-- SAMPLE DATA - Journal Entries (Financial Accounting Postings)
-- ============================================================================

-- Journal Entry 1: Invoice Posting for INV-2024001 (Material Purchase)
-- Dr. Materials/Inventory 5000 | Dr. Tax Input 250 | Cr. Accounts Payable 5250
INSERT INTO JournalEntries VALUES
('1000', '2024', '5000000001', 'KR', '2024-02-20', '2024-02-20', '02', 'INV-2024001', 'INVOICE', 'Vendor Invoice Posting - INV-2024001', 'USD', 'USD', 1.0, 'NORMAL', 0, NULL, NULL, 'AP-SYSTEM', '2024-02-20', '14:15:00', NULL);

INSERT INTO JournalEntryItems VALUES
('1000', '2024', '5000000001', 1, '400000', 'GR/IR Clearing Account', 5000.00, 'S', 5000.00, 'USD', 1.0, 'CC-1001', NULL, 'SUP-001', NULL, 'INV-2024001-1', 'Steel Plate purchase', NULL, NULL, NULL, NULL, 'PO-2024001', 10, 'MAT-1001', '1001'),
('1000', '2024', '5000000001', 2, '154000', 'Tax Input - Sales Tax', 250.00, 'S', 250.00, 'USD', 1.0, NULL, NULL, NULL, NULL, 'INV-2024001-TAX', 'Input tax', NULL, NULL, 'S1', 250.00, NULL, NULL, NULL, NULL),
('1000', '2024', '5000000001', 3, '210000', 'Accounts Payable - Trade', 5250.00, 'H', 5250.00, 'USD', 1.0, NULL, NULL, 'SUP-001', NULL, 'INV-2024001', 'Vendor payable', NULL, NULL, NULL, NULL, 'PO-2024001', NULL, NULL, NULL);

-- Journal Entry 2: Payment Clearing for INV-2024001
-- Dr. Accounts Payable 5250 | Cr. Bank/Cash 5250
INSERT INTO JournalEntries VALUES
('1000', '2024', '5000000002', 'KZ', '2024-03-20', '2024-03-20', '03', 'PAY-2024001', 'PAYMENT', 'Vendor Payment - PAY-2024001', 'USD', 'USD', 1.0, 'NORMAL', 0, NULL, NULL, 'PAYMENT-SYSTEM', '2024-03-20', '02:00:00', NULL);

INSERT INTO JournalEntryItems VALUES
('1000', '2024', '5000000002', 1, '210000', 'Accounts Payable - Trade', 5250.00, 'S', 5250.00, 'USD', 1.0, NULL, NULL, 'SUP-001', NULL, 'PAY-2024001', 'Payment clearing', '2024-03-20', '5000000001', NULL, NULL, NULL, NULL, NULL, NULL),
('1000', '2024', '5000000002', 2, '110000', 'Bank - Main Operating Account', 5250.00, 'H', 5250.00, 'USD', 1.0, NULL, NULL, NULL, NULL, 'ACH-2024-03-20-001', 'ACH payment', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- Journal Entry 3: Invoice Posting for INV-2024002 (Service Purchase)
-- Dr. Services Expense 5000 | Dr. Tax Input 250 | Cr. Accounts Payable 5250
INSERT INTO JournalEntries VALUES
('1000', '2024', '5000000003', 'KR', '2024-02-25', '2024-02-25', '02', 'INV-2024002', 'INVOICE', 'Vendor Invoice Posting - INV-2024002', 'USD', 'USD', 1.0, 'NORMAL', 0, NULL, NULL, 'AP-SYSTEM', '2024-02-25', '15:00:00', NULL);

INSERT INTO JournalEntryItems VALUES
('1000', '2024', '5000000003', 1, '420000', 'Maintenance Services Expense', 5000.00, 'S', 5000.00, 'USD', 1.0, 'CC-1002', NULL, 'SUP-005', NULL, 'INV-2024002-1', 'Equipment maintenance', NULL, NULL, NULL, NULL, 'PO-2024002', 10, NULL, '1001'),
('1000', '2024', '5000000003', 2, '154000', 'Tax Input - Sales Tax', 250.00, 'S', 250.00, 'USD', 1.0, NULL, NULL, NULL, NULL, 'INV-2024002-TAX', 'Input tax', NULL, NULL, 'S1', 250.00, NULL, NULL, NULL, NULL),
('1000', '2024', '5000000003', 3, '210000', 'Accounts Payable - Trade', 5250.00, 'H', 5250.00, 'USD', 1.0, NULL, NULL, 'SUP-005', NULL, 'INV-2024002', 'Vendor payable', NULL, NULL, NULL, NULL, 'PO-2024002', NULL, NULL, NULL);

-- Journal Entry 4: Invoice Posting for INV-2024003 (Material Purchase with Variance - HELD)
-- Dr. Materials/Inventory 14750 | Dr. Tax Input 738 | Cr. Accounts Payable 15488
-- Note: Blocked for price variance, posted but payment held
INSERT INTO JournalEntries VALUES
('2000', '2024', '5000000004', 'KR', '2024-03-08', '2024-03-08', '03', 'INV-2024003', 'INVOICE', 'Vendor Invoice Posting - INV-2024003 (Price Variance)', 'EUR', 'EUR', 1.0, 'NORMAL', 0, NULL, NULL, 'AP-BERLIN', '2024-03-08', '09:15:00', NULL);

INSERT INTO JournalEntryItems VALUES
('2000', '2024', '5000000004', 1, '410000', 'Raw Materials Inventory', 11750.00, 'S', 11750.00, 'EUR', 1.0, 'CC-2001', NULL, 'SUP-002', NULL, 'INV-2024003-1-2', 'Electronic components', NULL, NULL, NULL, NULL, 'PO-2024003', NULL, NULL, '2001'),
('2000', '2024', '5000000004', 2, '154000', 'Tax Input - VAT', 588.00, 'S', 588.00, 'EUR', 1.0, NULL, NULL, NULL, NULL, 'INV-2024003-TAX-1', 'Input VAT item 1-2', NULL, NULL, 'S1', 588.00, NULL, NULL, NULL, NULL),
('2000', '2024', '5000000004', 3, '410000', 'Raw Materials Inventory', 1750.00, 'S', 1750.00, 'EUR', 1.0, 'CC-2001', NULL, 'SUP-002', NULL, 'INV-2024003-3', 'Sensor modules', NULL, NULL, NULL, NULL, 'PO-2024003', 30, 'MAT-1007', '2001'),
('2000', '2024', '5000000004', 4, '154000', 'Tax Input - VAT', 88.00, 'S', 88.00, 'EUR', 1.0, NULL, NULL, NULL, NULL, 'INV-2024003-TAX-3', 'Input VAT item 3', NULL, NULL, 'S1', 88.00, NULL, NULL, NULL, NULL),
('2000', '2024', '5000000004', 5, '548000', 'Price Variance Account', 200.00, 'S', 200.00, 'EUR', 1.0, 'CC-2001', NULL, NULL, NULL, 'VARIANCE-INV-2024003', 'Price variance ECU', NULL, NULL, NULL, NULL, 'PO-2024003', 10, 'MAT-1003', '2001'),
('2000', '2024', '5000000004', 6, '210000', 'Accounts Payable - Trade', 15488.00, 'H', 15488.00, 'EUR', 1.0, NULL, NULL, 'SUP-002', NULL, 'INV-2024003', 'Vendor payable (HELD)', NULL, NULL, NULL, NULL, 'PO-2024003', NULL, NULL, NULL);

-- Journal Entry 5: Invoice Posting for INV-2024004 (International Service)
-- Dr. Services Expense 2550 | Dr. Tax Input 128 | Cr. Accounts Payable 2678
INSERT INTO JournalEntries VALUES
('3000', '2024', '5000000005', 'KR', '2024-03-22', '2024-03-22', '03', 'INV-2024004', 'INVOICE', 'Vendor Invoice Posting - INV-2024004', 'USD', 'SGD', 1.35, 'NORMAL', 0, NULL, NULL, 'AP-SINGAPORE', '2024-03-22', '13:30:00', NULL);

INSERT INTO JournalEntryItems VALUES
('3000', '2024', '5000000005', 1, '430000', 'Logistics Services Expense', 2550.00, 'S', 3442.50, 'USD', 1.35, 'CC-3001', NULL, 'SUP-003', NULL, 'INV-2024004-1', 'International shipping', NULL, NULL, NULL, NULL, 'PO-2024004', 10, NULL, '3001'),
('3000', '2024', '5000000005', 2, '154000', 'Tax Input - GST', 128.00, 'S', 172.80, 'USD', 1.35, NULL, NULL, NULL, NULL, 'INV-2024004-TAX', 'Input GST', NULL, NULL, 'S1', 128.00, NULL, NULL, NULL, NULL),
('3000', '2024', '5000000005', 3, '210000', 'Accounts Payable - Trade', 2678.00, 'H', 3615.30, 'USD', 1.35, NULL, NULL, 'SUP-003', NULL, 'INV-2024004', 'Vendor payable', NULL, NULL, NULL, NULL, 'PO-2024004', NULL, NULL, NULL);

-- ============================================================================
-- VIEWS FOR P2P WORKFLOW TRACKING
-- ============================================================================

-- Complete P2P Tracking View
CREATE VIEW vw_CompleteP2PTracking AS
SELECT 
    po.PurchaseOrderID,
    po.DocumentDate AS PODate,
    po.SupplierID,
    s.SupplierName,
    po.PurchaseOrderType,
    poi.ItemNumber AS POItem,
    
    -- Material or Service
    COALESCE(m.MaterialDescription, srv.ServiceDescription) AS ItemDescription,
    poi.OrderQuantity,
    poi.UnitOfMeasure,
    
    -- Goods Receipt Info
    gr.GoodsReceiptID,
    gr.PostingDate AS GRDate,
    gri.QuantityReceived,
    
    -- Service Entry Sheet Info
    ses.ServiceEntrySheetID,
    ses.DocumentDate AS SESDate,
    sesi.Quantity AS SESQuantity,
    ses.AcceptanceStatus AS SESAcceptance,
    
    -- Invoice Info
    si.InvoiceID,
    si.InvoiceDate,
    si.SupplierInvoiceNumber,
    sii.Quantity AS InvoiceQuantity,
    sii.NetAmount AS InvoiceAmount,
    si.InvoiceStatus,
    si.PaymentStatus,
    si.IsBlocked,
    si.BlockingReason,
    
    -- Payment Info
    ip.PaymentID,
    ip.PaymentDate,
    ip.PaymentAmount
    
FROM PurchaseOrders po
JOIN Suppliers s ON po.SupplierID = s.SupplierID
JOIN PurchaseOrderItems poi ON po.PurchaseOrderID = poi.PurchaseOrderID
LEFT JOIN Materials m ON poi.MaterialID = m.MaterialID
LEFT JOIN Services srv ON poi.ServiceID = srv.ServiceID
LEFT JOIN GoodsReceiptItems gri ON poi.PurchaseOrderID = gri.PurchaseOrderID AND poi.ItemNumber = gri.POItemNumber
LEFT JOIN GoodsReceipts gr ON gri.GoodsReceiptID = gr.GoodsReceiptID
LEFT JOIN ServiceEntrySheetItems sesi ON poi.PurchaseOrderID = sesi.PurchaseOrderID AND poi.ItemNumber = sesi.POItemNumber
LEFT JOIN ServiceEntrySheets ses ON sesi.ServiceEntrySheetID = ses.ServiceEntrySheetID
LEFT JOIN SupplierInvoiceItems sii ON poi.PurchaseOrderID = sii.PurchaseOrderID AND poi.ItemNumber = sii.POItemNumber
LEFT JOIN SupplierInvoices si ON sii.InvoiceID = si.InvoiceID
LEFT JOIN InvoicePayments ip ON si.InvoiceID = ip.InvoiceID
ORDER BY po.DocumentDate DESC, poi.ItemNumber;

-- Outstanding Invoices View
CREATE VIEW vw_OutstandingInvoices AS
SELECT 
    si.InvoiceID,
    si.SupplierInvoiceNumber,
    s.SupplierName,
    si.InvoiceDate,
    si.PostingDate,
    si.PaymentDueDate,
    si.GrossAmount,
    si.Currency,
    si.InvoiceStatus,
    si.PaymentStatus,
    si.IsBlocked,
    si.BlockingReason,
    pt.PaymentTermsName,
    CAST(julianday('now') - julianday(si.PaymentDueDate) AS INTEGER) AS DaysOverdue
FROM SupplierInvoices si
JOIN Suppliers s ON si.SupplierID = s.SupplierID
LEFT JOIN PaymentTerms pt ON si.PaymentTermsCode = pt.PaymentTermsCode
WHERE si.PaymentStatus != 'FULLY_PAID'
    AND si.InvoiceStatus NOT IN ('CANCELLED');

-- Invoice Variances View
CREATE VIEW vw_InvoiceVariances AS
SELECT 
    si.InvoiceID,
    si.SupplierInvoiceNumber,
    s.SupplierName,
    si.InvoiceDate,
    si.GrossAmount,
    si.Currency,
    si.BlockingReason,
    sii.ItemNumber,
    sii.MaterialDescription,
    sii.HasPriceVariance,
    sii.HasQuantityVariance,
    sii.PriceVarianceAmount,
    sii.QuantityVarianceAmount
FROM SupplierInvoices si
JOIN Suppliers s ON si.SupplierID = s.SupplierID
JOIN SupplierInvoiceItems sii ON si.InvoiceID = sii.InvoiceID
WHERE si.IsBlocked = 1
    OR sii.HasPriceVariance = 1
    OR sii.HasQuantityVariance = 1;

-- Supplier Performance View
CREATE VIEW vw_SupplierPerformance AS
SELECT 
    s.SupplierID,
    s.SupplierName,
    s.SupplierType,
    COUNT(DISTINCT si.InvoiceID) AS TotalInvoices,
    SUM(CASE WHEN si.IsBlocked = 1 THEN 1 ELSE 0 END) AS BlockedInvoices,
    ROUND(SUM(si.GrossAmount), 2) AS TotalInvoiceAmount,
    si.Currency,
    ROUND(AVG(julianday(si.PostingDate) - julianday(si.InvoiceDate)), 1) AS AvgProcessingDays,
    SUM(CASE WHEN si.PaymentStatus = 'FULLY_PAID' THEN 1 ELSE 0 END) AS PaidInvoices,
    SUM(CASE WHEN si.PaymentStatus = 'UNPAID' THEN 1 ELSE 0 END) AS UnpaidInvoices
FROM Suppliers s
LEFT JOIN SupplierInvoices si ON s.SupplierID = si.SupplierID
WHERE si.InvoiceStatus != 'CANCELLED' OR si.InvoiceStatus IS NULL
GROUP BY s.SupplierID, s.SupplierName, s.SupplierType, si.Currency;

-- Service Entry Sheet Status View
CREATE VIEW vw_ServiceEntrySheetStatus AS
SELECT 
    ses.ServiceEntrySheetID,
    ses.PurchaseOrderID,
    po.SupplierID,
    s.SupplierName,
    ses.DocumentDate,
    ses.AcceptanceStatus,
    ses.DocumentStatus,
    sesi.ServiceDescription,
    sesi.Quantity,
    sesi.UnitOfMeasure,
    sesi.NetAmount,
    ses.Currency
FROM ServiceEntrySheets ses
JOIN PurchaseOrders po ON ses.PurchaseOrderID = po.PurchaseOrderID
JOIN Suppliers s ON po.SupplierID = s.SupplierID
JOIN ServiceEntrySheetItems sesi ON ses.ServiceEntrySheetID = sesi.ServiceEntrySheetID
ORDER BY ses.DocumentDate DESC;

-- Purchase Order Status View
CREATE VIEW vw_PurchaseOrderStatus AS
SELECT 
    po.PurchaseOrderID,
    po.DocumentDate,
    po.SupplierID,
    s.SupplierName,
    po.PurchaseOrderType,
    po.Currency,
    po.TotalGrossAmount,
    po.POStatus,
    po.ReleaseStatus,
    COUNT(DISTINCT poi.ItemNumber) AS TotalItems,
    SUM(CASE WHEN poi.ItemStatus = 'FULLY_RECEIVED' THEN 1 ELSE 0 END) AS ReceivedItems,
    SUM(poi.OrderQuantity) AS TotalOrderedQty,
    SUM(poi.QuantityReceived) AS TotalReceivedQty,
    SUM(poi.QuantityInvoiced) AS TotalInvoicedQty
FROM PurchaseOrders po
JOIN Suppliers s ON po.SupplierID = s.SupplierID
LEFT JOIN PurchaseOrderItems poi ON po.PurchaseOrderID = poi.PurchaseOrderID
GROUP BY po.PurchaseOrderID, po.DocumentDate, po.SupplierID, s.SupplierName, 
         po.PurchaseOrderType, po.Currency, po.TotalGrossAmount, po.POStatus, po.ReleaseStatus
ORDER BY po.DocumentDate DESC;

-- Payment Terms Utilization View
CREATE VIEW vw_PaymentTermsUsage AS
SELECT 
    pt.PaymentTermsCode,
    pt.PaymentTermsName,
    pt.NetPaymentDays,
    pt.CashDiscount1Percent,
    COUNT(DISTINCT si.InvoiceID) AS TimesUsed,
    ROUND(SUM(si.GrossAmount), 2) AS TotalInvoiceAmount,
    si.Currency,
    SUM(CASE WHEN si.CashDiscount1Amount IS NOT NULL AND si.CashDiscount1Amount > 0 THEN 1 ELSE 0 END) AS DiscountsTaken,
    ROUND(SUM(COALESCE(si.CashDiscount1Amount, 0)), 2) AS TotalDiscountAmount
FROM PaymentTerms pt
LEFT JOIN SupplierInvoices si ON pt.PaymentTermsCode = si.PaymentTermsCode
WHERE si.InvoiceStatus != 'CANCELLED' OR si.InvoiceStatus IS NULL
GROUP BY pt.PaymentTermsCode, pt.PaymentTermsName, pt.NetPaymentDays, pt.CashDiscount1Percent, si.Currency
ORDER BY TimesUsed DESC;

-- Financial Postings View (Journal Entries with Source Documents)
CREATE VIEW vw_FinancialPostings AS
SELECT 
    je.CompanyCode,
    je.FiscalYear,
    je.AccountingDocument,
    je.AccountingDocumentType,
    CASE je.AccountingDocumentType
        WHEN 'KR' THEN 'Vendor Invoice'
        WHEN 'KZ' THEN 'Vendor Payment'
        WHEN 'SA' THEN 'GL Posting'
        ELSE je.AccountingDocumentType
    END AS DocumentTypeDescription,
    je.PostingDate,
    je.DocumentDate,
    je.AccountingDocumentHeaderText,
    
    -- Source Document Reference
    je.DocumentReferenceID,
    je.ReferenceDocumentType,
    
    -- Invoice Information (if applicable)
    si.SupplierInvoiceNumber,
    si.InvoiceDate,
    si.GrossAmount AS InvoiceAmount,
    
    -- Payment Information (if applicable)
    ip.PaymentReference,
    ip.PaymentAmount,
    
    -- Supplier Information
    s.SupplierName,
    
    -- Currency
    je.TransactionCurrency,
    je.ExchangeRate,
    
    -- Line Item Summary
    COUNT(jei.AccountingDocumentItem) AS NumberOfLineItems,
    ROUND(SUM(CASE WHEN jei.DebitCreditCode = 'S' THEN jei.AmountInTransactionCurrency ELSE 0 END), 2) AS TotalDebitAmount,
    ROUND(SUM(CASE WHEN jei.DebitCreditCode = 'H' THEN jei.AmountInTransactionCurrency ELSE 0 END), 2) AS TotalCreditAmount,
    
    -- Audit
    je.AccountingDocCreatedByUser,
    je.AccountingDocumentCreationDate,
    je.CreationTime
    
FROM JournalEntries je
LEFT JOIN JournalEntryItems jei ON je.CompanyCode = jei.CompanyCode 
    AND je.FiscalYear = jei.FiscalYear 
    AND je.AccountingDocument = jei.AccountingDocument
LEFT JOIN SupplierInvoices si ON je.DocumentReferenceID = si.InvoiceID 
    AND je.ReferenceDocumentType = 'INVOICE'
LEFT JOIN InvoicePayments ip ON je.DocumentReferenceID = ip.PaymentID 
    AND je.ReferenceDocumentType = 'PAYMENT'
LEFT JOIN Suppliers s ON si.SupplierID = s.SupplierID 
    OR jei.Supplier = s.SupplierID

GROUP BY 
    je.CompanyCode, je.FiscalYear, je.AccountingDocument, je.AccountingDocumentType,
    je.PostingDate, je.DocumentDate, je.AccountingDocumentHeaderText,
    je.DocumentReferenceID, je.ReferenceDocumentType,
    si.SupplierInvoiceNumber, si.InvoiceDate, si.GrossAmount,
    ip.PaymentReference, ip.PaymentAmount, s.SupplierName,
    je.TransactionCurrency, je.ExchangeRate,
    je.AccountingDocCreatedByUser, je.AccountingDocumentCreationDate, je.CreationTime

ORDER BY je.PostingDate DESC, je.AccountingDocument;
