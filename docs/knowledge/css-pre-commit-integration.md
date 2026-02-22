# CSS Pre-Commit Integration Guide

**Version**: 1.0  
**Date**: 2026-02-22  
**Related Tasks**: CSS-005  
**Dependencies**: [[css-design-tokens]], [[css-important-analysis-high-43-1]]

---

## Overview

The CSS Pre-Commit Integration provides automated validation of CSS files before they are committed to the repository. This ensures that:

1. **Design tokens** are used consistently (no magic numbers)
2. **`!important` declarations** are justified with comments
3. **Color contrast** meets WCAG AA standards
4. **BEM naming conventions** are followed
5. **Timing values** use standardized CSS variables

---

## Quick Start

### Installation

```bash
# Install pre-commit hooks
python scripts/install_pre_commit.py
```

This will:
- ✅ Install the `pre-commit` package
- ✅ Configure Git hooks
- ✅ Run initial validation

### Usage

Pre-commit hooks run **automatically** when you commit:

```bash
git add app_v2/static/css/main.css
git commit -m "feat: update button styles"
# ↑ Pre-commit hooks run here automatically
```

---

## What Gets Validated

### 1. Design Token Usage

**Check**: Detects magic numbers (hardcoded values) in CSS

**Example Violations**:
```css
/* ❌ BAD: Magic number */
.button {
    padding: 12px;
    margin: 8px;
}

/* ✅ GOOD: Uses design tokens */
.button {
    padding: var(--spacing-sm);
    margin: var(--spacing-xs);
}
```

**Action**: Replace magic numbers with CSS variables from `css-variables.css`

---

### 2. !important Declarations

**Check**: Ensures `!important` declarations have justification comments

**Example Violations**:
```css
/* ❌ BAD: No justification */
.override {
    color: red !important;
}

/* ✅ GOOD: Justified with comment */
.override {
    /* !important: Override third-party library styles (bootstrap.css:1234) */
    color: red !important;
}
```

**Action**: Add comment explaining why `!important` is necessary

---

### 3. Color Contrast (WCAG AA)

**Check**: Validates text/background color contrast ratios

**Requirements**:
- Normal text: **4.5:1** minimum
- Large text (18pt+ or 14pt+ bold): **3:1** minimum

**Example Violations**:
```css
/* ❌ BAD: Contrast ratio 2.1:1 (fails WCAG AA) */
.text {
    color: #999999;
    background-color: #ffffff;
}

/* ✅ GOOD: Contrast ratio 4.6:1 (passes WCAG AA) */
.text {
    color: var(--text-primary);  /* #333333 */
    background-color: var(--bg-primary);  /* #ffffff */
}
```

**Action**: Use compliant colors from `css-variables.css` or adjust colors

---

### 4. BEM Naming Conventions

**Check**: Validates Block__Element--Modifier naming pattern

**Example Violations**:
```css
/* ❌ BAD: Inconsistent naming */
.buttonPrimary { }
.button-icon { }
.button_large { }

/* ✅ GOOD: BEM convention */
.button { }                    /* Block */
.button__icon { }              /* Element */
.button--primary { }           /* Modifier */
.button__icon--large { }       /* Element + Modifier */
```

**Action**: Follow BEM naming pattern consistently

---

### 5. Timing Values

**Check**: Ensures animation/transition timing uses standardized variables

**Example Violations**:
```css
/* ❌ BAD: Magic timing value */
.fade {
    transition: opacity 300ms;
}

/* ✅ GOOD: Uses timing token */
.fade {
    transition: opacity var(--timing-normal);
}
```

**Action**: Use timing variables from `css-variables.css`

---

## Configuration

### Pre-Commit Config File

Location: `.pre-commit-config.yaml`

```yaml
repos:
  # Custom CSS validation (local hook)
  - repo: local
    hooks:
      - id: css-validation
        name: CSS Design Token & Quality Validation
        entry: python scripts/python/css_pre_commit_check.py
        language: system
        files: '\.(css)$'
        pass_filenames: true
        verbose: true
        stages: [commit]
```

### Validation Script

Location: `scripts/python/css_pre_commit_check.py`

**Features**:
- Accepts file arguments (pre-commit hook mode)
- Validates all files (standalone mode)
- Reports violations with file/line numbers
- Returns non-zero exit code on failures

