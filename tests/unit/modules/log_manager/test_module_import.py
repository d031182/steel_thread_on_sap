"""
Basic Import Test for Application Logging Module
===============================================
Simple test to verify module can be imported and basic functionality works.

Run with: python modules/application-logging/tests/test_module_import.py
"""

import sys
from pathlib import Path
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

print("=" * 60)
print("APPLICATION LOGGING MODULE - IMPORT TEST")
print("=" * 60)
print()

# Test 1: Import module
print("Test 1: Import module...")
try:
    # Note: Python imports use underscores, not hyphens
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    
    # Import from the actual module path
    from modules.application_logging.backend.sqlite_logger import SQLiteLogHandler, setup_logging
    from modules.application_logging.backend.api import create_blueprint
    print("✅ Module imported successfully")
    print(f"   - SQLiteLogHandler: {SQLiteLogHandler}")
    print(f"   - setup_logging: {setup_logging}")
    print(f"   - create_blueprint: {create_blueprint}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Create handler
print("Test 2: Create SQLiteLogHandler...")
try:
    handler = SQLiteLogHandler(db_path='logs/test_logs.db', retention_days=1)
    print("✅ Handler created successfully")
    print(f"   - Database: {handler.db_path}")
    print(f"   - Retention: {handler.retention_days} days")
except Exception as e:
    print(f"❌ Handler creation failed: {e}")
    sys.exit(1)

print()

# Test 3: Setup logging
print("Test 3: Setup logging on logger...")
try:
    import logging
    test_logger = logging.getLogger('test_module')
    test_logger.setLevel(logging.INFO)
    
    handler2 = setup_logging(test_logger, db_path='logs/test_logs2.db')
    print("✅ Logging setup successful")
    print(f"   - Logger: {test_logger.name}")
    print(f"   - Handlers: {len(test_logger.handlers)}")
except Exception as e:
    print(f"❌ Logging setup failed: {e}")
    sys.exit(1)

print()

# Test 4: Write test log
print("Test 4: Write test log...")
try:
    test_logger.info("Test log message from module import test")
    test_logger.warning("Test warning message")
    test_logger.error("Test error message")
    print("✅ Logs written successfully")
except Exception as e:
    print(f"❌ Log writing failed: {e}")
    sys.exit(1)

print()

# Test 5: Query logs
print("Test 5: Query logs...")
try:
    import time
    time.sleep(1)  # Wait for async writes
    
    logs = handler2.get_logs(limit=10)
    print(f"✅ Retrieved {len(logs)} logs")
    if logs:
        print(f"   Latest log: {logs[0]['level']} - {logs[0]['message'][:50]}")
except Exception as e:
    print(f"❌ Log query failed: {e}")
    sys.exit(1)

print()

# Test 6: Get statistics
print("Test 6: Get log statistics...")
try:
    total = handler2.get_log_count()
    info_count = handler2.get_log_count(level='INFO')
    warning_count = handler2.get_log_count(level='WARNING')
    error_count = handler2.get_log_count(level='ERROR')
    
    print("✅ Statistics retrieved")
    print(f"   Total: {total}")
    print(f"   INFO: {info_count}")
    print(f"   WARNING: {warning_count}")
    print(f"   ERROR: {error_count}")
except Exception as e:
    print(f"❌ Statistics failed: {e}")
    sys.exit(1)

print()

# Test 7: Cleanup
print("Test 7: Cleanup...")
try:
    handler.close()
    handler2.close()
    print("✅ Handlers closed successfully")
except Exception as e:
    print(f"❌ Cleanup failed: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print()
print("Module is working correctly and ready to use!")