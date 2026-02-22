# HIGH-33: KGV2 CSS Refactoring Phase 3 Roadmap

**Status**: IN PROGRESS  
**Phase**: 3 (Dark Mode, CSS Containment, Mobile-First, Motion Preferences)  
**Target Date**: 2026-02-21  
**Last Updated**: 2026-02-21 (Phase 3 Start)

---

## 🎯 Phase 3 Objectives

Phase 3 focuses on **advanced CSS optimization** for production readiness:

### Primary Goals
1. **Dark Mode Support** - CSS variables for color scheme switching
2. **CSS Containment** - Paint/layout/style containment for performance
3. **Mobile-First Responsive** - Refactor media queries from desktop-down to mobile-up
4. **Motion Preferences** - Enhanced prefers-reduced-motion support
5. **CSS Grid Layouts** - Modern responsive layout system

### Success Criteria
- ✅ Dark mode theme switching via CSS variables
- ✅ CSS containment on isolated components (legend, tooltips)
- ✅ Mobile-first media query structure
- ✅ prefers-reduced-motion applied to all transitions/animations
- ✅ No visual regressions on light or dark mode
- ✅ Performance metrics: CSS paint time < 16ms

---

## 📋 Implementation Plan

### Phase 3a: Dark Mode Support (Days 1-2)

**Objective**: Enable theme switching with CSS variables

**Changes**:
```css
/* Light mode (default) */
:root {
  --mode-bg-primary: #FFFFFF;
  --mode-text-primary: #32363A;
  --mode-border: #D5DADD;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --mode-bg-primary: #1F2023;
    --mode-text-primary: #E5E5E5;
    --mode-border: #444;
  }
}
```

**Components Affected**:
- ✅ Legend box (background, text, border)
- ✅ Tooltips (existing dark styling maintained)
- ✅ Canvas background
- ✅ Loading overlay

**Testing**:
- Visual inspection: Light mode (default)
- Visual inspection: Dark mode (dev tools: prefers-color-scheme: dark)
- System theme switching

---

### Phase 3b: CSS Containment (Days 3-4)

**Objective**: Optimize rendering performance via containment

**Implementation**:
```css
/* Contained elements render independently */
#kgv2-legend {
  contain: layout style paint;
  /* Prevents parent layout reflows */
}

.vis-network .vis-tooltip {
  contain: content; /* Minimal containment for tooltips */
}
```

**Performance Impact**:
- Legend repositioning: Independent paint (no canvas redraw)
- Tooltip rendering: Isolated from graph canvas repaints
- Expected improvement: 10-20% paint time reduction

---

### Phase 3c: Mobile-First Media Queries (Days 5-6)

**Objective**: Restructure media queries from desktop-down to mobile-up

**Current State** (Desktop-first):
```css
/* Large screens */
.vis-button { width: 40px; }

/* Small screens override */
@media (max-width: 768px) {
  .vis-button { width: 32px; }
}
```

**New State** (Mobile-first):
```css
/* Small screens default */
.vis-button { width: 32px; }

/* Large screens enhance */
@media (min-width: 769px) {
  .vis-button { width: 40px; }
}
```

**Breakpoints**:
- Mobile: < 480px (phones)
- Tablet: 481px - 768px
- Desktop: > 769px

**Components**:
- Navigation buttons (sizing)
- Legend (positioning, padding)
- Tooltips (font size, positioning)

---

### Phase 3d: Motion Preferences Enhancement (Days 7-8)

**Objective**: Comprehensive motion preference support

**Current Implementation**:
```css
@media (prefers-reduced-motion: reduce) {
  .vis-button {
    transition: none !important;
  }
  .vis-button:active {
    transform: none !important;
  }
}
```

**Enhanced Implementation**:
- Disable ALL transitions globally
- Disable scale/rotate transforms
- Disable fade-in animations
- Maintain accessibility focus states

---

### Phase 3e: CSS Grid Layouts (Days 9-10)

**Objective**: Modernize responsive layouts

**Legend Layout Migration**:
```css
/* From flexbox */
#kgv2-legend-content {
  display: flex;
  flex-direction: column;
}

/* To CSS Grid */
#kgv2-legend-content {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--spacing-sm);
  align-items: center;
}
```

