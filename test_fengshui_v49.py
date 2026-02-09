#!/usr/bin/env python3
"""Quick test script for Feng Shui v4.9 new validators"""

from pathlib import Path
from tools.fengshui.agents.architect_agent import ArchitectAgent
from collections import Counter

# Run Feng Shui on data_products_v2
agent = ArchitectAgent()
report = agent.analyze_module(Path('modules/data_products_v2'))

print("\n" + "="*60)
print("FENG SHUI v4.9 - NEW VALIDATORS TEST")
print("="*60)
print(f"\nModule: data_products_v2")
print(f"Summary: {report.summary}")
print(f"Execution Time: {report.execution_time_seconds:.2f}s")

# Group by category
print(f"\nFindings by Category:")
categories = Counter(f.category for f in report.findings)
for cat, count in sorted(categories.items()):
    print(f"  - {cat}: {count}")

# Show sample findings
print(f"\nSample Findings (First 5):")
print("-" * 60)
for i, f in enumerate(report.findings[:5], 1):
    print(f"\n{i}. [{f.severity.value}] {f.category}")
    file_name = f.file_path.name if hasattr(f.file_path, 'name') else str(f.file_path)
    print(f"   File: {file_name}")
    print(f"   Line: {f.line_number}")
    print(f"   Description: {f.description}")
    print(f"   Recommendation: {f.recommendation[:80]}...")

# Check if new validators detected issues
facade_findings = [f for f in report.findings if 'Facade Pattern' in f.category]
backend_findings = [f for f in report.findings if 'Backend Structure' in f.category]

print(f"\n" + "="*60)
print("NEW VALIDATORS (v4.9) RESULTS:")
print("="*60)
print(f"Facade Pattern Violations: {len(facade_findings)}")
print(f"Backend Structure Violations: {len(backend_findings)}")

if facade_findings:
    print(f"\nFacade Pattern Issues:")
    for f in facade_findings[:3]:
        print(f"  - {f.description}")

if backend_findings:
    print(f"\nBackend Structure Issues:")
    for f in backend_findings[:3]:
        print(f"  - {f.description}")

print(f"\n✅ Feng Shui v4.9 validators are {'WORKING' if (facade_findings or backend_findings) else 'NOT detecting issues'}")
print("="*60)