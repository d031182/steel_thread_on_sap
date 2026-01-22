-- ============================================================================
-- Procure-to-Pay (P2P) Supplier Invoice Database - SQLite Version
-- ============================================================================
-- This database supports the P2P workflow:
-- 1. Purchase Requisition → 2. Purchase Order → 3. Goods Receipt → 
-- 4. Supplier Invoice → 5. Payment
-- ============================================================================

-- SQLite specific settings
PRAGMA foreign_keys = ON;

-- ============================================================================
-- CORE MASTER DATA TABLES
-- ============================================================================

-- Suppliers (Vendors)
CREATE TABLE Suppliers (
    SupplierID TEXT PRIMARY KEY,
    SupplierName TEXT NOT NULL,
    SupplierType TEXT CHECK(SupplierType IN ('Material', 'Service', 'Both')),
    TaxID TEXT,
    PaymentTerms TEXT,
    Currency TEXT DEFAULT 'USD',
    ContactEmail TEXT,
    ContactPhone TEXT,
    IsActive INTEGER DEFAULT 1,
    CreatedDate TEXT DEFAULT (date('now'))
);

-- Company Codes (Legal Entities)
CREATE TABLE CompanyCodes (
    CompanyCode TEXT PRIMARY KEY,
    CompanyName TEXT NOT NULL,
    Country TEXT,
    Currency TEXT,
    TaxJurisdiction TEXT
);

