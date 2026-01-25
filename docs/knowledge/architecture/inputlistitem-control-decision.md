# InputListItem Control Decision

**Type**: Architecture Decision  
**Decision Date**: 2026-01-25  
**Status**: ✅ Adopted  
**Context**: Feature Manager UI with toggle switches

## Decision

**Use InputListItem (not CustomListItem) for settings lists with switches**

## Problem

When building a settings list with labels and toggle switches, which SAP UI5 control should be used?

**Options Considered**:
1. **InputListItem** - Designed for "label + input field" scenarios
2. **CustomListItem** - Designed for custom content layouts

## Context

### Initial Assumption
Documentation states InputListItem is for "label and input field", which we initially interpreted as text input fields only. This led to considering CustomListItem as the "proper" Fiori approach.

### Testing Results

**Implementation 1: InputListItem**
```javascript
new sap.m.InputListItem({
    label: "Application Logging",
    content: [new sap.m.Switch({ state: true })]
});
```

Result:
- ✅ Clean, compact appearance
- ✅ Perfect spacing (auto-handled by framework)
- ✅ Professional look
- ✅ User feedback: "Looks better"

**Implementation 2: CustomListItem**
```javascript
new sap.m.CustomListItem({
    content: [
        new sap.m.HBox({
            justifyContent: "SpaceBetween",
            items: [
                new sap.m.Label({ text: "Application Logging" }),
                new sap.m.Switch({ state: true })
            ]
        })
    ]
});
```

Result:
- ✅ Functionally correct
- ✅ Technically follows Fiori custom layout pattern
- ❌ User feedback: "Looks ugly"
- ❌ Excessive spacing
- ❌ Less professional appearance

## Key Insight

**Switch IS an Input Control**

A switch inputs boolean state (on/off, true/false), making it semantically an input control - just like:
- `sap.m.Input` inputs text
- `sap.m.DatePicker` inputs dates
- `sap.m.Select` inputs selections
- `sap.m.Switch` inputs boolean state ⭐

### User Interaction Pattern

**The determining factor**: What is the user trying to do?

- **StandardListItem**: User selects/clicks the list item itself (navigation, master-detail)
- **InputListItem**: User interacts with an input control within the item
- **CustomListItem**: Neither standard pattern fits

In our case:
- User is NOT selecting the list item
- User IS interacting with the switch (the input control)
- Therefore: InputListItem is semantically correct!

## Decision Rationale

### 1. Semantic Correctness ✅
- Switch is an input control (inputs boolean value)
- InputListItem = "label + input control" = Perfect fit
- More semantic than CustomListItem

### 2. User Experience ✅
- Clean, professional appearance
- Proper built-in spacing
- No CSS hacks needed
- Users prefer this implementation

### 3. Best Practices ✅
- Use standard controls over custom when possible
- Standard controls are battle-tested, maintained, accessible
- Only use CustomListItem when standard controls truly don't fit

### 4. Pragmatic Engineering ✅
- Cleaner code (no custom layouts)
- Easier to maintain
- Framework handles spacing/styling
- Less prone to future issues

## Consequences

### Positive
- ✅ Clean, professional UI
- ✅ Semantically correct implementation
- ✅ Follows "standard controls first" principle
- ✅ Easy to maintain
- ✅ Better user experience

### Negative
- ⚠️ Not the typical example shown in documentation
- ⚠️ Requires understanding that "input" means any input control

### Neutral
- Feature flag allows easy switching if needed
- Both implementations remain available for experimentation

## Related Documentation

- [[SAP Fiori Design Standards]] - Design principles applied
- [[SAP UI5 Common Pitfalls]] - Technical implementation guidelines
- [[HANA Connection UI]] - Another example using InputListItem pattern

## Implementation

### Current Production
```javascript
// Feature Manager in web/current/index.html
const USE_CUSTOM_LIST_ITEM = false;  // Using InputListItem

new sap.m.InputListItem({
    label: "Application Logging",
    content: [
        new sap.m.Switch({
            state: feature.enabled,
            change: function(oEvent) {
                handleFeatureToggle(feature.id, oEvent.getParameter("state"));
            }
        })
    ]
});
```

### Usage Pattern

**For any settings list with input controls**:
```javascript
const settingsList = new sap.m.List({
    items: [
        // Toggle switches
        new sap.m.InputListItem({
            label: "Dark Mode",
            content: [new sap.m.Switch({ state: true })]
        }),
        
        // Dropdowns
        new sap.m.InputListItem({
            label: "Theme",
            content: [new sap.m.Select({
                items: [
                    new sap.ui.core.Item({ text: "Light" }),
                    new sap.ui.core.Item({ text: "Dark" })
                ]
            })]
        }),
        
        // Sliders
        new sap.m.InputListItem({
            label: "Volume",
            content: [new sap.m.Slider({ 
                min: 0, max: 100, value: 50 
            })]
        })
    ]
});
```

## Control Selection Decision Tree

```
Need a list with controls?
│
├─ Does user INPUT data via a control?
│  └─ YES → InputListItem ✅
│     └─ Examples: Switch, Input, Select, Slider, DatePicker
│
├─ Does user SELECT the item itself?
│  └─ YES → StandardListItem ✅
│     └─ Examples: Navigation, master-detail, selection
│
└─ Complex custom layout needed?
   └─ YES → CustomListItem ⚠️
      └─ Use only as last resort
```

## Lessons Learned

### 1. Broader Definition of "Input"
Input control includes ANY control that accepts user input:
- Text fields (Input)
- Switches/toggles (Switch)
- Dropdowns (Select)
- Sliders (Slider)
- Date pickers (DatePicker)
- Checkboxes (CheckBox)

All are valid for InputListItem!

### 2. Semantic Over Literal
Don't interpret documentation too literally:
- Documentation: "label and input field"
- Our interpretation: "Only text input fields"
- Reality: "Any input control"

### 3. User Experience Validation
Hierarchy of truth:
1. User satisfaction (most important)
2. Semantic correctness (important)
3. Technical documentation (guideline, not law)

### 4. Standard Controls Priority
Always prefer standard controls:
- Even if not the obvious choice
- Even if docs don't show exact use case
- Standard = battle-tested + maintained + accessible

## References

### SAP UI5 SDK
- InputListItem: https://sapui5.hana.ondemand.com/#/api/sap.m.InputListItem
- CustomListItem: https://sapui5.hana.ondemand.com/#/api/sap.m.CustomListItem
- StandardListItem: https://sapui5.hana.ondemand.com/#/api/sap.m.StandardListItem

### Project Files
- Implementation: `web/current/index.html` (line ~850)
- Feature Manager: `modules/feature-manager/`
- Guidelines: `.clinerules`

## Status

✅ **ADOPTED** - Production implementation using InputListItem

**Applied in**:
- Feature Manager UI
- Settings screens
- Configuration panels

**Validated by**:
- User testing and feedback
- Semantic analysis
- Visual comparison
- Production usage

---

**Key Quote**:
> "The InputListItem expects not the user to select the listitem itself, but expect a specific input, and for that the switch on the InputListItem is a reasonable approach and preferable over a CustomListItem"
> 
> — User insight, January 25, 2026

This decision document preserves this important UX insight for all future development.