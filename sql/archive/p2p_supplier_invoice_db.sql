-- ============================================================================
-- Procure-to-Pay (P2P) Supplier Invoice Database
-- ============================================================================
-- This database supports the P2P workflow:
-- 1. Purchase Requisition → 2. Purchase Order → 3. Goods Receipt → 
-- 4. Supplier Invoice → 5. Payment
-- ============================================================================

-- ============================================================================
-- CORE MASTER DATA TABLES
-- ============================================================================

-- Suppliers (Vendors)
CREATE TABLE Suppliers (
    SupplierID VARCHAR(10) PRIMARY KEY,
    SupplierName VARCHAR(100) NOT NULL,
    SupplierType VARCHAR(20), -- 'Material', 'Service', 'Both'
    TaxID VARCHAR(20),
    PaymentTerms VARCHAR(20), -- 'NET30', 'NET60', '2/10NET30'
    Currency VARCHAR(3) DEFAULT 'USD',
    ContactEmail VARCHAR(100),
    ContactPhone VARCHAR(20),
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedDate DATE DEFAULT CURRENT_DATE
);

-- Company Codes (Legal Entities)
CREATE TABLE CompanyCodes (
    CompanyCode VARCHAR(4) PRIMARY KEY,
    CompanyName VARCHAR(100) NOT NULL,
    Country VARCHAR(2),
    Currency VARCHAR(3),
    TaxJurisdiction VARCHAR(20)
);

-- Plants (Physical Locations)
CREATE TABLE Plants (
    PlantID VARCHAR(4) PRIMARY KEY,
    PlantName VARCHAR(100) NOT NULL,
    CompanyCode VARCHAR(4),
    Address VARCHAR(200),
    City VARCHAR(50),
    Country VARCHAR(2),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Materials
CREATE TABLE Materials (
    MaterialID VARCHAR(18) PRIMARY KEY,
    MaterialDescription VARCHAR(200) NOT NULL,
    MaterialType VARCHAR(20), -- 'RAW', 'SEMI', 'FINISHED'
    BaseUnitOfMeasure VARCHAR(3), -- 'EA', 'KG', 'L'
    MaterialGroup VARCHAR(10),
    StandardPrice DECIMAL(15, 2)
);

-- ============================================================================
-- PROCUREMENT PROCESS TABLES
-- ============================================================================

-- Purchase Orders
CREATE TABLE PurchaseOrders (
    PurchaseOrderID VARCHAR(10) PRIMARY KEY,
    SupplierID VARCHAR(10) NOT NULL,
    CompanyCode VARCHAR(4) NOT NULL,
    OrderDate DATE NOT NULL,
    DeliveryDate DATE,
    TotalAmount DECIMAL(15, 2),
    Currency VARCHAR(3) DEFAULT 'USD',
    POStatus VARCHAR(20), -- 'OPEN', 'PARTIALLY_RECEIVED', 'FULLY_RECEIVED', 'CLOSED'
    CreatedBy VARCHAR(50),
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Purchase Order Items
CREATE TABLE PurchaseOrderItems (
    PurchaseOrderID VARCHAR(10),
    ItemNumber INT,
    MaterialID VARCHAR(18),
    PlantID VARCHAR(4),
    Quantity DECIMAL(13, 3) NOT NULL,
    UnitOfMeasure VARCHAR(3),
    UnitPrice DECIMAL(15, 2) NOT NULL,
    TotalPrice DECIMAL(15, 2),
    DeliveryDate DATE,
    ItemStatus VARCHAR(20), -- 'OPEN', 'PARTIALLY_RECEIVED', 'FULLY_RECEIVED'
    PRIMARY KEY (PurchaseOrderID, ItemNumber),
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID)
);

-- Goods Receipts (Material Documents)
CREATE TABLE GoodsReceipts (
    GoodsReceiptID VARCHAR(10) PRIMARY KEY,
    PurchaseOrderID VARCHAR(10) NOT NULL,
    ReceiptDate DATE NOT NULL,
    PlantID VARCHAR(4),
    CompanyCode VARCHAR(4),
    DocumentStatus VARCHAR(20), -- 'POSTED', 'CANCELLED'
    PostedBy VARCHAR(50),
    PostedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode)
);

