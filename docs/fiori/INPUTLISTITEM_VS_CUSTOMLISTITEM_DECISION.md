# InputListItem vs CustomListItem - UX Decision Document

**Date**: January 25, 2026  
**Context**: Feature Manager list with toggle switches  
**Decision**: Use **InputListItem** (not CustomListItem)  
**Status**: ✅ Production Implementation

---

## 🎯 The Question

**Scenario**: Building a settings list with labels and toggle switches

**Options**:
1. **InputListItem** - Designed for "label + input field" forms
2. **CustomListItem** - Designed for custom content layouts

**Question**: Which control should we use for a list with labels and switches?

---

## 📚 Official Documentation Analysis

### InputListItem Official Purpose

**From SAP UI5 SDK** (via Perplexity):
> "List item should be used for a **label and an input field**"

**Intended Use Cases**:
- ✅ Login forms (username/password inputs)
- ✅ Data entry lists (editable fields)
- ✅ Form-like scenarios on mobile
- ❌ NOT technically designed for settings with toggle switches

### CustomListItem Official Purpose

**From SAP UI5 SDK**:
> "Container for custom content when standard items don't fit"

**Intended Use Cases**:
- ✅ Complex layouts that standard items can't handle
- ✅ Multiple controls in custom arrangements
- ✅ When no standard item fits the requirement

---

## 🧪 Our Testing Results

### We Tested Both Implementations

#### Implementation 1: InputListItem
```javascript
new sap.m.InputListItem({
    label: "Application Logging",
    content: [new sap.m.Switch({ state: true })]
});
```

**Result**:
- ✅ Clean, compact appearance
- ✅ Perfect spacing (SAP UI5 auto-handles)
- ✅ Professional look
- ✅ User feedback: "Looks better"
- ⚠️ Not the official intended purpose

#### Implementation 2: CustomListItem (Fiori-recommended)
```javascript
new sap.m.CustomListItem({
    content: [
        new sap.m.HBox({
            justifyContent: "SpaceBetween",
            items: [
                new sap.m.VBox({
                    items: [
                        new sap.m.Label({ text: "Application Logging" }),
                        new sap.m.Text({ text: "SQLite-based logging system" })
                    ]
                }),
                new sap.m.Switch({ state: true })
            ]
        })
    ]
});
```

**Result**:
- ✅ Functionally perfect
- ✅ Technically "correct" per Fiori guidelines
- ❌ User feedback: "Looks ugly"
- ❌ Too much spacing
- ❌ Less professional feel

---

## 💡 The User's Expert Analysis

### Key Insight from Experience

> "The StandardListItem and the InputListItem is very same, except for that the StandardListItem is pure list usage, while the InputListItem expects not the user to select the listitem itself, but expect a specific input, and for that the switch on the InputListItem is a reasonable approach and preferable over a CustomListItem"

### Breaking Down This Insight

**1. StandardListItem vs InputListItem - The Difference**:
```
StandardListItem:
- User interacts with THE LIST ITEM ITSELF
- Click anywhere → selectionChange event
- Used for: Navigation, selection, master-detail

InputListItem:
- User interacts with THE INPUT CONTROL
- Click list item → nothing (just focus to input)
- Click input control → interact with control
- Used for: Forms, settings, data entry
```

**2. Why Switch on InputListItem Makes Sense**:
- ✅ User is NOT selecting the list item
- ✅ User is interacting with the SWITCH (the input)
- ✅ This matches InputListItem's design purpose perfectly!
- ✅ The "input" is the switch state (boolean input)

**3. Why NOT CustomListItem**:
- ❌ CustomListItem = "nothing else works, make it custom"
- ✅ InputListItem = "user needs to input something" (the switch state!)
- ✅ InputListItem is MORE semantic for this use case
- ✅ Using the right standard control > using custom control

---

## 🎓 The Principle

### User Interaction Pattern Determines Control Choice

**Ask yourself**: "What is the user trying to do?"

