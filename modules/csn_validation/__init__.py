"""
CSN Validation Module
====================
Validates CSN definitions against actual HANA table structures.

Quick Start:
    from modules.csn_validation.backend.validator import CSNValidator
    
    # Create validator
    validator = CSNValidator(
        hana_host='your-host.hanacloud.ondemand.com',
        hana_port=443,
        hana_user='your_user',
        hana_password='your_password'
    )
    
    # Connect to HANA
    validator.connect()
    
    # Find data product schema
    schema = validator.find_data_product_schema('PurchaseOrder')
    
    # Load CSN
    csn = validator.load_csn_file('PurchaseOrder')
    
    # Validate entity
    result = validator.validate_entity(csn, 'PurchaseOrder', schema)
    
    # Generate SQLite schema
    if result['success']:
        sqlite_schema = validator.generate_sqlite_schema(result)
    
    validator.close()

Features:
- Validate CSN entities against HANA tables
- Compare CSN fields with HANA columns  
- Map CDS types to HANA SQL types
- Generate SQLite schemas from HANA
- Detect missing fields and type mismatches
- Create validation reports
- Batch entity validation

Use Cases:
- Pre-migration schema validation
- Ensure data model consistency
- Generate accurate SQLite schemas
- Detect schema drift
- Document table structures
- Quality assurance

CLI Usage:
    python modules/csn_validation/backend/validator.py PurchaseOrder

Author: P2P Development Team
Version: 1.0.0
"""

__version__ = '1.0.0'