-- P2P Test Data Creation Script
-- ================================
-- Creates realistic P2P data for dashboard testing
-- 
-- Includes:
-- - 10 Suppliers
-- - 20 Purchase Orders
-- - 30 Invoices (including 10+ you requested)
-- - 5 Service Entry Sheets
-- - Supporting data (Payment Terms, Company Codes)
--
-- Author: P2P Development Team
-- Date: 2026-02-07

-- =============================================================================
-- SCHEMA CREATION
-- =============================================================================

-- Suppliers
CREATE TABLE IF NOT EXISTS Supplier (
    Supplier TEXT PRIMARY KEY,
    SupplierName TEXT,
    Country TEXT,
    City TEXT,
    PostalCode TEXT,
    StreetName TEXT,
    IsBlocked INTEGER DEFAULT 0,
    CreationDate TEXT,
    LastChangeDate TEXT
);

-- Purchase Orders
CREATE TABLE IF NOT EXISTS PurchaseOrder (
    PurchaseOrder TEXT PRIMARY KEY,
    Supplier TEXT,
    CompanyCode TEXT,
    PurchasingOrganization TEXT,
    PurchasingGroup TEXT,
    CreationDate TEXT,
    DocumentDate TEXT,
    PurchaseOrderDate TEXT,
    PaymentTerms TEXT,
    Currency TEXT DEFAULT 'EUR',
    OverallStatus TEXT,
    IsCompleted INTEGER DEFAULT 0,
    IsCancelled INTEGER DEFAULT 0,
    FOREIGN KEY (Supplier) REFERENCES Supplier(Supplier)
);

-- Purchase Order Items
CREATE TABLE IF NOT EXISTS PurchaseOrderItem (
    PurchaseOrder TEXT,
    PurchaseOrderItem TEXT,
    Material TEXT,
    MaterialGroup TEXT,
    OrderQuantity REAL,
    NetAmount REAL,
    TaxAmount REAL,
    GrossAmount REAL,
    Currency TEXT DEFAULT 'EUR',
    Plant TEXT,
    StorageLocation TEXT,
    PRIMARY KEY (PurchaseOrder, PurchaseOrderItem),
    FOREIGN KEY (PurchaseOrder) REFERENCES PurchaseOrder(PurchaseOrder)
);

-- Schedule Lines
CREATE TABLE IF NOT EXISTS PurchaseOrderScheduleLine (
    PurchaseOrder TEXT,
    PurchaseOrderItem TEXT,
    ScheduleLine TEXT,
    ScheduleLineDeliveryDate TEXT,
    ScheduleLineOrderQuantity REAL,
    ConfirmedDeliveryDate TEXT,
    DelivDateCategory TEXT,
    PRIMARY KEY (PurchaseOrder, PurchaseOrderItem, ScheduleLine),
    FOREIGN KEY (PurchaseOrder, PurchaseOrderItem) REFERENCES PurchaseOrderItem(PurchaseOrder, PurchaseOrderItem)
);

-- Supplier Invoices
CREATE TABLE IF NOT EXISTS SupplierInvoice (
    SupplierInvoice TEXT PRIMARY KEY,
    FiscalYear TEXT,
    Supplier TEXT,
    CompanyCode TEXT,
    DocumentDate TEXT,
    PostingDate TEXT,
    InvoiceGrossAmount REAL,
    Currency TEXT DEFAULT 'EUR',
    PaymentTerms TEXT,
    InvoiceStatus TEXT,
    IsReversed INTEGER DEFAULT 0,
    ReversalReason TEXT,
    FOREIGN KEY (Supplier) REFERENCES Supplier(Supplier)
);

-- Supplier Invoice Items
CREATE TABLE IF NOT EXISTS SupplierInvoiceItem (
    SupplierInvoice TEXT,
    FiscalYear TEXT,
    SupplierInvoiceItem TEXT,
    PurchaseOrder TEXT,
    PurchaseOrderItem TEXT,
    TaxCode TEXT,
    DocumentCurrency TEXT DEFAULT 'EUR',
    SupplierInvoiceItemAmount REAL,
    QuantityInPurchaseOrderUnit REAL,
    PurchaseOrderQuantityUnit TEXT,
    PRIMARY KEY (SupplierInvoice, FiscalYear, SupplierInvoiceItem),
    FOREIGN KEY (SupplierInvoice, FiscalYear) REFERENCES SupplierInvoice(SupplierInvoice, FiscalYear),
    FOREIGN KEY (PurchaseOrder, PurchaseOrderItem) REFERENCES PurchaseOrderItem(PurchaseOrder, PurchaseOrderItem)
);

