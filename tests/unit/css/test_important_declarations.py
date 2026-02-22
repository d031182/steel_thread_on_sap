"""
Test: CSS !important Declarations Compliance
Validates that !important declarations follow project guidelines and are properly documented.

Part of: HIGH-43.3 → t-004 (Create CSS Validation Tests)
Reference: docs/knowledge/css-important-analysis-high-43-1.md
"""

import re
import pytest
from pathlib import Path


class TestImportantDeclarations:
    """Validate !important usage follows project guidelines"""
    
    @pytest.fixture
    def css_files(self):
        """Get all CSS files in app_v2/static/css/"""
        css_dir = Path("app_v2/static/css")
        return list(css_dir.glob("*.css"))
    
    @pytest.fixture
    def module_css_files(self):
        """Get all CSS files in modules/*/frontend/styles/"""
        modules_dir = Path("modules")
        css_files = []
        for module_dir in modules_dir.iterdir():
            if module_dir.is_dir():
                styles_dir = module_dir / "frontend" / "styles"
                if styles_dir.exists():
                    css_files.extend(styles_dir.glob("*.css"))
        return css_files
    
    @pytest.fixture
    def allowed_important_contexts(self):
        """Contexts where !important is acceptable"""
        return {
            'utility_classes',    # .u-hidden, .u-visible, etc.
            'state_overrides',    # .is-disabled, .is-active, etc.
            'accessibility',      # .sr-only, high contrast modes
            'third_party_override' # Override external libraries
        }
    
    def test_important_has_documentation(self, css_files, module_css_files):
        """Test: Each !important has preceding comment explaining why"""
        violations = []
        
        important_pattern = re.compile(r'!\s*important', re.IGNORECASE)
        
        for css_file in css_files + module_css_files:
            content = css_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                if important_pattern.search(line):
                    # Check previous 3 lines for comment explaining !important
                    has_explanation = False
                    check_lines = min(3, line_num - 1)
                    
                    for i in range(1, check_lines + 1):
                        prev_line = lines[line_num - 1 - i].strip()
                        # Look for comment mentioning why !important is needed
                        if '/*' in prev_line and ('important' in prev_line.lower() or 
                                                   'override' in prev_line.lower() or
                                                   'utility' in prev_line.lower() or
                                                   'state' in prev_line.lower()):
                            has_explanation = True
                            break
                    
                    if not has_explanation:
                        violations.append({
                            'file': str(css_file),
                            'line': line_num,
                            'content': line.strip(),
                            'violation': '!important without preceding comment',
                            'suggestion': 'Add comment explaining why !important is necessary'
                        })
        
        assert len(violations) == 0, self._format_violations(
            "Undocumented !important Declarations",
            violations
        )
    
    def test_important_not_in_base_styles(self, css_files, module_css_files):
        """Test: !important not used in base element styles"""
        violations = []
        
        # Base element selectors (not classes or IDs)
        base_element_pattern = re.compile(
            r'^\s*(html|body|h[1-6]|p|a|ul|ol|li|table|tr|td|th|div|span|button|input|select|textarea)\s*\{',
            re.IGNORECASE
        )
        important_pattern = re.compile(r'!\s*important', re.IGNORECASE)
        
        for css_file in css_files + module_css_files:
            content = css_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            in_base_element = False
            base_element_name = None
            brace_count = 0
            
            for line_num, line in enumerate(lines, 1):
                # Check if entering base element rule
                match = base_element_pattern.match(line)
                if match and not in_base_element:
                    in_base_element = True
                    base_element_name = match.group(1)
                    brace_count = line.count('{') - line.count('}')
                elif in_base_element:
                    brace_count += line.count('{') - line.count('}')
                    
                    # Check for !important in base element
                    if important_pattern.search(line):
                        violations.append({
                            'file': str(css_file),
                            'line': line_num,
                            'element': base_element_name,
                            'content': line.strip(),
                            'violation': f'!important in base element "{base_element_name}"',
                            'suggestion': 'Use classes with appropriate specificity instead'
                        })
                    
                    # Exit base element rule
                    if brace_count == 0:
                        in_base_element = False
                        base_element_name = None
        
        assert len(violations) == 0, self._format_violations(
            "!important in Base Element Styles",
            violations
        )
    
    def test_utility_classes_use_important(self, css_files, module_css_files):
        """Test: Utility classes (u-*) properly use !important for single purpose"""
        violations = []
        
        # Utility class pattern: .u-*
        utility_pattern = re.compile(r'\.u-[\w-]+\s*\{')
        important_pattern = re.compile(r'!\s*important', re.IGNORECASE)
        
        for css_file in css_files + module_css_files:
            content = css_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            in_utility_class = False
            utility_name = None
            utility_properties = []
            brace_count = 0
            
            for line_num, line in enumerate(lines, 1):
                # Check if entering utility class
                match = utility_pattern.search(line)
                if match and not in_utility_class:
                    in_utility_class = True
                    utility_name = match.group(0).strip()
                    utility_properties = []
                    brace_count = line.count('{') - line.count('}')
                elif in_utility_class:
                    brace_count += line.count('{') - line.count('}')
                    
                    # Collect properties in utility class
                    if ':' in line and not line.strip().startswith('/*'):
                        property_line = line.strip()
                        has_important = important_pattern.search(property_line)
                        utility_properties.append({
                            'line': line_num,
                            'content': property_line,
                            'has_important': has_important is not None
                        })
                    
                    # Exit utility class
                    if brace_count == 0:
                        # Validate utility class has !important
                        if len(utility_properties) > 0:
                            properties_without_important = [
                                p for p in utility_properties if not p['has_important']
                            ]
                            
                            if properties_without_important:
                                for prop in properties_without_important:
                                    violations.append({
                                        'file': str(css_file),
                                        'line': prop['line'],
                                        'class': utility_name,
                                        'content': prop['content'],
                                        'violation': f'Utility class property missing !important',
                                        'suggestion': 'Utility classes should use !important for single-purpose overrides'
                                    })
                        
                        in_utility_class = False
                        utility_name = None
        
        assert len(violations) == 0, self._format_violations(
            "Utility Classes Missing !important",
            violations
        )
    
    def test_excessive_important_usage(self, css_files, module_css_files):
        """Test: !important usage is below acceptable threshold (< 5% of declarations)"""
        important_pattern = re.compile(r'!\s*important', re.IGNORECASE)
        property_pattern = re.compile(r'[a-z-]+\s*:\s*[^;]+;')
        
        results = []
        
        for css_file in css_files + module_css_files:
            # Skip css-variables.css
            if css_file.name == "css-variables.css":
                continue
                
            content = css_file.read_text(encoding='utf-8')
            
            # Count total property declarations
            total_properties = len(property_pattern.findall(content))
            
            # Count !important declarations
            important_count = len(important_pattern.findall(content))
            
            if total_properties > 0:
                percentage = (important_count / total_properties) * 100
                
                results.append({
                    'file': str(css_file),
                    'total': total_properties,
                    'important': important_count,
                    'percentage': percentage
                })
                
                # Threshold: < 5% acceptable, < 10% warning, >= 10% violation
                if percentage >= 10:
                    pytest.fail(
                        f"\n!important usage too high in {css_file.name}:\n"
                        f"  {important_count}/{total_properties} ({percentage:.1f}%)\n"
                        f"  Threshold: < 10% (warning at 5%)\n"
                        f"  Refactor to use proper specificity instead"
                    )
        
        # Print summary for information
        print("\n!important Usage Summary:")
        for r in sorted(results, key=lambda x: x['percentage'], reverse=True):
            status = "⚠️ " if r['percentage'] >= 5 else "✅"
            print(f"{status} {Path(r['file']).name}: {r['important']}/{r['total']} ({r['percentage']:.1f}%)")
    
    def test_no_important_in_animations(self, css_files, module_css_files):
        """Test: !important not used in @keyframes animations"""
        violations = []
        
        important_pattern = re.compile(r'!\s*important', re.IGNORECASE)
        
        for css_file in css_files + module_css_files:
            content = css_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            in_keyframes = False
            keyframes_name = None
            brace_count = 0
            
            for line_num, line in enumerate(lines, 1):
                # Check if entering @keyframes
                if '@keyframes' in line.lower():
                    in_keyframes = True
                    keyframes_name = line.split('@keyframes')[1].split('{')[0].strip()
                    brace_count = line.count('{') - line.count('}')
                elif in_keyframes:
                    brace_count += line.count('{') - line.count('}')
                    
                    # Check for !important in keyframes
                    if important_pattern.search(line):
                        violations.append({
                            'file': str(css_file),
                            'line': line_num,
                            'animation': keyframes_name,
                            'content': line.strip(),
                            'violation': f'!important in @keyframes "{keyframes_name}"',
                            'suggestion': '!important has no effect in animations and may cause confusion'
                        })
                    
                    # Exit keyframes
                    if brace_count == 0:
                        in_keyframes = False
                        keyframes_name = None
        
        assert len(violations) == 0, self._format_violations(
            "!important in @keyframes",
            violations
        )
    
    def _format_violations(self, title, violations):
        """Format violation report"""
        if not violations:
            return ""
        
        report = [f"\n{title}: {len(violations)}"]
        report.append("\nViolations found:")
        
        for v in violations[:10]:  # Show first 10
            report.append(f"\n  File: {v['file']}")
            report.append(f"  Line {v['line']}: {v['content']}")
            report.append(f"  Issue: {v['violation']}")
            report.append(f"  Fix: {v['suggestion']}")
        
        if len(violations) > 10:
            report.append(f"\n... and {len(violations) - 10} more violations")
        
        return '\n'.join(report)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])