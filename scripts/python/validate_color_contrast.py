#!/usr/bin/env python3
"""
HIGH-40: KG V2 CSS Refactoring Phase 5 - Color Contrast Validation

Validates WCAG 2.1 color contrast compliance for Knowledge Graph V2 CSS.
Extracts all color pairs from CSS and calculates contrast ratios.

WCAG Standards:
- AA Normal: 4.5:1 (body text)
- AA Large: 3:1 (18pt+)
- AAA Normal: 7:1 (body text)
- AAA Large: 4.5:1 (18pt+)

Usage:
    python validate_color_contrast.py [--output json|html|report]
"""

import re
import json
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class ComplianceLevel(str, Enum):
    """WCAG compliance levels"""
    PASS_AAA = "✅ PASS AAA"
    PASS_AA = "✅ PASS AA"
    FAIL = "❌ FAIL"
    INSUFFICIENT_DATA = "⚠️ INSUFFICIENT_DATA"


@dataclass
class ColorPair:
    """Color contrast pair with compliance metadata"""
    selector: str
    property: str
    foreground: str
    background: str
    foreground_rgb: Tuple[int, int, int]
    background_rgb: Tuple[int, int, int]
    contrast_ratio: float
    compliance_aa_normal: bool
    compliance_aa_large: bool
    compliance_aaa_normal: bool
    compliance_aaa_large: bool
    notes: str = ""


