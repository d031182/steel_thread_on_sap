#!/usr/bin/env python3
"""
Extract Magic Numbers from CSS files and generate CSS variables

HIGH-43.3: Phase 3 Extract Magic Numbers
Identifies all hardcoded numeric values and creates CSS variables for:
- Spacing (px, em, rem)
- Sizing (px, em, rem, %)
- Timing (ms, s)
- Opacity/alpha values
"""

import re
import json
from pathlib import Path
from collections import defaultdict

# CSS files to analyze
CSS_FILES = [
    'modules/ai_assistant/frontend/styles/markdown.css',
    'modules/ai_assistant/frontend/css/assistant.css',
    'modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css',
    'modules/knowledge_graph_v2/frontend/styles/knowledgeGraphV2.css',
]

def extract_magic_numbers(css_content):
    """Extract all hardcoded numeric values with their context"""
    
    # Pattern: number with unit, excluding those already in CSS variables or calc()
    pattern = r'(?:(?<!var\()(?<!calc\()(\d+(?:\.\d+)?)(px|em|rem|%|ms|s|vh|vw))'
    
    matches = []
    for match in re.finditer(pattern, css_content):
        value = match.group(1)
        unit = match.group(2)
        matches.append({
            'value': value,
            'unit': unit,
            'full': f"{value}{unit}"
        })
    
    return matches

def categorize_magic_numbers(magic_numbers):
    """Categorize magic numbers by purpose"""
    
    categories = {
        'spacing': defaultdict(int),      # margin, padding
        'sizing': defaultdict(int),       # width, height, font-size
        'timing': defaultdict(int),       # transition, animation
        'opacity': defaultdict(int),      # rgba alpha values
    }
    
    for num in magic_numbers:
        full = num['full']
        unit = num['unit']
        
        if unit in ['px', 'em', 'rem']:
            if float(num['value']) <= 2:
                categories['spacing'][full] += 1
            else:
                categories['sizing'][full] += 1
        elif unit in ['ms', 's']:
            categories['timing'][full] += 1
        # Opacity handled separately
    
    return categories

def generate_css_variables(categories):
    """Generate CSS variable declarations"""
    
    variables = {}
    
    # Spacing variables
    spacing_map = {
        '0.1875rem': '--spacing-xs-small',
        '0.25rem': '--spacing-xs',
        '0.2em': '--spacing-2em-ratio',
        '0.2rem': '--spacing-2rem-ratio',
        '0.3em': '--spacing-3em-ratio',
        '0.5em': '--spacing-sm-em',
        '0.5rem': '--spacing-sm',
        '0.75rem': '--spacing-md',
        '1em': '--spacing-lg-em',
        '1rem': '--spacing-lg',
        '2em': '--spacing-2em',
        '2px': '--spacing-2px',
    }
    
    # Sizing variables
    sizing_map = {
        '3px': '--border-radius-small',
        '3rem': '--size-3rem',
        '4px': '--border-radius-md',
        '8px': '--border-radius-lg',
        '12px': '--font-size-12px',
        '13px': '--font-size-13px',
        '14px': '--font-size-14px',
        '16px': '--size-icon-sm',
        '20px': '--size-icon-md',
        '32px': '--button-size-sm',
        '40px': '--button-size-md',
        '90vh': '--viewport-height-90',
        '95vw': '--viewport-width-95',
        '600px': '--breakpoint-tablet',
        '769px': '--breakpoint-desktop',
        '1024px': '--breakpoint-large',
    }
    
    # Timing variables
    timing_map = {
        '0.01ms': '--motion-instant',
        '0.1s': '--transition-fast',
        '0.2s': '--transition-base',
        '1.5s': '--animation-slow',
    }
    
    variables.update(spacing_map)
    variables.update(sizing_map)
    variables.update(timing_map)
    
    return variables