-- Plants (Physical Locations)
CREATE TABLE Plants (
    PlantID TEXT PRIMARY KEY,
    PlantName TEXT NOT NULL,
    CompanyCode TEXT,
    Address TEXT,
    City TEXT,
    Country TEXT,
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Materials
CREATE TABLE Materials (
    MaterialID TEXT PRIMARY KEY,
    MaterialDescription TEXT NOT NULL,
    MaterialType TEXT,
    BaseUnitOfMeasure TEXT,
    MaterialGroup TEXT,
    StandardPrice REAL
);

-- ============================================================================
-- PROCUREMENT PROCESS TABLES
-- ============================================================================

-- Purchase Orders
CREATE TABLE PurchaseOrders (
    PurchaseOrderID TEXT PRIMARY KEY,
    SupplierID TEXT NOT NULL,
    CompanyCode TEXT NOT NULL,
    OrderDate TEXT NOT NULL,
    DeliveryDate TEXT,
    TotalAmount REAL,
    Currency TEXT DEFAULT 'USD',
    POStatus TEXT CHECK(POStatus IN ('OPEN', 'PARTIALLY_RECEIVED', 'FULLY_RECEIVED', 'CLOSED')),
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Purchase Order Items
CREATE TABLE PurchaseOrderItems (
    PurchaseOrderID TEXT,
    ItemNumber INTEGER,
    MaterialID TEXT,
    PlantID TEXT,
    Quantity REAL NOT NULL,
    UnitOfMeasure TEXT,
    UnitPrice REAL NOT NULL,
    TotalPrice REAL,
    DeliveryDate TEXT,
    ItemStatus TEXT,
    PRIMARY KEY (PurchaseOrderID, ItemNumber),
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID)
);

-- Goods Receipts (Material Documents)
CREATE TABLE GoodsReceipts (
    GoodsReceiptID TEXT PRIMARY KEY,
    PurchaseOrderID TEXT NOT NULL,
    ReceiptDate TEXT NOT NULL,
    PlantID TEXT,
    CompanyCode TEXT,
    DocumentStatus TEXT CHECK(DocumentStatus IN ('POSTED', 'CANCELLED')),
    PostedBy TEXT,
    PostedDate TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Goods Receipt Items
CREATE TABLE GoodsReceiptItems (
    GoodsReceiptID TEXT,
    ItemNumber INTEGER,
    PurchaseOrderID TEXT,
    POItemNumber INTEGER,
    MaterialID TEXT,
    QuantityReceived REAL NOT NULL,
    UnitOfMeasure TEXT,
    PRIMARY KEY (GoodsReceiptID, ItemNumber),
    FOREIGN KEY (GoodsReceiptID) REFERENCES GoodsReceipts(GoodsReceiptID),
    FOREIGN KEY (PurchaseOrderID, POItemNumber) REFERENCES PurchaseOrderItems(PurchaseOrderID, ItemNumber),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID)
);

-- ============================================================================
-- SUPPLIER INVOICE TABLES (MAIN FOCUS)
-- ============================================================================

-- Supplier Invoice Header
CREATE TABLE SupplierInvoices (
    InvoiceID TEXT PRIMARY KEY,
    FiscalYear TEXT NOT NULL,
    CompanyCode TEXT NOT NULL,
    SupplierID TEXT NOT NULL,
    
    -- Document Dates
    InvoiceDate TEXT NOT NULL,
    PostingDate TEXT NOT NULL,
    
    -- Reference Information
    SupplierInvoiceNumber TEXT,
    PurchaseOrderID TEXT,
    
    -- Invoice Type
    IsInvoice INTEGER DEFAULT 1,
    InvoiceOrigin TEXT,
    
    -- Amounts
    Currency TEXT DEFAULT 'USD',
    GrossAmount REAL NOT NULL,
    NetAmount REAL,
    TaxAmount REAL,
    
    -- Status and Processing
    InvoiceStatus TEXT CHECK(InvoiceStatus IN ('PARKED', 'HELD', 'POSTED', 'PAID', 'CANCELLED')),
    PaymentStatus TEXT CHECK(PaymentStatus IN ('UNPAID', 'PARTIALLY_PAID', 'FULLY_PAID')),
    PaymentDueDate TEXT,
    PaymentTerms TEXT,
    
    -- Blocking/Hold Reasons
    IsBlocked INTEGER DEFAULT 0,
    BlockingReason TEXT,
    
    -- Audit Fields
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (datetime('now')),
    PostedBy TEXT,
    PostedDate TEXT,
    
    -- Foreign Keys
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode),
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID)
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
    
    -- Material/Service Details
    MaterialID TEXT,
    PlantID TEXT,
    MaterialDescription TEXT,
    
    -- Quantities and Amounts
    Quantity REAL,
    UnitOfMeasure TEXT,
    UnitPrice REAL,
    TotalAmount REAL NOT NULL,
    TaxCode TEXT,
    TaxAmount REAL,
    
    -- Variance Indicators
    HasPriceVariance INTEGER DEFAULT 0,
    HasQuantityVariance INTEGER DEFAULT 0,
    HasDateVariance INTEGER DEFAULT 0,
    
    -- Variance Amounts
    PriceVarianceAmount REAL,
    QuantityVarianceAmount REAL,
    
    PRIMARY KEY (InvoiceID, ItemNumber),
    FOREIGN KEY (InvoiceID) REFERENCES SupplierInvoices(InvoiceID),
    FOREIGN KEY (PurchaseOrderID, POItemNumber) REFERENCES PurchaseOrderItems(PurchaseOrderID, ItemNumber),
    FOREIGN KEY (GoodsReceiptID, GRItemNumber) REFERENCES GoodsReceiptItems(GoodsReceiptID, ItemNumber),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID)
);

-- Invoice Payment Information
CREATE TABLE InvoicePayments (
    PaymentID TEXT PRIMARY KEY,
    InvoiceID TEXT NOT NULL,
    PaymentDate TEXT NOT NULL,
    PaymentAmount REAL NOT NULL,
    PaymentMethod TEXT,
    PaymentReference TEXT,
    Currency TEXT,
    ExchangeRate REAL,
    CreatedBy TEXT,
    CreatedDate TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (InvoiceID) REFERENCES SupplierInvoices(InvoiceID)
);

-- ============================================================================
-- SAMPLE DATA - Master Data
-- ============================================================================

