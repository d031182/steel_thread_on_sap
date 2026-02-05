#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild Module Database from CSN Files

Creates P2P tables in modules/data_products/database/p2p_sample.db
"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from core.services.csn_parser import CSNParser

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SQLITE_DB = "modules/data_products/database/p2p_sample.db"
CSN_DIR = "docs/csn"

CORE_ENTITIES = [
    'PurchaseOrder', 'PurchaseOrderItem',
    'Supplier', 'SupplierInvoice', 'SupplierInvoiceItem',
    'JournalEntry', 'PaymentTerms', 'ServiceEntrySheet',
    'Product', 'CompanyCode', 'CostCenter',
]

def csn_type_to_sqlite(csn_type: str) -> str:
    if not csn_type:
        return 'TEXT'
    csn_type_lower = csn_type.lower()
    if 'string' in csn_type_lower:
        return 'TEXT'
    if 'int' in csn_type_lower:
        return 'INTEGER'
    if 'decimal' in csn_type_lower:
        return 'REAL'
    if any(x in csn_type_lower for x in ['date', 'time', 'timestamp']):
        return 'TEXT'
    if 'boolean' in csn_type_lower:
        return 'INTEGER'
    return 'TEXT'

def create_table_from_csn(conn, entity_name: str, parser: CSNParser):
    metadata = parser.get_entity_metadata(entity_name)
    if not metadata:
        print(f"  ❌ {entity_name} - Not found in CSN")
        return False
    
    col_defs = []
    pks = metadata.primary_keys or []
    
    for col in metadata.columns:
        col_def = f"{col.name} {csn_type_to_sqlite(col.type)}"
        if not col.is_nullable and col.name not in pks:
            col_def += " NOT NULL"
        col_defs.append(col_def)
    
    if pks:
        col_defs.append(f"PRIMARY KEY ({', '.join(pks)})")
    
    create_sql = f"CREATE TABLE {entity_name} (\n  " + ",\n  ".join(col_defs) + "\n)"
    
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {entity_name}")
    cursor.execute(create_sql)
    conn.commit()
    
    print(f"  ✅ {entity_name} - {len(metadata.columns)} cols, PK: {pks}")
    return True

def main():
    print("Rebuild Module Database from CSN")
    print(f"Target: {SQLITE_DB}\n")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(SQLITE_DB), exist_ok=True)
    
    parser = CSNParser(CSN_DIR)
    conn = sqlite3.connect(SQLITE_DB)
    
    success = 0
    for entity in CORE_ENTITIES:
        if create_table_from_csn(conn, entity, parser):
            success += 1
    
    conn.close()
    print(f"\n✅ Created {success}/{len(CORE_ENTITIES)} tables")
    return 0

if __name__ == '__main__':
    sys.exit(main())