#!/usr/bin/env python3
"""Generate WCAG 2.1 AA compliant colors (4.5:1+) for KG V2 legend"""

def hex_to_rgb(hex_color):
    hex_color = hex_color.strip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def luminance(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(fg_hex, bg_hex):
    l1 = luminance(hex_to_rgb(fg_hex))
    l2 = luminance(hex_to_rgb(bg_hex))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def find_darker_color(hex_color, steps=50):
    """Find darker version of color that achieves 4.5:1 on light background"""
    r, g, b = hex_to_rgb(hex_color)
    for i in range(steps):
        factor = (steps - i) / steps
        new_r = r * factor
        new_g = g * factor
        new_b = b * factor
        new_hex = rgb_to_hex((new_r, new_g, new_b))
        if contrast_ratio(new_hex, '#EBF5FE') >= 4.5:
            return new_hex, contrast_ratio(new_hex, '#EBF5FE')
    return None, None

def find_darker_orange(hex_color, bg_hex, target_ratio=4.5, max_iterations=100):
    """Find darker orange that achieves target contrast on background"""
    r, g, b = hex_to_rgb(hex_color)
    best = (hex_color, contrast_ratio(hex_color, bg_hex))
    
    for i in range(max_iterations):
        factor = 1.0 - (i * 0.02)  # Gradually darken
        new_r = min(255, r * factor)
        new_g = min(255, g * factor)
        new_b = min(255, b * factor)
        new_hex = rgb_to_hex((new_r, new_g, new_b))
        ratio = contrast_ratio(new_hex, bg_hex)
        if ratio >= target_ratio:
            return new_hex, ratio
        if ratio > best[1]:
            best = (new_hex, ratio)
    
    return best

print("WCAG 2.1 AA COMPLIANT COLOR GENERATION")
print("=" * 60)

# Problem 1: Light Table #0070F2 on #EBF5FE (4.14:1, need 4.5+)
print("\n1. LIGHT TABLE COLOR")
print("Current: #0070F2 on #EBF5FE = 4.14:1 ❌")
darker_blue, ratio = find_darker_color('#0070F2')
print(f"Solution: {darker_blue} on #EBF5FE = {ratio:.2f}:1 ✅")

# Problem 2: Light View #E9730C on #FEF7F1 (2.86:1, need 4.5+)
print("\n2. LIGHT VIEW COLOR")
print("Current: #E9730C on #FEF7F1 = 2.86:1 ❌")
darker_orange, ratio = find_darker_orange('#E9730C', '#FEF7F1')
print(f"Solution: {darker_orange} on #FEF7F1 = {ratio:.2f}:1 ✅")

print("\n" + "=" * 60)
print("COMPLETE NEW COLOR PALETTE")
print("=" * 60)

new_colors = {
    'light_table_fg': darker_blue if darker_blue else '#0070F2',
    'light_table_bg': '#EBF5FE',
    'light_view_fg': darker_orange if darker_orange else '#E9730C',
    'light_view_bg': '#FEF7F1',
    'light_synonym_fg': '#107E3E',
    'light_synonym_bg': '#F1FAF4',
    'light_default_fg': '#6A6D70',
    'light_default_bg': '#F5F6F7',
    'dark_table_fg': '#FFFFFF',
    'dark_table_bg': '#0D3A66',
    'dark_view_fg': '#E9730C',
    'dark_view_bg': '#3D2415',
    'dark_synonym_fg': '#FFFFFF',
    'dark_synonym_bg': '#1A4C2A',
    'dark_default_fg': '#A8A8A8',
    'dark_default_bg': '#2A2D30',
}

print("\nLIGHT MODE:")
print(f"  Table:   {new_colors['light_table_fg']} on {new_colors['light_table_bg']} = {contrast_ratio(new_colors['light_table_fg'], new_colors['light_table_bg']):.2f}:1")
print(f"  View:    {new_colors['light_view_fg']} on {new_colors['light_view_bg']} = {contrast_ratio(new_colors['light_view_fg'], new_colors['light_view_bg']):.2f}:1")
print(f"  Synonym: {new_colors['light_synonym_fg']} on {new_colors['light_synonym_bg']} = {contrast_ratio(new_colors['light_synonym_fg'], new_colors['light_synonym_bg']):.2f}:1")
print(f"  Default: {new_colors['light_default_fg']} on {new_colors['light_default_bg']} = {contrast_ratio(new_colors['light_default_fg'], new_colors['light_default_bg']):.2f}:1")

print("\nDARK MODE:")
print(f"  Table:   {new_colors['dark_table_fg']} on {new_colors['dark_table_bg']} = {contrast_ratio(new_colors['dark_table_fg'], new_colors['dark_table_bg']):.2f}:1")
print(f"  View:    {new_colors['dark_view_fg']} on {new_colors['dark_view_bg']} = {contrast_ratio(new_colors['dark_view_fg'], new_colors['dark_view_bg']):.2f}:1")
print(f"  Synonym: {new_colors['dark_synonym_fg']} on {new_colors['dark_synonym_bg']} = {contrast_ratio(new_colors['dark_synonym_fg'], new_colors['dark_synonym_bg']):.2f}:1")
print(f"  Default: {new_colors['dark_default_fg']} on {new_colors['dark_default_bg']} = {contrast_ratio(new_colors['dark_default_fg'], new_colors['dark_default_bg']):.2f}:1")

# Verification
all_pairs = [
    ('Light Table', contrast_ratio(new_colors['light_table_fg'], new_colors['light_table_bg'])),
    ('Light View', contrast_ratio(new_colors['light_view_fg'], new_colors['light_view_bg'])),
    ('Light Synonym', contrast_ratio(new_colors['light_synonym_fg'], new_colors['light_synonym_bg'])),
    ('Light Default', contrast_ratio(new_colors['light_default_fg'], new_colors['light_default_bg'])),
    ('Dark Table', contrast_ratio(new_colors['dark_table_fg'], new_colors['dark_table_bg'])),
    ('Dark View', contrast_ratio(new_colors['dark_view_fg'], new_colors['dark_view_bg'])),
    ('Dark Synonym', contrast_ratio(new_colors['dark_synonym_fg'], new_colors['dark_synonym_bg'])),
    ('Dark Default', contrast_ratio(new_colors['dark_default_fg'], new_colors['dark_default_bg'])),
]

pass_aa = sum(1 for name, ratio in all_pairs if ratio >= 4.5)
print(f"\n✅ AA Compliance: {pass_aa}/8 pairs")

if pass_aa == 8:
    print("\n" + "=" * 60)
    print("CSS VARIABLES TO USE:")
    print("=" * 60)
    print("""
--legend-table-light-fg: """ + new_colors['light_table_fg'] + """;
--legend-table-light-bg: """ + new_colors['light_table_bg'] + """;
--legend-view-light-fg: """ + new_colors['light_view_fg'] + """;
--legend-view-light-bg: """ + new_colors['light_view_bg'] + """;
--legend-synonym-light-fg: """ + new_colors['light_synonym_fg'] + """;
--legend-synonym-light-bg: """ + new_colors['light_synonym_bg'] + """;
--legend-default-light-fg: """ + new_colors['light_default_fg'] + """;
--legend-default-light-bg: """ + new_colors['light_default_bg'] + """;

--legend-table-dark-fg: """ + new_colors['dark_table_fg'] + """;
--legend-table-dark-bg: """ + new_colors['dark_table_bg'] + """;
--legend-view-dark-fg: """ + new_colors['dark_view_fg'] + """;
--legend-view-dark-bg: """ + new_colors['dark_view_bg'] + """;
--legend-synonym-dark-fg: """ + new_colors['dark_synonym_fg'] + """;
--legend-synonym-dark-bg: """ + new_colors['dark_synonym_bg'] + """;
--legend-default-dark-fg: """ + new_colors['dark_default_fg'] + """;
--legend-default-dark-bg: """ + new_colors['dark_default_bg'] + """;
    """)