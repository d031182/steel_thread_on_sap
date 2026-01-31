"""
Test Data Mode - Direct query approach
Bypasses complex FK detection, just shows records
"""

import sqlite3
import json

DB_PATH = "app/database/p2p_data_products.db"

def test_data_mode():
    """Test data mode with direct SQLite queries"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    nodes = []
    edges = []
    
    # Key P2P tables to visualize (PK column = table name!)
    tables_to_show = [
        ('Supplier', 'Supplier'),
        ('PurchaseOrder', 'PurchaseOrder'),
        ('SupplierInvoice', 'SupplierInvoice')
    ]
    
    record_map = {}
    
    # Create nodes for each table
    for table_name, pk_col in tables_to_show:
        try:
            query = f'SELECT * FROM {table_name} LIMIT 10'
            cursor.execute(query)
            records = cursor.fetchall()
            
            print(f"\n{table_name}: {len(records)} records")
            
            record_map[table_name] = {}
            
            for record in records:
                rec_dict = dict(record)
                pk_value = rec_dict.get(pk_col)
                
                if not pk_value:
                    continue
                
                node_id = f"{table_name}-{pk_value}"
                node_label = f"{table_name}\n{pk_col}: {pk_value}"
                
                nodes.append({
                    'id': node_id,
                    'label': node_label,
                    'title': f"{table_name}: {pk_value}",
                    'group': table_name,
                    'shape': 'box'
                })
                
                record_map[table_name][str(pk_value)] = {
                    'node_id': node_id,
                    'record': rec_dict
                }
                
                # Create edges based on FK columns
                if table_name == 'PurchaseOrder':
                    supplier_id = rec_dict.get('Supplier')  # FK column name = target table name
                    if supplier_id and 'Supplier' in record_map:
                        supplier_node = record_map['Supplier'].get(str(supplier_id))
                        if supplier_node:
                            edges.append({
                                'from': node_id,
                                'to': supplier_node['node_id'],
                                'label': 'Supplier',
                                'arrows': 'to'
                            })
                
                elif table_name == 'SupplierInvoice':
                    po_id = rec_dict.get('PurchaseOrder')  # FK column name = target table name
                    if po_id and 'PurchaseOrder' in record_map:
                        po_node = record_map['PurchaseOrder'].get(str(po_id))
                        if po_node:
                            edges.append({
                                'from': node_id,
                                'to': po_node['node_id'],
                                'label': 'PurchaseOrder',
                                'arrows': 'to'
                            })
        
        except Exception as e:
            print(f"Error with {table_name}: {e}")
            continue
    
    conn.close()
    
    print(f"\nRESULTS:")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")
    print(f"\nSample nodes:")
    for node in nodes[:5]:
        print(f"  - {node['label']}")
    print(f"\nSample edges:")
    for edge in edges[:5]:
        print(f"  - {edge['from']} → {edge['to']}")
    
    return {
        'success': True,
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'node_count': len(nodes),
            'edge_count': len(edges)
        }
    }

if __name__ == '__main__':
    result = test_data_mode()
    print(f"\nFinal: {result['stats']}")