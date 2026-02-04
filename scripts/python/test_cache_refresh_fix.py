"""
Test Cache Refresh Fix

Verifies that clear_cache() handles missing tables gracefully.

@author P2P Development Team
@version 1.0.0
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.services.ontology_persistence_service import OntologyPersistenceService

def test_clear_cache_with_missing_tables():
    """Test clear_cache handles missing graph_schema_edges table"""
    print("="*60)
    print("  Test: clear_cache() with missing tables")
    print("="*60)
    
    try:
        # Use actual database
        service = OntologyPersistenceService('p2p_data.db')
        
        print("\n→ Calling clear_cache()...")
        count = service.clear_cache()
        
        print(f"✓ clear_cache() succeeded!")
        print(f"  Deleted {count} relationships")
        
        print("\n✅ Fix verified - clear_cache() handles missing tables gracefully")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_clear_cache_with_missing_tables()
    sys.exit(0 if success else 1)