def main():
    """Main analysis function"""
    
    all_magic = []
    file_stats = {}
    
    print("=" * 70)
    print("CSS MAGIC NUMBER EXTRACTION ANALYSIS")
    print("HIGH-43.3: Phase 3 Extract Magic Numbers")
    print("=" * 70)
    print()
    
    for css_file in CSS_FILES:
        if not Path(css_file).exists():
            print(f"❌ SKIPPED: {css_file} (file not found)")
            continue
        
        with open(css_file, 'r') as f:
            content = f.read()
        
        magic = extract_magic_numbers(content)
        all_magic.extend(magic)
        
        categories = categorize_magic_numbers(magic)
        
        file_stats[css_file] = {
            'total': len(magic),
            'categories': {k: dict(v) for k, v in categories.items()}
        }
        
        print(f"📄 {css_file}")
        print(f"   Total magic numbers: {len(magic)}")
        for cat, nums in categories.items():
            if nums:
                print(f"   - {cat}: {len(nums)} unique values")
        print()
    
    # Generate variables
    variables = generate_css_variables({})
    
    print("=" * 70)
    print("CSS VARIABLE RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    print("SPACING VARIABLES (extracted from magic numbers)")
    print("-" * 70)
    spacing_vars = {k: v for k, v in variables.items() if 'spacing' in v or 'breakpoint' in v}
    for value, var in sorted(spacing_vars.items()):
        print(f"  {var}: {value};")
    print()
    
    print("SIZING VARIABLES (font-size, dimensions)")
    print("-" * 70)
    sizing_vars = {k: v for k, v in variables.items() if 'size' in v or 'radius' in v or 'viewport' in v}
    for value, var in sorted(sizing_vars.items()):
        print(f"  {var}: {value};")
    print()
    
    print("TIMING VARIABLES (transitions, animations)")
    print("-" * 70)
    timing_vars = {k: v for k, v in variables.items() if 'motion' in v or 'transition' in v or 'animation' in v}
    for value, var in sorted(timing_vars.items()):
        print(f"  {var}: {value};")
    print()
    
    # Statistics
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    total_files = len(file_stats)
    total_magic = sum(stats['total'] for stats in file_stats.values())
    unique_magic = len(set(m['full'] for m in all_magic))
    
    print(f"Total CSS files analyzed: {total_files}")
    print(f"Total magic number occurrences: {total_magic}")
    print(f"Unique magic numbers: {unique_magic}")
    print(f"Recommended CSS variables: {len(variables)}")
    print()
    
    # Top magic numbers by frequency
    magic_freq = defaultdict(int)
    for m in all_magic:
        magic_freq[m['full']] += 1
    
    print("TOP 20 MAGIC NUMBERS BY FREQUENCY")
    print("-" * 70)
    for i, (num, count) in enumerate(sorted(magic_freq.items(), key=lambda x: -x[1])[:20], 1):
        print(f"{i:2}. {num:10} - {count:2}x occurrences")
    print()
    
    # Output recommendations
    print("=" * 70)
    print("RECOMMENDED ACTIONS")
    print("=" * 70)
    print("""
1. Add CSS variables to :root selector in a dedicated file:
   - docs/css-variables/spacing.css
   - docs/css-variables/sizing.css
   - docs/css-variables/timing.css
   - docs/css-variables/colors.css (already exists in knowledge-graph-v2.css)

2. Replace magic numbers with variables in:
   - markdown.css (target: 50+ replacements)
   - assistant.css (target: 40+ replacements)
   - knowledgeGraphV2.css (target: 30+ replacements)
   - knowledge-graph-v2.css (already optimized - add remaining 20+)

3. Validation:
   - Run: pytest tests/unit/tools/fengshui/test_css_magic_numbers.py
   - Verify all magic numbers extracted
   - Confirm zero regressions

4. Documentation:
   - Create docs/knowledge/css-design-tokens.md
   - Document spacing, sizing, timing scales
   - Add usage examples

5. Follow-up tasks (auto-increment as t-001, t-002, etc.):
   - t-001: Replace all spacing magic numbers with CSS variables
   - t-002: Replace all sizing magic numbers with CSS variables
   - t-003: Replace all timing magic numbers with CSS variables
   - t-004: Create CSS variables documentation
   - t-005: Implement CSS variables validation in pre-commit
""")

if __name__ == '__main__':
    main()