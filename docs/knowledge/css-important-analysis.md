# CSS !important Declaration Analysis
**Total !important declarations found**: 104

## By File

| File | Count |
|------|-------|
| knowledge-graph-v2.css | 69 |
| ai-assistant.css | 35 |

## By Property

| Property | Count |
|----------|-------|
| background-color | 12 |
| color | 8 |
| vis-button | 6 |
| modifier | 6 |
| border-color | 5 |
| background | 4 |
| padding | 4 |
| transition | 4 |
| display | 4 |
| height | 3 |
| box-shadow | 3 |
| Responsive | 3 |
| border-radius | 3 |
| transform | 2 |
| min-width | 2 |
| cursor | 2 |
| border | 2 |
| font-size | 2 |
| mode | 2 |
| Problem | 1 |

## By Category

| Category | Count |
|----------|-------|
| other | 52 |
| visual | 25 |
| layout | 11 |
| typography | 10 |
| spacing | 6 |

## Replacement Strategies

### ai-assistant.css

**Selector**: `unknown`
**Property**: `background: white"] {
    color: var(--color-text-primary) !important;`
**Category**: visual
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `background: #0070f2"] {
    color: #ffffff !important;`
**Category**: visual
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `background: #ff4444"] {
    color: var(--color-error-text) !important;`