**If user selects the item itself** → StandardListItem
```javascript
// Example: Navigation list
new sap.m.StandardListItem({
    title: "Products",
    type: "Navigation",  // Click item → navigate
    press: function() { router.navTo("products"); }
});
```

**If user inputs data via a control** → InputListItem
```javascript
// Example: Settings with switch
new sap.m.InputListItem({
    label: "Dark Mode",
    content: [new sap.m.Switch()]  // User interacts with switch
});

// Example: Settings with slider
new sap.m.InputListItem({
    label: "Volume",
    content: [new sap.m.Slider({ value: 50 })]  // User interacts with slider
});
```

**If neither standard item works** → CustomListItem
```javascript
// Example: Complex layout with multiple interactions
new sap.m.CustomListItem({
    content: [/* complex custom layout */]
});
```

---

## ✅ Our Decision - InputListItem

### Reasoning

**1. Semantic Correctness** ✅
- User is INPUTTING switch state (boolean value)
- NOT selecting the list item for navigation/selection
- InputListItem = "label + input control" = Perfect fit!

**2. User Experience** ✅
- Clean, professional appearance
- Proper built-in spacing
- No CSS hacks needed
- Users prefer this implementation

**3. Pragmatic Choice** ✅
- Switch IS an input control (inputs boolean state)
- More semantic than CustomListItem
- Follows "use standard controls first" principle
- Only use CustomListItem when standard controls truly don't work

### The Key Insight

**Switch = Input Control**:
- Just like: Input (text), DatePicker (date), ComboBox (selection)
- A switch inputs: Boolean state (on/off, true/false)
- Therefore: InputListItem + Switch = Semantically correct!

---

## 📖 Design Pattern - Settings Lists

### The Pattern

**For any settings list with toggles/inputs**:

```javascript
// ✅ RECOMMENDED: InputListItem with input controls
const settingsList = new sap.m.List({
    items: [
        new sap.m.InputListItem({
            label: "Feature Name",
            content: [new sap.m.Switch({ state: true })]
        }),
        new sap.m.InputListItem({
            label: "Theme",
            content: [new sap.m.Select({
                items: [
                    new sap.ui.core.Item({ text: "Light" }),
                    new sap.ui.core.Item({ text: "Dark" })
                ]
            })]
        }),
        new sap.m.InputListItem({
            label: "Font Size",
            content: [new sap.m.Slider({ 
                min: 12, max: 24, value: 16 
            })]
        })
    ]
});
```

**Use Cases**:
- ✅ Settings/preferences screens
- ✅ Configuration panels
- ✅ Form-like lists
- ✅ Data entry workflows
- ✅ Any list where user inputs values (not selects items)

---

## 🔄 When To Use Each Control

### Decision Tree

```
Need a list with controls?
├─ Does user INPUT data?
│  ├─ YES → InputListItem ✅
│  │  └─ Examples: Switch, Input, Select, Slider, DatePicker
│  └─ NO → Continue...
│
├─ Does user SELECT the item?
│  ├─ YES → StandardListItem ✅
│  │  └─ Examples: Navigation, master-detail, selection lists
│  └─ NO → Continue...
│
└─ Complex custom layout?
   └─ YES → CustomListItem ⚠️
      └─ Examples: Multiple actions, complex data display
```

---

## 🎨 Visual Comparison

### InputListItem (Our Choice)
```
┌─────────────────────────────────────┐
│ Application Logging         [ON]   │ ← Clean
│ Feature Manager              [ON]   │ ← Compact
│ Debug Mode                  [OFF]   │ ← Professional
└─────────────────────────────────────┘
```

**Characteristics**:
- Single-line labels
- Right-aligned switches
- Consistent spacing (automatic)
- Tooltip for descriptions

### CustomListItem (Tested, Rejected)
```
┌─────────────────────────────────────┐
│ Application Logging                 │
│ SQLite-based logging system         │
│                               [ON]  │ ← Too spaced
│                                     │
│ Feature Manager                     │
│ Feature toggle system               │
│                               [ON]  │ ← Excessive space
└─────────────────────────────────────┘
```

