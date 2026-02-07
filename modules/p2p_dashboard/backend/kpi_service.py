"""
P2P Dashboard KPI Service
==========================
Business logic for KPI calculations using dependency injection.

This service executes parameterized SQL queries and transforms
results into dashboard-ready KPI data structures.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import time

from .aggregations import QUERIES, get_period_dates

logger = logging.getLogger(__name__)


class KPIService:
    """
    Service for calculating P2P dashboard KPIs.
    
    Uses dependency injection with DataSource interface (clean architecture).
    DataSource handles connection management internally via DI.
    All queries use parameterized execution to prevent SQL injection.
    """
    
    def __init__(self, data_source):
        """
        Initialize KPI service with DataSource interface.
        
        Args:
            data_source: DataSource interface (SQLiteDataSource or HANADataSource)
                        DataSource manages connection internally via DI
        """
        self.data_source = data_source
        logger.info("KPIService initialized with DataSource interface")
    
    def _execute_query(self, query_name: str, params: Dict[str, Any]) -> Optional[List[Dict]]:
        """
        Execute a parameterized query safely via DataSource interface.
        
        Args:
            query_name: Name of query from QUERIES registry
            params: Dictionary of named query parameters
        
        Returns:
            Query results as list of dictionaries, or None on error
        
        Note:
            Queries use named placeholders (:param_name). We need to convert
            the SQL to use positional ? placeholders and extract values in order.
        """
        try:
            query = QUERIES.get(query_name)
            if not query:
                logger.error(f"Query not found: {query_name}")
                return None
            
            # Convert named parameters (:param) to positional (?)
            # Extract parameter names from query in order they appear
            import re
            param_pattern = re.compile(r':(\w+)')
            param_names = param_pattern.findall(query)
            
            # Replace named placeholders with ?
            positional_query = param_pattern.sub('?', query)
            
            # Extract values in the order parameters appear in query
            param_values = tuple(params.get(name) for name in param_names)
            
            # Use DataSource.execute_query() - DataSource handles connection via DI
            # This maintains clean architecture: connection modules only accessed by DataSource
            result = self.data_source.execute_query(positional_query, param_values)
            
            if not result.get('success'):
                error = result.get('error', {})
                logger.error(f"Query {query_name} failed: {error.get('message', 'Unknown error')}")
                return None
            
            rows = result.get('rows', [])
            logger.debug(f"Query {query_name} returned {len(rows)} rows")
            return rows
            
        except Exception as e:
            logger.error(f"Error executing query {query_name}: {str(e)}")
            return None
    
    def get_all_kpis(self, period: str = 'last_30_days', 
                     company_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all KPIs for the dashboard.
        
        Args:
            period: Time period ('last_7_days', 'last_30_days', 'last_90_days', 'ytd')
            company_code: Filter by company code (None = all companies)
        
        Returns:
            Dictionary with all KPI categories
        """
        start_time = time.time()
        logger.info(f"Calculating all KPIs for period={period}, company_code={company_code}")
        
        start_date, end_date = get_period_dates(period)
        current_date = datetime.now().date().isoformat()
        
        # Base parameters for queries
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'current_date': current_date,
            'company_code': company_code,
            'limit': 10
        }
        
        # Calculate all KPI categories
        result = {
            'period': period,
            'period_dates': {'start': start_date, 'end': end_date},
            'company_code': company_code,
            'timestamp': datetime.now().isoformat(),
            'kpis': {
                'purchase_orders': self.get_po_metrics(params),
                'suppliers': self.get_supplier_metrics(params),
                'invoices': self.get_invoice_metrics(params),
                'financial': self.get_financial_metrics(params),
                'service_sheets': self.get_service_sheet_metrics(params)
            }
        }
        
        execution_time = time.time() - start_time
        result['execution_time_seconds'] = round(execution_time, 3)
        
        logger.info(f"All KPIs calculated in {execution_time:.3f}s")
        return result
    
    def get_po_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Purchase Order metrics."""
        try:
            # PO Summary
            summary = self._execute_query('po_summary', params)
            po_data = summary[0] if summary else {}
            
            # Late POs
            late_pos = self._execute_query('po_late', params)
            late_data = late_pos[0] if late_pos else {}
            
            # Processing Time
            processing = self._execute_query('po_processing_time', params)
            proc_data = processing[0] if processing else {}
            
            return {
                'total_value': po_data.get('total_value', 0) or 0,
                'po_count': po_data.get('po_count', 0) or 0,
                'avg_value': po_data.get('avg_value', 0) or 0,
                'completed_count': po_data.get('completed_count', 0) or 0,
                'cancelled_count': po_data.get('cancelled_count', 0) or 0,
                'late_po_count': late_data.get('late_po_count', 0) or 0,
                'late_po_value': late_data.get('late_po_value', 0) or 0,
                'avg_processing_days': proc_data.get('avg_processing_days', 0) or 0
            }
        except Exception as e:
            logger.error(f"Error calculating PO metrics: {str(e)}")
            return {}
    
    def get_supplier_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Supplier Performance metrics."""
        try:
            # Active Suppliers
            active = self._execute_query('active_suppliers', params)
            active_data = active[0] if active else {}
            
            # Top Suppliers by Spend
            top_suppliers = self._execute_query('top_suppliers', params) or []
            
            # Blocked Suppliers
            blocked = self._execute_query('blocked_suppliers', {})
            blocked_data = blocked[0] if blocked else {}
            
            # On-Time Delivery
            on_time = self._execute_query('supplier_on_time', params) or []
            
            return {
                'active_count': active_data.get('active_supplier_count', 0) or 0,
                'blocked_count': blocked_data.get('blocked_supplier_count', 0) or 0,
                'top_suppliers': top_suppliers,
                'on_time_delivery': on_time
            }
        except Exception as e:
            logger.error(f"Error calculating supplier metrics: {str(e)}")
            return {}
    
    def get_invoice_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Invoice Processing metrics."""
        try:
            # Invoice Summary
            summary = self._execute_query('invoice_summary', params)
            inv_data = summary[0] if summary else {}
            
            # Invoice Accuracy
            accuracy = self._execute_query('invoice_accuracy', params)
            acc_data = accuracy[0] if accuracy else {}
            
            # Processing Time
            processing = self._execute_query('invoice_processing_time', params)
            proc_data = processing[0] if processing else {}
            
            return {
                'total_value': inv_data.get('total_value', 0) or 0,
                'invoice_count': inv_data.get('invoice_count', 0) or 0,
                'pending_count': inv_data.get('pending_count', 0) or 0,
                'pending_value': inv_data.get('pending_value', 0) or 0,
                'accuracy_rate': acc_data.get('accuracy_rate', 0) or 0,
                'avg_processing_days': proc_data.get('avg_processing_days', 0) or 0
            }
        except Exception as e:
            logger.error(f"Error calculating invoice metrics: {str(e)}")
            return {}
    
    def get_financial_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Financial Health metrics."""
        try:
            # Cash Tied in POs
            cash = self._execute_query('cash_in_pos', params)
            cash_data = cash[0] if cash else {}
            
            # Spend by Category
            spend_cat = self._execute_query('spend_by_category', params) or []
            
            # Payment Terms Distribution
            payment_terms = self._execute_query('payment_terms_distribution', params) or []
            
            return {
                'cash_tied_in_pos': cash_data.get('cash_tied_in_pos', 0) or 0,
                'spend_by_category': spend_cat,
                'payment_terms_distribution': payment_terms
            }
        except Exception as e:
            logger.error(f"Error calculating financial metrics: {str(e)}")
            return {}
    
    def get_service_sheet_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Service Entry Sheet metrics."""
        try:
            # Service Sheet Summary
            summary = self._execute_query('service_sheet_summary', params)
            sheet_data = summary[0] if summary else {}
            
            # Approval Time
            approval = self._execute_query('service_sheet_approval_time', params)
            appr_data = approval[0] if approval else {}
            
            return {
                'sheet_count': sheet_data.get('sheet_count', 0) or 0,
                'total_value': sheet_data.get('total_value', 0) or 0,
                'pending_count': sheet_data.get('pending_count', 0) or 0,
                'pending_value': sheet_data.get('pending_value', 0) or 0,
                'avg_approval_days': appr_data.get('avg_approval_days', 0) or 0
            }
        except Exception as e:
            logger.error(f"Error calculating service sheet metrics: {str(e)}")
            return {}
    
    def get_trend_data(self, metric: str, period: str = 'last_90_days',
                       company_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get time-series trend data for a metric.
        
        Args:
            metric: 'po' or 'invoice'
            period: Time period for trend
            company_code: Filter by company code
        
        Returns:
            Trend data with daily values
        """
        try:
            start_date, end_date = get_period_dates(period)
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'company_code': company_code
            }
            
            query_name = f'{metric}_trend'
            trend_data = self._execute_query(query_name, params) or []
            
            return {
                'metric': metric,
                'period': period,
                'period_dates': {'start': start_date, 'end': end_date},
                'company_code': company_code,
                'data': trend_data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error calculating trend data: {str(e)}")
            return {'data': []}
    
    def get_recent_transactions(self, transaction_type: str = 'pos',
                                 limit: int = 20,
                                 company_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get recent transactions for display.
        
        Args:
            transaction_type: 'pos' (more types can be added)
            limit: Number of transactions to return
            company_code: Filter by company code
        
        Returns:
            Recent transactions list
        """
        try:
            params = {
                'company_code': company_code,
                'limit': limit
            }
            
            if transaction_type == 'pos':
                transactions = self._execute_query('recent_pos', params) or []
            else:
                transactions = []
            
            return {
                'transaction_type': transaction_type,
                'company_code': company_code,
                'transactions': transactions,
                'count': len(transactions),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting recent transactions: {str(e)}")
            return {'transactions': []}