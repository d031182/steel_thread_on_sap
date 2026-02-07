"""
P2P Dashboard SQL Aggregations
================================
Parameterized SQL queries for KPI calculations.

CRITICAL: All queries use parameterized placeholders (:param_name) 
to prevent SQL injection vulnerabilities.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Tuple


def get_period_dates(period: str) -> Tuple[str, str]:
    """
    Calculate start and end dates for a given period.
    
    Args:
        period: One of 'last_7_days', 'last_30_days', 'last_90_days', 'ytd', 'custom'
    
    Returns:
        Tuple of (start_date, end_date) in ISO format
    """
    today = datetime.now().date()
    
    if period == 'last_7_days':
        start_date = today - timedelta(days=7)
    elif period == 'last_30_days':
        start_date = today - timedelta(days=30)
    elif period == 'last_90_days':
        start_date = today - timedelta(days=90)
    elif period == 'ytd':
        start_date = datetime(today.year, 1, 1).date()
    else:  # Default to last 30 days
        start_date = today - timedelta(days=30)
    
    return start_date.isoformat(), today.isoformat()


# ============================================================================
# Purchase Order Metrics
# ============================================================================

QUERY_PO_SUMMARY = """
SELECT 
    COUNT(DISTINCT poi.PurchaseOrder) as po_count,
    SUM(poi.NetAmount) as total_value,
    AVG(poi.NetAmount) as avg_value,
    COUNT(DISTINCT CASE WHEN poi.IsCompletelyDelivered = 1 THEN poi.PurchaseOrder END) as completed_count,
    COUNT(DISTINCT CASE WHEN poi.PurchasingDocumentDeletionCode IS NOT NULL THEN poi.PurchaseOrder END) as cancelled_count
FROM PurchaseOrderItem poi
WHERE poi.CreationDate >= :start_date
  AND poi.CreationDate <= :end_date
  AND (:company_code IS NULL OR poi.CompanyCode = :company_code)
"""

QUERY_PO_LATE = """
SELECT 
    COUNT(DISTINCT pol.PurchaseOrder) as late_po_count,
    SUM(poi.NetAmount) as late_po_value
FROM PurchaseOrderScheduleLine pol
JOIN PurchaseOrderItem poi ON pol.PurchaseOrder = poi.PurchaseOrder 
    AND pol.PurchaseOrderItem = poi.PurchaseOrderItem
WHERE pol.ScheduleLineDeliveryDate < :current_date
  AND pol.IsCompletelyDelivered = 0
  AND (:company_code IS NULL OR poi.CompanyCode = :company_code)
"""

QUERY_PO_PROCESSING_TIME = """
SELECT 
    AVG(JULIANDAY(po.LastChangeDateTime) - JULIANDAY(po.CreationDate)) as avg_processing_days
FROM PurchaseOrder po
WHERE po.CreationDate >= :start_date
  AND po.CreationDate <= :end_date
  AND (:company_code IS NULL OR po.CompanyCode = :company_code)
"""


# ============================================================================
# Supplier Performance Metrics
# ============================================================================

QUERY_ACTIVE_SUPPLIERS = """
SELECT 
    COUNT(DISTINCT s.Supplier) as active_supplier_count
FROM Supplier s
JOIN PurchaseOrder po ON po.Supplier = s.Supplier
WHERE po.PurchaseOrderDate >= :start_date
  AND po.PurchaseOrderDate <= :end_date
  AND (:company_code IS NULL OR po.CompanyCode = :company_code)
  AND s.PurchasingIsBlocked = 0
"""

QUERY_TOP_SUPPLIERS_BY_SPEND = """
SELECT 
    s.Supplier,
    s.SupplierName,
    SUM(poi.NetAmount) as total_spend,
    COUNT(DISTINCT poi.PurchaseOrder) as po_count