**Characteristics**:
- Multi-line layout
- More vertical spacing
- Description visible always
- User feedback: "Ugly"

---

## 📝 Lessons Learned

### 1. "Input" Has Broader Meaning

**Input control ≠ Just text fields**

**Input controls include**:
- sap.m.Input (text)
- sap.m.Switch (boolean) ⭐
- sap.m.Select (selection)
- sap.m.Slider (number)
- sap.m.DatePicker (date)
- sap.m.CheckBox (boolean)
- sap.m.RadioButton (choice)

**All are valid for InputListItem!**

### 2. Semantic Over Literal

**Don't interpret documentation too literally**:
- Documentation says: "label and input field"
- We interpreted: "Only text input fields"
- Reality: "Any input control"
- Switch IS an input control (inputs boolean state)

### 3. User Experience Trumps Technical Purity

**The hierarchy of truth**:
1. **User satisfaction** (most important)
2. **Semantic correctness** (important)
3. **Technical documentation** (guideline, not law)

**In our case**:
- ✅ User satisfied (looks better)
- ✅ Semantically correct (switch = input)
- ⚠️ Not the example in docs (but still valid)

### 4. Standard Controls > Custom Controls

**Always prefer standard controls**:
- Even if not the obvious choice
- Even if docs don't show that exact use case
- Standard controls = battle-tested, maintained, accessible
- Only go custom when standard truly doesn't work

---

## 🔧 Implementation Details

### Feature Flag for Easy Switching

```javascript
// Line ~850 in web/current/index.html
const USE_CUSTOM_LIST_ITEM = false;  // Currently: InputListItem

// To experiment: Change to true for CustomListItem
```

**Benefits**:
- Easy A/B testing
- User can decide
- Both implementations proven working
- Switch in seconds

### Current Production Setting

**Active**: InputListItem (USE_CUSTOM_LIST_ITEM = false)

**Reasoning**:
1. ✅ User prefers appearance
2. ✅ Semantically correct (switch = input)
3. ✅ Cleaner spacing
4. ✅ More professional look
5. ✅ Better UX in practice

---

## 📚 References

### SAP UI5 SDK
- **InputListItem**: https://sapui5.hana.ondemand.com/#/api/sap.m.InputListItem
- **CustomListItem**: https://sapui5.hana.ondemand.com/#/api/sap.m.CustomListItem
- **StandardListItem**: https://sapui5.hana.ondemand.com/#/api/sap.m.StandardListItem

### Our Documentation
- Implementation: `web/current/index.html` (line ~850)
- Guidelines: `docs/DEVELOPMENT_GUIDELINES.md`
- Research: This document

---

## 🎯 Final Verdict

### InputListItem for Settings with Switches = ✅ CORRECT CHOICE

**Why**:
1. ✅ **Semantically correct** - Switch is an input control
2. ✅ **User approved** - Better appearance and UX
3. ✅ **Cleaner code** - Standard control, no custom layout
4. ✅ **Best practice** - Standard controls over custom
5. ✅ **Proven** - Working perfectly in production

**When someone asks**: "Is InputListItem correct for switches?"
**Answer**: "Yes! Switch is an input control (inputs boolean state), so InputListItem is semantically correct. User experience also confirms it's the better choice."

---

## 💬 Quote for the Archives

> "The StandardListItem and the InputListItem is very same, except for that the StandardListItem is pure list usage, while the InputListItem expects not the user to select the listitem itself, but expect a specific input, and for that the switch on the InputListItem is a reasonable approach and preferable over a CustomListItem"
> 
> — User, January 25, 2026, 2:17 AM

**This insight should be taught to all developers working with SAP UI5 settings screens!**

---

**Document Version**: 1.0  
**Author**: AI Documentation Team (based on user expertise)  
**Purpose**: Preserve this important UX insight for future development  
**Impact**: Prevents wasted time second-guessing control choice