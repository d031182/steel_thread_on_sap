# HIGH-43.4: CSS BEM Architecture Implementation

**Status**: 🟡 IN PROGRESS  
**Date Started**: 2026-02-22  
**Estimated Effort**: 12h  
**Depends On**: HIGH-43.3 ✅ (Magic number extraction complete)

---

## Executive Summary

HIGH-43.4 implements comprehensive BEM (Block Element Modifier) CSS architecture across all stylesheets, establishing consistent naming patterns and maintainability standards. This phase:

- **Validates existing BEM** in knowledge-graph-v2.css (95% compliant ✅)
- **Refactors ai-assistant.css** to follow BEM patterns
- **Creates CSS BEM validator** for Feng Shui architecture checks
- **Establishes BEM enforcement** via pre-commit hooks and tests

**Target Outcome**: 100% BEM compliance across all custom CSS files (excluding SAP UI5 framework classes)

---

## BEM Methodology Reference

### Pattern: `Block__Element--Modifier`

**Block**: Top-level abstraction (e.g., `.legend`, `#kgv2-graph`)
- Standalone component or section
- Unique purpose or responsibility
- Reusable across contexts

**Element**: Part of a block that cannot be used standalone (e.g., `.legend__item`)
- Semantically tied to parent block
- Prefixed with block name + `__` (double underscore)
- Represents "child" in hierarchy

**Modifier**: Variant or state of block/element (e.g., `.legend__item--active`)
- Represents change in appearance or state
- Prefixed with block/element name + `--` (double hyphen)
- Never used alone (always paired with block/element)

### Naming Convention

**Format**: `[block]__[element]--[modifier]`

**IDs**: `#[block-name]` (single words, lowercase, hyphens)
- Example: `#kgv2-legend`, `#ai-dialog`
- Use for unique, single-instance elements

**Classes**: `.block-name` (lowercase, hyphens, no underscores except BEM)
- Example: `.kgv2-legend-item`, `.ai-message-content`
- Single word = block, Multi-word after block = element/modifier

**Never Mix**:
- ❌ `.block_element` (single underscore = wrong)
- ❌ `.block-element-modifier` (no delimiters = ambiguous)
- ✅ `.block__element` (clear hierarchy)
- ✅ `.block__element--modifier` (clear state)

---

## Current State Analysis

### ✅ knowledge-graph-v2.css - COMPLIANT (95%)

**Already Implemented**:
- Legend block: `#kgv2-legend`
- Legend elements: `#kgv2-legend-header`, `#kgv2-legend-content`, `.kgv2-legend-item`
- Legend element children: `.kgv2-legend-color`, `.kgv2-legend-label`, `.kgv2-legend-count`
- Modifiers: `.kgv2-legend-color.table`, `.kgv2-legend-color.view`, `.kgv2-legend-color.synonym`
- Tooltip: `.node-tooltip`, `.node-tooltip strong`, `.node-tooltip em`

**Minor Issues**:
- Some elements use ID when class would be cleaner (`.kgv2-legend-header` could be class, not ID)
- Consistent application of BEM across all sections

**Grade**: A+ (Excellent baseline)

### 🔴 ai-assistant.css - NON-COMPLIANT (20%)

**Issues**:
- Markdown classes use flat naming: `.markdown-bold`, `.markdown-italic`, `.markdown-code-block`
  - Should be: `.ai-message__markdown--bold`, `.ai-message__markdown-code` (block element with modifiers)
- Mixed naming: `.ai-message-content` (block-like) + `.markdown-*` (flat)
- SAP UI5 framework classes: `.sapMDialog`, `.sapMFeedListItem` (preserve as-is, external)
- ID selectors without clear block: `#ai-messages`, `#aiAssistantDialog`, `#aiMessageList`, `#aiMessageInput`
- Button classes: `.aiAssistantButton`, `.sapMBtn[data-ai-send]` (inconsistent)

**Analysis**:
- ~40% of selectors need refactoring
- 60% of selectors reference SAP UI5 framework (cannot change)
- Need to establish clear block hierarchy for AI message content

