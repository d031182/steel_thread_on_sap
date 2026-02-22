#!/usr/bin/env python3
"""
Analyze and help eliminate !important declarations in CSS files.

This script:
1. Scans all CSS files for !important declarations
2. Analyzes specificity conflicts
3. Generates replacement strategies
4. Provides detailed migration plan

HIGH-43.1: Phase 1 - Eliminate !important
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class ImportantAnalyzer:
    """Analyzes !important usage and suggests specificity-based replacements."""
    
    def __init__(self, css_dir: str = "app_v2/static/css"):
        self.css_dir = Path(css_dir)
        self.module_css_paths = [
            Path("modules/ai_assistant/frontend/styles"),
            Path("modules/knowledge_graph_v2/frontend/styles")
        ]
        self.results = {
            'total_important': 0,
            'by_file': {},
            'by_property': defaultdict(int),
            'by_category': defaultdict(int)
        }
        
    def find_css_files(self) -> List[Path]:
        """Find all CSS files to analyze."""
        css_files = []
        
        # App-level CSS
        if self.css_dir.exists():
            css_files.extend(self.css_dir.glob("*.css"))
        
        # Module-level CSS
        for module_path in self.module_css_paths:
            if module_path.exists():
                css_files.extend(module_path.glob("*.css"))
        
        return sorted(css_files)
    
    def extract_important_rules(self, content: str) -> List[Dict]:
        """Extract all rules containing !important."""
        important_rules = []
        
        # Pattern to match CSS rules with !important
        # Matches: property: value !important;
        pattern = r'([a-z-]+)\s*:\s*([^;!]+)\s*!important\s*;'
        
        for match in re.finditer(pattern, content, re.IGNORECASE):
            property_name = match.group(1).strip()
            value = match.group(2).strip()
            
            # Find the selector for this rule (work backwards)
            before_match = content[:match.start()]
            selector_match = re.findall(r'([^{}]+)\s*\{[^}]*$', before_match)
            selector = selector_match[-1].strip() if selector_match else "unknown"
            
            important_rules.append({
                'selector': selector,
                'property': property_name,
                'value': value,
                'full_declaration': f"{property_name}: {value} !important;",
                'position': match.start()
            })
            
        return important_rules
    
    def categorize_property(self, property_name: str) -> str:
        """Categorize CSS property for analysis."""
        layout_props = ['display', 'position', 'top', 'bottom', 'left', 'right', 
                       'float', 'clear', 'z-index', 'width', 'height', 'min-width', 
                       'max-width', 'min-height', 'max-height']
        spacing_props = ['margin', 'margin-top', 'margin-right', 'margin-bottom', 
                        'margin-left', 'padding', 'padding-top', 'padding-right', 
                        'padding-bottom', 'padding-left']
        typography_props = ['font', 'font-size', 'font-weight', 'font-family', 
                          'line-height', 'text-align', 'text-decoration', 'color']
        visual_props = ['background', 'background-color', 'border', 'border-radius', 
                       'box-shadow', 'opacity', 'visibility']
        
        if property_name in layout_props:
            return 'layout'
        elif property_name in spacing_props:
            return 'spacing'
        elif property_name in typography_props:
            return 'typography'
        elif property_name in visual_props:
            return 'visual'
        else:
            return 'other'
    
    def calculate_specificity(self, selector: str) -> Tuple[int, int, int]:
        """
        Calculate CSS specificity (a, b, c) where:
        a = count of ID selectors
        b = count of class selectors, attributes, pseudo-classes
        c = count of element selectors, pseudo-elements
        """
        # Remove pseudo-elements and content in parentheses for simpler parsing
        selector = re.sub(r'::[a-z-]+', '', selector)
        selector = re.sub(r'\([^)]*\)', '', selector)
        
        id_count = len(re.findall(r'#[a-z0-9_-]+', selector, re.IGNORECASE))
        class_count = len(re.findall(r'\.[a-z0-9_-]+', selector, re.IGNORECASE))
        attr_count = len(re.findall(r'\[[^\]]+\]', selector))
        pseudo_class_count = len(re.findall(r':[a-z-]+', selector, re.IGNORECASE))
        element_count = len(re.findall(r'(?:^|[\s>+~])([a-z][a-z0-9]*)', selector, re.IGNORECASE))
        
        return (id_count, class_count + attr_count + pseudo_class_count, element_count)
    
    def suggest_replacement(self, rule: Dict) -> Dict:
        """Suggest a specificity-based replacement for !important."""
        selector = rule['selector']
        property_name = rule['property']
        value = rule['value']
        
        # Calculate current specificity
        spec = self.calculate_specificity(selector)
        
        suggestions = []
        
        # Strategy 1: Increase specificity with element duplication
        if spec[0] == 0:  # No ID
            suggestions.append({
                'strategy': 'duplicate_selector',
                'selector': f"{selector}{selector.split()[0] if ' ' in selector else selector}",
                'reason': 'Duplicate first part of selector to increase specificity',
                'specificity_increase': (0, 0, 1)
            })
        
        # Strategy 2: Add body prefix
        if not selector.startswith('body'):
            suggestions.append({
                'strategy': 'body_prefix',
                'selector': f"body {selector}",
                'reason': 'Add body prefix to increase specificity',
                'specificity_increase': (0, 0, 1)
            })
        
        # Strategy 3: Use :where() for specificity control (modern CSS)
        suggestions.append({
            'strategy': 'where_pseudo',
            'selector': f":where({selector})",
            'reason': 'Use :where() to have 0 specificity, then layer appropriately',
            'specificity_increase': (0, 0, 0),
            'note': 'Requires CSS cascade layers'
        })
        
        # Strategy 4: Add attribute selector
        if '[' not in selector:
            suggestions.append({
                'strategy': 'attribute_selector',
                'selector': f"{selector}[class]",
                'reason': 'Add generic attribute selector to increase specificity',
                'specificity_increase': (0, 1, 0)
            })
        
        # Strategy 5: Context-specific suggestions
        category = self.categorize_property(property_name)
        if category == 'layout' and property_name in ['display', 'position']:
            suggestions.append({
                'strategy': 'component_scoping',
                'selector': f".component-root {selector}",
                'reason': f'Scope {property_name} to component root to avoid conflicts',
                'specificity_increase': (0, 1, 0)
            })
        
        return {
            'original': rule,
            'current_specificity': spec,
            'suggestions': suggestions,
            'category': category
        }
    
    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze a single CSS file for !important usage."""
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            return {'error': str(e), 'important_count': 0}
        
        important_rules = self.extract_important_rules(content)
        
        file_results = {
            'path': str(filepath),
            'important_count': len(important_rules),
            'rules': important_rules,
            'replacements': []
        }
        
        # Generate replacement suggestions
        for rule in important_rules:
            replacement = self.suggest_replacement(rule)
            file_results['replacements'].append(replacement)
            
            # Track statistics
            self.results['by_property'][rule['property']] += 1
            category = self.categorize_property(rule['property'])
            self.results['by_category'][category] += 1
        
        return file_results
    
    def analyze_all(self) -> Dict:
        """Analyze all CSS files."""
        css_files = self.find_css_files()
        
        print(f"Found {len(css_files)} CSS files to analyze")
        print("=" * 80)
        
        for filepath in css_files:
            print(f"\nAnalyzing: {filepath}")
            file_results = self.analyze_file(filepath)
            
            if 'error' in file_results:
                print(f"  ERROR: {file_results['error']}")
                continue
            
            self.results['by_file'][str(filepath)] = file_results
            self.results['total_important'] += file_results['important_count']
            
            print(f"  Found {file_results['important_count']} !important declarations")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive analysis report."""
        report = []
        report.append("# CSS !important Declaration Analysis")
        report.append(f"**Total !important declarations found**: {self.results['total_important']}")
        report.append("")
        
        # Summary by file
        report.append("## By File")
        report.append("")
        report.append("| File | Count |")
        report.append("|------|-------|")
        for filepath, data in sorted(self.results['by_file'].items(), 
                                    key=lambda x: x[1]['important_count'], 
                                    reverse=True):
            count = data['important_count']
            if count > 0:
                report.append(f"| {Path(filepath).name} | {count} |")
        report.append("")
        
        # Summary by property
        report.append("## By Property")
        report.append("")
        report.append("| Property | Count |")
        report.append("|----------|-------|")
        for prop, count in sorted(self.results['by_property'].items(), 
                                  key=lambda x: x[1], 
                                  reverse=True)[:20]:
            report.append(f"| {prop} | {count} |")
        report.append("")
        
        # Summary by category
        report.append("## By Category")
        report.append("")
        report.append("| Category | Count |")
        report.append("|----------|-------|")
        for category, count in sorted(self.results['by_category'].items(), 
                                      key=lambda x: x[1], 
                                      reverse=True):
            report.append(f"| {category} | {count} |")
        report.append("")
        
        # Detailed replacement strategies
        report.append("## Replacement Strategies")
        report.append("")
        
        for filepath, data in self.results['by_file'].items():
            if data['important_count'] == 0:
                continue
                
            report.append(f"### {Path(filepath).name}")
            report.append("")
            
            for replacement in data['replacements']:
                rule = replacement['original']
                report.append(f"**Selector**: `{rule['selector']}`")
                report.append(f"**Property**: `{rule['property']}: {rule['value']} !important;`")
                report.append(f"**Category**: {replacement['category']}")
                report.append(f"**Current Specificity**: {replacement['current_specificity']}")
                report.append("")
                report.append("**Suggested Replacements**:")
                report.append("")
                
                for i, suggestion in enumerate(replacement['suggestions'][:3], 1):
                    report.append(f"{i}. **{suggestion['strategy']}**")
                    report.append(f"   - Selector: `{suggestion['selector']}`")
                    report.append(f"   - Reason: {suggestion['reason']}")
                    if 'note' in suggestion:
                        report.append(f"   - Note: {suggestion['note']}")
                    report.append("")
                
                report.append("---")
                report.append("")
        
        return "\n".join(report)
    
    def generate_migration_plan(self) -> str:
        """Generate a step-by-step migration plan."""
        plan = []
        plan.append("# !important Elimination Migration Plan")
        plan.append("")
        plan.append("## Overview")
        plan.append("")
        plan.append(f"- Total !important declarations: {self.results['total_important']}")
        plan.append(f"- Files affected: {len([f for f, d in self.results['by_file'].items() if d['important_count'] > 0])}")
        plan.append("")
        
        plan.append("## Migration Strategy")
        plan.append("")
        plan.append("1. **Backup**: Create git checkpoint before starting")
        plan.append("2. **Categorize**: Group by category (layout, typography, visual, spacing)")
        plan.append("3. **Prioritize**: Start with low-risk categories (spacing, visual)")
        plan.append("4. **Test**: Visual regression test after each file")
        plan.append("5. **Commit**: Atomic commits per file for easy rollback")
        plan.append("")
        
        plan.append("## Phase 1: Low-Risk Categories (Spacing, Visual)")
        plan.append("")
        
        low_risk_props = []
        for filepath, data in self.results['by_file'].items():
            for replacement in data['replacements']:
                if replacement['category'] in ['spacing', 'visual']:
                    low_risk_props.append({
                        'file': Path(filepath).name,
                        'selector': replacement['original']['selector'],
                        'property': replacement['original']['property'],
                        'category': replacement['category']
                    })
        
        plan.append(f"**Count**: {len(low_risk_props)} declarations")
        plan.append("")
        
        plan.append("## Phase 2: Medium-Risk Categories (Typography)")
        plan.append("")
        
        medium_risk_props = []
        for filepath, data in self.results['by_file'].items():
            for replacement in data['replacements']:
                if replacement['category'] in ['typography']:
                    medium_risk_props.append({
                        'file': Path(filepath).name,
                        'selector': replacement['original']['selector'],
                        'property': replacement['original']['property'],
                        'category': replacement['category']
                    })
        
        plan.append(f"**Count**: {len(medium_risk_props)} declarations")
        plan.append("")
        
        plan.append("## Phase 3: High-Risk Categories (Layout)")
        plan.append("")
        
        high_risk_props = []
        for filepath, data in self.results['by_file'].items():
            for replacement in data['replacements']:
                if replacement['category'] in ['layout']:
                    high_risk_props.append({
                        'file': Path(filepath).name,
                        'selector': replacement['original']['selector'],
                        'property': replacement['original']['property'],
                        'category': replacement['category']
                    })
        
        plan.append(f"**Count**: {len(high_risk_props)} declarations")
        plan.append("")
        
        plan.append("## Testing Checklist")
        plan.append("")
        plan.append("- [ ] Run CSS validation tests")
        plan.append("- [ ] Visual regression testing in Chrome")
        plan.append("- [ ] Visual regression testing in Firefox")
        plan.append("- [ ] Visual regression testing in Safari")
        plan.append("- [ ] Test responsive layouts (mobile, tablet, desktop)")
        plan.append("- [ ] Test dark mode (if applicable)")
        plan.append("- [ ] Test all module overlays (AI Assistant, Knowledge Graph)")
        plan.append("")
        
        return "\n".join(plan)


def main():
    """Run the !important declaration analysis."""
    analyzer = ImportantAnalyzer()
    
    print("Starting CSS !important declaration analysis...")
    print("=" * 80)
    
    # Run analysis
    results = analyzer.analyze_all()
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print(f"Total !important declarations: {results['total_important']}")
    
    # Generate and save report
    report = analyzer.generate_report()
    report_path = Path("docs/knowledge/css-important-analysis.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    print(f"\nDetailed report saved to: {report_path}")
    
    # Generate and save migration plan
    plan = analyzer.generate_migration_plan()
    plan_path = Path("docs/knowledge/css-important-migration-plan.md")
    plan_path.write_text(plan, encoding='utf-8')
    print(f"Migration plan saved to: {plan_path}")
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("1. Review the analysis report: docs/knowledge/css-important-analysis.md")
    print("2. Review the migration plan: docs/knowledge/css-important-migration-plan.md")
    print("3. Create git checkpoint: git add . && git commit -m 'checkpoint: before !important removal'")
    print("4. Start with Phase 1 (Low-Risk) replacements")
    print("5. Test thoroughly after each file modification")


if __name__ == "__main__":
    main()