FROM Supplier s
JOIN PurchaseOrder po ON po.Supplier = s.Supplier
JOIN PurchaseOrderItem poi ON poi.PurchaseOrder = po.PurchaseOrder
WHERE po.PurchaseOrderDate >= :start_date
  AND po.PurchaseOrderDate <= :end_date
  AND (:company_code IS NULL OR poi.CompanyCode = :company_code)
GROUP BY s.Supplier, s.SupplierName
ORDER BY total_spend DESC
LIMIT :limit
"""

QUERY_SUPPLIER_BLOCKED = """
SELECT 
    COUNT(DISTINCT s.Supplier) as blocked_supplier_count
FROM Supplier s
WHERE s.PurchasingIsBlocked = 1
"""

QUERY_SUPPLIER_ON_TIME_DELIVERY = """
SELECT 
    s.Supplier,
    s.SupplierName,
    COUNT(*) as total_deliveries,
    SUM(CASE WHEN pol.IsCompletelyDelivered = 1 
             AND pol.ScheduleLineDeliveryDate >= pol.ScheduleLineDeliveryDate 
        THEN 1 ELSE 0 END) as on_time_deliveries,
    CAST(SUM(CASE WHEN pol.IsCompletelyDelivered = 1 
                  AND pol.ScheduleLineDeliveryDate >= pol.ScheduleLineDeliveryDate 
             THEN 1 ELSE 0 END) AS REAL) * 100.0 / COUNT(*) as on_time_rate
FROM Supplier s
JOIN PurchaseOrder po ON po.Supplier = s.Supplier
JOIN PurchaseOrderScheduleLine pol ON pol.PurchaseOrder = po.PurchaseOrder
WHERE pol.ScheduleLineDeliveryDate >= :start_date
  AND pol.ScheduleLineDeliveryDate <= :end_date
  AND (:company_code IS NULL OR po.CompanyCode = :company_code)
GROUP BY s.Supplier, s.SupplierName
HAVING COUNT(*) >= 5
ORDER BY on_time_rate DESC
LIMIT 10
"""


# ============================================================================
# Invoice Processing Metrics
# ============================================================================

QUERY_INVOICE_SUMMARY = """
SELECT 
    COUNT(DISTINCT si.SupplierInvoice) as invoice_count,
    SUM(si.InvoiceGrossAmount) as total_value,
    COUNT(DISTINCT CASE WHEN si.SupplierInvoiceStatus = 'PENDING' THEN si.SupplierInvoice END) as pending_count,
    SUM(CASE WHEN si.SupplierInvoiceStatus = 'PENDING' THEN si.InvoiceGrossAmount ELSE 0 END) as pending_value
FROM SupplierInvoice si
WHERE si.PostingDate >= :start_date
  AND si.PostingDate <= :end_date
  AND (:company_code IS NULL OR si.CompanyCode = :company_code)
"""

QUERY_INVOICE_ACCURACY = """
SELECT 
    COUNT(*) as total_invoices,
    SUM(CASE WHEN sii.SuplrInvcItmHasQualityVariance = 0
             AND sii.SuplrInvcItemHasOrdPrcQtyVarc = 0
             AND sii.SuplrInvcItemHasQtyVariance = 0
             AND sii.SuplrInvcItemHasPriceVariance = 0
             AND sii.SuplrInvcItemHasOtherVariance = 0
        THEN 1 ELSE 0 END) as accurate_invoices,
    CAST(SUM(CASE WHEN sii.SuplrInvcItmHasQualityVariance = 0
                  AND sii.SuplrInvcItemHasOrdPrcQtyVarc = 0
                  AND sii.SuplrInvcItemHasQtyVariance = 0
                  AND sii.SuplrInvcItemHasPriceVariance = 0
                  AND sii.SuplrInvcItemHasOtherVariance = 0
             THEN 1 ELSE 0 END) AS REAL) * 100.0 / COUNT(*) as accuracy_rate
FROM SupplierInvoiceItem sii
WHERE sii.PostingDate >= :start_date
  AND sii.PostingDate <= :end_date
  AND (:company_code IS NULL OR sii.CompanyCode = :company_code)
