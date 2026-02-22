# HIGH-43: CSS Systematic Remediation Plan

**Status**: In Progress  
**Phase**: CSS Refactoring - Comprehensive Strategy  
**Date**: 2026-02-22  
**Effort**: 6-8 hours (broken into phases)  
**Dependencies**: HIGH-41 ✅, HIGH-42 ✅

---

## Overview

Systematic remediation of 92 `!important` declarations in `knowledge-graph-v2.css` through SAP Fiori Design Token integration and proper CSS specificity hierarchy.

**Current State**: 96 HIGH findings from Feng Shui
- 85 `!important` overrides (CSS maintainability crisis)
- 11 color accessibility issues (WCAG violations)
- Ecosystem health: 0/100 for knowledge_graph_v2 module

---

## Phase Strategy

### Phase 5b: WCAG Color Compliance (IMMEDIATE) ⭐ 1-2 hours
**Status**: 🟡 IN PROGRESS  
**Priority**: CRITICAL (accessibility blocker)

Fix 2 WCAG violations in legend colors:
- `.kgv2-legend-color.table`: 2.54:1 → 9.0:1+ ✅
- `.kgv2-legend-color.synonym`: 1.93:1 → 9.2:1+ ✅

**Implementation**: Add CSS variables for dark mode legend borders
```css
@media (prefers-color-scheme: dark) {
    :root {
        --color-kgv2-legend-table-border: #FFFFFF;
        --color-kgv2-legend-synonym-border: #FFFFFF;
    }
}
```

**Deliverable**: 100% WCAG AA compliance (4.5:1+), actually achieves AAA (7.0:1+)

---

### Phase 6: SAP Fiori Token System (2-3 hours)
**Status**: 🟢 PLANNED  
**Priority**: HIGH (architecture foundation)

**Goal**: Replace hard-coded values with semantic design tokens

#### Step 1: Define Token Categories (30 min)

Create CSS custom property system mirroring SAP Fiori:

```css
:root {
    /* === COMPONENT TOKENS === */
    /* Navigation Controls */
    --kgv2-nav-button-size: 32px;
    --kgv2-nav-button-bg: var(--color-sap-white);
    --kgv2-nav-button-border: var(--color-sap-grayscale-t9);
    --kgv2-nav-button-color: var(--color-sap-text-t3);
    --kgv2-nav-button-hover-bg: var(--color-sap-surface-s1);
    --kgv2-nav-button-hover-border: var(--color-sap-brand-blue);
    --kgv2-nav-button-active-bg: var(--color-sap-brand-blue-light);
    
    /* Tooltips */
    --kgv2-tooltip-bg: var(--color-sap-dark-surface);
    --kgv2-tooltip-border: var(--color-sap-dark-surface);
    --kgv2-tooltip-color: var(--color-sap-white);
    --kgv2-tooltip-shadow: var(--shadow-tooltip);
    
    /* Legend */
    --kgv2-legend-bg: var(--color-sap-surface-s2);
    --kgv2-legend-border: var(--color-sap-border);
    --kgv2-legend-color-size: 16px;
    
    /* === ACCESSIBILITY TOKENS === */
    /* High Contrast Mode */
    --kgv2-hc-border-width: 2px;
    --kgv2-hc-border-color: #000000;
    
    /* Reduced Motion */
    --kgv2-motion-duration: 0.2s;
    --kgv2-motion-timing: ease-in-out;
}

@media (prefers-color-scheme: dark) {
    :root {
        --kgv2-legend-table-border: #FFFFFF;
        --kgv2-legend-synonym-border: #FFFFFF;
    }
}

@media (prefers-reduced-motion: reduce) {
    :root {
        --kgv2-motion-duration: 0.01ms;
    }
}
```

#### Step 2: Replace VIS.JS Overrides (60-90 min)

**KEEP Category** - Required `!important` for vis.js inline styles:
- Navigation button styling (background, border, color, sizing)
- Button states (hover, active, focus, disabled)
- Slider controls
- High contrast mode overrides
- Reduced motion preferences

**Strategy**: Document WHY each `!important` is necessary
```css
/* KEEP !important - vis.js uses inline styles with higher specificity */
.vis-network .vis-navigation .vis-button {
    background-color: var(--kgv2-nav-button-bg) !important;
    border: 1px solid var(--kgv2-nav-button-border) !important;
    /* ...more properties */
}
```

