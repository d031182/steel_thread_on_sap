"""
Test: CSS Timing Values Compliance
Validates that all timing values (transition, animation) use CSS variables instead of magic numbers.

Part of: HIGH-43.3 → t-004 (Create CSS Validation Tests)
Reference: docs/knowledge/css-design-tokens.md (Timing section)
"""

import re
import pytest
from pathlib import Path


class TestTimingCompliance:
    """Validate timing values use design tokens from css-variables.css"""
    
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
    def allowed_timing_variables(self):
        """Timing variables defined in css-variables.css"""
        return {
            '--duration-fast',
            '--duration-normal',
            '--duration-slow',
        }
    
    def test_no_transition_magic_numbers(self, css_files, module_css_files, allowed_timing_variables):
        """Test: All transition durations use CSS variables"""
        violations = []
        
        # Pattern: transition: property duration timing-function
        # Example: transition: opacity 0.3s ease; (VIOLATION)
        # Allowed: transition: opacity var(--timing-fast) ease;
        transition_pattern = re.compile(
            r'transition(?:-duration)?:\s*(?:.*?\s+)?(\d+\.?\d*(?:s|ms))(?:\s|;|$)',
            re.IGNORECASE
        )
        
        for css_file in css_files + module_css_files:
            # Skip css-variables.css (contains definitions)
            if css_file.name == "css-variables.css":
                continue
                
            content = css_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('/*') or line.strip().startswith('*'):
                    continue
                
                matches = transition_pattern.finditer(line)
                for match in matches:
                    duration = match.group(1)
                    # Check if using variable
                    if 'var(' not in line:
                        violations.append({
                            'file': str(css_file),
                            'line': line_num,
                            'content': line.strip(),
                            'violation': f'Transition duration "{duration}" should use CSS variable',
                            'suggestion': f'Use var(--timing-*) instead of {duration}'
                        })
        
        assert len(violations) == 0, self._format_violations(
            "Transition Duration Magic Numbers",
            violations,
            allowed_timing_variables
        )
    
    def test_no_animation_magic_numbers(self, css_files, module_css_files, allowed_timing_variables):
        """Test: All animation durations use CSS variables"""
        violations = []
        
        # Pattern: animation: name duration timing-function
        # Example: animation: fadeIn 0.5s ease; (VIOLATION)
        # Allowed: animation: fadeIn var(--timing-normal) ease;
        animation_pattern = re.compile(
            r'animation(?:-duration)?:\s*(?:.*?\s+)?(\d+\.?\d*(?:s|ms))(?:\s|;|$)',
            re.IGNORECASE
        )
        
        for css_file in css_files + module_css_files:
            if css_file.name == "css-variables.css":
                continue
                
            content = css_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                if line.strip().startswith('/*') or line.strip().startswith('*'):
                    continue
                
                matches = animation_pattern.finditer(line)
                for match in matches:
                    duration = match.group(1)
                    if 'var(' not in line:
                        violations.append({
                            'file': str(css_file),
                            'line': line_num,
                            'content': line.strip(),
                            'violation': f'Animation duration "{duration}" should use CSS variable',
                            'suggestion': f'Use var(--timing-*) instead of {duration}'
                        })
        
        assert len(violations) == 0, self._format_violations(
            "Animation Duration Magic Numbers",
            violations,
            allowed_timing_variables
        )
    
    def test_timing_variables_defined(self):
        """Test: All timing variables are defined in css-variables.css"""
        css_vars_file = Path("app_v2/static/css/css-variables.css")
        content = css_vars_file.read_text(encoding='utf-8')
        
        required_timing_vars = [
            '--duration-fast',
            '--duration-normal',
            '--duration-slow',
        ]
        
        missing = []
        for var in required_timing_vars:
            if var not in content:
                missing.append(var)
        
        assert len(missing) == 0, f"Missing timing variables in css-variables.css: {missing}"
    
    def test_timing_values_valid_units(self):
        """Test: Timing variables use valid CSS time units (s or ms)"""
        css_vars_file = Path("app_v2/static/css/css-variables.css")
        content = css_vars_file.read_text(encoding='utf-8')
        
        # Pattern: --timing-*: value;
        timing_pattern = re.compile(r'(--timing-\w+):\s*([^;]+);')
        
        violations = []
        for match in timing_pattern.finditer(content):
            var_name = match.group(1)
            value = match.group(2).strip()
            
            # Valid time units: s, ms
            if not re.match(r'^\d+\.?\d*(?:s|ms)$', value):
                violations.append({
                    'variable': var_name,
                    'value': value,
                    'violation': f'Invalid time unit in {var_name}: {value}',
                    'suggestion': 'Use s (seconds) or ms (milliseconds)'
                })
        
        assert len(violations) == 0, f"Invalid timing values:\n" + '\n'.join(
            f"  {v['variable']}: {v['value']} - {v['suggestion']}"
            for v in violations
        )
    
    def test_no_delay_magic_numbers(self, css_files, module_css_files):
        """Test: Transition/animation delays use CSS variables"""
        violations = []
        
        # Pattern: transition-delay: 0.5s; or animation-delay: 1s;
        delay_pattern = re.compile(
            r'(?:transition|animation)-delay:\s*(\d+\.?\d*(?:s|ms))(?:\s|;|$)',
            re.IGNORECASE
        )
        
        for css_file in css_files + module_css_files:
            if css_file.name == "css-variables.css":
                continue
                
            content = css_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                if line.strip().startswith('/*') or line.strip().startswith('*'):
                    continue
                
                matches = delay_pattern.finditer(line)
                for match in matches:
                    delay = match.group(1)
                    if 'var(' not in line and delay != '0s' and delay != '0ms':
                        violations.append({
                            'file': str(css_file),
                            'line': line_num,
                            'content': line.strip(),
                            'violation': f'Delay "{delay}" should use CSS variable',
                            'suggestion': 'Use var(--timing-*) for non-zero delays'
                        })
        
        assert len(violations) == 0, self._format_violations(
            "Delay Magic Numbers",
            violations,
            {'--duration-fast', '--duration-normal', '--duration-slow'}
        )
    
    def _format_violations(self, title, violations, allowed_vars):
        """Format violation report"""
        if not violations:
            return ""
        
        report = [f"\n{title} Violations: {len(violations)}"]
        report.append("\nAllowed timing variables:")
        for var in sorted(allowed_vars):
            report.append(f"  {var}")
        
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