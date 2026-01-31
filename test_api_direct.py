"""Direct test of build_data_graph via API"""
import sys
sys.path.insert(0, 'app')
sys.path.insert(0, '.')

from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource
from modules.knowledge_graph.backend.data_graph_service import DataGraphService

# Initialize
db_path = "app/database/p2p_data_products.db"
data_source = SQLiteDataSource(db_path)
graph_service = DataGraphService(data_source)

# Test _get_all_tables first
print("Testing _get_all_tables...")
tables = graph_service._get_all_tables()
print(f"Tables found: {len(tables)}")
if tables:
    print("First 3 tables:")
    for t in tables[:3]:
        print(f"  - {t}")

# Test query execution
print("\nTesting direct query on Supplier table...")
query_result = data_source.execute_query("SELECT * FROM Supplier LIMIT 5")
print(f"Query success: {query_result.get('success')}")
print(f"Data rows: {len(query_result.get('data', []))}")
if query_result.get('data'):
    print(f"First record: {query_result['data'][0]}")

print("\nTesting build_data_graph...")
result = graph_service.build_data_graph(max_records_per_table=20)

print(f"\nSuccess: {result.get('success')}")
print(f"Nodes: {len(result.get('nodes', []))}")
print(f"Edges: {len(result.get('edges', []))}")
if 'message' in result:
    print(f"Message: {result['message']}")
if 'error' in result:
    print(f"Error: {result['error']}")

# Show first few nodes
nodes = result.get('nodes', [])
if nodes:
    print(f"\nFirst 3 nodes:")
    for node in nodes[:3]:
        print(f"  - {node['label']}")