#### Step 3: Remove Unnecessary `!important` (30-60 min)

**REMOVE Category** - We control these elements:
- `#kgv2-graph-canvas` styling
- `#kgv2-legend` positioning
- `.kgv2-legend-content` state management
- `.kgv2-legend-item` typography

**Strategy**: Replace with proper CSS specificity
```css
/* BEFORE: Unnecessary !important */
#kgv2-legend {
    background-color: var(--color-sap-surface-s2) !important;
}

/* AFTER: Proper specificity */
#kgv2-legend {
    background-color: var(--kgv2-legend-bg);
}
```

#### Step 4: Validation (30 min)

1. Run color contrast validation: `python scripts/python/validate_color_contrast.py`
2. Visual regression testing (light/dark mode)
3. Verify vis.js controls still work
4. Test accessibility features (high contrast, reduced motion)

---

### Phase 7: !important Elimination (2-3 hours)
**Status**: 🟢 PLANNED  
**Priority**: HIGH (code quality)

**Current State**: 92 `!important` declarations
**Target**: ~40-50 (only vis.js overrides + accessibility)

#### Elimination Strategy

| Category | Count | Action | Justification |
|----------|-------|--------|---------------|
| VIS.JS Navigation Buttons | ~35 | **KEEP** | Required for inline style override |
| VIS.JS Slider | ~3 | **KEEP** | Required for inline style override |
| Tooltips (vis.js) | ~5 | **KEEP** | Required for dynamic positioning |
| Accessibility (HC + RM) | ~10 | **KEEP** | User preference enforcement |
| Legend Colors | ~8 | **REMOVE** | We control element (use tokens) |
| Canvas Styling | ~5 | **REMOVE** | We control element |
| State Management | ~3 | **REMOVE** | Use proper specificity |
| Typography | ~8 | **REMOVE** | Use BEM methodology |
| **TOTAL** | **92** | **~50 KEEP, ~42 REMOVE** | **54% reduction** |

#### Implementation Pattern

**Pattern 1: Token Replacement**
```css
/* BEFORE */
.kgv2-legend-color.table {
    border-color: #0069e3 !important;
    background-color: #EBF5FE !important;
}

/* AFTER */
.kgv2-legend-color.table {
    border-color: var(--color-sap-brand-blue);
    background-color: var(--color-sap-brand-blue-light);
}
```

**Pattern 2: BEM Specificity**
```css
/* BEFORE */
.kgv2-legend-item {
    font-size: 0.875rem !important;
}

/* AFTER - Use BEM element specificity */
.kgv2-legend__item {
    font-size: 0.875rem;
}
```

**Pattern 3: State Classes**
```css
/* BEFORE */
#kgv2-legend-content.collapsed {
    display: none !important;
}

/* AFTER - State class has sufficient specificity */
#kgv2-legend-content.kgv2-legend-content--collapsed {
    display: none;
}
```

---

## Implementation Workflow

### Step-by-Step Execution

1. ✅ **Phase 5b: Fix WCAG violations** (1-2h)
   - Add dark mode CSS variables for legend borders
   - Run validation script
   - Verify 100% compliance

2. **Phase 6: Token System** (2-3h)
   - Define all CSS custom properties
   - Document token categories
   - Create token reference table

3. **Phase 7: !important Elimination** (2-3h)
   - Replace legend colors with tokens
   - Remove canvas/state !important
   - Update typography with BEM
   - Validate with Feng Shui

---

## Validation Checklist

### Automated Checks
- [ ] `python scripts/python/validate_color_contrast.py` - 100% pass
- [ ] `python -m tools.fengshui analyze` - HIGH findings reduced from 96 → ~50
- [ ] Visual regression: Light mode screenshots match
- [ ] Visual regression: Dark mode screenshots match

### Manual Checks
- [ ] VIS.JS navigation controls functional
- [ ] Tooltip positioning correct
- [ ] Legend colors WCAG compliant
- [ ] High contrast mode working
- [ ] Reduced motion respected
- [ ] Mobile responsive

---

## Expected Results

### Metrics After Completion

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| `!important` Count | 92 | ~50 | 54% reduction |
| WCAG Violations | 2 | 0 | 100% compliance |
| Feng Shui HIGH | 96 | ~50 | 48% reduction |
| Module Health | 0/100 | 65+/100 | +65 points |
| Maintainability | CRITICAL | GOOD | 2 grades up |

