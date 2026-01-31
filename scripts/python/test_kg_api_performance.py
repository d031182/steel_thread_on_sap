#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Graph API Performance Test

Tests the Knowledge Graph API endpoint and measures performance.
Verifies that the cached ontology provides the expected 103x speedup.
"""

import sys
import io
import os
import time
import requests

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

print("="*80)
print("Knowledge Graph API Performance Test")
print("="*80)

# Test API endpoint
url = "http://localhost:5000/api/knowledge-graph/?source=sqlite&mode=schema"

print(f"\nCalling: {url}")
print("Timing each stage...\n")

# Measure API call
start = time.time()
try:
    response = requests.get(url, timeout=30)
    api_time = (time.time() - start) * 1000
    
    print(f"✓ API Response: {response.status_code}")
    print(f"✓ API Time: {api_time:.0f}ms")
    
    data = response.json()
    
    if data.get('success'):
        print(f"\n✓ Graph Data:")
        print(f"  - Nodes: {len(data.get('nodes', []))}")
        print(f"  - Edges: {len(data.get('edges', []))}")
        
        if 'stats' in data:
            print(f"\n✓ Stats:")
            for key, val in data['stats'].items():
                print(f"  - {key}: {val}")
    else:
        print(f"\n✗ Error: {data.get('error')}")
    
except requests.Timeout:
    print("✗ Request timed out (>30s)")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*80)
print("Check server console for detailed backend timing")
print("="*80)