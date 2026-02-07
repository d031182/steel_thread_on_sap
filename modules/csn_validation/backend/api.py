"""
CSN Validation API Blueprint
============================
Flask blueprint for CSN (Core Schema Notation) validation and retrieval.

Routes:
- GET /api/csn/<schema_name> - Get CSN definition for a data product

This module provides CSN capabilities with:
- CSN URL resolution via ORD ID mapping
- SAP Discovery API integration
- Response caching for performance
- Error handling and validation

Part of: CSN Validation Module
Version: 1.0
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import traceback
import requests
from functools import lru_cache

# Import CSN utilities (from backend directory)
import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

import sys
import os
# Add app directory to path for csn_urls import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app'))
from csn_urls import get_csn_url, schema_name_to_ord_id, get_all_p2p_products

# Create blueprint
csn_validation_api = Blueprint('csn_validation', __name__, url_prefix='/api/csn')

# Logger
logger = logging.getLogger(__name__)


@lru_cache(maxsize=20)
def fetch_csn_from_discovery_api(csn_url):
    """
    Fetch CSN from SAP Discovery API (cached)
    
    Args:
        csn_url: URL to fetch CSN from
    
    Returns:
        CSN data as dict
    
    Raises:
        Exception: If fetch fails
    """
    logger.info(f"[Discovery API] Fetching CSN from: {csn_url}")
    
    try:
        response = requests.get(csn_url, timeout=10)
        response.raise_for_status()
        csn_data = response.json()
        logger.info(f"[Discovery API] CSN fetched ({len(str(csn_data))} bytes)")
        return csn_data
    except requests.exceptions.Timeout:
        logger.error(f"[Discovery API] Timeout")
        raise Exception("Timeout fetching CSN")
    except requests.exceptions.RequestException as e:
        logger.error(f"[Discovery API] HTTP error: {e}")
        raise Exception(f"Failed to fetch CSN: {str(e)}")
    except Exception as e:
        logger.error(f"[Discovery API] Error: {e}")
        raise


@csn_validation_api.route('/<schema_name>', methods=['GET'])
def get_data_product_csn(schema_name):
    """
    Get CSN definition for a data product
    
    Args:
        schema_name: Name of the schema/data product
    
    Returns:
        JSON with CSN definition or error
    """
    try:
        if not schema_name:
            return jsonify({
                'success': False,
                'error': {'message': 'Schema name required', 'code': 'MISSING_SCHEMA_NAME'}
            }), 400
        
        logger.info(f"[CSN] Fetching definition for: {schema_name}")
        
        # Map schema name to ORD ID
        ord_id = schema_name_to_ord_id(schema_name)
        if not ord_id:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'No CSN mapping for: {schema_name}',
                    'code': 'SCHEMA_NOT_MAPPED',
                    'availableProducts': [p['name'] for p in get_all_p2p_products()]
                }
            }), 404
        
        # Get CSN URL from ORD ID
        csn_url = get_csn_url(ord_id)
        if not csn_url:
            return jsonify({
                'success': False,
                'error': {'message': f'No CSN URL for: {ord_id}', 'code': 'CSN_URL_NOT_FOUND'}
            }), 404
        
        # Fetch CSN from Discovery API
        csn_data = fetch_csn_from_discovery_api(csn_url)
        
        return jsonify({
            'success': True,
            'schemaName': schema_name,
            'ordId': ord_id,
            'csnUrl': csn_url,
            'csn': csn_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_data_product_csn: {str(e)}\n{traceback.format_exc()}")
        
        # Get ENV from app config
        env = current_app.config.get('ENV', 'production')
        error_message = str(e) if env == 'development' else 'Internal server error'
        
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@csn_validation_api.route('/products', methods=['GET'])
def list_p2p_products():
    """
    List all available P2P products with CSN mappings
    
    Returns:
        JSON with list of products
    """
    try:
        products = get_all_p2p_products()
        
        return jsonify({
            'success': True,
            'count': len(products),
            'products': products
        })
        
    except Exception as e:
        logger.error(f"Error in list_p2p_products: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'SERVER_ERROR'}
        }), 500


# Health check for this module
@csn_validation_api.route('/health', methods=['GET'])
def health():
    """Module health check"""
    return jsonify({
        'success': True,
        'module': 'csn_validation',
        'status': 'healthy',
        'cache_info': {
            'size': fetch_csn_from_discovery_api.cache_info().currsize,
            'max_size': 20
        }
    })