-- Goods Receipt Items
CREATE TABLE GoodsReceiptItems (
    GoodsReceiptID VARCHAR(10),
    ItemNumber INT,
    PurchaseOrderID VARCHAR(10),
    POItemNumber INT,
    MaterialID VARCHAR(18),
    QuantityReceived DECIMAL(13, 3) NOT NULL,
    UnitOfMeasure VARCHAR(3),
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
    InvoiceID VARCHAR(10) PRIMARY KEY,
    FiscalYear VARCHAR(4) NOT NULL,
    CompanyCode VARCHAR(4) NOT NULL,
    SupplierID VARCHAR(10) NOT NULL,
    
    -- Document Dates
    InvoiceDate DATE NOT NULL,
    PostingDate DATE NOT NULL,
    
    -- Reference Information
    SupplierInvoiceNumber VARCHAR(16), -- Supplier's own invoice number
    PurchaseOrderID VARCHAR(10), -- Reference PO (can be NULL for non-PO invoices)
    
    -- Invoice Type
    IsInvoice BOOLEAN DEFAULT TRUE, -- TRUE = Invoice, FALSE = Credit Memo
    InvoiceOrigin VARCHAR(20), -- 'MANUAL', 'EDI', 'OCR', 'ERS'
    
    -- Amounts
    Currency VARCHAR(3) DEFAULT 'USD',
    GrossAmount DECIMAL(15, 2) NOT NULL,
    NetAmount DECIMAL(15, 2),
    TaxAmount DECIMAL(15, 2),
    
    -- Status and Processing
    InvoiceStatus VARCHAR(20), -- 'PARKED', 'HELD', 'POSTED', 'PAID', 'CANCELLED'
    PaymentStatus VARCHAR(20), -- 'UNPAID', 'PARTIALLY_PAID', 'FULLY_PAID'
    PaymentDueDate DATE,
    PaymentTerms VARCHAR(20),
    
    -- Blocking/Hold Reasons
    IsBlocked BOOLEAN DEFAULT FALSE,
    BlockingReason VARCHAR(50), -- 'PRICE_VARIANCE', 'QUANTITY_VARIANCE', 'DATE_VARIANCE', 'MANUAL', 'QUALITY'
    
    -- Audit Fields
    CreatedBy VARCHAR(50),
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PostedBy VARCHAR(50),
    PostedDate TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (CompanyCode) REFERENCES CompanyCodes(CompanyCode),
    FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrders(PurchaseOrderID)
);

-- Supplier Invoice Items
CREATE TABLE SupplierInvoiceItems (
    InvoiceID VARCHAR(10),
    ItemNumber INT,
    
    -- Reference Documents
    PurchaseOrderID VARCHAR(10),
    POItemNumber INT,
    GoodsReceiptID VARCHAR(10),
    GRItemNumber INT,
    
    -- Material/Service Details
    MaterialID VARCHAR(18),
    PlantID VARCHAR(4),
    MaterialDescription VARCHAR(200),
    
    -- Quantities and Amounts
    Quantity DECIMAL(13, 3),
    UnitOfMeasure VARCHAR(3),
    UnitPrice DECIMAL(15, 2),
    TotalAmount DECIMAL(15, 2) NOT NULL,
    TaxCode VARCHAR(2),
    TaxAmount DECIMAL(15, 2),
    
    -- Variance Indicators
    HasPriceVariance BOOLEAN DEFAULT FALSE,
    HasQuantityVariance BOOLEAN DEFAULT FALSE,
    HasDateVariance BOOLEAN DEFAULT FALSE,
    
    -- Variance Amounts
    PriceVarianceAmount DECIMAL(15, 2),
    QuantityVarianceAmount DECIMAL(15, 2),
    
    PRIMARY KEY (InvoiceID, ItemNumber),
    FOREIGN KEY (InvoiceID) REFERENCES SupplierInvoices(InvoiceID),
    FOREIGN KEY (PurchaseOrderID, POItemNumber) REFERENCES PurchaseOrderItems(PurchaseOrderID, ItemNumber),
    FOREIGN KEY (GoodsReceiptID, GRItemNumber) REFERENCES GoodsReceiptItems(GoodsReceiptID, ItemNumber),
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID),
    FOREIGN KEY (PlantID) REFERENCES Plants(PlantID)
);

