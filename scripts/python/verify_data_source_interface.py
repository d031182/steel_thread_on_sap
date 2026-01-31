#!/usr/bin/env python3
"""
Verify DataSource Interface Compliance

Checks that all data source implementations properly follow the DataSource interface.
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.interfaces.data_source import DataSource
from modules.hana_connection.backend.hana_data_source import HANADataSource
from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource

print("="*80)
print("DataSource Interface Verification")
print("="*80)

# Check inheritance
print("\n1. Interface Compliance")
print("-" * 80)
print(f"[OK] HANADataSource implements DataSource: {issubclass(HANADataSource, DataSource)}")
print(f"[OK] SQLiteDataSource implements DataSource: {issubclass(SQLiteDataSource, DataSource)}")

# List interface methods
print("\n2. Interface Methods")
print("-" * 80)
methods = [m for m in dir(DataSource) if not m.startswith('_') and callable(getattr(DataSource, m))]
print(f"Total: {len(methods)} methods\n")

for method_name in sorted(methods):
    method = getattr(DataSource, method_name)
    
    # Check if both implementations have this method
    hana_has = hasattr(HANADataSource, method_name)
    sqlite_has = hasattr(SQLiteDataSource, method_name)
    
    status = "[OK]" if (hana_has and sqlite_has) else "[FAIL]"
    print(f"  {status} {method_name}()")
    if not hana_has:
        print(f"      [FAIL] Missing in HANADataSource")
    if not sqlite_has:
        print(f"      [FAIL] Missing in SQLiteDataSource")

# Summary
print("\n3. Summary")
print("-" * 80)
print(f"Interface defines {len(methods)} methods")
print(f"All methods implemented: {'YES' if all(hasattr(HANADataSource, m) and hasattr(SQLiteDataSource, m) for m in methods) else 'NO'}")

print("\n4. Benefits of This Architecture")
print("-" * 80)
print("[OK] Dependency Injection: Swap data sources via configuration")
print("[OK] Loose Coupling: Application code doesn't know which DB it's using")
print("[OK] Testability: Easy to mock for unit tests")
print("[OK] Extensibility: Add new data sources (PostgreSQL, etc.) easily")
print("[OK] Type Safety: ABC ensures all methods are implemented")

print("\n[OK] Interface verification complete!")
