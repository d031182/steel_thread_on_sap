# SAP UI5 Common Pitfalls

**Type**: Guideline  
**Category**: Development  
**Created**: 2026-01-24  
**Updated**: 2026-01-25

## Overview

Common mistakes when developing with SAP UI5, particularly with pure JavaScript (no XML views). These issues were discovered through real development and are documented to prevent recurrence.

## Critical Pitfall #1: Using 'class' Property

### The Problem ❌

```javascript
// DO NOT DO THIS
var oPage = new sap.m.Page({
    title: "My Page",
    class: "sapUiContentPadding"  // ❌ WRONG!
});
```

### The Error

```
Assertion failed: ManagedObject.apply: encountered unknown setting 'class'
Assertion failed: Method 'class' must be called with exactly one class name
```

### The Solution ✅

```javascript
// Step 1: Create control without class property
var oPage = new sap.m.Page({
    title: "My Page"
});

// Step 2: Add CSS classes using method
oPage.addStyleClass("sapUiContentPadding");
oPage.addStyleClass("sapUiSmallMargin");

// Step 3: Use the control
app.addPage(oPage);
```

### Why It Fails

SAP UI5 controls **do not support** a `class` property in their constructor. The word "class" is reserved.

### Automated Detection

```javascript
// Test to catch invalid usage
const invalidPattern = /new sap\.[a-z]+\.\w+\({[^}]*class:/;
assert.false(invalidPattern.test(html));
```

## Standard SAP UI5 CSS Classes

### Content Padding
```javascript
control.addStyleClass("sapUiContentPadding");    // 1rem (16px)
control.addStyleClass("sapUiNoContentPadding");  // Remove
```

### Margins
```javascript
control.addStyleClass("sapUiTinyMargin");      // 0.25rem (4px)
control.addStyleClass("sapUiSmallMargin");     // 0.5rem (8px)
control.addStyleClass("sapUiMediumMargin");    // 1rem (16px)
control.addStyleClass("sapUiLargeMargin");     // 2rem (32px)
```

### Responsive
```javascript
control.addStyleClass("sapUiResponsiveMargin");
control.addStyleClass("sapUiResponsiveMarginTop");
```

## Common Pitfall #2: JSON Structure Mismatches

### Problem

Loading JSON that doesn't match expected structure.

### Solution

```javascript
// Handle both formats
const data = JSON.parse(content);
if ('features' in data) {
    this.features = data.features;
} else {
    this.features = data;
}
```

## Common Pitfall #3: Mock Data in Tests

### Problem

Tests use simplified mocks, production uses real files.

### Solution

```javascript
// ✅ Test with actual production file
const features = loadFromFile('feature_flags.json');
assert(features.count > 0);
```

## Best Practices

1. ✅ Use `addStyleClass()` method
2. ✅ Test with real production files
3. ✅ Add integration tests
4. ✅ Check browser console for assertions
5. ✅ Document discovered pitfalls

## Related Components

- [[Feature Manager Module]] - Follows these patterns

## Related Architecture

- [[Modular Architecture]] - Testing approach
- [[CSN HANA Cloud Solution]] - Follows guidelines

## Related Guidelines

- [[Development Guidelines]] - Testing and quality standards

## Checklist for New Features

- [ ] No `class:` properties in constructors
- [ ] Using `addStyleClass()` properly
- [ ] Tested with real data
- [ ] Integration tests added
- [ ] Browser console clean
- [ ] Documentation updated

## Status

✅ **ACTIVE** - Updated with latest pitfalls and solutions