-- Invoice Payment Information
CREATE TABLE InvoicePayments (
    PaymentID VARCHAR(10) PRIMARY KEY,
    InvoiceID VARCHAR(10) NOT NULL,
    PaymentDate DATE NOT NULL,
    PaymentAmount DECIMAL(15, 2) NOT NULL,
    PaymentMethod VARCHAR(20), -- 'WIRE', 'CHECK', 'ACH', 'CARD'
    PaymentReference VARCHAR(50),
    Currency VARCHAR(3),
    ExchangeRate DECIMAL(9, 5),
    CreatedBy VARCHAR(50),
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (InvoiceID) REFERENCES SupplierInvoices(InvoiceID)
);

-- ============================================================================
-- SAMPLE DATA - Master Data
-- ============================================================================

-- Company Codes
INSERT INTO CompanyCodes (CompanyCode, CompanyName, Country, Currency, TaxJurisdiction) VALUES
('1000', 'ACME Corporation USA', 'US', 'USD', 'US-CA'),
('2000', 'ACME Europe GmbH', 'DE', 'EUR', 'DE'),
('3000', 'ACME Asia Pacific', 'SG', 'SGD', 'SG');

-- Plants
INSERT INTO Plants (PlantID, PlantName, CompanyCode, Address, City, Country) VALUES
('1001', 'Los Angeles Manufacturing', '1000', '123 Main St', 'Los Angeles', 'US'),
('1002', 'New York Distribution', '1000', '456 Broadway', 'New York', 'US'),
('2001', 'Berlin Production', '2000', 'Hauptstraße 10', 'Berlin', 'DE'),
('3001', 'Singapore Warehouse', '3000', '88 Marina Bay', 'Singapore', 'SG');

-- Suppliers
INSERT INTO Suppliers (SupplierID, SupplierName, SupplierType, TaxID, PaymentTerms, Currency, ContactEmail, ContactPhone, IsActive) VALUES
('V00001', 'Global Steel Supply Inc', 'Material', 'US-12345678', 'NET30', 'USD', 'orders@globalsteel.com', '+1-555-0100', TRUE),
('V00002', 'Premium Electronics GmbH', 'Material', 'DE-98765432', '2/10NET30', 'EUR', 'sales@premiumelec.de', '+49-30-12345', TRUE),
('V00003', 'Logistics Services Ltd', 'Service', 'US-87654321', 'NET60', 'USD', 'billing@logservices.com', '+1-555-0200', TRUE),
('V00004', 'Pacific Components Co', 'Material', 'SG-11223344', 'NET30', 'SGD', 'support@pacificcomp.sg', '+65-6123-4567', TRUE),
('V00005', 'Quality Consulting Partners', 'Service', 'US-55667788', 'NET45', 'USD', 'invoices@qualitycp.com', '+1-555-0300', TRUE);

-- Materials
INSERT INTO Materials (MaterialID, MaterialDescription, MaterialType, BaseUnitOfMeasure, MaterialGroup, StandardPrice) VALUES
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
INSERT INTO PurchaseOrders (PurchaseOrderID, SupplierID, CompanyCode, OrderDate, DeliveryDate, TotalAmount, Currency, POStatus, CreatedBy) VALUES
('PO-2024001', 'V00001', '1000', '2024-01-10', '2024-02-15', 15066.00, 'USD', 'FULLY_RECEIVED', 'John.Smith'),
('PO-2024002', 'V00002', '2000', '2024-01-15', '2024-02-20', 9000.00, 'EUR', 'FULLY_RECEIVED', 'Maria.Mueller'),
('PO-2024003', 'V00003', '1000', '2024-01-20', '2024-02-28', 5000.00, 'USD', 'FULLY_RECEIVED', 'John.Smith'),
('PO-2024004', 'V00004', '3000', '2024-01-25', '2024-03-10', 12500.00, 'SGD', 'PARTIALLY_RECEIVED', 'Lisa.Tan'),
('PO-2024005', 'V00001', '1000', '2024-02-01', '2024-03-15', 8000.00, 'USD', 'OPEN', 'John.Smith');

