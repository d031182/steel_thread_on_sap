#!/usr/bin/env python
"""Analyze timing magic numbers in CSS files for CSS-003 task."""

import re

files_to_check = [
    'app_v2/static/css/css-variables.css',
    'modules/ai_assistant/frontend/styles/markdown.css',
    'app_v2/static/css/ai-assistant.css',
    'modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css'
]

# Search for numeric values followed by ms/s
numeric_timing = r':\s*(\d+(?:\.\d+)?)(m?s)(?![a-z])'
numeric_timing_vals = {}

print("=" * 80)
print("TIMING MAGIC NUMBERS ANALYSIS (CSS-003)")
print("=" * 80)

for filepath in files_to_check:
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                if any(x in line.lower() for x in ['transition', 'animation', 'delay', 'duration']):
                    matches = re.findall(numeric_timing, line)
                    for match in matches:
                        val_key = f"{match[0]}{match[1]}"
                        if val_key not in numeric_timing_vals:
                            numeric_timing_vals[val_key] = {'count': 0, 'examples': []}
                        numeric_timing_vals[val_key]['count'] += 1
                        if len(numeric_timing_vals[val_key]['examples']) < 2:
                            numeric_timing_vals[val_key]['examples'].append(f"{filepath}:{line_num}")
    except FileNotFoundError:
        pass

print("\nNUMERIC TIMING VALUES TO REPLACE:")
print("=" * 80)
for val, data in sorted(numeric_timing_vals.items(), key=lambda x: x[1]['count'], reverse=True):
    print(f"  {val:10s} - {data['count']:2d} occurrences | Examples: {', '.join(data['examples'])}")

print("\n" + "=" * 80)
print("RECOMMENDED TIMING TOKENS:")
print("=" * 80)
print("""
--timing-transition-fast: 150ms       (quick feedback)
--timing-transition-normal: 300ms     (standard transitions)
--timing-transition-slow: 500ms       (elaborate animations)
--timing-delay-animation: 100ms       (animation stagger)
--timing-animation-duration: 300ms    (default animation)
""")

total_count = sum(data['count'] for data in numeric_timing_vals.values())
print(f"TOTAL TIMING MAGIC NUMBERS FOUND: {total_count}")