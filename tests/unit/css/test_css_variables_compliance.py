"""
CSS Variables Compliance Tests
===============================
Validates that all CSS files use design tokens instead of magic numbers.
Part of CSS-004: Create CSS Validation Tests
"""

import re
import pytest


class TestCSSVariablesCompliance:
    """Test suite for CSS variable usage compliance."""

    @pytest.fixture
    def css_files(self):
        """Load CSS files for testing."""
        return {
            'ai-assistant': 'app_v2/static/css/ai-assistant.css',
            'variables': 'app_v2/static/css/css-variables.css',
        }

    def test_css_variables_file_exists(self, css_files):
        """CSS-004.1: Verify css-variables.css exists and is not empty."""
        with open(css_files['variables']) as f:
            content = f.read()
        assert len(content) > 0
        assert ':root' in content

    def test_css_variables_required_spacing_tokens(self, css_files):
        """CSS-004.2: Verify all required spacing tokens are defined."""
        with open(css_files['variables']) as f:
            content = f.read()
        
        required_tokens = [
            '--spacing-xs', '--spacing-sm', '--spacing-md',
            '--spacing-lg', '--spacing-xl', '--spacing-xxl'
        ]
        for token in required_tokens:
            assert token in content, f"Missing spacing token: {token}"

    def test_css_variables_required_sizing_tokens(self, css_files):
        """CSS-004.3: Verify all required sizing tokens are defined."""
        with open(css_files['variables']) as f:
            content = f.read()
        
        required_tokens = [
            '--touch-target-size', '--button-min-width',
            '--input-min-width', '--radius-sm', '--radius-md', '--radius-lg'
        ]
        for token in required_tokens:
            assert token in content, f"Missing sizing token: {token}"

    def test_css_variables_required_timing_tokens(self, css_files):
        """CSS-004.4: Verify all required timing tokens are defined."""
        with open(css_files['variables']) as f:
            content = f.read()
        
        required_tokens = [
            '--duration-fast', '--duration-normal', '--duration-slow',
            '--easing-ease', '--easing-ease-in-out', '--easing-linear'
        ]
        for token in required_tokens:
            assert token in content, f"Missing timing token: {token}"

    def test_ai_assistant_css_imports_variables(self, css_files):
        """CSS-005.1: Verify ai-assistant.css imports css-variables.css."""
        with open(css_files['ai-assistant']) as f:
            content = f.read()
        
        assert "@import url('css-variables.css')" in content, \
            "ai-assistant.css must import css-variables.css"

    def test_ai_assistant_uses_spacing_variables(self, css_files):
        """CSS-005.2: Verify ai-assistant.css uses spacing variables."""
        with open(css_files['ai-assistant']) as f:
            content = f.read()
        
        # Check for usage of spacing variables
        spacing_usages = [
            'var(--spacing-xs)',
            'var(--spacing-sm)',
            'var(--spacing-md)',
            'var(--spacing-lg)',
        ]
        usages_found = sum(1 for usage in spacing_usages if usage in content)
        assert usages_found >= 4, \
            f"ai-assistant.css should use spacing variables (found {usages_found}/4)"

    def test_ai_assistant_uses_timing_variables(self, css_files):
        """CSS-005.3: Verify ai-assistant.css uses timing variables."""
        with open(css_files['ai-assistant']) as f:
            content = f.read()
        
        assert 'var(--duration-fast)' in content or 'var(--duration-normal)' in content, \
            "ai-assistant.css should use timing variables"

    def test_ai_assistant_minimal_magic_numbers(self, css_files):
        """CSS-005.4: Verify ai-assistant.css has minimal remaining magic numbers."""
        with open(css_files['ai-assistant']) as f:
            content = f.read()
        
        # Find all px/rem/em/ms values that are NOT in comments
        # and NOT part of 'var(' expressions
        lines = content.split('\n')
        magic_count = 0
        
        for line in lines:
            if '/*' in line or '*' in line and '*/' in line:
                continue  # Skip comments
            if 'var(' in line:
                continue  # Skip CSS variable references
            if 'rgba(' in line or 'rgb(' in line:
                continue  # Skip colors
            
            # Count remaining direct values (should be minimal)
            matches = re.findall(r'\b\d+(?:\.\d+)?(?:px|rem|em|ms|s)\b', line)
            magic_count += len(matches)
        
        # After CSS-001/002/003, reasonable exceptions remain (20px list padding, font-size em values, etc)
        assert magic_count < 30, \
            f"ai-assistant.css has too many magic numbers: {magic_count}"

    @pytest.mark.parametrize("spacing_var", [
        'spacing-xs', 'spacing-sm', 'spacing-md', 'spacing-lg'
    ])
    def test_spacing_variables_valid_units(self, css_files, spacing_var):
        """CSS-005.5: Verify spacing variables have valid rem units."""
        with open(css_files['variables']) as f:
            content = f.read()
        
        pattern = f"--{spacing_var}:\\s*([\\d.]+)(rem|px)"
        match = re.search(pattern, content)
        assert match, f"Spacing variable --{spacing_var} not found or invalid"
        assert match.group(2) == 'rem', \
            f"Spacing variable --{spacing_var} should use rem units, got {match.group(2)}"

    def test_color_variables_consistent_format(self, css_files):
        """CSS-005.6: Verify color variables use consistent hex format."""
        with open(css_files['variables']) as f:
            content = f.read()
        
        # Find all color variable definitions (handle spaces after colon)
        color_vars = re.findall(r'--color-[\w-]+:\s*(#[0-9a-fA-F]+)', content)
        assert len(color_vars) > 0, "No color variables found"
        
        # All should be hex format
        for color in color_vars:
            assert color.startswith('#'), f"Invalid color format: {color}"
            assert len(color) in [4, 7], f"Hex color should be #RGB or #RRGGBB: {color}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])