-- Purchase Order Items
INSERT INTO PurchaseOrderItems (PurchaseOrderID, ItemNumber, MaterialID, PlantID, Quantity, UnitOfMeasure, UnitPrice, TotalPrice, DeliveryDate, ItemStatus) VALUES
('PO-2024001', 10, 'MAT-001', '1001', 100, 'EA', 125.50, 12550.00, '2024-02-15', 'FULLY_RECEIVED'),
('PO-2024001', 20, 'MAT-004', '1001', 50, 'L', 45.00, 2250.00, '2024-02-15', 'FULLY_RECEIVED'),
('PO-2024001', 30, 'MAT-005', '1001', 200, 'EA', 0.85, 170.00, '2024-02-15', 'FULLY_RECEIVED'),
('PO-2024001', 40, 'MAT-003', '1001', 3, 'EA', 280.75, 842.25, '2024-02-15', 'FULLY_RECEIVED'),
('PO-2024002', 10, 'MAT-002', '2001', 20, 'EA', 450.00, 9000.00, '2024-02-20', 'FULLY_RECEIVED'),
('PO-2024003', 10, NULL, '1001', 1, 'EA', 5000.00, 5000.00, '2024-02-28', 'FULLY_RECEIVED'),
('PO-2024004', 10, 'MAT-006', '3001', 500, 'EA', 15.30, 7650.00, '2024-03-10', 'PARTIALLY_RECEIVED'),
('PO-2024004', 20, 'MAT-007', '3001', 50, 'EA', 89.99, 4499.50, '2024-03-10', 'OPEN');

-- Goods Receipts
INSERT INTO GoodsReceipts (GoodsReceiptID, PurchaseOrderID, ReceiptDate, PlantID, CompanyCode, DocumentStatus, PostedBy) VALUES
('GR-001', 'PO-2024001', '2024-02-16', '1001', '1000', 'POSTED', 'warehouse.la'),
('GR-002', 'PO-2024002', '2024-02-21', '2001', '2000', 'POSTED', 'warehouse.berlin'),
('GR-003', 'PO-2024003', '2024-03-01', '1001', '1000', 'POSTED', 'warehouse.la'),
('GR-004', 'PO-2024004', '2024-03-11', '3001', '3000', 'POSTED', 'warehouse.sg');

-- Goods Receipt Items
INSERT INTO GoodsReceiptItems (GoodsReceiptID, ItemNumber, PurchaseOrderID, POItemNumber, MaterialID, QuantityReceived, UnitOfMeasure) VALUES
('GR-001', 1, 'PO-2024001', 10, 'MAT-001', 100, 'EA'),
('GR-001', 2, 'PO-2024001', 20, 'MAT-004', 50, 'L'),
('GR-001', 3, 'PO-2024001', 30, 'MAT-005', 200, 'EA'),
('GR-001', 4, 'PO-2024001', 40, 'MAT-003', 3, 'EA'),
('GR-002', 1, 'PO-2024002', 10, 'MAT-002', 20, 'EA'),
('GR-003', 1, 'PO-2024003', 10, NULL, 1, 'EA'),
('GR-004', 1, 'PO-2024004', 10, 'MAT-006', 300, 'EA'); -- Only partial delivery

-- ============================================================================
-- SAMPLE DATA - Supplier Invoices
-- ============================================================================