-- Service Entry Sheets
CREATE TABLE IF NOT EXISTS ServiceEntrySheet (
    ServiceEntrySheet TEXT PRIMARY KEY,
    PurchaseOrder TEXT,
    ServiceEntrySheetDate TEXT,
    SupplierServiceEntrySheet TEXT,
    ServicePerformer TEXT,
    ServiceEntrySheetStatus TEXT,
    ApprovalDate TEXT,
    FOREIGN KEY (PurchaseOrder) REFERENCES PurchaseOrder(PurchaseOrder)
);

-- Service Entry Sheet Items
CREATE TABLE IF NOT EXISTS ServiceEntrySheetItem (
    ServiceEntrySheet TEXT,
    ServiceEntrySheetItem TEXT,
    PurchaseOrder TEXT,
    PurchaseOrderItem TEXT,
    Quantity REAL,
    NetAmount REAL,
    Currency TEXT DEFAULT 'EUR',
    PRIMARY KEY (ServiceEntrySheet, ServiceEntrySheetItem),
    FOREIGN KEY (ServiceEntrySheet) REFERENCES ServiceEntrySheet(ServiceEntrySheet),
    FOREIGN KEY (PurchaseOrder, PurchaseOrderItem) REFERENCES PurchaseOrderItem(PurchaseOrder, PurchaseOrderItem)
);

-- Payment Terms
CREATE TABLE IF NOT EXISTS PaymentTerms (
    PaymentTerms TEXT PRIMARY KEY,
    PaymentTermsName TEXT,
    CashDiscount1Days INTEGER,
    CashDiscount1Percent REAL,
    CashDiscount2Days INTEGER,
    CashDiscount2Percent REAL,
    NetPaymentDays INTEGER
);

-- Company Codes
CREATE TABLE IF NOT EXISTS CompanyCode (
    CompanyCode TEXT PRIMARY KEY,
    CompanyCodeName TEXT,
    Country TEXT,
    Currency TEXT DEFAULT 'EUR',
    Language TEXT DEFAULT 'EN'
);

-- =============================================================================
-- TEST DATA POPULATION
-- =============================================================================

-- Payment Terms (supporting data)
INSERT INTO PaymentTerms VALUES ('Z001', 'Net 30 Days', 10, 2.0, 20, 1.0, 30);
INSERT INTO PaymentTerms VALUES ('Z002', 'Net 60 Days', 0, 0, 0, 0, 60);
INSERT INTO PaymentTerms VALUES ('Z003', 'Net 15 Days', 5, 3.0, 10, 1.5, 15);

-- Company Codes
INSERT INTO CompanyCode VALUES ('1000', 'SAP SE', 'DE', 'EUR', 'EN');
INSERT INTO CompanyCode VALUES ('2000', 'SAP US', 'US', 'USD', 'EN');

-- 10 Suppliers
INSERT INTO Supplier VALUES ('0000100001', 'Global Tech Solutions GmbH', 'DE', 'Munich', '80331', 'Marienplatz 1', 0, '2025-01-15', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100002', 'Enterprise Software AG', 'DE', 'Berlin', '10117', 'Unter den Linden 10', 0, '2025-02-20', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100003', 'Cloud Services Ltd', 'GB', 'London', 'EC1A 1BB', '1 Fleet Street', 0, '2025-03-10', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100004', 'Data Systems Corp', 'US', 'New York', '10001', '350 Fifth Avenue', 0, '2025-04-05', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100005', 'Innovation Partners SAS', 'FR', 'Paris', '75001', '1 Rue de Rivoli', 0, '2025-05-15', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100006', 'Quality Goods BV', 'NL', 'Amsterdam', '1012', 'Dam 1', 0, '2025-06-01', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100007', 'Precision Manufacturing SpA', 'IT', 'Milan', '20121', 'Piazza del Duomo', 0, '2025-07-12', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100008', 'Digital Solutions AB', 'SE', 'Stockholm', '11153', 'Drottninggatan 1', 0, '2025-08-20', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100009', 'Smart Logistics SA', 'ES', 'Madrid', '28013', 'Gran Via 1', 1, '2025-09-05', '2026-02-01');
INSERT INTO Supplier VALUES ('0000100010', 'Future Tech KK', 'JP', 'Tokyo', '100-0001', 'Chiyoda 1-1', 0, '2025-10-10', '2026-02-01');