-- Company Codes
INSERT INTO CompanyCodes VALUES
('1000', 'ACME Corporation USA', 'US', 'USD', 'US-CA'),
('2000', 'ACME Europe GmbH', 'DE', 'EUR', 'DE'),
('3000', 'ACME Asia Pacific', 'SG', 'SGD', 'SG');

-- Plants
INSERT INTO Plants VALUES
('1001', 'Los Angeles Manufacturing', '1000', '123 Main St', 'Los Angeles', 'US'),
('1002', 'New York Distribution', '1000', '456 Broadway', 'New York', 'US'),
('2001', 'Berlin Production', '2000', 'Hauptstraße 10', 'Berlin', 'DE'),
('3001', 'Singapore Warehouse', '3000', '88 Marina Bay', 'Singapore', 'SG');

-- Suppliers
INSERT INTO Suppliers VALUES
('V00001', 'Global Steel Supply Inc', 'Material', 'US-12345678', 'NET30', 'USD', 'orders@globalsteel.com', '+1-555-0100', 1, date('now')),
('V00002', 'Premium Electronics GmbH', 'Material', 'DE-98765432', '2/10NET30', 'EUR', 'sales@premiumelec.de', '+49-30-12345', 1, date('now')),
('V00003', 'Logistics Services Ltd', 'Service', 'US-87654321', 'NET60', 'USD', 'billing@logservices.com', '+1-555-0200', 1, date('now')),
('V00004', 'Pacific Components Co', 'Material', 'SG-11223344', 'NET30', 'SGD', 'support@pacificcomp.sg', '+65-6123-4567', 1, date('now')),
('V00005', 'Quality Consulting Partners', 'Service', 'US-55667788', 'NET45', 'USD', 'invoices@qualitycp.com', '+1-555-0300', 1, date('now'));

-- Materials
INSERT INTO Materials VALUES
('MAT-001', 'Steel Sheet 2mm x 1200mm', 'RAW', 'EA', 'STEEL', 125.50),
('MAT-002', 'Electronic Control Board v2.1', 'SEMI', 'EA', 'ELEC', 450.00),
('MAT-003', 'Hydraulic Cylinder 50mm', 'SEMI', 'EA', 'HYDR', 280.75),
('MAT-004', 'Industrial Lubricant 5L', 'RAW', 'L', 'CHEM', 45.00),
('MAT-005', 'Assembly Bolt M8x50', 'RAW', 'EA', 'FAST', 0.85),
('MAT-006', 'Plastic Housing Component', 'SEMI', 'EA', 'PLST', 15.30),
('MAT-007', 'Power Supply Unit 500W', 'SEMI', 'EA', 'ELEC', 89.99);

-- ============================================================================
-- SAMPLE DATA - Procurement Process
-- ============================================================================

-- Purchase Orders
INSERT INTO PurchaseOrders VALUES
('PO-2024001', 'V00001', '1000', '2024-01-10', '2024-02-15', 15066.00, 'USD', 'FULLY_RECEIVED', 'John.Smith', datetime('now')),
('PO-2024002', 'V00002', '2000', '2024-01-15', '2024-02-20', 9000.00, 'EUR', 'FULLY_RECEIVED', 'Maria.Mueller', datetime('now')),
('PO-2024003', 'V00003', '1000', '2024-01-20', '2024-02-28', 5000.00, 'USD', 'FULLY_RECEIVED', 'John.Smith', datetime('now')),
('PO-2024004', 'V00004', '3000', '2024-01-25', '2024-03-10', 12500.00, 'SGD', 'PARTIALLY_RECEIVED', 'Lisa.Tan', datetime('now')),
('PO-2024005', 'V00001', '1000', '2024-02-01', '2024-03-15', 8000.00, 'USD', 'OPEN', 'John.Smith', datetime('now'));