### Knowledge Graph V2 Health Scorecard

**Current**: 0/100 (CRITICAL ❌)  
**Target**: 65+/100 (GOOD ✅)

**Improvements**:
- ✅ CSS architecture: CRITICAL → GOOD
- ✅ Accessibility: CRITICAL → GOOD (100% WCAG compliance)
- ✅ Code maintainability: CRITICAL → GOOD (token system)
- ✅ Documentation: Updated with token reference

---

## Documentation Deliverables

1. **CSS Token Reference** (`docs/knowledge/kgv2-css-token-reference.md`)
   - Complete list of all design tokens
   - Usage examples
   - Light/dark mode variants

2. **!important Usage Guide** (`docs/knowledge/kgv2-important-usage-guide.md`)
   - When to use `!important` (vis.js overrides only)
   - When NOT to use (proper specificity patterns)
   - Enforcement via Feng Shui UX Architect Agent

3. **Phase 5b Report** (`docs/knowledge/high-40-kgv2-css-refactoring-phase-5b-results.md`)
   - WCAG validation results
   - Before/after contrast ratios
   - Visual regression screenshots

---

## Risk Mitigation

### Potential Issues

1. **VIS.JS Breaking Changes**
   - Risk: Removing `!important` breaks vis.js controls
   - Mitigation: Only remove from elements we fully control
   - Validation: Manual testing of all navigation controls

2. **Color Contrast Regressions**
   - Risk: Token replacement introduces new violations
   - Mitigation: Run validation script after each change
   - Validation: Automated contrast ratio checks

3. **Dark Mode Broken**
   - Risk: CSS variable fallback not working
   - Mitigation: Test both light/dark modes
   - Validation: Visual regression screenshots

4. **Mobile Breakage**
   - Risk: Specificity changes break mobile layout
   - Mitigation: Test responsive breakpoints
   - Validation: Mobile viewport screenshots

---

## Success Criteria

### Phase 5b Complete When:
- ✅ 0 WCAG violations (100% AA compliance)
- ✅ All 4 legend color pairs passing validation
- ✅ Dark mode legend borders use white (#FFFFFF)
- ✅ Validation script confirms 4.5:1+ ratios

### Phase 6 Complete When:
- ✅ All design tokens defined in `:root`
- ✅ Token reference documentation created
- ✅ No hard-coded colors/sizes remain
- ✅ Light/dark mode tokens separated

### Phase 7 Complete When:
- ✅ `!important` count reduced from 92 → ~50
- ✅ All unnecessary `!important` removed
- ✅ BEM methodology applied consistently
- ✅ Feng Shui HIGH findings reduced by 48%

### Overall HIGH-43 Complete When:
- ✅ Module health 65+/100 (GOOD ✅)
- ✅ 100% WCAG AA compliance
- ✅ CSS architecture documented
- ✅ Token system established

---

## Next Steps

1. **Execute Phase 5b** (THIS SESSION)
   - Implement WCAG color fixes
   - Run validation
   - Verify dark mode

2. **Plan Phase 6** (NEXT SESSION)
   - Design complete token system
   - Document token categories
   - Create usage guide

3. **Execute Phase 7** (FUTURE SESSION)
   - Systematic `!important` removal
   - BEM refactoring
   - Final validation

---

## Files to Modify

### Phase 5b (Immediate)
- `modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css`
  - Add dark mode CSS variables for legend borders
  - Update `.kgv2-legend-color` selectors

### Phase 6 (Next)
- `modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css`
  - Define complete token system
  - Replace hard-coded values

### Phase 7 (Future)
- `modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css`
  - Remove unnecessary `!important`
  - Apply BEM methodology

---

## References

- [[High-40 KGV2 CSS Refactoring Phase 5 Color Contrast]]
- [[High-40 KGV2 CSS Refactoring Phase 5b Color Redesign]]
- [[High-34 KGV2 CSS Refactoring Phase 1 Audit]]
- [[High-38 KGV2 CSS Refactoring Phase 2 Implementation]]
- [[SAP Fiori Color Integration]]
- [[Module Federation Standard]]

---

**Summary**: Systematic CSS remediation through 3 phases - immediate WCAG fixes (Phase 5b), token system foundation (Phase 6), and `!important` elimination (Phase 7). Target: 54% reduction in `!important` usage, 100% WCAG compliance, and module health improvement from 0/100 → 65+/100.