-- 20 Purchase Orders (mix of dates, values, statuses)
INSERT INTO PurchaseOrder VALUES ('4500000001', '0000100001', '1000', 'P001', 'G01', '2026-01-10', '2026-01-10', '2026-01-10', 'Z001', 'EUR', 'APPROVED', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000002', '0000100002', '1000', 'P001', 'G01', '2026-01-12', '2026-01-12', '2026-01-12', 'Z001', 'EUR', 'IN_DELIVERY', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000003', '0000100003', '1000', 'P001', 'G02', '2026-01-15', '2026-01-15', '2026-01-15', 'Z002', 'EUR', 'COMPLETED', 1, 0);
INSERT INTO PurchaseOrder VALUES ('4500000004', '0000100001', '1000', 'P001', 'G01', '2026-01-18', '2026-01-18', '2026-01-18', 'Z001', 'EUR', 'APPROVED', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000005', '0000100004', '1000', 'P002', 'G03', '2026-01-20', '2026-01-20', '2026-01-20', 'Z003', 'EUR', 'IN_DELIVERY', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000006', '0000100005', '1000', 'P001', 'G02', '2026-01-22', '2026-01-22', '2026-01-22', 'Z001', 'EUR', 'COMPLETED', 1, 0);
INSERT INTO PurchaseOrder VALUES ('4500000007', '0000100002', '1000', 'P001', 'G01', '2026-01-25', '2026-01-25', '2026-01-25', 'Z002', 'EUR', 'APPROVED', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000008', '0000100006', '1000', 'P002', 'G04', '2026-01-27', '2026-01-27', '2026-01-27', 'Z001', 'EUR', 'IN_DELIVERY', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000009', '0000100007', '1000', 'P001', 'G03', '2026-01-29', '2026-01-29', '2026-01-29', 'Z003', 'EUR', 'COMPLETED', 1, 0);
INSERT INTO PurchaseOrder VALUES ('4500000010', '0000100003', '1000', 'P002', 'G02', '2026-02-01', '2026-02-01', '2026-02-01', 'Z001', 'EUR', 'APPROVED', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000011', '0000100008', '1000', 'P001', 'G01', '2026-02-03', '2026-02-03', '2026-02-03', 'Z001', 'EUR', 'IN_DELIVERY', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000012', '0000100001', '1000', 'P002', 'G04', '2026-02-04', '2026-02-04', '2026-02-04', 'Z002', 'EUR', 'APPROVED', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000013', '0000100004', '1000', 'P001', 'G03', '2026-02-05', '2026-02-05', '2026-02-05', 'Z001', 'EUR', 'COMPLETED', 1, 0);
INSERT INTO PurchaseOrder VALUES ('4500000014', '0000100005', '1000', 'P002', 'G02', '2026-02-06', '2026-02-06', '2026-02-06', 'Z003', 'EUR', 'IN_DELIVERY', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000015', '0000100010', '1000', 'P001', 'G01', '2026-02-07', '2026-02-07', '2026-02-07', 'Z001', 'EUR', 'APPROVED', 0, 0);
INSERT INTO PurchaseOrder VALUES ('4500000016', '0000100006', '2000', 'P003', 'G05', '2025-12-15', '2025-12-15', '2025-12-15', 'Z002', 'USD', 'COMPLETED', 1, 0);
INSERT INTO PurchaseOrder VALUES ('4500000017', '0000100007', '2000', 'P003', 'G05', '2025-12-20', '2025-12-20', '2025-12-20', 'Z001', 'USD', 'COMPLETED', 1, 0);
INSERT INTO PurchaseOrder VALUES ('4500000018', '0000100002', '1000', 'P001', 'G01', '2025-11-10', '2025-11-10', '2025-11-10', 'Z001', 'EUR', 'COMPLETED', 1, 0);
INSERT INTO PurchaseOrder VALUES ('4500000019', '0000100003', '1000', 'P002', 'G02', '2025-11-25', '2025-11-25', '2025-11-25', 'Z002', 'EUR', 'CANCELLED', 0, 1);
INSERT INTO PurchaseOrder VALUES ('4500000020', '0000100001', '1000', 'P001', 'G03', '2025-10-05', '2025-10-05', '2025-10-05', 'Z001', 'EUR', 'COMPLETED', 1, 0);

-- Purchase Order Items (2-3 items per PO)
INSERT INTO PurchaseOrderItem VALUES ('4500000001', '00010', 'MAT001', 'ELECTRONICS', 10, 15000.00, 2850.00, 17850.00, 'EUR', 'P001', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000001', '00020', 'MAT002', 'ELECTRONICS', 5, 8000.00, 1520.00, 9520.00, 'EUR', 'P001', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000002', '00010', 'MAT003', 'COMPUTERS', 20, 45000.00, 8550.00, 53550.00, 'EUR', 'P001', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000003', '00010', 'MAT004', 'SOFTWARE', 50, 125000.00, 23750.00, 148750.00, 'EUR', 'P001', 'SL02');
INSERT INTO PurchaseOrderItem VALUES ('4500000004', '00010', 'MAT001', 'ELECTRONICS', 15, 22500.00, 4275.00, 26775.00, 'EUR', 'P001', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000005', '00010', 'MAT005', 'FURNITURE', 8, 12000.00, 2280.00, 14280.00, 'EUR', 'P002', 'SL03');
INSERT INTO PurchaseOrderItem VALUES ('4500000006', '00010', 'MAT003', 'COMPUTERS', 12, 27000.00, 5130.00, 32130.00, 'EUR', 'P001', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000007', '00010', 'MAT006', 'OFFICE_SUPPLIES', 100, 5000.00, 950.00, 5950.00, 'EUR', 'P001', 'SL02');
INSERT INTO PurchaseOrderItem VALUES ('4500000008', '00010', 'MAT004', 'SOFTWARE', 30, 75000.00, 14250.00, 89250.00, 'EUR', 'P002', 'SL02');
INSERT INTO PurchaseOrderItem VALUES ('4500000009', '00010', 'MAT007', 'SERVICES', 1, 95000.00, 18050.00, 113050.00, 'EUR', 'P001', 'SL04');
INSERT INTO PurchaseOrderItem VALUES ('4500000010', '00010', 'MAT002', 'ELECTRONICS', 25, 40000.00, 7600.00, 47600.00, 'EUR', 'P002', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000011', '00010', 'MAT008', 'CONSULTING', 1, 185000.00, 35150.00, 220150.00, 'EUR', 'P001', 'SL04');
INSERT INTO PurchaseOrderItem VALUES ('4500000012', '00010', 'MAT003', 'COMPUTERS', 18, 40500.00, 7695.00, 48195.00, 'EUR', 'P002', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000013', '00010', 'MAT001', 'ELECTRONICS', 30, 45000.00, 8550.00, 53550.00, 'EUR', 'P001', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000014', '00010', 'MAT005', 'FURNITURE', 6, 9000.00, 1710.00, 10710.00, 'EUR', 'P002', 'SL03');
INSERT INTO PurchaseOrderItem VALUES ('4500000015', '00010', 'MAT004', 'SOFTWARE', 40, 100000.00, 19000.00, 119000.00, 'EUR', 'P001', 'SL02');
INSERT INTO PurchaseOrderItem VALUES ('4500000016', '00010', 'MAT006', 'OFFICE_SUPPLIES', 200, 10000.00, 1900.00, 11900.00, 'USD', 'P003', 'SL02');
INSERT INTO PurchaseOrderItem VALUES ('4500000017', '00010', 'MAT007', 'SERVICES', 1, 120000.00, 22800.00, 142800.00, 'USD', 'P003', 'SL04');
INSERT INTO PurchaseOrderItem VALUES ('4500000018', '00010', 'MAT002', 'ELECTRONICS', 8, 12800.00, 2432.00, 15232.00, 'EUR', 'P001', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000019', '00010', 'MAT003', 'COMPUTERS', 5, 11250.00, 2137.50, 13387.50, 'EUR', 'P002', 'SL01');
INSERT INTO PurchaseOrderItem VALUES ('4500000020', '00010', 'MAT008', 'CONSULTING', 1, 220000.00, 41800.00, 261800.00, 'EUR', 'P001', 'SL04');

-- Schedule Lines (delivery tracking)
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000001', '00010', '0001', '2026-01-20', 10, '2026-01-20', 'ON_TIME');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000001', '00020', '0001', '2026-01-20', 5, '2026-01-22', 'DELAYED');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000002', '00010', '0001', '2026-01-22', 20, '2026-01-21', 'EARLY');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000003', '00010', '0001', '2026-01-25', 50, '2026-01-24', 'ON_TIME');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000004', '00010', '0001', '2026-01-28', 15, NULL, 'PENDING');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000005', '00010', '0001', '2026-01-30', 8, '2026-02-05', 'DELAYED');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000006', '00010', '0001', '2026-02-01', 12, '2026-02-01', 'ON_TIME');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000007', '00010', '0001', '2026-02-05', 100, NULL, 'PENDING');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000008', '00010', '0001', '2026-02-07', 30, NULL, 'PENDING');
INSERT INTO PurchaseOrderScheduleLine VALUES ('4500000009', '00010', '0001', '2026-02-08', 1, '2026-02-07', 'ON_TIME');

-- 30 Supplier Invoices (covering multiple months)
INSERT INTO SupplierInvoice VALUES ('5100000001', '2026', '0000100001', '1000', '2026-01-15', '2026-01-16', 17850.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000002', '2026', '0000100001', '1000', '2026-01-15', '2026-01-16', 9520.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000003', '2026', '0000100002', '1000', '2026-01-17', '2026-01-18', 53550.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000004', '2026', '0000100003', '1000', '2026-01-20', '2026-01-21', 148750.00, 'EUR', 'Z002', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000005', '2026', '0000100001', '1000', '2026-01-23', '2026-01-24', 26775.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000006', '2026', '0000100004', '1000', '2026-01-25', '2026-01-26', 14280.00, 'EUR', 'Z003', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000007', '2026', '0000100005', '1000', '2026-01-27', '2026-01-28', 32130.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000008', '2026', '0000100002', '1000', '2026-01-30', '2026-01-31', 5950.00, 'EUR', 'Z002', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000009', '2026', '0000100006', '1000', '2026-02-01', '2026-02-02', 89250.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000010', '2026', '0000100007', '1000', '2026-02-03', '2026-02-04', 113050.00, 'EUR', 'Z003', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000011', '2026', '0000100003', '1000', '2026-02-04', '2026-02-05', 47600.00, 'EUR', 'Z001', 'PENDING', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000012', '2026', '0000100008', '1000', '2026-02-05', '2026-02-06', 220150.00, 'EUR', 'Z001', 'PENDING', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000013', '2026', '0000100001', '1000', '2026-02-06', '2026-02-07', 48195.00, 'EUR', 'Z002', 'PENDING', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000014', '2026', '0000100004', '1000', '2026-02-07', '2026-02-08', 53550.00, 'EUR', 'Z001', 'PENDING', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000015', '2026', '0000100005', '1000', '2026-01-14', '2026-01-15', 10710.00, 'EUR', 'Z003', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000016', '2026', '0000100010', '1000', '2026-01-16', '2026-01-17', 119000.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000017', '2026', '0000100006', '2000', '2025-12-20', '2025-12-21', 11900.00, 'USD', 'Z002', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000018', '2025', '0000100007', '2000', '2025-12-28', '2025-12-29', 142800.00, 'USD', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000019', '2025', '0000100002', '1000', '2025-11-15', '2025-11-16', 15232.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000020', '2025', '0000100003', '1000', '2025-11-30', '2025-12-01', 13387.50, 'EUR', 'Z002', 'REVERSED', 1, 'DUPLICATE');
INSERT INTO SupplierInvoice VALUES ('5100000021', '2026', '0000100001', '1000', '2026-01-08', '2026-01-09', 261800.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000022', '2026', '0000100002', '1000', '2026-01-10', '2026-01-11', 65000.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000023', '2026', '0000100003', '1000', '2026-01-12', '2026-01-13', 89500.00, 'EUR', 'Z002', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000024', '2026', '0000100004', '1000', '2026-01-14', '2026-01-15', 42000.00, 'EUR', 'Z003', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000025', '2026', '0000100005', '1000', '2026-01-16', '2026-01-17', 78500.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000026', '2026', '0000100006', '1000', '2026-01-18', '2026-01-19', 34200.00, 'EUR', 'Z002', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000027', '2026', '0000100007', '1000', '2026-01-20', '2026-01-21', 156000.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000028', '2026', '0000100008', '1000', '2026-01-22', '2026-01-23', 92300.00, 'EUR', 'Z003', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000029', '2026', '0000100001', '1000', '2026-01-24', '2026-01-25', 68700.00, 'EUR', 'Z001', 'POSTED', 0, NULL);
INSERT INTO SupplierInvoice VALUES ('5100000030', '2026', '0000100010', '1000', '2026-01-26', '2026-01-27', 105000.00, 'EUR', 'Z002', 'PENDING', 0, NULL);

-- Supplier Invoice Items (link invoices to POs)
INSERT INTO SupplierInvoiceItem VALUES ('5100000001', '2026', '00010', '4500000001', '00010', 'V1', 'EUR', 17850.00, 10, 'EA');
INSERT INTO SupplierInvoiceItem VALUES ('5100000002', '2026', '00010', '4500000001', '00020', 'V1', 'EUR', 9520.00, 5, 'EA');
INSERT INTO SupplierInvoiceItem VALUES ('5100000003', '2026', '00010', '4500000002', '00010', 'V1', 'EUR', 53550.00, 20, 'EA');
INSERT INTO SupplierInvoiceItem VALUES ('5100000004', '2026', '00010', '4500000003', '00010', 'V1', 'EUR', 148750.00, 50, 'LIC');
INSERT INTO SupplierInvoiceItem VALUES ('5100000005', '2026', '00010', '4500000004', '00010', 'V1', 'EUR', 26775.00, 15, 'EA');
INSERT INTO SupplierInvoiceItem VALUES ('5100000006', '2026', '00010', '4500000005', '00010', 'V1', 'EUR', 14280.00, 8, 'EA');
INSERT INTO SupplierInvoiceItem VALUES ('5100000007', '2026', '00010', '4500000006', '00010', 'V1', 'EUR', 32130.00, 12, 'EA');
INSERT INTO SupplierInvoiceItem VALUES ('5100000008', '2026', '00010', '4500000007', '00010', 'V1', 'EUR', 5950.00, 100, 'EA');
INSERT INTO SupplierInvoiceItem VALUES ('5100000009', '2026', '00010', '4500000008', '00010', 'V1', 'EUR', 89250.00, 30, 'LIC');
INSERT INTO SupplierInvoiceItem VALUES ('5100000010', '2026', '00010', '4500000009', '00010', 'V1', 'EUR', 113050.00, 1, 'SRV');

-- 5 Service Entry Sheets
INSERT INTO ServiceEntrySheet VALUES ('0100000001', '4500000009', '2026-02-02', 'EXT-001', '0000100007', 'APPROVED', '2026-02-03');
INSERT INTO ServiceEntrySheet VALUES ('0100000002', '4500000011', '2026-02-04', 'EXT-002', '0000100008', 'APPROVED', '2026-02-05');
INSERT INTO ServiceEntrySheet VALUES ('0100000003', '4500000020', '2025-10-15', 'EXT-003', '0000100001', 'APPROVED', '2025-10-16');
INSERT INTO ServiceEntrySheet VALUES ('0100000004', '4500000008', '2026-02-01', 'EXT-004', '0000100006', 'PENDING', NULL);
INSERT INTO ServiceEntrySheet VALUES ('0100000005', '4500000017', '2025-12-29', 'EXT-005', '0000100007', 'APPROVED', '2025-12-30');

-- Service Entry Sheet Items
INSERT INTO ServiceEntrySheetItem VALUES ('0100000001', '00010', '4500000009', '00010', 1, 95000.00, 'EUR');
INSERT INTO ServiceEntrySheetItem VALUES ('0100000002', '00010', '4500000011', '00010', 1, 185000.00, 'EUR');
INSERT INTO ServiceEntrySheetItem VALUES ('0100000003', '00010', '4500000020', '00010', 1, 220000.00, 'EUR');
INSERT INTO ServiceEntrySheetItem VALUES ('0100000004', '00010', '4500000008', '00010', 0.5, 37500.00, 'EUR');
INSERT INTO ServiceEntrySheetItem VALUES ('0100000005', '00010', '4500000017', '00010', 1, 120000.00, 'USD');

-- =============================================================================
-- SUMMARY STATISTICS
-- =============================================================================
-- Suppliers: 10 (9 active, 1 blocked)
-- Purchase Orders: 20 (5 completed, 14 in progress, 1 cancelled)
-- Invoices: 30 (26 posted, 4 pending, 1 reversed) ← 10+ as requested
-- Service Sheets: 5 (4 approved, 1 pending)
-- Total PO Value: €1,248,250 + $154,700 (€1.4M equivalent)
-- Total Invoice Value: €1,839,504.50
-- =============================================================================