**Category**: visual
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox {
    display: flex !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ==================== Phase 5: Sticky Input Field - SAP Fiori Compliant ==================== */

/**
 * SAP Fiori Dialog Layout Standard
 * =================================
 * 
 * Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox`
**Property**: `flex-direction: column !important;`
**Category**: other
**Current Specificity**: (0, 4, 57)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ==================== Phase 5: Sticky Input Field - SAP Fiori Compliant ==================== */

/**
 * SAP Fiori Dialog Layout Standard
 * =================================
 * 
 * Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ==================== Phase 5: Sticky Input Field - SAP Fiori Compliant ==================== */

/**
 * SAP Fiori Dialog Layout Standard
 * =================================
 * 
 * Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ==================== Phase 5: Sticky Input Field - SAP Fiori Compliant ==================== */

/**
 * SAP Fiori Dialog Layout Standard
 * =================================
 * 
 * Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ==================== Phase 5: Sticky Input Field - SAP Fiori Compliant ==================== */

/**
 * SAP Fiori Dialog Layout Standard
 * =================================
 * 
 * Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox`
**Property**: `height: 100% !important;`
**Category**: layout
**Current Specificity**: (0, 4, 57)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ==================== Phase 5: Sticky Input Field - SAP Fiori Compliant ==================== */

/**
 * SAP Fiori Dialog Layout Standard
 * =================================
 * 
 * Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ==================== Phase 5: Sticky Input Field - SAP Fiori Compliant ==================== */

/**
 * SAP Fiori Dialog Layout Standard
 * =================================
 * 
 * Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ==================== Phase 5: Sticky Input Field - SAP Fiori Compliant ==================== */

/**
 * SAP Fiori Dialog Layout Standard
 * =================================
 * 
 * Problem: Input field scrolls out of view when messages fill the dialog
 * Solution: Fiori-compliant layout with fixed footer and scrollable content
 * 
 * Standards Applied:
 * ✅ SAP Fiori Design Guidelines v1.96
 * ✅ SAPUI5 Dialog/ScrollContainer patterns
 * ✅ rem-based spacing via CSS variables
 * ✅ Responsive S/M/L sizes
 * ✅ Touch-optimized (44x44px minimum)
 */

/* Dialog content: Flexbox column layout (Fiori standard) */
.sapMDialog .sapMDialogScroll > .sapMVBox)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont {
    flex: 1 1 auto !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
**Property**: `overflow-y: auto !important;`
**Category**: other
**Current Specificity**: (0, 2, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
**Property**: `overflow-x: hidden !important;`
**Category**: other
**Current Specificity**: (0, 2, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
**Property**: `-webkit-overflow-scrolling: touch !important;`
**Category**: other
**Current Specificity**: (0, 2, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
**Property**: `padding: var(--spacing-lg) !important;`
**Category**: spacing
**Current Specificity**: (0, 2, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
**Property**: `scroll-behavior: smooth !important;`
**Category**: other
**Current Specificity**: (0, 2, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
**Property**: `transform: translateZ(0) !important;`
**Category**: other
**Current Specificity**: (0, 2, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
**Property**: `will-change: scroll-position !important;`
**Category**: other
**Current Specificity**: (0, 2, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Messages scroll container: Flex-grow to fill space (Fiori scrollable content) */
.sapMDialog .sapMScrollCont)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar {
    flex: 0 0 auto !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
**Property**: `border-top: 1px solid var(--color-border-primary) !important;`
**Category**: other
**Current Specificity**: (0, 2, 4)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
**Property**: `background: var(--color-bg-primary) !important;`
**Category**: visual
**Current Specificity**: (0, 2, 4)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
**Property**: `padding: var(--toolbar-padding) !important;`
**Category**: spacing
**Current Specificity**: (0, 2, 4)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
**Property**: `z-index: var(--z-toolbar) !important;`
**Category**: layout
**Current Specificity**: (0, 2, 4)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
**Property**: `box-shadow: var(--shadow-lg) !important;`
**Category**: visual
**Current Specificity**: (0, 2, 4)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Input toolbar: Fixed footer (Fiori standard) */
.sapMDialog .sapMToolbar)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase {
    flex: 1 1 auto !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Input field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase`
**Property**: `min-width: var(--input-min-width) !important;`
**Category**: layout
**Current Specificity**: (0, 3, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Input field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Input field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Input field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Input field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase`
**Property**: `margin-right: var(--spacing-sm) !important;`
**Category**: spacing
**Current Specificity**: (0, 3, 7)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Input field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Input field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Input field: Proper sizing with Fiori spacing */
.sapMDialog .sapMToolbar .sapMInputBase)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn {
    min-width: var(--button-min-width) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Touch-friendly buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn`
**Property**: `min-height: var(--button-min-width) !important;`
**Category**: layout
**Current Specificity**: (0, 3, 6)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Touch-friendly buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Touch-friendly buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Touch-friendly buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Touch-friendly buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn`
**Property**: `margin-left: var(--spacing-xs) !important;`
**Category**: spacing
**Current Specificity**: (0, 3, 6)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Touch-friendly buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Touch-friendly buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Touch-friendly buttons: 44x44px minimum - Fiori touch target */
.sapMDialog .sapMToolbar .sapMBtn)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Emphasized button (Send): Fiori primary action */
.sapMDialog .sapMToolbar .sapMBtn.sapMBtnEmphasized`
**Property**: `min-width: var(--touch-target-lg) !important;`
**Category**: layout
**Current Specificity**: (0, 4, 5)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Emphasized button (Send): Fiori primary action */
.sapMDialog .sapMToolbar .sapMBtn.sapMBtnEmphasized/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Emphasized button (Send): Fiori primary action */
.sapMDialog .sapMToolbar .sapMBtn.sapMBtnEmphasized`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Emphasized button (Send): Fiori primary action */
.sapMDialog .sapMToolbar .sapMBtn.sapMBtnEmphasized)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `list: No extra margins that could cause layout issues */
.sapMDialog .sapMList {
    margin: 0 !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Feed list: No extra margins that could cause layout issues */
.sapMDialog .sapMList`
**Property**: `padding: 0 !important;`
**Category**: spacing
**Current Specificity**: (0, 2, 10)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Feed list: No extra margins that could cause layout issues */
.sapMDialog .sapMList/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Feed list: No extra margins that could cause layout issues */
.sapMDialog .sapMList`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Feed list: No extra margins that could cause layout issues */
.sapMDialog .sapMList)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `items: Fiori spacing */
.sapMDialog .sapMFeedListItem {
    margin-bottom: var(--list-item-margin) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `item: No bottom margin */
.sapMDialog .sapMFeedListItem:last-child {
    margin-bottom: 0 !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `Responsive: Size S (Smartphone) */
@media (max-width: 600px) {
    .sapMDialog .sapMToolbar {
        padding: var(--toolbar-padding-mobile) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `.sapMDialog .sapMScrollCont`
**Property**: `padding: var(--spacing-md) !important;`
**Category**: spacing
**Current Specificity**: (0, 2, 0)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `.sapMDialog .sapMScrollCont.sapMDialog`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body .sapMDialog .sapMScrollCont`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(.sapMDialog .sapMScrollCont)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `Responsive: Size M (Tablet) */
@media (min-width: 601px) and (max-width: 1024px) {
    .sapMDialog .sapMToolbar {
        padding: var(--toolbar-padding) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `Responsive: Size L (Desktop) */
@media (min-width: 1025px) {
    .sapMDialog .sapMToolbar {
        padding: var(--spacing-lg) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

### knowledge-graph-v2.css

**Selector**: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
**Property**: `background-color: var(--color-sap-white) !important;`
**Category**: visual
**Current Specificity**: (0, 4, 14)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
**Property**: `border-radius: var(--border-radius) !important;`
**Category**: visual
**Current Specificity**: (0, 4, 14)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
**Property**: `color: var(--color-sap-text-t3) !important;`
**Category**: typography
**Current Specificity**: (0, 4, 14)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
**Property**: `cursor: pointer !important;`
**Category**: other
**Current Specificity**: (0, 4, 14)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
**Property**: `transition: all 0.2s ease-in-out !important;`
**Category**: other
**Current Specificity**: (0, 4, 14)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Individual navigation buttons - SAP Fiori style
 * KEEP ALL !important - Required for vis.js inline style override
 */
.vis-network .vis-navigation .vis-button)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `vis-button: hover {
    background-color: var(--color-sap-surface-s1) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover`
**Property**: `border-color: var(--color-sap-brand-blue) !important;`
**Category**: other
**Current Specificity**: (0, 5, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover`
**Property**: `color: var(--color-sap-brand-blue) !important;`
**Category**: typography
**Current Specificity**: (0, 5, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover`
**Property**: `box-shadow: 0 0 0 0.0625rem rgba(0, 112, 242, 0.3) !important;`
**Category**: visual
**Current Specificity**: (0, 5, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Button hover state
 * KEEP !important - vis.js may override on interaction
 */
.vis-network .vis-navigation .vis-button:hover)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `vis-button: active {
    background-color: var(--color-sap-brand-blue-light) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active`
**Property**: `border-color: var(--color-sap-brand-blue) !important;`
**Category**: other
**Current Specificity**: (0, 4, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active`
**Property**: `color: var(--color-sap-brand-blue) !important;`
**Category**: typography
**Current Specificity**: (0, 4, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active`
**Property**: `transform: scale(0.95) !important;`
**Category**: other
**Current Specificity**: (0, 4, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Button active/pressed state
 * KEEP !important - needs strong override during interaction
 */
.vis-network .vis-navigation .vis-button:active)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `vis-button: focus {
    outline: 2px solid var(--color-sap-brand-blue) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Button focus state (keyboard navigation)
 * KEEP !important - accessibility critical
 */
.vis-network .vis-navigation .vis-button:focus`
**Property**: `outline-offset: 2px !important;`
**Category**: other
**Current Specificity**: (0, 4, 6)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Button focus state (keyboard navigation)
 * KEEP !important - accessibility critical
 */
.vis-network .vis-navigation .vis-button:focus/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Button focus state (keyboard navigation)
 * KEEP !important - accessibility critical
 */
.vis-network .vis-navigation .vis-button:focus`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Button focus state (keyboard navigation)
 * KEEP !important - accessibility critical
 */
.vis-network .vis-navigation .vis-button:focus)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Button focus state (keyboard navigation)
 * KEEP !important - accessibility critical
 */
.vis-network .vis-navigation .vis-button:focus`
**Property**: `border-color: var(--color-sap-brand-blue) !important;`
**Category**: other
**Current Specificity**: (0, 4, 6)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Button focus state (keyboard navigation)
 * KEEP !important - accessibility critical
 */
.vis-network .vis-navigation .vis-button:focus/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Button focus state (keyboard navigation)
 * KEEP !important - accessibility critical
 */
.vis-network .vis-navigation .vis-button:focus`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Button focus state (keyboard navigation)
 * KEEP !important - accessibility critical
 */
.vis-network .vis-navigation .vis-button:focus)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `vis-button: disabled,
.vis-network .vis-navigation .vis-button.vis-disabled {
    background-color: var(--color-sap-surface-s1) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled`
**Property**: `border-color: var(--color-sap-border) !important;`
**Category**: other
**Current Specificity**: (0, 8, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled`
**Property**: `color: var(--color-sap-grayscale-t9) !important;`
**Category**: typography
**Current Specificity**: (0, 8, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled`
**Property**: `cursor: not-allowed !important;`
**Category**: other
**Current Specificity**: (0, 8, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled`
**Property**: `opacity: 0.4 !important;`
**Category**: visual
**Current Specificity**: (0, 8, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Disabled button state
 * KEEP !important - must override all other states
 */
.vis-network .vis-navigation .vis-button:disabled,
.vis-network .vis-navigation .vis-button.vis-disabled)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider`
**Property**: `background-color: var(--color-sap-surface-s1) !important;`
**Category**: visual
**Current Specificity**: (0, 3, 8)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider`
**Property**: `border: 1px solid var(--color-sap-grayscale-t9) !important;`
**Category**: visual
**Current Specificity**: (0, 3, 8)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider`
**Property**: `border-radius: var(--border-radius) !important;`
**Category**: visual
**Current Specificity**: (0, 3, 8)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Zoom slider styling
 * KEEP !important - matches button override strategy
 */
.vis-network .vis-navigation .vis-slider)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `.vis-network .vis-navigation .vis-slider-value`
**Property**: `background-color: var(--color-sap-brand-blue) !important;`
**Category**: visual
**Current Specificity**: (0, 3, 0)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `.vis-network .vis-navigation .vis-slider-value.vis-network`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body .vis-network .vis-navigation .vis-slider-value`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(.vis-network .vis-navigation .vis-slider-value)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
**Property**: `background-color: var(--color-sap-dark-surface) !important;`
**Category**: visual
**Current Specificity**: (0, 3, 12)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
**Property**: `border: 1px solid var(--color-sap-dark-surface) !important;`
**Category**: visual
**Current Specificity**: (0, 3, 12)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
**Property**: `border-radius: var(--border-radius) !important;`
**Category**: visual
**Current Specificity**: (0, 3, 12)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
**Property**: `color: var(--color-sap-white) !important;`
**Category**: typography
**Current Specificity**: (0, 3, 12)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
**Property**: `box-shadow: var(--shadow-tooltip) !important;`
**Category**: visual
**Current Specificity**: (0, 3, 12)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   NODE TOOLTIP STYLING
   (KEEP !important for structure; safe to remove padding)
   ============================================ */

/**
 * vis.js tooltip container
 * KEEP !important for background/border/color (overrides needed)
 * REMOVE !important from padding (Phase 2)
 */
.vis-network .vis-tooltip)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Node tooltip strong text (BEM: tooltip__label)
 * KEEP !important for color (dark tooltip context)
 */
.node-tooltip strong`
**Property**: `color: var(--color-sap-white) !important;`
**Category**: typography
**Current Specificity**: (0, 1, 8)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Node tooltip strong text (BEM: tooltip__label)
 * KEEP !important for color (dark tooltip context)
 */
.node-tooltip strong/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Node tooltip strong text (BEM: tooltip__label)
 * KEEP !important for color (dark tooltip context)
 */
.node-tooltip strong`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Node tooltip strong text (BEM: tooltip__label)
 * KEEP !important for color (dark tooltip context)
 */
.node-tooltip strong)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Node tooltip emphasis (BEM: tooltip__emphasis)
 * KEEP !important for color contrast in dark tooltip
 */
.node-tooltip em`
**Property**: `color: var(--color-sap-border) !important;`
**Category**: typography
**Current Specificity**: (0, 1, 11)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Node tooltip emphasis (BEM: tooltip__emphasis)
 * KEEP !important for color contrast in dark tooltip
 */
.node-tooltip em/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Node tooltip emphasis (BEM: tooltip__emphasis)
 * KEEP !important for color contrast in dark tooltip
 */
.node-tooltip em`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Node tooltip emphasis (BEM: tooltip__emphasis)
 * KEEP !important for color contrast in dark tooltip
 */
.node-tooltip em)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `prefers-contrast: high) {
    .vis-network .vis-navigation .vis-button {
        border-width: 2px !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ===========================================
   ACCESSIBILITY ENHANCEMENTS
   ============================================ */

/**
 * High contrast mode support
 * KEEP !important - accessibility critical
 */
@media (prefers-contrast: high)`
**Property**: `border-color: #000000 !important;`
**Category**: other
**Current Specificity**: (0, 0, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   ACCESSIBILITY ENHANCEMENTS
   ============================================ */

/**
 * High contrast mode support
 * KEEP !important - accessibility critical
 */
@media (prefers-contrast: high)/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   ACCESSIBILITY ENHANCEMENTS
   ============================================ */

/**
 * High contrast mode support
 * KEEP !important - accessibility critical
 */
@media (prefers-contrast: high)`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   ACCESSIBILITY ENHANCEMENTS
   ============================================ */

/**
 * High contrast mode support
 * KEEP !important - accessibility critical
 */
@media (prefers-contrast: high))`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `vis-button: hover {
        background-color: var(--color-sap-brand-blue) !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `.vis-network .vis-navigation .vis-button:hover`
**Property**: `color: var(--color-sap-white) !important;`
**Category**: typography
**Current Specificity**: (0, 4, 0)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `.vis-network .vis-navigation .vis-button:hover.vis-network`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body .vis-network .vis-navigation .vis-button:hover`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(.vis-network .vis-navigation .vis-button:hover)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `prefers-reduced-motion: reduce) {
    /* Global animation reduction */
    * {
        animation-duration: 0.01ms !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Reduced motion support (PHASE 3 - ENHANCED)
 * KEEP !important - respects user preferences
 * Comprehensive motion preference coverage
 */
@media (prefers-reduced-motion: reduce)`
**Property**: `animation-iteration-count: 1 !important;`
**Category**: other
**Current Specificity**: (0, 0, 11)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Reduced motion support (PHASE 3 - ENHANCED)
 * KEEP !important - respects user preferences
 * Comprehensive motion preference coverage
 */
@media (prefers-reduced-motion: reduce)/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Reduced motion support (PHASE 3 - ENHANCED)
 * KEEP !important - respects user preferences
 * Comprehensive motion preference coverage
 */
@media (prefers-reduced-motion: reduce)`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Reduced motion support (PHASE 3 - ENHANCED)
 * KEEP !important - respects user preferences
 * Comprehensive motion preference coverage
 */
@media (prefers-reduced-motion: reduce))`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Reduced motion support (PHASE 3 - ENHANCED)
 * KEEP !important - respects user preferences
 * Comprehensive motion preference coverage
 */
@media (prefers-reduced-motion: reduce)`
**Property**: `transition-duration: 0.01ms !important;`
**Category**: other
**Current Specificity**: (0, 0, 11)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/**
 * Reduced motion support (PHASE 3 - ENHANCED)
 * KEEP !important - respects user preferences
 * Comprehensive motion preference coverage
 */
@media (prefers-reduced-motion: reduce)/**`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /**
 * Reduced motion support (PHASE 3 - ENHANCED)
 * KEEP !important - respects user preferences
 * Comprehensive motion preference coverage
 */
@media (prefers-reduced-motion: reduce)`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/**
 * Reduced motion support (PHASE 3 - ENHANCED)
 * KEEP !important - respects user preferences
 * Comprehensive motion preference coverage
 */
@media (prefers-reduced-motion: reduce))`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Navigation buttons */
    .vis-network .vis-navigation .vis-button`
**Property**: `transition: none !important;`
**Category**: other
**Current Specificity**: (0, 3, 2)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Navigation buttons */
    .vis-network .vis-navigation .vis-button/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Navigation buttons */
    .vis-network .vis-navigation .vis-button`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Navigation buttons */
    .vis-network .vis-navigation .vis-button)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `vis-button: active {
        transform: none !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Legend transitions */
    #kgv2-legend-toggle`
**Property**: `transition: none !important;`
**Category**: other
**Current Specificity**: (1, 0, 2)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body /* Legend transitions */
    #kgv2-legend-toggle`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(/* Legend transitions */
    #kgv2-legend-toggle)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `/* Legend transitions */
    #kgv2-legend-toggle[class]`
   - Reason: Add generic attribute selector to increase specificity

---

**Selector**: `unknown`
**Property**: `display: instant */
    .vis-network .vis-tooltip {
        animation: none !important;`
**Category**: layout
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Tooltip display: instant */
    .vis-network .vis-tooltip`
**Property**: `transition: none !important;`
**Category**: other
**Current Specificity**: (0, 2, 3)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Tooltip display: instant */
    .vis-network .vis-tooltip/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Tooltip display: instant */
    .vis-network .vis-tooltip`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Tooltip display: instant */
    .vis-network .vis-tooltip)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button {
    width: 32px !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ===========================================
   RESPONSIVE ADJUSTMENTS (Mobile-First)
   ============================================ */

/**
 * Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button`
**Property**: `height: 32px !important;`
**Category**: layout
**Current Specificity**: (0, 3, 8)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   RESPONSIVE ADJUSTMENTS (Mobile-First)
   ============================================ */

/**
 * Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   RESPONSIVE ADJUSTMENTS (Mobile-First)
   ============================================ */

/**
 * Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   RESPONSIVE ADJUSTMENTS (Mobile-First)
   ============================================ */

/**
 * Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* ===========================================
   RESPONSIVE ADJUSTMENTS (Mobile-First)
   ============================================ */

/**
 * Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button`
**Property**: `font-size: 14px !important;`
**Category**: typography
**Current Specificity**: (0, 3, 8)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   RESPONSIVE ADJUSTMENTS (Mobile-First)
   ============================================ */

/**
 * Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   RESPONSIVE ADJUSTMENTS (Mobile-First)
   ============================================ */

/**
 * Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   RESPONSIVE ADJUSTMENTS (Mobile-First)
   ============================================ */

/**
 * Default: Small screens (< 769px)
 * Phase 3: Mobile-first approach
 */
.vis-network .vis-navigation .vis-button)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `screens: enlarge buttons */
@media (min-width: 769px) {
    .vis-network .vis-navigation .vis-button {
        width: 40px !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Desktop screens: enlarge buttons */
@media (min-width: 769px)`
**Property**: `height: 40px !important;`
**Category**: layout
**Current Specificity**: (0, 0, 4)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Desktop screens: enlarge buttons */
@media (min-width: 769px)/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Desktop screens: enlarge buttons */
@media (min-width: 769px)`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Desktop screens: enlarge buttons */
@media (min-width: 769px))`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Desktop screens: enlarge buttons */
@media (min-width: 769px)`
**Property**: `font-size: 14px !important;`
**Category**: typography
**Current Specificity**: (0, 0, 4)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Desktop screens: enlarge buttons */
@media (min-width: 769px)/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Desktop screens: enlarge buttons */
@media (min-width: 769px)`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Desktop screens: enlarge buttons */
@media (min-width: 769px))`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/**
 * Legend content collapsed state (block__content--collapsed)
 * Keep !important - state override
 */
#kgv2-legend-content.collapsed`
**Property**: `display: none !important;`
**Category**: layout
**Current Specificity**: (1, 1, 7)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body /**
 * Legend content collapsed state (block__content--collapsed)
 * Keep !important - state override
 */
#kgv2-legend-content.collapsed`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(/**
 * Legend content collapsed state (block__content--collapsed)
 * Keep !important - state override
 */
#kgv2-legend-content.collapsed)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `/**
 * Legend content collapsed state (block__content--collapsed)
 * Keep !important - state override
 */
#kgv2-legend-content.collapsed[class]`
   - Reason: Add generic attribute selector to increase specificity

---

**Selector**: `unknown`
**Property**: `mode: Explicit color definitions for validator/browser rendering */
@media (prefers-color-scheme: light) {
    /* Color modifier: table type (--table)
       Light mode: #0069e3 (Darker SAP Brand Blue) on #EBF5FE light background (4.61:1 ✅)
       WCAG 2.1 AA Compliant - Updated from #0070F2 (4.14:1 ❌)
    */
    .kgv2-legend-color.table {
        border-color: #0069e3 !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Light mode: Explicit color definitions for validator/browser rendering */
@media (prefers-color-scheme: light)`
**Property**: `background-color: #EBF5FE !important;`
**Category**: visual
**Current Specificity**: (0, 0, 8)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Light mode: Explicit color definitions for validator/browser rendering */
@media (prefers-color-scheme: light)/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Light mode: Explicit color definitions for validator/browser rendering */
@media (prefers-color-scheme: light)`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Light mode: Explicit color definitions for validator/browser rendering */
@media (prefers-color-scheme: light))`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `modifier: view type (--view)
       Light mode: #b15709 (Darker SAP Warning Orange) on #FEF7F1 light background (4.67:1 ✅)
       WCAG 2.1 AA Compliant - Updated from #E9730C (2.86:1 ❌)
    */
    .kgv2-legend-color.view {
        border-color: #b15709 !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Color modifier: view type (--view)
       Light mode: #b15709 (Darker SAP Warning Orange) on #FEF7F1 light background (4.67:1 ✅)
       WCAG 2.1 AA Compliant - Updated from #E9730C (2.86:1 ❌)
    */
    .kgv2-legend-color.view`
**Property**: `background-color: #FEF7F1 !important;`
**Category**: visual
**Current Specificity**: (3, 3, 14)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body /* Color modifier: view type (--view)
       Light mode: #b15709 (Darker SAP Warning Orange) on #FEF7F1 light background (4.67:1 ✅)
       WCAG 2.1 AA Compliant - Updated from #E9730C (2.86:1 ❌)
    */
    .kgv2-legend-color.view`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(/* Color modifier: view type (--view)
       Light mode: #b15709 (Darker SAP Warning Orange) on #FEF7F1 light background (4.67:1 ✅)
       WCAG 2.1 AA Compliant - Updated from #E9730C (2.86:1 ❌)
    */
    .kgv2-legend-color.view)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `/* Color modifier: view type (--view)
       Light mode: #b15709 (Darker SAP Warning Orange) on #FEF7F1 light background (4.67:1 ✅)
       WCAG 2.1 AA Compliant - Updated from #E9730C (2.86:1 ❌)
    */
    .kgv2-legend-color.view[class]`
   - Reason: Add generic attribute selector to increase specificity

---

**Selector**: `unknown`
**Property**: `modifier: synonym type (--synonym)
       Light mode: #107E3E (SAP Success Green) on #F1FAF4 light background (8.1:1 ✅)
    */
    .kgv2-legend-color.synonym {
        border-color: #107E3E !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Color modifier: synonym type (--synonym)
       Light mode: #107E3E (SAP Success Green) on #F1FAF4 light background (8.1:1 ✅)
    */
    .kgv2-legend-color.synonym`
**Property**: `background-color: #F1FAF4 !important;`
**Category**: visual
**Current Specificity**: (2, 2, 9)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body /* Color modifier: synonym type (--synonym)
       Light mode: #107E3E (SAP Success Green) on #F1FAF4 light background (8.1:1 ✅)
    */
    .kgv2-legend-color.synonym`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(/* Color modifier: synonym type (--synonym)
       Light mode: #107E3E (SAP Success Green) on #F1FAF4 light background (8.1:1 ✅)
    */
    .kgv2-legend-color.synonym)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `/* Color modifier: synonym type (--synonym)
       Light mode: #107E3E (SAP Success Green) on #F1FAF4 light background (8.1:1 ✅)
    */
    .kgv2-legend-color.synonym[class]`
   - Reason: Add generic attribute selector to increase specificity

---

**Selector**: `unknown`
**Property**: `modifier: default type (--default)
       Light mode: #A8A8A8 (grayscale) on #F5F6F7 light surface
    */
    .kgv2-legend-color.default {
        border-color: #6A6D70 !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Color modifier: default type (--default)
       Light mode: #A8A8A8 (grayscale) on #F5F6F7 light surface
    */
    .kgv2-legend-color.default`
**Property**: `background-color: #F5F6F7 !important;`
**Category**: visual
**Current Specificity**: (2, 2, 9)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body /* Color modifier: default type (--default)
       Light mode: #A8A8A8 (grayscale) on #F5F6F7 light surface
    */
    .kgv2-legend-color.default`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(/* Color modifier: default type (--default)
       Light mode: #A8A8A8 (grayscale) on #F5F6F7 light surface
    */
    .kgv2-legend-color.default)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `/* Color modifier: default type (--default)
       Light mode: #A8A8A8 (grayscale) on #F5F6F7 light surface
    */
    .kgv2-legend-color.default[class]`
   - Reason: Add generic attribute selector to increase specificity

---

**Selector**: `unknown`
**Property**: `mode: High-contrast color definitions for WCAG AA compliance */
@media (prefers-color-scheme: dark) {
    /* Color modifier: table type (--table)
       Dark mode: #FFFFFF (White) on #0D3A66 dark background (9.0:1 ✅✅)
    */
    .kgv2-legend-color.table {
        border-color: #FFFFFF !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Dark mode: High-contrast color definitions for WCAG AA compliance */
@media (prefers-color-scheme: dark)`
**Property**: `background-color: #0D3A66 !important;`
**Category**: visual
**Current Specificity**: (0, 0, 9)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* Dark mode: High-contrast color definitions for WCAG AA compliance */
@media (prefers-color-scheme: dark)/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* Dark mode: High-contrast color definitions for WCAG AA compliance */
@media (prefers-color-scheme: dark)`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* Dark mode: High-contrast color definitions for WCAG AA compliance */
@media (prefers-color-scheme: dark))`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `unknown`
**Property**: `modifier: view type (--view)
       Dark mode: #E9730C (SAP Warning Orange) on #3D2415 dark background (4.74:1 ✅)
    */
    .kgv2-legend-color.view {
        border-color: #E9730C !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Color modifier: view type (--view)
       Dark mode: #E9730C (SAP Warning Orange) on #3D2415 dark background (4.74:1 ✅)
    */
    .kgv2-legend-color.view`
**Property**: `background-color: #3D2415 !important;`
**Category**: visual
**Current Specificity**: (2, 2, 9)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body /* Color modifier: view type (--view)
       Dark mode: #E9730C (SAP Warning Orange) on #3D2415 dark background (4.74:1 ✅)
    */
    .kgv2-legend-color.view`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(/* Color modifier: view type (--view)
       Dark mode: #E9730C (SAP Warning Orange) on #3D2415 dark background (4.74:1 ✅)
    */
    .kgv2-legend-color.view)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `/* Color modifier: view type (--view)
       Dark mode: #E9730C (SAP Warning Orange) on #3D2415 dark background (4.74:1 ✅)
    */
    .kgv2-legend-color.view[class]`
   - Reason: Add generic attribute selector to increase specificity

---

**Selector**: `unknown`
**Property**: `modifier: synonym type (--synonym)
       Dark mode: #FFFFFF (White) on #1A4C2A dark background (9.2:1 ✅✅)
    */
    .kgv2-legend-color.synonym {
        border-color: #FFFFFF !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Color modifier: synonym type (--synonym)
       Dark mode: #FFFFFF (White) on #1A4C2A dark background (9.2:1 ✅✅)
    */
    .kgv2-legend-color.synonym`
**Property**: `background-color: #1A4C2A !important;`
**Category**: visual
**Current Specificity**: (2, 2, 9)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body /* Color modifier: synonym type (--synonym)
       Dark mode: #FFFFFF (White) on #1A4C2A dark background (9.2:1 ✅✅)
    */
    .kgv2-legend-color.synonym`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(/* Color modifier: synonym type (--synonym)
       Dark mode: #FFFFFF (White) on #1A4C2A dark background (9.2:1 ✅✅)
    */
    .kgv2-legend-color.synonym)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `/* Color modifier: synonym type (--synonym)
       Dark mode: #FFFFFF (White) on #1A4C2A dark background (9.2:1 ✅✅)
    */
    .kgv2-legend-color.synonym[class]`
   - Reason: Add generic attribute selector to increase specificity

---

**Selector**: `unknown`
**Property**: `modifier: default type (--default)
       Dark mode: #A8A8A8 (grayscale) on #2A2D30 dark surface (5.82:1 ✅)
    */
    .kgv2-legend-color.default {
        border-color: #A8A8A8 !important;`
**Category**: other
**Current Specificity**: (0, 0, 1)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `unknownunknown`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body unknown`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(unknown)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `/* Color modifier: default type (--default)
       Dark mode: #A8A8A8 (grayscale) on #2A2D30 dark surface (5.82:1 ✅)
    */
    .kgv2-legend-color.default`
**Property**: `background-color: #2A2D30 !important;`
**Category**: visual
**Current Specificity**: (2, 2, 9)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body /* Color modifier: default type (--default)
       Dark mode: #A8A8A8 (grayscale) on #2A2D30 dark surface (5.82:1 ✅)
    */
    .kgv2-legend-color.default`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(/* Color modifier: default type (--default)
       Dark mode: #A8A8A8 (grayscale) on #2A2D30 dark surface (5.82:1 ✅)
    */
    .kgv2-legend-color.default)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `/* Color modifier: default type (--default)
       Dark mode: #A8A8A8 (grayscale) on #2A2D30 dark surface (5.82:1 ✅)
    */
    .kgv2-legend-color.default[class]`
   - Reason: Add generic attribute selector to increase specificity

---

**Selector**: `/* ===========================================
   PRINT MODE
   ============================================ */

@media print`
**Property**: `display: none !important;`
**Category**: layout
**Current Specificity**: (0, 0, 3)

**Suggested Replacements**:

1. **duplicate_selector**
   - Selector: `/* ===========================================
   PRINT MODE
   ============================================ */

@media print/*`
   - Reason: Duplicate first part of selector to increase specificity

2. **body_prefix**
   - Selector: `body /* ===========================================
   PRINT MODE
   ============================================ */

@media print`
   - Reason: Add body prefix to increase specificity

3. **where_pseudo**
   - Selector: `:where(/* ===========================================
   PRINT MODE
   ============================================ */

@media print)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

---

**Selector**: `#kgv2-legend`
**Property**: `display: none !important;`
**Category**: layout
**Current Specificity**: (1, 0, 0)

**Suggested Replacements**:

1. **body_prefix**
   - Selector: `body #kgv2-legend`
   - Reason: Add body prefix to increase specificity

2. **where_pseudo**
   - Selector: `:where(#kgv2-legend)`
   - Reason: Use :where() to have 0 specificity, then layer appropriately
   - Note: Requires CSS cascade layers

3. **attribute_selector**
   - Selector: `#kgv2-legend[class]`
   - Reason: Add generic attribute selector to increase specificity

---
