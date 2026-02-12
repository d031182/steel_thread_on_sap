"""
CSN URL Mapping for P2P Data Products
======================================
Maps data product ORD IDs to their CSN schema URLs from SAP Discovery API.

These URLs are retrieved from BDC MCP availableDataProducts tool and point to
SAP's public Open Resource Discovery API for CSN definitions.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-01-23
"""

# P2P Data Product CSN URLs
# Format: ordId -> CSN URL from SAP Discovery API
CSN_URL_MAP = {
    # Core P2P Data Products
    'sap.s4com:apiResource:Supplier:v1': 
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/b6d7050b-8c9a-4c4d-9689-346e4ab14855/specification/5b6cb175-7b2e-4fbc-bdf3-bfd315abeab5',
    
    'sap.s4com:apiResource:PurchaseOrder:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/0d482118-58d8-4bd8-b403-d57e233eec9e/specification/a51f4b14-3e18-45d2-8a87-8a11c524c45c',
    
    'sap.s4com:apiResource:SupplierInvoice:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/53c00db8-0872-4d82-84a4-42fbdfd8003f/specification/bab89521-f7f6-4609-b572-6e9d99c5b2d8',
    
    'sap.s4com:apiResource:ServiceEntrySheet:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/64ead95d-bd9d-4d08-99ea-9f7b6ed42e13/specification/64bd91ff-e63c-4f8d-83d3-dbef2b679d65',
    
    'sap.s4com:apiResource:PaymentTerms:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/0579bee3-aeb0-4cc7-bc47-216bf8119c06/specification/4a73f9c9-23fa-44be-acc4-5a44c9f73ab7',
    
    'sap.s4com:apiResource:JournalEntryHeader:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/1528adf0-24fe-4bdf-8ac2-f33252acda3f/specification/ea58282e-e096-4f0d-88dd-e7f027ea0a37',
    
    # Additional related products
    'sap.s4com:apiResource:PurchaseRequisition:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/f170716e-897d-4464-9b42-6f9c36e85490/specification/708bebdf-8f19-4149-abfe-a03c8bcdcfe5',
    
    'sap.s4com:apiResource:PurchaseContract:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/0b98596d-e5a4-4ef9-b96a-779131cd8bb4/specification/e76ed116-4d7b-4b34-82bb-56b5acdcf564',
    
    'sap.s4com:apiResource:Customer:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/2409ffdb-0367-4776-bbf4-50bc568b97f8/specification/193e6dfc-435b-4790-b2b7-23d01201cdab',
    
    'sap.s4com:apiResource:Product:v1':
        'https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/753b7115-f3a9-44b2-bbfb-041764484da3/specification/70bde547-4ba6-46d2-bc73-5d6e574f96f9',
}

# Reverse mapping: schema name pattern -> ORD ID
SCHEMA_TO_ORD_ID_MAP = {
    'Supplier': 'sap.s4com:apiResource:Supplier:v1',
    'PurchaseOrder': 'sap.s4com:apiResource:PurchaseOrder:v1',
    'SupplierInvoice': 'sap.s4com:apiResource:SupplierInvoice:v1',
    'ServiceEntrySheet': 'sap.s4com:apiResource:ServiceEntrySheet:v1',
    'PaymentTerms': 'sap.s4com:apiResource:PaymentTerms:v1',
    'JournalEntryHeader': 'sap.s4com:apiResource:JournalEntryHeader:v1',
    'PurchaseRequisition': 'sap.s4com:apiResource:PurchaseRequisition:v1',
    'PurchaseContract': 'sap.s4com:apiResource:PurchaseContract:v1',
    'Customer': 'sap.s4com:apiResource:Customer:v1',
    'Product': 'sap.s4com:apiResource:Product:v1',
}


def get_csn_url(ord_id):
    """
    Get CSN URL for a given ORD ID
    
    Args:
        ord_id: ORD ID (e.g., 'sap.s4com:apiResource:Supplier:v1')
    
    Returns:
        CSN URL string or None if not found
    """
    return CSN_URL_MAP.get(ord_id)