-- Purchase Order Items
INSERT INTO PurchaseOrderItems VALUES
('PO-2024001', 10, 'MAT-001', '1001', 100, 'EA', 125.50, 12550.00, '2024-02-15', 'FULLY_RECEIVED'),
('PO-2024001', 20, 'MAT-004', '1001', 50, 'L', 45.00, 2250.00, '2024-02-15', 'FULLY_RECEIVED'),
('PO-2024001', 30, 'MAT-005', '1001', 200, 'EA', 0.85, 170.00, '2024-02-15', 'FULLY_RECEIVED'),
('PO-2024001', 40, 'MAT-003', '1001', 3, 'EA', 280.75, 842.25, '2024-02-15', 'FULLY_RECEIVED'),
('PO-2024002', 10, 'MAT-002', '2001', 20, 'EA', 450.00, 9000.00, '2024-02-20', 'FULLY_RECEIVED'),
('PO-2024003', 10, NULL, '1001', 1, 'EA', 5000.00, 5000.00, '2024-02-28', 'FULLY_RECEIVED'),
('PO-2024004', 10, 'MAT-006', '3001', 500, 'EA', 15.30, 7650.00, '2024-03-10', 'PARTIALLY_RECEIVED'),
('PO-2024004', 20, 'MAT-007', '3001', 50, 'EA', 89.99, 4499.50, '2024-03-10', 'OPEN');

-- Goods Receipts
INSERT INTO GoodsReceipts VALUES
('GR-001', 'PO-2024001', '2024-02-16', '1001', '1000', 'POSTED', 'warehouse.la', datetime('now')),
('GR-002', 'PO-2024002', '2024-02-21', '2001', '2000', 'POSTED', 'warehouse.berlin', datetime('now')),
('GR-003', 'PO-2024003', '2024-03-01', '1001', '1000', 'POSTED', 'warehouse.la', datetime('now')),
('GR-004', 'PO-2024004', '2024-03-11', '3001', '3000', 'POSTED', 'warehouse.sg', datetime('now'));

-- Goods Receipt Items
INSERT INTO GoodsReceiptItems VALUES
('GR-001', 1, 'PO-2024001', 10, 'MAT-001', 100, 'EA'),
('GR-001', 2, 'PO-2024001', 20, 'MAT-004', 50, 'L'),
('GR-001', 3, 'PO-2024001', 30, 'MAT-005', 200, 'EA'),
('GR-001', 4, 'PO-2024001', 40, 'MAT-003', 3, 'EA'),
('GR-002', 1, 'PO-2024002', 10, 'MAT-002', 20, 'EA'),
('GR-003', 1, 'PO-2024003', 10, NULL, 1, 'EA'),
('GR-004', 1, 'PO-2024004', 10, 'MAT-006', 300, 'EA');

-- ============================================================================
-- SAMPLE DATA - Supplier Invoices
-- ============================================================================