"""

QUERY_INVOICE_PROCESSING_TIME = """
SELECT 
    AVG(JULIANDAY(si.PostingDate) - JULIANDAY(si.DocumentDate)) as avg_processing_days
FROM SupplierInvoice si
WHERE si.PostingDate >= :start_date
  AND si.PostingDate <= :end_date
  AND (:company_code IS NULL OR si.CompanyCode = :company_code)
"""


# ============================================================================
# Financial Health Metrics
# ============================================================================

QUERY_CASH_IN_POS = """
SELECT 
    SUM(poi.NetAmount) as cash_tied_in_pos
FROM PurchaseOrderItem poi
WHERE poi.IsCompletelyDelivered = 0
  AND poi.IsFinallyInvoiced = 0
  AND (:company_code IS NULL OR poi.CompanyCode = :company_code)
"""

QUERY_SPEND_BY_CATEGORY = """
SELECT 
    poi.MaterialGroup,
    SUM(poi.NetAmount) as total_spend,
    COUNT(DISTINCT poi.PurchaseOrder) as po_count
FROM PurchaseOrderItem poi
WHERE poi.CreationDate >= :start_date
  AND poi.CreationDate <= :end_date
  AND (:company_code IS NULL OR poi.CompanyCode = :company_code)
  AND poi.MaterialGroup IS NOT NULL
GROUP BY poi.MaterialGroup
ORDER BY total_spend DESC
LIMIT :limit
"""

QUERY_PAYMENT_TERMS_DISTRIBUTION = """
SELECT 
    pt.PaymentTerms,
    ptt.PaymentTermsName,
    COUNT(DISTINCT po.PurchaseOrder) as po_count,
    SUM(poi.NetAmount) as total_value
FROM PurchaseOrder po
JOIN PurchaseOrderItem poi ON poi.PurchaseOrder = po.PurchaseOrder
LEFT JOIN PaymentTerms pt ON pt.PaymentTerms = po.PaymentTerms
LEFT JOIN PaymentTermsText ptt ON ptt.PaymentTerms = pt.PaymentTerms AND ptt.Language = 'EN'
WHERE po.PurchaseOrderDate >= :start_date
  AND po.PurchaseOrderDate <= :end_date
  AND (:company_code IS NULL OR po.CompanyCode = :company_code)
GROUP BY pt.PaymentTerms, ptt.PaymentTermsName
ORDER BY total_value DESC
"""


# ============================================================================
# Service Entry Sheet Metrics
# ============================================================================

QUERY_SERVICE_SHEET_SUMMARY = """
SELECT 
    COUNT(DISTINCT ses.ServiceEntrySheet) as sheet_count,
    SUM(sesi.NetAmount) as total_value,
    COUNT(DISTINCT CASE WHEN ses.ApprovalStatus = 'PENDING' THEN ses.ServiceEntrySheet END) as pending_count,
    SUM(CASE WHEN ses.ApprovalStatus = 'PENDING' THEN sesi.NetAmount ELSE 0 END) as pending_value
FROM ServiceEntrySheet ses
JOIN ServiceEntrySheetItem sesi ON sesi.ServiceEntrySheet = ses.ServiceEntrySheet
WHERE ses.CreationDateTime >= :start_date
  AND ses.CreationDateTime <= :end_date
  AND (:company_code IS NULL OR ses.PurchasingOrganization IS NOT NULL)
"""

QUERY_SERVICE_SHEET_APPROVAL_TIME = """
SELECT 
    AVG(JULIANDAY(ses.ApprovalDateTime) - JULIANDAY(ses.CreationDateTime)) as avg_approval_days
FROM ServiceEntrySheet ses
WHERE ses.ApprovalDateTime IS NOT NULL
  AND ses.CreationDateTime >= :start_date
  AND ses.CreationDateTime <= :end_date
  AND (:company_code IS NULL OR ses.PurchasingOrganization IS NOT NULL)
