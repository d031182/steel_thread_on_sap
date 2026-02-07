"""
P2P Dashboard Backend Package
==============================
Flask blueprint for P2P Dashboard REST API.

REFERENCE IMPLEMENTATION: First module using Repository Pattern v3.0.0

Exports:
    p2p_dashboard_api: Flask Blueprint for dashboard endpoints
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import traceback
from typing import Optional

from core.repositories import AbstractRepository
from .kpi_service import KPIService

# Create blueprint
p2p_dashboard_api = Blueprint('p2p_dashboard', __name__)

# Logger
logger = logging.getLogger(__name__)


def get_kpi_service() -> KPIService:
    """
    Get KPI service instance with Repository Pattern (Industry Standard DDD).
    
    Returns:
        KPIService instance
    
    Raises:
        RuntimeError: If Repository not available
    
    Architecture (Repository Pattern):
        P2P Dashboard -> AbstractRepository Interface -> Private Implementation
        
        Benefits:
        - Module has ZERO knowledge of SQLite/HANA specifics
        - Repository encapsulates connection management
        - Easy to test (mock AbstractRepository)
        - Multi-backend support (config-driven)
    
    REFERENCE IMPLEMENTATION: Shows correct Repository Pattern usage:
    - Access via current_app.sqlite_repository (injected by app.py)
    - Type hint: AbstractRepository (interface, not implementation)
    - No direct import of _SqliteRepository (encapsulation)
    """
    # Get Repository interface from app context (injected by app.py)
    # Note: Using new 'repository' terminology (industry standard)
    if hasattr(current_app, 'sqlite_repository'):
        repository = current_app.sqlite_repository
    elif hasattr(current_app, 'sqlite_data_source'):
        # Backward compatibility during migration
        repository = current_app.sqlite_data_source
        logger.warning("Using deprecated 'sqlite_data_source' - update to 'sqlite_repository'")
    else:
        raise RuntimeError("Repository not configured")
    
    # Pass Repository interface to KPIService
    # Repository Pattern: Service has NO knowledge of SQLite/HANA/connections
    return KPIService(repository)


@p2p_dashboard_api.route('/kpis', methods=['GET'])
def get_all_kpis():
    """
    Get all KPIs for the dashboard.
    
    Query Parameters:
        period: Time period ('last_7_days', 'last_30_days', 'last_90_days', 'ytd')
        company_code: Filter by company code (optional)
    
    Returns:
        JSON with all KPI categories
    """
    try:
        period = request.args.get('period', 'last_30_days')
        company_code = request.args.get('company_code')
        
        logger.info(f"[P2P Dashboard] Getting all KPIs: period={period}, company_code={company_code}")
        
        kpi_service = get_kpi_service()
        kpis = kpi_service.get_all_kpis(period=period, company_code=company_code)
        
        return jsonify({
            'success': True,
            'data': kpis
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_kpis: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@p2p_dashboard_api.route('/kpis/purchase-orders', methods=['GET'])
def get_po_kpis():
    """
    Get detailed Purchase Order KPIs.
    
    Query Parameters:
        period: Time period
        company_code: Filter by company code (optional)
    
    Returns:
        JSON with PO metrics
    """
    try:
        period = request.args.get('period', 'last_30_days')
        company_code = request.args.get('company_code')
        
        logger.info(f"[P2P Dashboard] Getting PO KPIs: period={period}")
        
        kpi_service = get_kpi_service()
        all_kpis = kpi_service.get_all_kpis(period=period, company_code=company_code)
        
        return jsonify({
            'success': True,
            'data': {
                'period': all_kpis['period'],
                'period_dates': all_kpis['period_dates'],
                'kpis': all_kpis['kpis']['purchase_orders']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_po_kpis: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@p2p_dashboard_api.route('/kpis/suppliers', methods=['GET'])
def get_supplier_kpis():
    """
    Get Supplier Performance KPIs.
    
    Query Parameters:
        period: Time period
        company_code: Filter by company code (optional)
    
    Returns:
        JSON with supplier metrics
    """
    try:
        period = request.args.get('period', 'last_30_days')
        company_code = request.args.get('company_code')
        
        logger.info(f"[P2P Dashboard] Getting Supplier KPIs: period={period}")
        
        kpi_service = get_kpi_service()
        all_kpis = kpi_service.get_all_kpis(period=period, company_code=company_code)
        
        return jsonify({
            'success': True,
            'data': {
                'period': all_kpis['period'],
                'period_dates': all_kpis['period_dates'],
                'kpis': all_kpis['kpis']['suppliers']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_supplier_kpis: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@p2p_dashboard_api.route('/kpis/invoices', methods=['GET'])
def get_invoice_kpis():
    """
    Get Invoice Processing KPIs.
    
    Query Parameters:
        period: Time period
        company_code: Filter by company code (optional)
    
    Returns:
        JSON with invoice metrics
    """
    try:
        period = request.args.get('period', 'last_30_days')
        company_code = request.args.get('company_code')
        
        logger.info(f"[P2P Dashboard] Getting Invoice KPIs: period={period}")
        
        kpi_service = get_kpi_service()
        all_kpis = kpi_service.get_all_kpis(period=period, company_code=company_code)
        
        return jsonify({
            'success': True,
            'data': {
                'period': all_kpis['period'],
                'period_dates': all_kpis['period_dates'],
                'kpis': all_kpis['kpis']['invoices']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_invoice_kpis: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@p2p_dashboard_api.route('/trends/<metric>', methods=['GET'])
def get_trend_data(metric: str):
    """
    Get trend data for a specific metric.
    
    Path Parameters:
        metric: 'po' or 'invoice'
    
    Query Parameters:
        period: Time period (default: 'last_90_days')
        company_code: Filter by company code (optional)
    
    Returns:
        JSON with time-series trend data
    """
    try:
        if metric not in ['po', 'invoice']:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Invalid metric. Use "po" or "invoice"',
                    'code': 'INVALID_METRIC'
                }
            }), 400
        
        period = request.args.get('period', 'last_90_days')
        company_code = request.args.get('company_code')
        
        logger.info(f"[P2P Dashboard] Getting trend data: metric={metric}, period={period}")
        
        kpi_service = get_kpi_service()
        trend_data = kpi_service.get_trend_data(
            metric=metric,
            period=period,
            company_code=company_code
        )
        
        return jsonify({
            'success': True,
            'data': trend_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_trend_data: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@p2p_dashboard_api.route('/transactions/recent', methods=['GET'])
def get_recent_transactions():
    """
    Get recent transactions for display.
    
    Query Parameters:
        type: Transaction type ('pos')
        limit: Number of transactions (default: 20, max: 100)
        company_code: Filter by company code (optional)
    
    Returns:
        JSON with recent transactions
    """
    try:
        transaction_type = request.args.get('type', 'pos')
        limit = min(int(request.args.get('limit', 20)), 100)
        company_code = request.args.get('company_code')
        
        logger.info(f"[P2P Dashboard] Getting recent transactions: type={transaction_type}, limit={limit}")
        
        kpi_service = get_kpi_service()
        transactions = kpi_service.get_recent_transactions(
            transaction_type=transaction_type,
            limit=limit,
            company_code=company_code
        )
        
        return jsonify({
            'success': True,
            'data': transactions
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': {
                'message': 'Invalid limit parameter',
                'code': 'INVALID_PARAMETER'
            }
        }), 400
    except Exception as e:
        logger.error(f"Error in get_recent_transactions: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@p2p_dashboard_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'module': 'p2p_dashboard',
        'version': '2.0.0',
        'architecture': 'Repository Pattern (v3.0.0)'
    })