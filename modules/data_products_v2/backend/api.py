"""
Data Products V2 API Blueprint

REST API for data products with source switching capability.
Uses Constructor Injection for dependency management.

Author: P2P Development Team
Version: 3.0.0 (DI Refactoring)
Date: 2026-02-15
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Optional
from core.interfaces.data_product_repository import DataAccessError
from modules.data_products_v2.facade.data_products_facade import DataProductsFacade


logger = logging.getLogger(__name__)


class DataProductsV2API:
    """
    API layer with Constructor Injection
    
    Facades are injected via constructor instead of being
    retrieved from Flask's current_app (Service Locator anti-pattern).
    
    Benefits:
    - No dependency on Flask context
    - Easy to test (inject mock facades)
    - Clear dependencies (explicit in constructor)
    
    Usage:
        # Create API instance with injected facades
        api = DataProductsV2API(
            sqlite_facade=sqlite_facade,
            hana_facade=hana_facade
        )
        
        # Create blueprint from API instance
        blueprint = create_blueprint(api)
        app.register_blueprint(blueprint, url_prefix='/api/data-products')
    """
    
    def __init__(
        self,
        sqlite_facade: DataProductsFacade,
        hana_facade: Optional[DataProductsFacade] = None
    ):
        """
        Initialize API with injected facades
        
        Args:
            sqlite_facade: Pre-configured SQLite facade (required)
            hana_facade: Pre-configured HANA facade (optional)
        """
        self._facades: Dict[str, Optional[DataProductsFacade]] = {
            'sqlite': sqlite_facade,
            'hana': hana_facade
        }
    
    def get_facade(self, source: str) -> DataProductsFacade:
        """
        Get facade from injected dependencies
        
        Args:
            source: 'hana' or 'sqlite'
        
        Returns:
            Pre-configured facade instance
        
        Raises:
            ValueError: If source invalid or facade not configured
        """
        if source not in self._facades:
            raise ValueError(f"Unknown source: {source}. Use 'hana' or 'sqlite'")
        
        facade = self._facades[source]
        if facade is None:
            raise ValueError(f"{source.upper()} facade not configured")
        
        return facade
    
    def list_data_products(self):
        """
        List data products from specified source
        
        Query Parameters:
            source: 'hana' or 'sqlite' (default: 'sqlite')
        
        Returns:
            JSON with list of data products
        """
        try:
            source = request.args.get('source', 'sqlite').lower()
            
            if source not in ['hana', 'sqlite']:
                return jsonify({
                    'success': False,
                    'error': 'Invalid source. Use "hana" or "sqlite"'
                }), 400
            
            # Get facade and fetch data
            facade = self.get_facade(source)
            products = facade.get_data_products()
            
            # Convert domain models to dict
            products_dict = [
                {
                    'product_name': p.product_name,
                    'display_name': p.display_name,
                    'namespace': p.namespace,
                    'version': p.version,
                    'schema_name': p.schema_name,
                    'source': p.source,
                    'description': p.description,
                    'table_count': p.table_count
                }
                for p in products
            ]
            
            return jsonify({
                'success': True,
                'count': len(products_dict),
                'data_products': products_dict,
                'source': source
            })
            
        except (ValueError, DataAccessError) as e:
            logger.error(f"Data access error: {str(e)}")
            # HTTP 503 Service Unavailable
            return jsonify({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'DATA_ACCESS_ERROR',
                    'userMessage': 'Failed to load data products from HANA Cloud. Please check your connection or switch to SQLite as fallback.'
                }
            }), 503
        except Exception as e:
            logger.error(f"Unexpected error listing data products: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_tables(self, product_name: str):
        """Get tables in a data product"""
        try:
            source = request.args.get('source', 'sqlite').lower()
            facade = self.get_facade(source)
            tables = facade.get_tables(product_name)
            
            tables_dict = [
                {
                    'table_name': t.table_name,
                    'table_type': t.table_type,
                    'record_count': t.record_count,
                    'schema_name': t.schema_name
                }
                for t in tables
            ]
            
            return jsonify({
                'success': True,
                'count': len(tables_dict),
                'tables': tables_dict,
                'source': source
            })
            
        except (ValueError, DataAccessError) as e:
            logger.error(f"Data access error: {str(e)}")
            return jsonify({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'DATA_ACCESS_ERROR',
                    'userMessage': 'Failed to access HANA Cloud. Please use SQLite as data source.'
                }
            }), 503
        except Exception as e:
            logger.error(f"Unexpected error getting tables: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_table_structure(self, product_name: str, table_name: str):
        """Get table structure (columns)"""
        try:
            source = request.args.get('source', 'sqlite').lower()
            facade = self.get_facade(source)
            columns = facade.get_table_structure(product_name, table_name)
            
            columns_dict = [
                {
                    'column_name': c.column_name,
                    'data_type': c.data_type,
                    'length': c.length,
                    'is_nullable': c.is_nullable,
                    'is_primary_key': c.is_primary_key,
                    'foreign_key': c.foreign_key
                }
                for c in columns
            ]
            
            return jsonify({
                'success': True,
                'columns': columns_dict,
                'source': source
            })
            
        except (ValueError, DataAccessError) as e:
            logger.error(f"Data access error: {str(e)}")
            return jsonify({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'DATA_ACCESS_ERROR',
                    'userMessage': 'Failed to access HANA Cloud. Please use SQLite as data source.'
                }
            }), 503
        except Exception as e:
            logger.error(f"Unexpected error getting structure: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def query_table(self, product_name: str, table_name: str):
        """Query table data"""
        try:
            source = request.args.get('source', 'sqlite').lower()
            data = request.get_json() or {}
            
            facade = self.get_facade(source)
            result = facade.query_table(
                product_name,
                table_name,
                limit=min(int(data.get('limit', 100)), 1000),
                offset=max(int(data.get('offset', 0)), 0)
            )
            
            result['success'] = True
            result['source'] = source
            return jsonify(result)
            
        except (ValueError, DataAccessError) as e:
            logger.error(f"Data access error: {str(e)}")
            return jsonify({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'DATA_ACCESS_ERROR',
                    'userMessage': 'Failed to access HANA Cloud. Please use SQLite as data source.'
                }
            }), 503
        except Exception as e:
            logger.error(f"Unexpected error querying table: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


def create_blueprint(api_instance: DataProductsV2API) -> Blueprint:
    """
    Factory function to create Flask Blueprint from API instance
    
    This allows us to use dependency injection while still working
    with Flask's blueprint system.
    
    Args:
        api_instance: Pre-configured DataProductsV2API instance
    
    Returns:
        Flask Blueprint with routes bound to API instance methods
    
    Usage:
        api = DataProductsV2API(sqlite_facade, hana_facade)
        blueprint = create_blueprint(api)
        app.register_blueprint(blueprint, url_prefix='/api/data-products')
    """
    bp = Blueprint('data_products_v2', __name__)
    
    @bp.route('/', methods=['GET'])
    def list_data_products():
        return api_instance.list_data_products()
    
    @bp.route('/<product_name>/tables', methods=['GET'])
    def get_tables(product_name):
        return api_instance.get_tables(product_name)
    
    @bp.route('/<product_name>/<table_name>/structure', methods=['GET'])
    def get_table_structure(product_name, table_name):
        return api_instance.get_table_structure(product_name, table_name)
    
    @bp.route('/<product_name>/<table_name>/query', methods=['POST'])
    def query_table(product_name, table_name):
        return api_instance.query_table(product_name, table_name)
    
    return bp


# For backwards compatibility, export the old blueprint creation
# This will be removed after server.py is updated
data_products_v2_api = None  # Deprecated: Use create_blueprint() instead