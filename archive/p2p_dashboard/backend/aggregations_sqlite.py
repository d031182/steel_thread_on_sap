"""
P2P Dashboard SQL Aggregations - SQLite Version
================================================
Simplified queries compatible with local SQLite test database schema.

CRITICAL: All queries use parameterized placeholders (:param_name) 
to prevent SQL injection vulnerabilities.

Author: P2P Development Team
Version: 1.0.0 (SQLite)
Date: 2026-02-07
"""

from datetime import datetime, timedelta
from typing import Tuple


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
# Purchase Order Metrics (SQLite Schema)
# ============================================================================

QUERY_PO_SUMMARY = """
SELECT 
    COUNT(DISTINCT po.PurchaseOrder) as po_count,
    SUM(poi.GrossAmount) as total_value,
    AVG(poi.GrossAmount) as avg_value,
    COUNT(DISTINCT CASE WHEN po.IsCompleted = 1 THEN po.PurchaseOrder END) as completed_count,
    COUNT(DISTINCT CASE WHEN po.IsCancelled = 1 THEN po.PurchaseOrder END) as cancelled_count
FROM PurchaseOrder po
JOIN PurchaseOrderItem poi ON poi.PurchaseOrder = po.PurchaseOrder
WHERE po.CreationDate >= :start_date
  AND po.CreationDate <= :end_date