-- Invoice 1: Normal invoice matching PO and GR (POSTED and PAID)
INSERT INTO SupplierInvoices VALUES (
    'INV-001', '2024', '1000', 'V00001',
    '2024-02-18', '2024-02-20',
    'SI-2024-0156', 'PO-2024001',
    TRUE, 'EDI',
    'USD', 15812.25, 15066.00, 746.25,
    'PAID', 'FULLY_PAID', '2024-03-20', 'NET30',
    FALSE, NULL,
    'ap.clerk', '2024-02-20 10:30:00', 'ap.manager', '2024-02-20 14:15:00'
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-001', 1, 'PO-2024001', 10, 'GR-001', 1, 'MAT-001', '1001', 'Steel Sheet 2mm x 1200mm', 100, 'EA', 125.50, 12550.00, 'S1', 995.00, FALSE, FALSE, FALSE, 0, 0),
('INV-001', 2, 'PO-2024001', 20, 'GR-001', 2, 'MAT-004', '1001', 'Industrial Lubricant 5L', 50, 'L', 45.00, 2250.00, 'S1', 178.50, FALSE, FALSE, FALSE, 0, 0),
('INV-001', 3, 'PO-2024001', 30, 'GR-001', 3, 'MAT-005', '1001', 'Assembly Bolt M8x50', 200, 'EA', 0.85, 170.00, 'S1', 13.50, FALSE, FALSE, FALSE, 0, 0),
('INV-001', 4, 'PO-2024001', 40, 'GR-001', 4, 'MAT-003', '1001', 'Hydraulic Cylinder 50mm', 3, 'EA', 280.75, 842.25, 'S1', 66.75, FALSE, FALSE, FALSE, 0, 0);

-- Invoice 2: Normal invoice (POSTED, awaiting payment)
INSERT INTO SupplierInvoices VALUES (
    'INV-002', '2024', '2000', 'V00002',
    '2024-02-23', '2024-02-25',
    'ELEC-2024-789', 'PO-2024002',
    TRUE, 'EDI',
    'EUR', 9450.00, 9000.00, 450.00,
    'POSTED', 'UNPAID', '2024-03-25', '2/10NET30',
    FALSE, NULL,
    'ap.berlin', '2024-02-25 09:15:00', 'ap.berlin.mgr', '2024-02-25 11:30:00'
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-002', 1, 'PO-2024002', 10, 'GR-002', 1, 'MAT-002', '2001', 'Electronic Control Board v2.1', 20, 'EA', 450.00, 9000.00, 'S1', 450.00, FALSE, FALSE, FALSE, 0, 0);

-- Invoice 3: Service invoice (POSTED, awaiting payment)
INSERT INTO SupplierInvoices VALUES (
    'INV-003', '2024', '1000', 'V00003',
    '2024-03-02', '2024-03-05',
    'LOG-2024-321', 'PO-2024003',
    TRUE, 'MANUAL',
    'USD', 5250.00, 5000.00, 250.00,
    'POSTED', 'UNPAID', '2024-05-04', 'NET60',
    FALSE, NULL,
    'ap.clerk', '2024-03-05 13:20:00', 'ap.manager', '2024-03-05 15:45:00'
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-003', 1, 'PO-2024003', 10, 'GR-003', 1, NULL, '1001', 'Logistics Consulting Services', 1, 'EA', 5000.00, 5000.00, 'S1', 250.00, FALSE, FALSE, FALSE, 0, 0);

-- Invoice 4: Invoice with PRICE VARIANCE (HELD for review)
INSERT INTO SupplierInvoices VALUES (
    'INV-004', '2024', '3000', 'V00004',
    '2024-03-12', '2024-03-14',
    'PC-SG-2024-055', 'PO-2024004',
    TRUE, 'EDI',
    'SGD', 5130.00, 4890.00, 240.00,
    'HELD', 'UNPAID', '2024-04-13', 'NET30',
    TRUE, 'PRICE_VARIANCE',
    'ap.singapore', '2024-03-14 08:30:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-004', 1, 'PO-2024004', 10, 'GR-004', 1, 'MAT-006', '3001', 'Plastic Housing Component', 300, 'EA', 16.30, 4890.00, 'S1', 240.00, TRUE, FALSE, FALSE, 300.00, 0);
-- Note: Supplier charged 16.30 per unit instead of PO price 15.30, creating a 300 SGD variance

-- Invoice 5: Invoice with QUANTITY VARIANCE (HELD for review)
INSERT INTO SupplierInvoices VALUES (
    'INV-005', '2024', '1000', 'V00001',
    '2024-03-15', '2024-03-18',
    'SI-2024-0234', 'PO-2024005',
    TRUE, 'MANUAL',
    'USD', 8400.00, 8000.00, 400.00,
    'HELD', 'UNPAID', '2024-04-17', 'NET30',
    TRUE, 'QUANTITY_VARIANCE',
    'ap.clerk', '2024-03-18 11:00:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-005', 1, 'PO-2024005', 10, NULL, NULL, 'MAT-001', '1001', 'Steel Sheet 2mm x 1200mm', 70, 'EA', 125.50, 8785.00, 'S1', 439.25, FALSE, TRUE, FALSE, 0, 1255.00);
-- Note: Supplier invoiced for 70 units but PO was for 64 units (based on 8000/125.50)

-- Invoice 6: Non-PO invoice (PARKED, awaiting approval)
INSERT INTO SupplierInvoices VALUES (
    'INV-006', '2024', '1000', 'V00005',
    '2024-03-20', '2024-03-22',
    'QCP-2024-112', NULL,
    TRUE, 'MANUAL',
    'USD', 3150.00, 3000.00, 150.00,
    'PARKED', 'UNPAID', '2024-05-06', 'NET45',
    FALSE, NULL,
    'ap.clerk', '2024-03-22 14:30:00', NULL, NULL
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-006', 1, NULL, NULL, NULL, NULL, NULL, '1001', 'Quality Audit Consulting - March 2024', 1, 'EA', 3000.00, 3000.00, 'S1', 150.00, FALSE, FALSE, FALSE, 0, 0);

-- Invoice 7: Credit Memo (POSTED)
INSERT INTO SupplierInvoices VALUES (
    'INV-007', '2024', '1000', 'V00001',
    '2024-03-10', '2024-03-12',
    'CM-2024-0012', 'PO-2024001',
    FALSE, 'MANUAL',
    'USD', -500.00, -500.00, 0.00,
    'POSTED', 'UNPAID', '2024-04-11', 'NET30',
    FALSE, NULL,
    'ap.clerk', '2024-03-12 10:00:00', 'ap.manager', '2024-03-12 11:30:00'
);

INSERT INTO SupplierInvoiceItems VALUES
('INV-007', 1, 'PO-2024001', 10, 'GR-001', 1, 'MAT-001', '1001', 'Steel Sheet 2mm - Damaged Units Credit', 4, 'EA', -125.00, -500.00, 'S1', 0.00, FALSE, FALSE, FALSE, 0, 0);

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
    DATEDIFF(CURRENT_DATE, si.PaymentDueDate) AS DaysOverdue
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
WHERE si.IsBlocked = TRUE
    OR sii.HasPriceVariance = TRUE
    OR sii.HasQuantityVariance = TRUE;

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
    SUM(CASE WHEN si.IsBlocked = TRUE THEN 1 ELSE 0 END) AS BlockedInvoices,
    SUM(si.GrossAmount) AS TotalInvoiceAmount,
    AVG(DATEDIFF(si.PostingDate, si.InvoiceDate)) AS AvgProcessingDays,
    SUM(CASE WHEN si.PaymentStatus = 'FULLY_PAID' THEN 1 ELSE 0 END) AS PaidInvoices
FROM Suppliers s
LEFT JOIN SupplierInvoices si ON s.SupplierID = si.SupplierID
WHERE si.InvoiceStatus != 'CANCELLED'
GROUP BY s.SupplierID, s.SupplierName;

-- ============================================================================
-- USEFUL QUERIES
-- ============================================================================

-- Query 1: Find all held invoices with variances
-- SELECT * FROM vw_InvoiceVariances ORDER BY InvoiceDate DESC;

-- Query 2: Outstanding invoices due soon (within 7 days)
-- SELECT * FROM vw_OutstandingInvoices 
-- WHERE PaymentDueDate BETWEEN CURRENT_DATE AND DATE_ADD(CURRENT_DATE, INTERVAL 7 DAY)
-- ORDER BY PaymentDueDate;

-- Query 3: Complete P2P cycle tracking for a specific PO
-- SELECT * FROM vw_POtoInvoiceTracking WHERE PurchaseOrderID = 'PO-2024001';

-- Query 4: Supplier invoice statistics
-- SELECT * FROM vw_SupplierPerformance ORDER BY TotalInvoiceAmount DESC;