def schema_name_to_ord_id(schema_name):
    """
    Convert HANA schema name to ORD ID
    
    Args:
        schema_name: Schema name (e.g., '_SAP_DATAPRODUCT_sap_s4com_Supplier_v1_uuid')
                     or simplified name (e.g., 'Supplier', 'sap_s4com_Supplier_v1')
    
    Returns:
        ORD ID or None if not found
    
    Examples:
        >>> schema_name_to_ord_id('_SAP_DATAPRODUCT_sap_s4com_Supplier_v1_123')
        'sap.s4com:apiResource:Supplier:v1'
        
        >>> schema_name_to_ord_id('sap_s4com_Supplier_v1')
        'sap.s4com:apiResource:Supplier:v1'
        
        >>> schema_name_to_ord_id('Supplier')
        'sap.s4com:apiResource:Supplier:v1'
    """
    # Try direct match first (simple name like "Supplier")
    if schema_name in SCHEMA_TO_ORD_ID_MAP:
        return SCHEMA_TO_ORD_ID_MAP[schema_name]
    
    # Parse full schema name: _SAP_DATAPRODUCT_sap_s4com_Supplier_v1_uuid
    if schema_name.startswith('_SAP_DATAPRODUCT'):
        parts = schema_name.split('_')
        
        # Extract product name (after 'dataProduct' or by pattern)
        if 'dataProduct' in parts:
            dp_index = parts.index('dataProduct')
            if dp_index + 1 < len(parts):
                product_name = parts[dp_index + 1]
                if product_name in SCHEMA_TO_ORD_ID_MAP:
                    return SCHEMA_TO_ORD_ID_MAP[product_name]
        
        # Alternative: look for known product names
        for product_name in SCHEMA_TO_ORD_ID_MAP.keys():
            if product_name in parts:
                return SCHEMA_TO_ORD_ID_MAP[product_name]
    
    # Parse simplified format: sap_s4com_Supplier_v1
    if '_' in schema_name:
        parts = schema_name.split('_')
        # Find product name (usually before version)
        for i, part in enumerate(parts):
            if part.startswith('v') and i > 0:
                product_name = parts[i-1]
                if product_name in SCHEMA_TO_ORD_ID_MAP:
                    return SCHEMA_TO_ORD_ID_MAP[product_name]
    
    return None


def get_all_p2p_products():
    """
    Get list of all P2P data products with their metadata
    
    Returns:
        List of dicts with product information
    """
    return [
        {
            'ordId': 'sap.s4com:apiResource:Supplier:v1',
            'name': 'Supplier',
            'displayName': 'Supplier',
            'description': 'A business partner who provides materials and/or services',
            'namespace': 'sap.s4com',
            'version': 'v1',
            'csnUrl': CSN_URL_MAP['sap.s4com:apiResource:Supplier:v1']
        },
        {
            'ordId': 'sap.s4com:apiResource:PurchaseOrder:v1',
            'name': 'PurchaseOrder',
            'displayName': 'Purchase Order',
            'description': 'A request or instruction to a supplier for materials or services',
            'namespace': 'sap.s4com',
            'version': 'v1',
            'csnUrl': CSN_URL_MAP['sap.s4com:apiResource:PurchaseOrder:v1']
        },
        {
            'ordId': 'sap.s4com:apiResource:SupplierInvoice:v1',
            'name': 'SupplierInvoice',
            'displayName': 'Supplier Invoice',
            'description': 'A document specifying amounts due for purchase transactions',
            'namespace': 'sap.s4com',
            'version': 'v1',
            'csnUrl': CSN_URL_MAP['sap.s4com:apiResource:SupplierInvoice:v1']
        },
        {
            'ordId': 'sap.s4com:apiResource:ServiceEntrySheet:v1',
            'name': 'ServiceEntrySheet',
            'displayName': 'Service Entry Sheet',
            'description': 'A document recording services performed by a supplier',
            'namespace': 'sap.s4com',
            'version': 'v1',
            'csnUrl': CSN_URL_MAP['sap.s4com:apiResource:ServiceEntrySheet:v1']
        },
        {
            'ordId': 'sap.s4com:apiResource:PaymentTerms:v1',
            'name': 'PaymentTerms',
            'displayName': 'Payment Terms',
            'description': 'Terms of payment with cash discount and payment periods',
            'namespace': 'sap.s4com',
            'version': 'v1',
            'csnUrl': CSN_URL_MAP['sap.s4com:apiResource:PaymentTerms:v1']
        },
        {
            'ordId': 'sap.s4com:apiResource:JournalEntryHeader:v1',
            'name': 'JournalEntryHeader',
            'displayName': 'Journal Entry Header',
            'description': 'An accounting record for business transactions',
            'namespace': 'sap.s4com',
            'version': 'v1',
            'csnUrl': CSN_URL_MAP['sap.s4com:apiResource:JournalEntryHeader:v1']
        },
    ]