-- Invoice 1: Normal invoice matching PO and GR (POSTED and PAID)
INSERT INTO SupplierInvoices VALUES (
    'INV-001', '2024', '1000', 'V00001',
    '2024-02-18', '2024-02-20',
    'SI-2024-0156', 'PO-2024001',
    1, 'EDI',
    'USD', 15812.25, 15066.00, 746.25,
    'PAID', 'FULLY_PAID', '2024-03-20', 'NET30',
    0, NULL,
    'ap.clerk', '2024-02-20 10:30:00', 'ap.manager', '2024-02-20 14:15:00'
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-001', 1, 'PO-2024001', 10, 'GR-001', 1, 'MAT-001', '1001', 'Steel Sheet 2mm x 1200mm', 100, 'EA', 125.50, 12550.00, 'S1', 995.00, 0, 0, 0, 0, 0),
('INV-001', 2, 'PO-2024001', 20, 'GR-001', 2, 'MAT-004', '1001', 'Industrial Lubricant 5L', 50, 'L', 45.00, 2250.00, 'S1', 178.50, 0, 0, 0, 0, 0),
('INV-001', 3, 'PO-2024001', 30, 'GR-001', 3, 'MAT-005', '1001', 'Assembly Bolt M8x50', 200, 'EA', 0.85, 170.00, 'S1', 13.50, 0, 0, 0, 0, 0),
('INV-001', 4, 'PO-2024001', 40, 'GR-001', 4, 'MAT-003', '1001', 'Hydraulic Cylinder 50mm', 3, 'EA', 280.75, 842.25, 'S1', 66.75, 0, 0, 0, 0, 0);

-- Invoice 2: Normal invoice (POSTED, awaiting payment)
INSERT INTO SupplierInvoices VALUES (
    'INV-002', '2024', '2000', 'V00002',
    '2024-02-23', '2024-02-25',
    'ELEC-2024-789', 'PO-2024002',
    1, 'EDI',
    'EUR', 9450.00, 9000.00, 450.00,
    'POSTED', 'UNPAID', '2024-03-25', '2/10NET30',
    0, NULL,
    'ap.berlin', '2024-02-25 09:15:00', 'ap.berlin.mgr', '2024-02-25 11:30:00'
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-002', 1, 'PO-2024002', 10, 'GR-002', 1, 'MAT-002', '2001', 'Electronic Control Board v2.1', 20, 'EA', 450.00, 9000.00, 'S1', 450.00, 0, 0, 0, 0, 0);

-- Invoice 3: Service invoice (POSTED, awaiting payment)
INSERT INTO SupplierInvoices VALUES (
    'INV-003', '2024', '1000', 'V00003',
    '2024-03-02', '2024-03-05',
    'LOG-2024-321', 'PO-2024003',
    1, 'MANUAL',
    'USD', 5250.00, 5000.00, 250.00,
    'POSTED', 'UNPAID', '2024-05-04', 'NET60',
    0, NULL,
    'ap.clerk', '2024-03-05 13:20:00', 'ap.manager', '2024-03-05 15:45:00'
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-003', 1, 'PO-2024003', 10, 'GR-003', 1, NULL, '1001', 'Logistics Consulting Services', 1, 'EA', 5000.00, 5000.00, 'S1', 250.00, 0, 0, 0, 0, 0);

-- Invoice 4: Invoice with PRICE VARIANCE (HELD for review)
INSERT INTO SupplierInvoices VALUES (
    'INV-004', '2024', '3000', 'V00004',
    '2024-03-12', '2024-03-14',
    'PC-SG-2024-055', 'PO-2024004',
    1, 'EDI',
    'SGD', 5130.00, 4890.00, 240.00,
    'HELD', 'UNPAID', '2024-04-13', 'NET30',
    1, 'PRICE_VARIANCE',
    'ap.singapore', '2024-03-14 08:30:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-004', 1, 'PO-2024004', 10, 'GR-004', 1, 'MAT-006', '3001', 'Plastic Housing Component', 300, 'EA', 16.30, 4890.00, 'S1', 240.00, 1, 0, 0, 300.00, 0);

-- Invoice 5: Invoice with QUANTITY VARIANCE (HELD for review)
INSERT INTO SupplierInvoices VALUES (
    'INV-005', '2024', '1000', 'V00001',
    '2024-03-15', '2024-03-18',
    'SI-2024-0234', 'PO-2024005',
    1, 'MANUAL',
    'USD', 8400.00, 8000.00, 400.00,
    'HELD', 'UNPAID', '2024-04-17', 'NET30',
    1, 'QUANTITY_VARIANCE',
    'ap.clerk', '2024-03-18 11:00:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-005', 1, 'PO-2024005', 10, NULL, NULL, 'MAT-001', '1001', 'Steel Sheet 2mm x 1200mm', 70, 'EA', 125.50, 8785.00, 'S1', 439.25, 0, 1, 0, 0, 1255.00);

-- Invoice 6: Non-PO invoice (PARKED, awaiting approval)
INSERT INTO SupplierInvoices VALUES (
    'INV-006', '2024', '1000', 'V00005',
    '2024-03-20', '2024-03-22',
    'QCP-2024-112', NULL,
    1, 'MANUAL',
    'USD', 3150.00, 3000.00, 150.00,
    'PARKED', 'UNPAID', '2024-05-06', 'NET45',
    0, NULL,
    'ap.clerk', '2024-03-22 14:30:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-006', 1, NULL, NULL, NULL, NULL, NULL, '1001', 'Quality Audit Consulting - March 2024', 1, 'EA', 3000.00, 3000.00, 'S1', 150.00, 0, 0, 0, 0, 0);

-- Invoice 7: Credit Memo (POSTED)
INSERT INTO SupplierInvoices VALUES (
    'INV-007', '2024', '1000', 'V00001',
    '2024-03-10', '2024-03-12',
    'CM-2024-0012', 'PO-2024001',
    0, 'MANUAL',
    'USD', -500.00, -500.00, 0.00,
    'POSTED', 'UNPAID', '2024-04-11', 'NET30',
    0, NULL,
    'ap.clerk', '2024-03-12 10:00:00', 'ap.manager', '2024-03-12 11:30:00'
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-007', 1, 'PO-2024001', 10, 'GR-001', 1, 'MAT-001', '1001', 'Steel Sheet 2mm - Damaged Units Credit', 4, 'EA', -125.00, -500.00, 'S1', 0.00, 0, 0, 0, 0, 0);

-- Payment Records
INSERT INTO InvoicePayments VALUES
('PAY-001', 'INV-001', '2024-03-15', 15812.25, 'ACH', 'ACH-2024-03-15-001', 'USD', 1.00000, 'payment.system', '2024-03-15 02:00:00');

-- ============================================================================
-- USEFUL VIEWS FOR P2P WORKFLOW
-- ============================================================================

-- View: Outstanding Invoices
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
    julianday('now') - julianday(si.PaymentDueDate) AS DaysOverdue
FROM SupplierInvoices si
JOIN Suppliers s ON si.SupplierID = s.SupplierID
WHERE si.PaymentStatus != 'FULLY_PAID'
    AND si.InvoiceStatus NOT IN ('CANCELLED');

-- View: Invoice Variances
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

-- View: PO to Invoice Tracking
CREATE VIEW vw_POtoInvoiceTracking AS
SELECT 
    po.PurchaseOrderID,
    po.OrderDate,
    po.SupplierID,
    s.SupplierName,
    po.TotalAmount AS POAmount,
    po.Currency,
    po.POStatus,
    gr.GoodsReceiptID,
    gr.ReceiptDate,
    si.InvoiceID,
    si.SupplierInvoiceNumber,
    si.InvoiceDate,
    si.GrossAmount AS InvoiceAmount,
    si.InvoiceStatus,
    si.PaymentStatus
FROM PurchaseOrders po
JOIN Suppliers s ON po.SupplierID = s.SupplierID
LEFT JOIN GoodsReceipts gr ON po.PurchaseOrderID = gr.PurchaseOrderID
LEFT JOIN SupplierInvoices si ON po.PurchaseOrderID = si.PurchaseOrderID
ORDER BY po.OrderDate DESC;

-- View: Supplier Performance
CREATE VIEW vw_SupplierPerformance AS
SELECT 
    s.SupplierID,
    s.SupplierName,
    COUNT(DISTINCT si.InvoiceID) AS TotalInvoices,
    SUM(CASE WHEN si.IsBlocked = 1 THEN 1 ELSE 0 END) AS BlockedInvoices,
    SUM(si.GrossAmount) AS TotalInvoiceAmount,
    AVG(julianday(si.PostingDate) - julianday(si.InvoiceDate)) AS AvgProcessingDays,
    SUM(CASE WHEN si.PaymentStatus = 'FULLY_PAID' THEN 1 ELSE 0 END) AS PaidInvoices
FROM Suppliers s
LEFT JOIN SupplierInvoices si ON s.SupplierID = si.SupplierID
WHERE si.InvoiceStatus != 'CANCELLED'
GROUP BY s.SupplierID, s.SupplierName;