"""


# ============================================================================
# Trending Queries
# ============================================================================

QUERY_PO_TREND_BY_DAY = """
SELECT 
    DATE(poi.CreationDate) as date,
    COUNT(DISTINCT poi.PurchaseOrder) as po_count,
    SUM(poi.NetAmount) as total_value
FROM PurchaseOrderItem poi
WHERE poi.CreationDate >= :start_date
  AND poi.CreationDate <= :end_date
  AND (:company_code IS NULL OR poi.CompanyCode = :company_code)
GROUP BY DATE(poi.CreationDate)
ORDER BY date
"""

QUERY_INVOICE_TREND_BY_DAY = """
SELECT 
    DATE(si.PostingDate) as date,
    COUNT(DISTINCT si.SupplierInvoice) as invoice_count,
    SUM(si.InvoiceGrossAmount) as total_value
FROM SupplierInvoice si
WHERE si.PostingDate >= :start_date
  AND si.PostingDate <= :end_date
  AND (:company_code IS NULL OR si.CompanyCode = :company_code)
GROUP BY DATE(si.PostingDate)
ORDER BY date
"""


# ============================================================================
# Recent Transactions
# ============================================================================

QUERY_RECENT_POS = """
SELECT 
    po.PurchaseOrder,
    po.Supplier,
    s.SupplierName,
    SUM(poi.NetAmount) as total_value,
    po.DocumentCurrency,
    po.PurchaseOrderDate,
    MAX(pol.ScheduleLineDeliveryDate) as due_date,
    CASE 
        WHEN MAX(poi.IsCompletelyDelivered) = 1 THEN 'Completed'
        WHEN MAX(pol.ScheduleLineDeliveryDate) < DATE('now') THEN 'Late'
        ELSE 'In Progress'
    END as status
FROM PurchaseOrder po
JOIN PurchaseOrderItem poi ON poi.PurchaseOrder = po.PurchaseOrder
JOIN PurchaseOrderScheduleLine pol ON pol.PurchaseOrder = po.PurchaseOrder
LEFT JOIN Supplier s ON s.Supplier = po.Supplier
WHERE (:company_code IS NULL OR po.CompanyCode = :company_code)
GROUP BY po.PurchaseOrder, po.Supplier, s.SupplierName, po.DocumentCurrency, po.PurchaseOrderDate
ORDER BY po.PurchaseOrderDate DESC
LIMIT :limit
"""


# ============================================================================
# Query Registry
# ============================================================================

QUERIES = {
    # Purchase Orders
    'po_summary': QUERY_PO_SUMMARY,
    'po_late': QUERY_PO_LATE,
    'po_processing_time': QUERY_PO_PROCESSING_TIME,
    
    # Suppliers
    'active_suppliers': QUERY_ACTIVE_SUPPLIERS,
    'top_suppliers': QUERY_TOP_SUPPLIERS_BY_SPEND,
    'blocked_suppliers': QUERY_SUPPLIER_BLOCKED,
    'supplier_on_time': QUERY_SUPPLIER_ON_TIME_DELIVERY,
    
    # Invoices
    'invoice_summary': QUERY_INVOICE_SUMMARY,
    'invoice_accuracy': QUERY_INVOICE_ACCURACY,
    'invoice_processing_time': QUERY_INVOICE_PROCESSING_TIME,
    
    # Financial
    'cash_in_pos': QUERY_CASH_IN_POS,
    'spend_by_category': QUERY_SPEND_BY_CATEGORY,
    'payment_terms_distribution': QUERY_PAYMENT_TERMS_DISTRIBUTION,
    
    # Service Sheets
    'service_sheet_summary': QUERY_SERVICE_SHEET_SUMMARY,
    'service_sheet_approval_time': QUERY_SERVICE_SHEET_APPROVAL_TIME,
    
    # Trends
    'po_trend': QUERY_PO_TREND_BY_DAY,
    'invoice_trend': QUERY_INVOICE_TREND_BY_DAY,
    
    # Recent Transactions
    'recent_pos': QUERY_RECENT_POS,
}