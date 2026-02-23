"""Debug which database file is being used."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.sqlite_data_products_service import SQLiteDataProductsService
import sqlite3

service = SQLiteDataProductsService()

# Check the database path
print(f"Database path: {service.db_path}")
print(f"File exists: {Path(service.db_path).exists()}")
print(f"File size: {Path(service.db_path).stat().st_size if Path(service.db_path).exists() else 'N/A'} bytes")

# Check tables directly
conn = sqlite3.connect(service.db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print(f"\nTables in database:")
for table in tables:
    print(f"  - {table[0]}")
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"    Rows: {count}")

conn.close()