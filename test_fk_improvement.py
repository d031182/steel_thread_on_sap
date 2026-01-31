"""
Test improved FK detection logic
Compare current detection vs improved detection
"""
import sqlite3

# Current logic (from data_graph_service.py)
def current_infer_fk(column_name: str, source_table: str) -> str:
    """Current FK detection logic"""
    col_lower = column_name.lower()
    source_lower = source_table.lower()
    
    if col_lower == source_lower:
        return None
    
    # Strategy 1: Role mappings
    role_mappings = {
        'invoicingparty': 'Supplier',
        'supplier': 'Supplier',
        'vendor': 'Supplier',
        'companycode': 'CompanyCode',
        'company': 'CompanyCode',
        'purchaseorder': 'PurchaseOrder',
        'po': 'PurchaseOrder',
        'product': 'Product',
        'material': 'Product',
        'costcenter': 'CostCenter',
        'plant': 'Plant'
    }
    
    if col_lower in role_mappings:
        target = role_mappings[col_lower]
        if target.lower() != source_lower:
            return target
    
    # Strategy 2: Check for ID/Code/Key/Number suffixes
    for suffix in ['ID', 'Code', 'Key', 'Number']:
        if column_name.endswith(suffix):
            base_name = column_name[:-len(suffix)]
            if base_name and base_name.lower() != source_lower:
                return base_name
    
    # Strategy 3: Known tables
    known_tables = [
        'Supplier', 'Product', 'CompanyCode', 'CostCenter', 
        'PurchaseOrder', 'ServiceEntrySheet', 'JournalEntry',
        'PaymentTerms', 'Plant', 'Material'
    ]
    
    for table in known_tables:
        if table.lower() in col_lower and table.lower() != source_lower:
            return table
    
    return None

# Improved logic
def improved_infer_fk(column_name: str, source_table: str, all_table_names: list) -> str:
    """Improved FK detection - checks actual table existence"""
    col_lower = column_name.lower()
    source_lower = source_table.lower()
    
    if col_lower == source_lower:
        return None
    
    # Strategy 1: Exact table name match (e.g., "Supplier" column → Supplier table)
    for table in all_table_names:
        if table.lower() == col_lower and table.lower() != source_lower:
            return table
    
    # Strategy 2: Strip common suffixes and check tables
    for suffix in ['ID', 'Code', 'Key', 'Number', 'UUID']:
        if column_name.endswith(suffix):
            base_name = column_name[:-len(suffix)]
            for table in all_table_names:
                if table.lower() == base_name.lower() and table.lower() != source_lower:
                    return table
    
    # Strategy 3: Check if column contains any table name
    for table in all_table_names:
        # Skip very short table names to avoid false positives
        if len(table) < 4:
            continue
        if table.lower() in col_lower and table.lower() != source_lower:
            return table
    
    return None

# Test with actual data
conn = sqlite3.connect('app/database/p2p_data_products.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
all_tables = [row[0] for row in cursor.fetchall()]

print(f"Found {len(all_tables)} tables\n")

# Test FK detection on PurchaseOrderItem
print("=== Testing PurchaseOrderItem ===")
cursor.execute("PRAGMA table_info(PurchaseOrderItem)")
columns = [row[1] for row in cursor.fetchall()]

print(f"\nColumns: {len(columns)}")
print("\nFK Detection Comparison:")
print(f"{'Column':<40} {'Current':<25} {'Improved':<25} {'Match?'}")
print("-" * 100)

improvements = 0
for col in columns[:20]:  # First 20 columns
    current_result = current_infer_fk(col, 'PurchaseOrderItem')
    improved_result = improved_infer_fk(col, 'PurchaseOrderItem', all_tables)
    
    match = "OK" if current_result == improved_result else "IMPROVED!" if improved_result and not current_result else ""
    
    if improved_result and not current_result:
        improvements += 1
    
    print(f"{col:<40} {str(current_result):<25} {str(improved_result):<25} {match}")

print(f"\nImprovements: {improvements} additional FKs detected!")

conn.close()