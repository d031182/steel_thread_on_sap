# Root-level conftest.py for pytest path configuration
# This file is loaded BEFORE test collection starts

import sys
from pathlib import Path

# Add project root to Python path BEFORE any test imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))