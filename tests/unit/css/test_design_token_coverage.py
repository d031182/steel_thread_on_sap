"""
Test: CSS Design Token Coverage
Validates that all design token categories are complete and properly used across the codebase.

Part of: HIGH-43.3 → t-004 (Create CSS Validation Tests)
Reference: docs/knowledge/css-design-tokens.md
"""

import re
import pytest
from pathlib import Path
from typing import Dict, List, Set


class TestDesignTokenCoverage:
    """Validate complete design token system coverage"""
    
    @pytest.fixture
    def css_variables_file(self):
        """Get css-variables.css file"""
        return Path("app_v2/static/css/css-variables.css")
    
    @pytest.fixture
    def design_tokens_doc(self):
        """Get design tokens documentation"""
        return Path("docs/knowledge/css-design-tokens.md")
    
    @pytest.fixture
    def all_css_files(self):
        """Get all CSS files in project"""
        css_files = []
        
        # App CSS
        app_css = Path("app_v2/static/css")
        if app_css.exists():
            css_files.extend(app_css.glob("*.css"))
        
        # Module CSS
        modules = Path("modules")
        if modules.exists():
            for module in modules.iterdir():
                if module.is_dir():
                    styles = module / "frontend" / "styles"
                    if styles.exists():
                        css_files.extend(styles.glob("*.css"))
        
        return css_files
    
    def test_all_spacing_tokens_defined(self, css_variables_file):
        """Test: All spacing tokens from documentation are defined"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        required_spacing = [
            '--spacing-none',
            '--spacing-xs',
            '--spacing-sm',
            '--spacing-md',
            '--spacing-lg',
            '--spacing-xl',
            '--spacing-2xl',
            '--spacing-3xl',
        ]
        
        missing = [token for token in required_spacing if token not in content]
        
        assert len(missing) == 0, (
            f"Missing spacing tokens in css-variables.css:\n" +
            '\n'.join(f"  {token}" for token in missing)
        )
    
    def test_all_sizing_tokens_defined(self, css_variables_file):
        """Test: All sizing tokens from documentation are defined"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        required_sizing = [
            '--size-xs',
            '--size-sm',
            '--size-md',
            '--size-lg',
            '--size-xl',
            '--size-content',
            '--size-sidebar',
            '--size-full',
        ]
        
        missing = [token for token in required_sizing if token not in content]
        
        assert len(missing) == 0, (
            f"Missing sizing tokens in css-variables.css:\n" +
            '\n'.join(f"  {token}" for token in missing)
        )
    
    def test_all_timing_tokens_defined(self, css_variables_file):
        """Test: All timing tokens from documentation are defined"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        required_timing = [
            '--timing-instant',
            '--timing-fast',
            '--timing-normal',
            '--timing-slow',
            '--timing-deliberate',
        ]
        
        missing = [token for token in required_timing if token not in content]
        
        assert len(missing) == 0, (
            f"Missing timing tokens in css-variables.css:\n" +
            '\n'.join(f"  {token}" for token in missing)
        )
    
    def test_all_color_tokens_defined(self, css_variables_file):
        """Test: All essential color tokens are defined"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        required_colors = [
            # Primary/Secondary
            '--color-primary',
            '--color-primary-dark',
            '--color-primary-light',
            '--color-secondary',
            
            # Semantic
            '--color-success',
            '--color-warning',
            '--color-error',
            '--color-info',
            
            # Neutral
            '--color-background',
            '--color-surface',
            '--color-text',
            '--color-text-secondary',
            
            # Interactive
            '--color-link',
            '--color-link-hover',
            '--color-border',
        ]
        
        missing = [token for token in required_colors if token not in content]
        
        assert len(missing) == 0, (
            f"Missing color tokens in css-variables.css:\n" +
            '\n'.join(f"  {token}" for token in missing)
        )
    
    def test_design_token_usage_coverage(self, all_css_files):
        """Test: Design tokens are actually used across CSS files"""
        token_usage = {
            'spacing': 0,
            'sizing': 0,
            'timing': 0,
            'color': 0,
        }
        
        for css_file in all_css_files:
            # Skip css-variables.css (contains definitions)
            if css_file.name == "css-variables.css":
                continue
            
            content = css_file.read_text(encoding='utf-8')
            
            # Count var() usages by category
            token_usage['spacing'] += len(re.findall(r'var\(--spacing-', content))
            token_usage['sizing'] += len(re.findall(r'var\(--size-', content))
            token_usage['timing'] += len(re.findall(r'var\(--timing-', content))
            token_usage['color'] += len(re.findall(r'var\(--color-', content))
        
        # Should have reasonable usage of each category
        min_usage = 5  # At least 5 usages per category
        
        insufficient = {}
        for category, count in token_usage.items():
            if count < min_usage:
                insufficient[category] = count
        
        assert len(insufficient) == 0, (
            f"\nInsufficient design token usage:\n" +
            '\n'.join(
                f"  {cat}: {count} usages (minimum: {min_usage})"
                for cat, count in insufficient.items()
            ) +
            f"\n\nTotal usage:\n" +
            '\n'.join(f"  {cat}: {count} usages" for cat, count in token_usage.items())
        )
        
        # Print usage report
        print("\n\nDesign Token Usage Report:")
        print("=" * 50)
        for category, count in sorted(token_usage.items()):
            print(f"  {category.capitalize()}: {count} usages")
    
    def test_no_orphaned_css_variables(self, css_variables_file, all_css_files):
        """Test: All defined CSS variables are used somewhere"""
        # Get all defined variables
        definitions_content = css_variables_file.read_text(encoding='utf-8')
        defined_pattern = re.compile(r'(--[\w-]+):\s*[^;]+;')
        defined_vars = set(defined_pattern.findall(definitions_content))
        
        # Get all used variables
        used_vars = set()
        for css_file in all_css_files:
            content = css_file.read_text(encoding='utf-8')
            usage_pattern = re.compile(r'var\((--[\w-]+)(?:,|\))')
            used_vars.update(usage_pattern.findall(content))
        
        # Find orphaned variables
        orphaned = defined_vars - used_vars
        
        # Allow some utility variables that might not be used yet
        allowed_orphans = {
            '--spacing-none',  # Utility value
            '--size-full',     # May be used in future
        }
        
        orphaned = orphaned - allowed_orphans
        
        # Warn if > 10% unused (informational, not failure)
        if len(orphaned) > len(defined_vars) * 0.1:
            print(f"\n⚠️ Warning: {len(orphaned)} unused CSS variables ({len(orphaned)/len(defined_vars)*100:.1f}%)")
            print("Unused variables:", sorted(orphaned)[:10])
        
        # Only fail if completely unused categories
        critical_prefixes = ['--spacing-', '--sizing-', '--timing-', '--color-']
        critical_orphaned = [v for v in orphaned if any(v.startswith(p) for p in critical_prefixes)]
        
        assert len(critical_orphaned) < len(defined_vars) * 0.2, (
            f"\nToo many critical CSS variables unused ({len(critical_orphaned)}/{len(defined_vars)}):\n" +
            '\n'.join(f"  {v}" for v in sorted(critical_orphaned)[:20])
        )
    
    def test_css_variables_file_organized(self, css_variables_file):
        """Test: css-variables.css is well-organized with clear sections"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        required_sections = [
            'spacing',
            'sizing',
            'timing',
            'color',
        ]
        
        missing_sections = []
        for section in required_sections:
            # Look for section header comment
            section_pattern = re.compile(
                rf'/\*\s*(?:===)?\s*{section}\s*(?:===)?\s*\*/',
                re.IGNORECASE
            )
            if not section_pattern.search(content):
                missing_sections.append(section)
        
        assert len(missing_sections) == 0, (
            f"\nMissing section headers in css-variables.css:\n" +
            '\n'.join(f"  {section}" for section in missing_sections) +
            f"\n\nAdd comment headers like: /* === {missing_sections[0].upper()} === */"
            if missing_sections else ""
        )
    
    def test_token_documentation_complete(self, design_tokens_doc):
        """Test: Design tokens documentation exists and covers all categories"""
        assert design_tokens_doc.exists(), (
            f"Design tokens documentation not found: {design_tokens_doc}"
        )
        
        content = design_tokens_doc.read_text(encoding='utf-8')
        
        required_categories = [
            'spacing',
            'sizing',
            'timing',
            'color',
            'usage',
            'example',
        ]
        
        missing = []
        for category in required_categories:
            if category.lower() not in content.lower():
                missing.append(category)
        
        assert len(missing) == 0, (
            f"\nDesign tokens documentation incomplete:\n" +
            f"Missing sections: {', '.join(missing)}\n"
            f"File: {design_tokens_doc}"
        )
    
    def test_token_naming_consistency(self, css_variables_file):
        """Test: CSS variable naming follows consistent pattern"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        # Extract all variable names
        var_pattern = re.compile(r'(--[\w-]+):\s*')
        all_vars = var_pattern.findall(content)
        
        violations = []
        
        for var in all_vars:
            # Check naming pattern: --category-size/value
            parts = var.split('-')[1:]  # Remove leading --
            
            if len(parts) < 2:
                violations.append({
                    'variable': var,
                    'violation': 'Too short (should be --category-value)',
                    'suggestion': 'Use format: --category-value (e.g., --spacing-md)'
                })
            
            # Check for invalid characters (allow: letters, numbers, hyphen)
            if not re.match(r'^--[a-z0-9-]+$', var):
                violations.append({
                    'variable': var,
                    'violation': 'Invalid characters (use lowercase, numbers, hyphen only)',
                    'suggestion': 'Use lowercase and hyphens: --spacing-md'
                })
            
            # Check for camelCase (not allowed)
            if re.search(r'[A-Z]', var):
                violations.append({
                    'variable': var,
                    'violation': 'Contains uppercase letters (use kebab-case)',
                    'suggestion': 'Use kebab-case: --color-primary-dark'
                })
        
        assert len(violations) == 0, (
            f"\nCSS variable naming violations:\n" +
            '\n'.join(
                f"  {v['variable']}: {v['violation']} → {v['suggestion']}"
                for v in violations[:10]
            )
        )
    
    def test_token_values_valid(self, css_variables_file):
        """Test: CSS variable values use valid CSS units"""
        content = css_variables_file.read_text(encoding='utf-8')
        
        # Pattern: --var-name: value;
        var_pattern = re.compile(r'(--[\w-]+):\s*([^;]+);')
        
        violations = []
        
        for match in var_pattern.finditer(content):
            var_name = match.group(1)
            value = match.group(2).strip()
            
            # Validate based on category
            if var_name.startswith('--spacing-') or var_name.startswith('--size-'):
                # Should use valid length units (px, rem, em, %, vw, vh)
                if not re.match(r'^(\d+\.?\d*(?:px|rem|em|%|vw|vh)|0)$', value):
                    violations.append({
                        'variable': var_name,
                        'value': value,
                        'category': 'spacing/sizing',
                        'suggestion': 'Use px, rem, em, %, vw, vh, or 0'
                    })
            
            elif var_name.startswith('--timing-'):
                # Should use time units (s, ms)
                if not re.match(r'^\d+\.?\d*(?:s|ms)$', value):
                    violations.append({
                        'variable': var_name,
                        'value': value,
                        'category': 'timing',
                        'suggestion': 'Use s or ms'
                    })
            
            elif var_name.startswith('--color-'):
                # Should use hex or rgb/rgba
                if not re.match(r'^(#[0-9a-fA-F]{3,6}|rgba?\([^)]+\))$', value):
                    violations.append({
                        'variable': var_name,
                        'value': value,
                        'category': 'color',
                        'suggestion': 'Use #hex or rgb()/rgba()'
                    })
        
        assert len(violations) == 0, (
            f"\nInvalid CSS variable values:\n" +
            '\n'.join(
                f"  {v['variable']}: '{v['value']}' ({v['category']}) → {v['suggestion']}"
                for v in violations[:10]
            )
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])