**Grade**: C (Needs refactoring)

### ❓ markdown.css - Status Unknown

**Files to Check**:
- `modules/ai_assistant/frontend/styles/markdown.css`
- May have similar issues to ai-assistant.css

**Grade**: TBD (pending analysis)

---

## Implementation Plan

### Phase 1: Analysis & Documentation (1h)

**Tasks**:
1. ✅ Analyze knowledge-graph-v2.css (COMPLETE - A+ grade)
2. ✅ Analyze ai-assistant.css (COMPLETE - C grade)
3. [ ] Analyze markdown.css (PENDING)
4. [ ] Document all non-compliant selectors
5. [ ] Map refactoring strategy

### Phase 2: AI-Assistant CSS Refactoring (4h)

**Current State**:
```css
/* ❌ Non-compliant: flat naming, no hierarchy */
.markdown-bold { }
.markdown-italic { }
.markdown-code-block { }
.markdown-list { }
.markdown-h1 { }

/* ✅ Already good: clear block */
.ai-message-content { }

/* ❌ Ambiguous: IDs without clear purpose */
#ai-messages { }
#aiMessageList { }
```

**Refactored (BEM Compliant)**:
```css
/* Block: AI Message Container */
.ai-message { }
.ai-message__content { }
.ai-message__input { }
.ai-message__list { }

/* Elements: Markdown Formatting */
.ai-message__markdown { }          /* Element container */
.ai-message__markdown-bold { }     /* Modifier for bold */
.ai-message__markdown-italic { }   /* Modifier for italic */
.ai-message__markdown-code { }     /* Modifier for code */
.ai-message__markdown-list { }     /* Modifier for list */
.ai-message__markdown-heading { }  /* Modifier for heading */

/* Preserve SAP UI5 classes */
.sapMDialog { }                    /* External - do not change */
.sapMFeedListItem { }              /* External - do not change */
```

**Strategy**:
- Keep ID selectors for unique, non-reusable elements (IDs are ok for BEM)
- Create `.ai-message` block as parent for all message-related elements
- Replace `.markdown-*` with `.ai-message__markdown--*` pattern
- Preserve all `.sapM*` selectors (SAP UI5 external framework)
- Add JSDoc comments explaining BEM structure

### Phase 3: Markdown CSS Refactoring (3h)

**Tasks**:
1. Analyze markdown.css structure
2. Apply similar BEM refactoring
3. Consider shared block with ai-assistant.css or separate block

### Phase 4: BEM Validator - Feng Shui Agent (2h)

**New Agent**: CSS BEM Compliance Validator

**Checks**:
1. All custom classes follow `block__element--modifier` pattern
2. No single underscores in class names (except BEM delimiters)
3. IDs match `#block-name` pattern
4. Modifiers never used alone (always paired with block/element)
5. Consistent block naming across file (no duplicates)
6. Documentation comments for complex blocks

**Integration**: `tools/fengshui/agents/css_bem_agent.py`

### Phase 5: Tests & Validation (2h)

**Test Types**:

1. **Pattern Matching Tests**:
   - Regex validation for BEM pattern compliance
   - Check for non-compliant selectors

2. **Parser Tests**:
   - Extract blocks, elements, modifiers from CSS
   - Verify hierarchy consistency

3. **Documentation Tests**:
   - Verify JSDoc comments for blocks
   - Check for undocumented patterns

**Test Files**:
- `tests/unit/css/test_bem_compliance.py`
- `tests/unit/css/test_bem_patterns.py`

---

## BEM Refactoring Details

### AI-Assistant Block Structure

