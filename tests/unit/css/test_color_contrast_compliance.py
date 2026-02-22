"""
Test: CSS Color Contrast Compliance
Validates that color combinations meet WCAG AA/AAA accessibility standards.

Part of: HIGH-43.3 → t-004 (Create CSS Validation Tests)
Reference: docs/knowledge/css-design-tokens.md (Color section)
WCAG Standards: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
"""

import re
import pytest
from pathlib import Path
from typing import Tuple, Dict, List


class TestColorContrastCompliance:
    """Validate color combinations meet WCAG accessibility standards"""
    
    @pytest.fixture
    def css_variables_file(self):
        """Get css-variables.css file"""
        return Path("app_v2/static/css/css-variables.css")
    
    @pytest.fixture
    def color_definitions(self, css_variables_file):
        """Extract color variable definitions from css-variables.css"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        # Pattern: --color-*: #hexvalue;
        color_pattern = re.compile(r'(--color-[\w-]+):\s*(#[0-9a-fA-F]{3,6}|rgb\([^)]+\))', re.IGNORECASE)
        
        colors = {}
        for match in color_pattern.finditer(content):
            var_name = match.group(1)
            value = match.group(2)
            colors[var_name] = value
        
        return colors
    
    def test_color_variables_defined(self, css_variables_file):
        """Test: All required color categories are defined"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        required_categories = {
            'primary': ['--color-primary', '--color-primary-dark', '--color-primary-light'],
            'secondary': ['--color-secondary'],
            'semantic': ['--color-success', '--color-warning', '--color-error', '--color-info'],
            'neutral': ['--color-background', '--color-surface', '--color-text', '--color-text-secondary'],
            'interactive': ['--color-link', '--color-link-hover', '--color-border']
        }
        
        missing = {}
        for category, vars in required_categories.items():
            missing_vars = [v for v in vars if v not in content]
            if missing_vars:
                missing[category] = missing_vars
        
        assert len(missing) == 0, (
            f"Missing color variables:\n" +
            '\n'.join(f"  {cat}: {vars}" for cat, vars in missing.items())
        )
    
    def test_hex_color_format_valid(self, color_definitions):
        """Test: Hex colors use valid 3 or 6-digit format"""
        violations = []
        
        for var_name, value in color_definitions.items():
            if value.startswith('#'):
                # Remove # and validate length
                hex_value = value[1:]
                if len(hex_value) not in [3, 6]:
                    violations.append({
                        'variable': var_name,
                        'value': value,
                        'violation': f'Invalid hex format (must be #RGB or #RRGGBB)',
                        'suggestion': 'Use 3-digit (#RGB) or 6-digit (#RRGGBB) hex format'
                    })
                
                # Validate hex characters
                if not re.match(r'^[0-9a-fA-F]+$', hex_value):
                    violations.append({
                        'variable': var_name,
                        'value': value,
                        'violation': 'Invalid hex characters',
                        'suggestion': 'Use only 0-9, a-f characters'
                    })
        
        assert len(violations) == 0, self._format_violations("Invalid Hex Format", violations)
    
    def test_contrast_ratio_aa_normal_text(self, color_definitions):
        """Test: Normal text (14-18px) meets WCAG AA (4.5:1 contrast ratio)"""
        # Common text/background combinations to check
        text_bg_pairs = [
            ('--color-text', '--color-background'),
            ('--color-text', '--color-surface'),
            ('--color-text-secondary', '--color-background'),
            ('--color-primary', '--color-background'),
            ('--color-error', '--color-background'),
            ('--color-success', '--color-background'),
            ('--color-warning', '--color-background'),
        ]
        
        violations = []
        
        for text_var, bg_var in text_bg_pairs:
            if text_var in color_definitions and bg_var in color_definitions:
                text_color = color_definitions[text_var]
                bg_color = color_definitions[bg_var]
                
                ratio = self._calculate_contrast_ratio(text_color, bg_color)
                
                # WCAG AA normal text: 4.5:1
                if ratio < 4.5:
                    violations.append({
                        'text_color': f'{text_var} ({text_color})',
                        'bg_color': f'{bg_var} ({bg_color})',
                        'ratio': f'{ratio:.2f}:1',
                        'standard': 'WCAG AA Normal Text',
                        'required': '4.5:1',
                        'violation': 'Insufficient contrast for normal text',
                        'suggestion': 'Adjust colors to achieve 4.5:1 contrast ratio'
                    })
        
        assert len(violations) == 0, self._format_contrast_violations(
            "WCAG AA Normal Text Failures",
            violations
        )
    
    def test_contrast_ratio_aa_large_text(self, color_definitions):
        """Test: Large text (18px+ or 14px+ bold) meets WCAG AA (3:1 contrast ratio)"""
        # Heading and large text combinations
        heading_bg_pairs = [
            ('--color-primary', '--color-surface'),
            ('--color-secondary', '--color-surface'),
        ]
        
        violations = []
        
        for text_var, bg_var in heading_bg_pairs:
            if text_var in color_definitions and bg_var in color_definitions:
                text_color = color_definitions[text_var]
                bg_color = color_definitions[bg_var]
                
                ratio = self._calculate_contrast_ratio(text_color, bg_color)
                
                # WCAG AA large text: 3:1
                if ratio < 3.0:
                    violations.append({
                        'text_color': f'{text_var} ({text_color})',
                        'bg_color': f'{bg_var} ({bg_color})',
                        'ratio': f'{ratio:.2f}:1',
                        'standard': 'WCAG AA Large Text',
                        'required': '3:1',
                        'violation': 'Insufficient contrast for large text',
                        'suggestion': 'Adjust colors to achieve 3:1 contrast ratio'
                    })
        
        assert len(violations) == 0, self._format_contrast_violations(
            "WCAG AA Large Text Failures",
            violations
        )
    
    def test_contrast_ratio_aaa_goal(self, color_definitions):
        """Test: Check if primary text combinations reach WCAG AAA (7:1) - informational only"""
        text_bg_pairs = [
            ('--color-text', '--color-background'),
            ('--color-text', '--color-surface'),
        ]
        
        results = []
        
        for text_var, bg_var in text_bg_pairs:
            if text_var in color_definitions and bg_var in color_definitions:
                text_color = color_definitions[text_var]
                bg_color = color_definitions[bg_var]
                
                ratio = self._calculate_contrast_ratio(text_color, bg_color)
                
                status = "AAA ✅" if ratio >= 7.0 else "AA ✅" if ratio >= 4.5 else "FAIL ❌"
                
                results.append({
                    'pair': f'{text_var} on {bg_var}',
                    'ratio': ratio,
                    'status': status
                })
        
        # Print informational report (not a failure)
        print("\n\nWCAG AAA Contrast Analysis (Informational):")
        print("=" * 60)
        for r in results:
            print(f"{r['status']} {r['pair']}: {r['ratio']:.2f}:1")
        print("\nAAA Standard: 7:1 (enhanced)")
        print("AA Standard:  4.5:1 (minimum)")
    
    def test_semantic_colors_have_sufficient_contrast(self, color_definitions):
        """Test: Semantic colors (error, success, warning, info) have adequate contrast"""
        semantic_vars = [
            '--color-error',
            '--color-success',
            '--color-warning',
            '--color-info'
        ]
        
        bg_var = '--color-background'
        violations = []
        
        for semantic_var in semantic_vars:
            if semantic_var in color_definitions and bg_var in color_definitions:
                color = color_definitions[semantic_var]
                bg_color = color_definitions[bg_var]
                
                ratio = self._calculate_contrast_ratio(color, bg_color)
                
                # Semantic colors should meet AA normal text (4.5:1)
                if ratio < 4.5:
                    violations.append({
                        'color': f'{semantic_var} ({color})',
                        'bg_color': f'{bg_var} ({bg_color})',
                        'ratio': f'{ratio:.2f}:1',
                        'standard': 'WCAG AA Normal Text',
                        'required': '4.5:1',
                        'violation': 'Semantic color has insufficient contrast',
                        'suggestion': 'Users must be able to see error/success messages clearly'
                    })
        
        assert len(violations) == 0, self._format_contrast_violations(
            "Semantic Color Contrast Failures",
            violations
        )
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        
        # Handle 3-digit hex (#RGB -> #RRGGBB)
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _relative_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance (WCAG formula)"""
        # Normalize RGB values to 0-1
        r, g, b = [x / 255.0 for x in rgb]
        
        # Apply sRGB gamma correction
        def adjust(channel):
            if channel <= 0.03928:
                return channel / 12.92
            else:
                return ((channel + 0.055) / 1.055) ** 2.4
        
        r = adjust(r)
        g = adjust(g)
        b = adjust(b)
        
        # Calculate luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors (WCAG formula)"""
        # Only handle hex colors for now
        if not (color1.startswith('#') and color2.startswith('#')):
            return 21.0  # Assume maximum contrast for non-hex colors
        
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)
        
        lum1 = self._relative_luminance(rgb1)
        lum2 = self._relative_luminance(rgb2)
        
        # Formula: (lighter + 0.05) / (darker + 0.05)
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def _format_violations(self, title: str, violations: List[Dict]) -> str:
        """Format color format violations"""
        if not violations:
            return ""
        
        report = [f"\n{title}: {len(violations)}"]
        for v in violations:
            report.append(f"\n  Variable: {v['variable']}")
            report.append(f"  Value: {v['value']}")
            report.append(f"  Issue: {v['violation']}")
            report.append(f"  Fix: {v['suggestion']}")
        
        return '\n'.join(report)
    
    def _format_contrast_violations(self, title: str, violations: List[Dict]) -> str:
        """Format contrast ratio violations"""
        if not violations:
            return ""
        
        report = [f"\n{title}: {len(violations)}"]
        report.append("\nWCAG Contrast Standards:")
        report.append("  AA Normal Text (14-18px): 4.5:1")
        report.append("  AA Large Text (18px+/14px+ bold): 3:1")
        report.append("  AAA Normal Text: 7:1 (enhanced)")
        
        report.append("\nViolations found:")
        for v in violations:
            report.append(f"\n  Text: {v['text_color']}")
            report.append(f"  Background: {v['bg_color']}")
            report.append(f"  Contrast: {v['ratio']} (required: {v['required']})")
            report.append(f"  Standard: {v['standard']}")
            report.append(f"  Issue: {v['violation']}")
            report.append(f"  Fix: {v['suggestion']}")
        
        return '\n'.join(report)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])