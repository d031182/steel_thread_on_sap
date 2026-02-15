#!/usr/bin/env python3
"""
Test script to demonstrate Feng Shui API Contract Test Detection

This script simulates what happens when you stage an API file
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.fengshui.api_contract_analyzer import (
    is_api_file,
    has_api_contract_test,
    detect_api_contract_gaps
)

print("=" * 70)
print("FENG SHUI API CONTRACT TEST DETECTION - DEMO")
print("=" * 70)
print()

# Test 1: Check if files are recognized as API files
print("[TEST 1] API File Detection")
print("-" * 70)

test_files = [
    "modules/ai_assistant/backend/api.py",
    "modules/data_products_v2/backend/api.py", 
    "modules/knowledge_graph_v2/backend/api.py",
    "modules/logger/backend/api.py",
    "core/api/frontend_registry.py",
    "modules/ai_assistant/backend/service.py",  # NOT an API file
]

for file_path_str in test_files:
    file_path = PROJECT_ROOT / file_path_str
    is_api = is_api_file(file_path)
    icon = "✅ API" if is_api else "❌ NOT API"
    print(f"{icon}: {file_path_str}")

print()

# Test 2: Check which modules have API contract tests
print("[TEST 2] API Contract Test Detection")
print("-" * 70)

modules = ["ai_assistant", "data_products_v2", "knowledge_graph_v2", "logger"]

for module in modules:
    has_backend, has_frontend = has_api_contract_test(module)
    
    backend_icon = "✅" if has_backend else "❌"
    frontend_icon = "✅" if has_frontend else "❌"
    
    print(f"Module: {module}")
    print(f"  {backend_icon} Backend API test:  tests/test_{module}_backend.py")
    print(f"  {frontend_icon} Frontend API test: tests/test_{module}_frontend_api.py")

print()

# Test 3: Detect gaps for staged API files
print("[TEST 3] API Contract Gap Detection")
print("-" * 70)

staged_files = [
    "modules/ai_assistant/backend/api.py",
    "modules/logger/backend/api.py",
]

gaps = detect_api_contract_gaps(staged_files)

if gaps:
    print(f"[!] {len(gaps)} API contract test gap(s) detected:\n")
    
    for i, gap in enumerate(gaps, 1):
        severity_icon = "🔴" if gap["severity"] == "CRITICAL" else "⚠️"
        print(f"{severity_icon} Gap #{i}")
        print(f"   File: {gap['file']}")
        print(f"   Type: {gap['gap_type']}")
        print(f"   Severity: {gap['severity']}")
        print(f"   Details: {gap['details']}")
        print(f"   Recommendation: {gap['recommendation']}")
        print()
else:
    print("[OK] No API contract gaps found!")

print("=" * 70)
print("DEMO COMPLETE")
print("=" * 70)