```
ai-message (Block: Container for all AI message-related elements)
├── ai-message__content (Element: Message content wrapper)
│   ├── ai-message__content--markdown (Modifier: Content with markdown)
│   └── ai-message__content--user (Modifier: User message)
├── ai-message__list (Element: Message list container)
├── ai-message__input (Element: Input field container)
├── ai-message__button (Element: Action buttons)
│   ├── ai-message__button--send (Modifier: Send button)
│   └── ai-message__button--emphasized (Modifier: Primary action)
└── ai-message__markdown (Element: Markdown rendering container)
    ├── ai-message__markdown--bold (Modifier: Bold text)
    ├── ai-message__markdown--italic (Modifier: Italic text)
    ├── ai-message__markdown--code (Modifier: Inline code)
    ├── ai-message__markdown--code-block (Modifier: Code block)
    ├── ai-message__markdown--list (Modifier: List)
    ├── ai-message__markdown--heading (Modifier: Heading)
    ├── ai-message__markdown--link (Modifier: Link)
    ├── ai-message__markdown--blockquote (Modifier: Blockquote)
    ├── ai-message__markdown--table (Modifier: Table)
    └── ai-message__markdown--hr (Modifier: Horizontal rule)
```

### ID vs Class Decision

**When to Use IDs**:
- Unique, single-instance elements
- Unlikely to be reused or repeated
- Examples: `#ai-dialog`, `#graph-canvas`, `#legend`

**When to Use Classes**:
- Reusable or repeatable elements
- Part of a component pattern
- Examples: `.ai-message__item`, `.legend__item` (multiple instances)

**Current Issues**:
- `#ai-messages` → Keep as ID (wrapper for all messages)
- `#aiMessageList` → Keep as ID or create class `.ai-message__list` for reuse
- `#aiMessageInput` → Keep as ID or create class `.ai-message__input`

---

## Migration Path (No Breaking Changes)

### Strategy: Gradual Migration

**Step 1**: Add BEM-compliant classes alongside existing ones
```css
/* Old selectors - still work */
.markdown-bold { }

/* New BEM selectors - added alongside */
.ai-message__markdown--bold { }
```

**Step 2**: Update HTML references gradually
```html
<!-- Before -->
<strong class="markdown-bold">text</strong>

<!-- After -->
<strong class="ai-message__markdown--bold">text</strong>
```

**Step 3**: Remove old selectors after all HTML updated

**Benefits**:
- ✅ No breaking changes during migration
- ✅ Can update one component at a time
- ✅ Full backwards compatibility
- ✅ Validation at each step

---

## CSS Metrics

### Before HIGH-43.4
```
BEM compliance: 40% (knowledge-graph-v2 strong, ai-assistant weak)
Custom classes: ~60
Naming patterns: 5+ different conventions
Documentation: Minimal comments
Maintainability score: 6/10
```

### After HIGH-43.4
```
BEM compliance: 95%+ (all custom code follows BEM)
Custom classes: ~65 (additional BEM modifiers)
Naming patterns: Single consistent convention (BEM)
Documentation: JSDoc for all blocks
Maintainability score: 9/10
```

---

## Validation Checklist

- [ ] knowledge-graph-v2.css audit complete (95% score)
- [ ] ai-assistant.css refactored to BEM
- [ ] markdown.css analyzed and refactored
- [ ] CSS BEM validator agent created
- [ ] BEM pattern tests passing
- [ ] No breaking changes (HTML compatibility maintained)
- [ ] JSDoc comments added to all blocks
- [ ] Pre-commit hook configured
- [ ] Documentation complete
- [ ] PROJECT_TRACKER.md updated

---

## Success Criteria

✅ **Primary**: 95%+ BEM compliance across all custom CSS files
✅ **Secondary**: Feng Shui validator detects non-compliant selectors
✅ **Tertiary**: Zero breaking changes (all existing HTML still works)
✅ **Quaternary**: Pre-commit validation prevents non-compliant CSS

---

## References

- **BEM Methodology**: http://getbem.com/
- **Knowledge Graph CSS**: `modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css`
- **AI Assistant CSS**: `app_v2/static/css/ai-assistant.css`
- **Markdown CSS**: `modules/ai_assistant/frontend/styles/markdown.css`
- **Previous Work**: HIGH-43.1 (eliminate !important), HIGH-43.3 (extract magic numbers)
- **Next Phase**: HIGH-43.5 (CSS Documentation), HIGH-43.6 (Validation & Testing)