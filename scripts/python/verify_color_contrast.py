#!/usr/bin/env python3
"""Verify color contrast ratios for KG V2 legend colors (WCAG 2.1)"""

def hex_to_rgb(hex_color):
    hex_color = hex_color.strip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def luminance(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(fg_hex, bg_hex):
    l1 = luminance(hex_to_rgb(fg_hex))
    l2 = luminance(hex_to_rgb(bg_hex))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

print('LIGHT MODE COLORS:')
print(f'Table: #0069e3 on #EBF5FE = {contrast("#0069e3", "#EBF5FE"):.2f}:1 (Target: 4.5+)')
print(f'View: #b15709 on #FEF7F1 = {contrast("#b15709", "#FEF7F1"):.2f}:1 (Target: 4.5+)')
print(f'Synonym: #107E3E on #F1FAF4 = {contrast("#107E3E", "#F1FAF4"):.2f}:1 (Target: 4.5+)')
print(f'Default: #6A6D70 on #F5F6F7 = {contrast("#6A6D70", "#F5F6F7"):.2f}:1 (Target: 4.5+)')

print('\nDARK MODE COLORS:')
print(f'Table: #FFFFFF on #0D3A66 = {contrast("#FFFFFF", "#0D3A66"):.2f}:1 (Target: 4.5+)')
print(f'View: #E9730C on #3D2415 = {contrast("#E9730C", "#3D2415"):.2f}:1 (Target: 4.5+)')
print(f'Synonym: #FFFFFF on #1A4C2A = {contrast("#FFFFFF", "#1A4C2A"):.2f}:1 (Target: 4.5+)')
print(f'Default: #A8A8A8 on #2A2D30 = {contrast("#A8A8A8", "#2A2D30"):.2f}:1 (Target: 4.5+)')

print('\n' + '='*60)
print('COMPLIANCE SUMMARY')
print('='*60)

all_pairs = [
    ('Light Table', contrast("#0069e3", "#EBF5FE")),
    ('Light View', contrast("#b15709", "#FEF7F1")),
    ('Light Synonym', contrast("#107E3E", "#F1FAF4")),
    ('Light Default', contrast("#6A6D70", "#F5F6F7")),
    ('Dark Table', contrast("#FFFFFF", "#0D3A66")),
    ('Dark View', contrast("#E9730C", "#3D2415")),
    ('Dark Synonym', contrast("#FFFFFF", "#1A4C2A")),
    ('Dark Default', contrast("#A8A8A8", "#2A2D30")),
]

pass_aa = sum(1 for name, ratio in all_pairs if ratio >= 4.5)
pass_aaa = sum(1 for name, ratio in all_pairs if ratio >= 7.0)

print(f'\n✅ AA Compliance (4.5:1+): {pass_aa}/{len(all_pairs)} pairs')
print(f'✅ AAA Compliance (7.0:1+): {pass_aaa}/{len(all_pairs)} pairs')

print('\nDetailed Results:')
for name, ratio in all_pairs:
    if ratio >= 7.0:
        status = '✅✅'  # AAA
    elif ratio >= 4.5:
        status = '✅'    # AA
    else:
        status = '❌'    # Fail
    print(f'  {status} {name:20s}: {ratio:.2f}:1')

overall_pass = pass_aa == len(all_pairs)
print(f'\nOverall Result: {"✅ PASS" if overall_pass else "❌ FAIL"}')