**Benefits**:
- Simpler layout logic
- Better mobile responsiveness
- Grid auto-fit for dynamic items

---

## 🏗️ Implementation Steps

### Step 1: Add Dark Mode Variables to :root

**File**: `modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css`

Add to `:root` block:
```css
/* Color scheme mode variables */
--mode-bg-primary: var(--color-sap-white);
--mode-bg-secondary: var(--color-sap-surface-s1);
--mode-text-primary: var(--color-sap-text-t3);
--mode-text-secondary: var(--color-sap-grayscale-t7);
--mode-border: var(--color-sap-border);
--mode-shadow: var(--shadow-subtle);
```

Add dark mode override:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --mode-bg-primary: #1F2023;
    --mode-bg-secondary: #2A2D30;
    --mode-text-primary: #E5E5E5;
    --mode-text-secondary: #A8A8A8;
    --mode-border: #444;
    --mode-shadow: 0 0 0.25rem rgba(0, 0, 0, 0.5);
  }
}
```

### Step 2: Apply CSS Containment

Add to elements:
- `#kgv2-legend`: `contain: layout style paint;`
- `.vis-network .vis-tooltip`: `contain: content;`
- `.vis-network .vis-navigation`: `contain: style;` (minimal)

### Step 3: Refactor Media Queries to Mobile-First

**Process**:
1. Move default (small screen) properties outside media query
2. Change `@media (max-width: X)` → `@media (min-width: X+1px)`
3. Update breakpoint logic

### Step 4: Enhance Motion Preferences

Add comprehensive rules for `prefers-reduced-motion: reduce`:
```css
@media (prefers-reduced-motion: reduce) {
  /* Global transition disable */
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Step 5: Implement CSS Grid

Migrate legend layout to CSS Grid for better responsiveness.

---

## 📊 Expected Outcomes

### Performance
- **Paint time**: < 16ms (current: ~20ms)
- **Reflow on legend toggle**: Isolated (no canvas redraw)
- **Memory**: CSS variables reduce calc complexity

### UX
- **Dark mode**: Native system preference support
- **Accessibility**: prefers-reduced-motion comprehensive coverage
- **Mobile**: Optimized breakpoints for all screen sizes
- **Maintainability**: Modern CSS patterns (containment, Grid)

### Testing
- ✅ Light mode: Pixel-perfect match to Phase 2
- ✅ Dark mode: Consistent color palette
- ✅ Motion disabled: Instant state changes (no delays)
- ✅ Mobile/tablet/desktop: Responsive breakpoint validation

---

## 🔗 Related Documentation

- [[high-34-kgv2-css-refactoring-phase-1-audit.md]] - Phase 1: Baseline
- [[high-38-kgv2-css-refactoring-phase-2-implementation.md]] - Phase 2: BEM/Specificity
- [[sap-fiori-color-integration.md]] - Color token reference

---

## 📝 Learnings & Rationale

### Why Dark Mode?
- **User Preference**: 40-60% of users prefer dark mode (dependent on OS)
- **Accessibility**: Reduces eye strain in low-light environments
- **Performance**: Dark colors = lower power consumption on OLED displays
- **Implementation**: CSS variables + prefers-color-scheme media query

### Why CSS Containment?
- **Browser Optimization**: Tells browser which elements render independently
- **Paint Reduction**: Legend/tooltip changes don't trigger canvas repaints
- **Scalability**: Containment rules scale with complexity

### Why Mobile-First?
- **Progressive Enhancement**: Base styles work everywhere
- **Media Query Volume**: Fewer overrides vs. desktop-first approach
- **Performance**: Smaller default CSS, layered enhancements
- **Maintenance**: Cleaner separation of concerns

### Why Motion Preferences?
- **Accessibility Compliance**: WCAG 2.1 guideline 2.3
- **User Respect**: Honor system/app preferences
- **Reduced Cognitive Load**: Users with vestibular disorders benefit

---

## 📌 Next Phase (Phase 4)

- CSS Grid component library
- Advanced color contrast validation
- Animation performance profiling
- Browser compatibility matrix

---

**Created**: 2026-02-21  
**Author**: P2P Development Team  
**Status**: Planning Complete → Implementation Starting