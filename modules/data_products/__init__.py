"""
Data Products Viewer Module
===========================
SAP HANA Cloud Data Products browser and query interface.

Quick Start:
    from modules.data_products.frontend.dataProductsAPI import DataProductsAPI
    
    # Create API instance
    api = DataProductsAPI(baseURL='http://localhost:5000')
    
    # List all data products
    products = await api.listDataProducts()
    
    # Get tables in a schema
    tables = await api.getTables('sap_s4com_Supplier_v1')
    
    # Query table data
    result = await api.queryTable('schema', 'table', {
        'limit': 100,
        'columns': ['*']
    })

Features:
- List all installed data product schemas
- Browse tables within data products
- View table structure and column metadata
- Query data with filters and pagination
- Parse CSN schema definitions
- Extract metadata from schema names
- Intelligent caching (1-minute TTL)
- Backend connectivity testing

Use Cases:
- Browse SAP data products
- Explore P2P data models (Supplier, Invoice, PO)
- Query business data
- View CSN schemas
- Build data exploration tools
- Create custom viewers

Author: P2P Development Team
Version: 1.0.0
"""

__version__ = '1.0.0'