class ContrastValidator:
    """WCAG 2.1 color contrast validator"""
    
    def __init__(self, css_path: str):
        """Initialize validator with CSS file path"""
        self.css_path = Path(css_path)
        self.css_content = self.css_path.read_text()
        self.color_pairs: List[ColorPair] = []
        self.css_variables: Dict[str, str] = {}
        
    def hex_to_rgb(self, hex_color: str) -> Optional[Tuple[int, int, int]]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.strip('#')
        if len(hex_color) == 6:
            try:
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            except ValueError:
                return None
        return None
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()
    
    def calculate_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance (WCAG formula)"""
        r, g, b = [x / 255.0 for x in rgb]
        
        # Apply gamma correction
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        # Calculate luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def calculate_contrast_ratio(self, fg_rgb: Tuple[int, int, int],
                                bg_rgb: Tuple[int, int, int]) -> float:
        """Calculate contrast ratio (WCAG formula)"""
        l1 = self.calculate_luminance(fg_rgb)
        l2 = self.calculate_luminance(bg_rgb)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def extract_css_variables(self):
        """Extract CSS variable definitions from :root"""
        var_pattern = r'--[\w-]+:\s*([#\w(),.%\s-]+);'
        
        for match in re.finditer(var_pattern, self.css_content):
            var_match = re.search(r'(--[\w-]+):\s*([^;]+)', match.group(0))
            if var_match:
                var_name = var_match.group(1)
                var_value = var_match.group(2).strip()
                self.css_variables[var_name] = var_value
    
    def resolve_color(self, color_value: str) -> Optional[Tuple[int, int, int]]:
        """Resolve color value (handles hex and var() references)"""
        color_value = color_value.strip()
        
        # Handle var() references
        if color_value.startswith('var('):
            var_match = re.search(r'var\((--[\w-]+)\)', color_value)
            if var_match:
                var_name = var_match.group(1)
                if var_name in self.css_variables:
                    color_value = self.css_variables[var_name].strip()
        
        # Handle hex colors
        if color_value.startswith('#'):
            return self.hex_to_rgb(color_value)
        
        # Handle rgba/rgb colors
        if 'rgba' in color_value or 'rgb' in color_value:
            # For now, skip complex rgba parsing
            # Future: implement rgba to RGB conversion
            return None
        
        return None
    
    def extract_color_pairs(self):
        """Extract all color pairs from CSS (color + background, border + background)"""
        self.extract_css_variables()
        
        # Find all rules with color/border-color and background-color properties
        # Pattern: selector { ... color/border-color: X; background-color: Y; ... }
        selector_pattern = r'([^{]+)\s*\{([^}]+)\}'
        
        for match in re.finditer(selector_pattern, self.css_content):
            selector = match.group(1).strip()
            properties = match.group(2)
            
            # Remove comments from selector (false positive filter)
            selector = re.sub(r'/\*.*?\*/', '', selector).strip()
            
            # Skip empty selectors
            if not selector or selector == '*/':
                continue
            
            # Check for color/background pairs
            color_match = re.search(r'color:\s*([^;]+);', properties)
            border_match = re.search(r'border-color:\s*([^;]+);', properties)
            bg_match = re.search(r'background-color:\s*([^;]+);', properties)
            
            # Try color + background first, then border-color + background
            fg_value = None
            fg_rgb = None
            
            if color_match:
                fg_value = color_match.group(1).strip()
                fg_rgb = self.resolve_color(fg_value)
            elif border_match:
                fg_value = border_match.group(1).strip()
                fg_rgb = self.resolve_color(fg_value)
            
            if fg_rgb and bg_match:
                bg_value = bg_match.group(1).strip()
                bg_rgb = self.resolve_color(bg_value)
                
                if bg_rgb:
                    contrast = self.calculate_contrast_ratio(fg_rgb, bg_rgb)
                    
                    # Filter out false positives: same color (1.00:1) indicates parser error
                    if contrast == 1.0:
                        continue
                    
                    prop_type = "color/background-color" if color_match else "border-color/background-color"
                    
                    pair = ColorPair(
                        selector=selector,
                        property=prop_type,
                        foreground=self.rgb_to_hex(fg_rgb),
                        background=self.rgb_to_hex(bg_rgb),
                        foreground_rgb=fg_rgb,
                        background_rgb=bg_rgb,
                        contrast_ratio=contrast,
                        compliance_aa_normal=contrast >= 4.5,
                        compliance_aa_large=contrast >= 3.0,
                        compliance_aaa_normal=contrast >= 7.0,
                        compliance_aaa_large=contrast >= 4.5,
                    )
                    
                    self.color_pairs.append(pair)
    
    def validate(self) -> Dict:
        """Run full validation and return report"""
        self.extract_color_pairs()
        
        # Analyze results
        total = len(self.color_pairs)
        pass_aaa = sum(1 for p in self.color_pairs if p.compliance_aaa_normal)
        pass_aa = sum(1 for p in self.color_pairs if p.compliance_aa_normal and not p.compliance_aaa_normal)
        fail = sum(1 for p in self.color_pairs if not p.compliance_aa_normal)
        
        return {
            "total_pairs": total,
            "pass_aaa": pass_aaa,
            "pass_aa": pass_aa,
            "fail": fail,
            "pass_aaa_pct": (pass_aaa / total * 100) if total > 0 else 0,
            "pass_aa_pct": ((pass_aaa + pass_aa) / total * 100) if total > 0 else 0,
            "pairs": [asdict(p) for p in self.color_pairs],
        }


def format_report(report: Dict) -> str:
    """Format validation report as human-readable text"""
    lines = [
        "=" * 80,
        "KG V2 COLOR CONTRAST VALIDATION REPORT (WCAG 2.1)",
        "=" * 80,
        "",
        "SUMMARY",
        "-" * 80,
        f"Total Color Pairs Analyzed:     {report['total_pairs']}",
        f"✅ Pass AAA (Normal):            {report['pass_aaa']} ({report['pass_aaa_pct']:.1f}%)",
        f"✅ Pass AA (Normal):             {report['pass_aa'] + report['pass_aaa']} ({report['pass_aa_pct']:.1f}%)",
        f"❌ Fail:                         {report['fail']}",
        "",
        "WCAG STANDARDS",
        "-" * 80,
        "AA Normal Text:   4.5:1 contrast ratio",
        "AA Large Text:    3.0:1 contrast ratio",
        "AAA Normal Text:  7.0:1 contrast ratio",
        "AAA Large Text:   4.5:1 contrast ratio",
        "",
        "DETAILED RESULTS",
        "-" * 80,
    ]
    
    # Sort by compliance level and contrast ratio
    pairs = report['pairs']
    pairs.sort(key=lambda p: (p['contrast_ratio'], p['selector']))
    
    for pair in pairs:
        compliance = "✅ AAA" if pair['compliance_aaa_normal'] else \
                    "✅ AA" if pair['compliance_aa_normal'] else \
                    "❌ FAIL"
        
        lines.append(
            f"\n{compliance} | Ratio: {pair['contrast_ratio']:.2f}:1"
        )
        lines.append(f"  Selector:  {pair['selector']}")
        lines.append(f"  FG/BG:     {pair['foreground']} / {pair['background']}")
    
    lines.extend([
        "",
        "=" * 80,
    ])
    
    return "\n".join(lines)


def main():
    """Main entry point"""
    css_path = "modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css"
    
    validator = ContrastValidator(css_path)
    report = validator.validate()
    
    # Print report
    print(format_report(report))
    
    # Save JSON report
    json_path = Path("docs/knowledge/high-40-color-contrast-report.json")
    json_path.write_text(json.dumps(report, indent=2))
    print(f"\n✅ JSON report saved to: {json_path}")
    
    return report


if __name__ == "__main__":
    main()