**Usage**:
```bash
# Pre-commit hook mode (specific files)
python scripts/python/css_pre_commit_check.py app_v2/static/css/main.css

# Standalone mode (all CSS files)
python scripts/python/css_pre_commit_check.py

# Verbose output
python scripts/python/css_pre_commit_check.py --verbose
```

---

## Testing

### Automated Tests

Location: `tests/unit/css/test_pre_commit_integration.py`

```bash
# Run pre-commit integration tests
pytest tests/unit/css/test_pre_commit_integration.py -v

# Expected output:
# ✅ test_pre_commit_script_exists
# ✅ test_css_validation_detects_magic_numbers
# ✅ test_css_validation_detects_important_without_comment
# ✅ test_css_validation_passes_compliant_css
```

### Manual Testing

```bash
# Test pre-commit hooks on all files
pre-commit run --all-files

# Test specific hook
pre-commit run css-validation --all-files

# Test on staged files only
pre-commit run css-validation
```

---

## Bypassing Hooks (Emergency Only)

**⚠️ Not recommended** - Only use in emergencies

```bash
# Skip all pre-commit hooks
git commit --no-verify -m "emergency fix"
```

**Better Approach**: Fix validation issues or add justification comments

---

## Common Issues & Solutions

### Issue 1: Pre-commit Not Running

**Symptom**: Hooks don't run on commit

**Solution**:
```bash
# Reinstall hooks
pre-commit install

# Verify installation
ls -la .git/hooks/pre-commit
```

---

### Issue 2: Hook Fails on Valid CSS

**Symptom**: False positive violations

**Solution**:
1. Check if CSS variable is defined in `css-variables.css`
2. Verify syntax (e.g., `var(--spacing-sm)` not `var(spacing-sm)`)
3. Add justification comment if intentional exception

---

### Issue 3: Slow Hook Execution

**Symptom**: Commits take too long

**Solution**:
```bash
# Run hooks in parallel (if supported)
pre-commit run --all-files --show-diff-on-failure

# Update to latest hook versions
pre-commit autoupdate
```

---

## Maintenance

### Updating Hooks

```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Test after update
pre-commit run --all-files
```

### Adding New Validations

1. Update `scripts/python/css_pre_commit_check.py`
2. Add test cases to `tests/unit/css/test_pre_commit_integration.py`
3. Run tests: `pytest tests/unit/css/ -v`
4. Update this documentation

---

## Integration with CI/CD

### GitHub Actions (Planned)

```yaml
# .github/workflows/css-validation.yml
name: CSS Validation

on: [push, pull_request]

jobs:
  validate-css:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run CSS validation
        run: python scripts/python/css_pre_commit_check.py
```

---

## Related Documentation

- [[css-design-tokens]] - CSS variable definitions and usage
- [[css-important-analysis-high-43-1]] - !important declaration analysis
- [[Module Federation Standard]] - Overall architecture standards
- [[Gu Wu API Contract Testing Foundation]] - Testing methodology

---

## Validation Results

### Success Output

```
🔍 CSS Pre-Commit Validation
============================================================
📄 Found 5 CSS file(s)

✅ All CSS files passed validation!
============================================================
```

### Failure Output

```
🔍 CSS Pre-Commit Validation
============================================================
📄 Found 5 CSS file(s)

❌ app_v2/static/css/main.css
   - Line 45: Magic number '12px' detected (use design token)
   - Line 67: !important without justification comment

❌ modules/ai_assistant/frontend/styles/markdown.css
   - Line 23: Color contrast ratio 2.8:1 fails WCAG AA (need 4.5:1)

============================================================
❌ 2 file(s) with violations
============================================================
```

---

## Benefits

1. **Consistency**: Enforces design token usage across all CSS
2. **Quality**: Catches common CSS issues before commit
3. **Accessibility**: Ensures WCAG AA color contrast compliance
4. **Documentation**: Forces justification for `!important` usage
5. **Automation**: No manual validation required

---

## Version History

- **v1.0** (2026-02-22): Initial implementation (CSS-005)
  - Pre-commit hook configuration
  - Installation script
  - Comprehensive documentation
  - Test coverage