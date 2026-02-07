"""
Unit Tests for P2P Dashboard KPI Service
=========================================
Tests the KPI calculation logic with mocked database connections.

Following Gu Wu Testing Standards:
- AAA pattern (Arrange, Act, Assert)
- Fast execution (mocked DB)
- 100% coverage of business logic
- Parameterized tests for multiple scenarios

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

from modules.p2p_dashboard.backend.kpi_service import KPIService
from modules.p2p_dashboard.backend.aggregations import get_period_dates


@pytest.mark.unit
@pytest.mark.fast
class TestKPIService:
    """Test suite for KPIService class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection."""
        db = Mock()
        cursor = Mock()
        db.cursor.return_value = cursor
        return db, cursor
    
    @pytest.fixture
    def kpi_service(self, mock_db):
        """Create KPIService instance with mocked DB."""
        db, _ = mock_db
        return KPIService(db)
    
    # ========================================================================
    # Period Date Calculation Tests
    # ========================================================================
    
    def test_get_period_dates_last_7_days(self):
        """Test period calculation for last 7 days."""
        # ARRANGE
        period = 'last_7_days'
        
        # ACT
        start_date, end_date = get_period_dates(period)
        
        # ASSERT
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        delta = (end - start).days
        assert delta == 7, "Should calculate 7-day period"
    
    def test_get_period_dates_last_30_days(self):
        """Test period calculation for last 30 days."""
        # ARRANGE
        period = 'last_30_days'
        
        # ACT
        start_date, end_date = get_period_dates(period)
        
        # ASSERT
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        delta = (end - start).days
        assert delta == 30, "Should calculate 30-day period"
    
    def test_get_period_dates_ytd(self):
        """Test period calculation for year-to-date."""
        # ARRANGE
        period = 'ytd'
        
        # ACT
        start_date, end_date = get_period_dates(period)
        
        # ASSERT
        start = datetime.fromisoformat(start_date)
        today = datetime.now().date()
        assert start.month == 1 and start.day == 1, "Should start at Jan 1"
        assert start.year == today.year, "Should be current year"
    
    # ========================================================================
    # PO Metrics Tests
    # ========================================================================
    
    def test_get_po_metrics_success(self, kpi_service, mock_db):
        """Test successful PO metrics calculation with mock database."""
        # ARRANGE
        db, cursor = mock_db
        
        # Set up mock to return data for all three queries in sequence
        cursor.description = [('value',)]  # Generic description
        cursor.fetchall.side_effect = [
            # Query 1: po_summary - returns dict-like tuple
            [(150, 2400000.50, 16000.00, 120, 5)],
            # Query 2: po_late - returns dict-like tuple  
            [(10, 89000.00)],
            # Query 3: po_processing_time - returns single value
            [(3.5,)]
        ]
        
        # Mock description to match query results
        def get_description():
            call_count = cursor.execute.call_count
            if call_count == 1:
                return [('po_count',), ('total_value',), ('avg_value',), ('completed_count',), ('cancelled_count',)]
            elif call_count == 2:
                return [('late_po_count',), ('late_po_value',)]
            else:
                return [('avg_processing_days',)]
        
        type(cursor).description = property(lambda self: get_description())
        
        params = {
            'start_date': '2026-01-07',
            'end_date': '2026-02-07',
            'current_date': '2026-02-07',
            'company_code': None,
            'limit': 10
        }
        
        # ACT
        result = kpi_service.get_po_metrics(params)
        
        # ASSERT
        assert result['po_count'] == 150
        assert result['total_value'] == 2400000.50
        assert result['avg_value'] == 16000.00
        assert result['completed_count'] == 120
        assert result['late_po_count'] == 10
        assert result['avg_processing_days'] == 3.5
    
    def test_get_po_metrics_no_data(self, kpi_service, mock_db):
        """Test PO metrics when no data available."""
        # ARRANGE
        _, cursor = mock_db
        cursor.description = [('po_count',)]
        cursor.fetchall.return_value = []
        
        params = {'start_date': '2026-01-01', 'end_date': '2026-01-01'}
        
        # ACT
        result = kpi_service.get_po_metrics(params)
        
        # ASSERT
        assert result['po_count'] == 0
        assert result['total_value'] == 0
        assert result['avg_value'] == 0
    
    # ========================================================================
    # Supplier Metrics Tests
    # ========================================================================
    
    def test_get_supplier_metrics_success(self, kpi_service, mock_db):
        """Test successful supplier metrics calculation."""
        # ARRANGE
        db, cursor = mock_db
        
        def mock_execute_side_effect(query, params):
            if 'active_supplier_count' in query:
                cursor.description = [('active_supplier_count',)]
                cursor.fetchall.return_value = [(156,)]
            elif 'total_spend' in query or 'ORDER BY total_spend' in query:
                cursor.description = [('Supplier',), ('SupplierName',), ('total_spend',), ('po_count',)]
                cursor.fetchall.return_value = [
                    ('SUP001', 'Supplier A', 500000, 50),
                    ('SUP002', 'Supplier B', 400000, 40)
                ]
            elif 'blocked_supplier_count' in query:
                cursor.description = [('blocked_supplier_count',)]
                cursor.fetchall.return_value = [(5,)]
            elif 'on_time_rate' in query:
                cursor.description = [('Supplier',), ('SupplierName',), ('total_deliveries',), ('on_time_deliveries',), ('on_time_rate',)]
                cursor.fetchall.return_value = [('SUP001', 'Supplier A', 100, 95, 95.0)]
        
        cursor.execute = Mock(side_effect=mock_execute_side_effect)
        
        params = {'start_date': '2026-01-07', 'end_date': '2026-02-07', 'limit': 10}
        
        # ACT
        result = kpi_service.get_supplier_metrics(params)
        
        # ASSERT
        assert result['active_count'] == 156
        assert result['blocked_count'] == 5
        assert len(result['top_suppliers']) == 2
        assert result['top_suppliers'][0]['total_spend'] == 500000
    
    # ========================================================================
    # Invoice Metrics Tests
    # ========================================================================
    
    def test_get_invoice_metrics_success(self, kpi_service, mock_db):
        """Test successful invoice metrics calculation."""
        # ARRANGE
        db, cursor = mock_db
        
        def mock_execute_side_effect(query, params):
            if 'invoice_count' in query and 'pending_count' in query:
                cursor.description = [
                    ('invoice_count',), ('total_value',),
                    ('pending_count',), ('pending_value',)
                ]
                cursor.fetchall.return_value = [(250, 1800000.00, 42, 120000.00)]
            elif 'accuracy_rate' in query:
                cursor.description = [('total_invoices',), ('accurate_invoices',), ('accuracy_rate',)]
                cursor.fetchall.return_value = [(100, 95, 95.0)]
            elif 'avg_processing_days' in query and 'SupplierInvoice' in query:
                cursor.description = [('avg_processing_days',)]
                cursor.fetchall.return_value = [(2.5,)]
        
        cursor.execute = Mock(side_effect=mock_execute_side_effect)
        
        params = {'start_date': '2026-01-07', 'end_date': '2026-02-07'}
        
        # ACT
        result = kpi_service.get_invoice_metrics(params)
        
        # ASSERT
        assert result['invoice_count'] == 250
        assert result['total_value'] == 1800000.00
        assert result['pending_count'] == 42
        assert result['accuracy_rate'] == 95.0
        assert result['avg_processing_days'] == 2.5
    
    # ========================================================================
    # Financial Metrics Tests
    # ========================================================================
    
    def test_get_financial_metrics_success(self, kpi_service, mock_db):
        """Test successful financial metrics calculation."""
        # ARRANGE
        _, cursor = mock_db
        cursor.description = [('cash_tied_in_pos',)]
        cursor.fetchall.side_effect = [
            [(850000.00,)],  # cash_in_pos
            [  # spend_by_category
                ('MAT001', 300000, 30),
                ('MAT002', 200000, 20)
            ],
            [  # payment_terms_distribution
                ('Z001', 'Net 30', 100, 500000),
                ('Z002', 'Net 60', 50, 300000)
            ]
        ]
        
        params = {'start_date': '2026-01-07', 'end_date': '2026-02-07', 'limit': 10}
        
        # ACT
        result = kpi_service.get_financial_metrics(params)
        
        # ASSERT
        assert result['cash_tied_in_pos'] == 850000.00
        assert len(result['spend_by_category']) == 2
        assert len(result['payment_terms_distribution']) == 2
    
    # ========================================================================
    # Service Sheet Metrics Tests
    # ========================================================================
    
    def test_get_service_sheet_metrics_success(self, kpi_service, mock_db):
        """Test successful service sheet metrics calculation."""
        # ARRANGE
        db, cursor = mock_db
        
        def mock_execute_side_effect(query, params):
            if 'sheet_count' in query:
                cursor.description = [
                    ('sheet_count',), ('total_value',),
                    ('pending_count',), ('pending_value',)
                ]
                cursor.fetchall.return_value = [(80, 400000.00, 15, 75000.00)]
            elif 'avg_approval_days' in query:
                cursor.description = [('avg_approval_days',)]
                cursor.fetchall.return_value = [(1.8,)]
        
        cursor.execute = Mock(side_effect=mock_execute_side_effect)
        
        params = {'start_date': '2026-01-07', 'end_date': '2026-02-07'}
        
        # ACT
        result = kpi_service.get_service_sheet_metrics(params)
        
        # ASSERT
        assert result['sheet_count'] == 80
        assert result['total_value'] == 400000.00
        assert result['pending_count'] == 15
        assert result['avg_approval_days'] == 1.8
    
    # ========================================================================
    # Integration Tests (All KPIs)
    # ========================================================================
    
    def test_get_all_kpis_success(self, kpi_service, mock_db):
        """Test successful retrieval of all KPIs."""
        # ARRANGE
        _, cursor = mock_db
        cursor.description = [('value',)]
        cursor.fetchall.return_value = [(0,)]  # Simple mock for all queries
        
        # ACT
        result = kpi_service.get_all_kpis(period='last_30_days', company_code='1000')
        
        # ASSERT
        assert 'period' in result
        assert 'period_dates' in result
        assert 'timestamp' in result
        assert 'kpis' in result
        assert 'purchase_orders' in result['kpis']
        assert 'suppliers' in result['kpis']
        assert 'invoices' in result['kpis']
        assert 'financial' in result['kpis']
        assert 'service_sheets' in result['kpis']
        assert 'execution_time_seconds' in result
    
    # ========================================================================
    # Trend Data Tests
    # ========================================================================
    
    def test_get_trend_data_po(self, kpi_service, mock_db):
        """Test PO trend data retrieval."""
        # ARRANGE
        db, cursor = mock_db
        cursor.description = [('date',), ('po_count',), ('total_value',)]
        cursor.fetchall.return_value = [
            ('2026-02-01', 10, 100000),
            ('2026-02-02', 12, 120000),
            ('2026-02-03', 8, 80000)
        ]
        
        # ACT
        result = kpi_service.get_trend_data('po', 'last_90_days')
        
        # ASSERT
        assert result['metric'] == 'po'
        assert len(result['data']) == 3
        assert result['data'][0]['po_count'] == 10  # Dict access, not tuple
    
    # ========================================================================
    # Recent Transactions Tests
    # ========================================================================
    
    def test_get_recent_transactions_pos(self, kpi_service, mock_db):
        """Test recent PO transactions retrieval."""
        # ARRANGE
        _, cursor = mock_db
        cursor.description = [
            ('PurchaseOrder',), ('Supplier',), ('total_value',), ('status',)
        ]
        cursor.fetchall.return_value = [
            ('PO001', 'SUP001', 15000, 'In Progress'),
            ('PO002', 'SUP002', 25000, 'Completed')
        ]
        
        # ACT
        result = kpi_service.get_recent_transactions('pos', limit=20)
        
        # ASSERT
        assert result['transaction_type'] == 'pos'
        assert result['count'] == 2
        assert len(result['transactions']) == 2
    
    # ========================================================================
    # Error Handling Tests
    # ========================================================================
    
    def test_execute_query_invalid_query_name(self, kpi_service):
        """Test error handling for invalid query name."""
        # ARRANGE
        params = {}
        
        # ACT
        result = kpi_service._execute_query('invalid_query', params)
        
        # ASSERT
        assert result is None
    
    def test_get_po_metrics_db_error(self, kpi_service, mock_db):
        """Test error handling when database query fails."""
        # ARRANGE
        db, cursor = mock_db
        cursor.execute.side_effect = Exception("Database error")
        
        params = {'start_date': '2026-01-07', 'end_date': '2026-02-07'}
        
        # ACT
        result = kpi_service.get_po_metrics(params)
        
        # ASSERT
        # Service returns zeroed metrics on error (graceful degradation)
        assert result['po_count'] == 0
        assert result['total_value'] == 0


@pytest.mark.unit
@pytest.mark.fast
class TestAggregations:
    """Test suite for aggregation helper functions."""
    
    def test_get_period_dates_default_to_30_days(self):
        """Test default period calculation."""
        # ARRANGE
        period = 'unknown_period'
        
        # ACT
        start_date, end_date = get_period_dates(period)
        
        # ASSERT
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        delta = (end - start).days
        assert delta == 30, "Should default to 30 days for unknown period"