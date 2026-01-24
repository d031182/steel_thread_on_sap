# Fiori Control Selection Guide - Research & Documentation Task

**Created**: January 24, 2026  
**Priority**: High  
**Purpose**: Learn and document "WHEN to use which control" from official Fiori Design System  
**Source**: https://www.sap.com/design-system/fiori-design-web/

---

## 🎯 Objective

Create a comprehensive guide that answers:
> **"Which control should be used for this purpose according to Fiori guidelines?"**

This addresses the **STEP 0** principle in our development guidelines.

---

## 📚 Why This Matters

### **Current Challenge**
- Multiple controls may technically work for a scenario
- But only ONE is the Fiori-recommended choice
- Fiori guidelines specify WHEN to use which control
- We need this documented for quick reference

### **Lesson from Feature Manager**
```
❌ Wrong approach: "I'll use CustomListItem because it's flexible"
   → Result: CSS hacks needed, fighting the framework

✅ Right approach: "Which control is for lists with input controls?"
   → Answer: InputListItem (from Fiori guidelines)
   → Result: Built-in spacing, no CSS needed
```

---

## 🔍 Research Sources

### **Primary Source**
- **Fiori Design System**: https://www.sap.com/design-system/fiori-design-web/
  - This is THE authoritative source for WHEN to use controls
  - Contains design patterns, UX guidelines, control selection criteria

### **Secondary Sources**
- **SAP UI5 SDK**: https://sapui5.hana.ondemand.com/
  - For HOW to implement (API reference)
  - For technical details after choosing the right control

### **Project Documentation**
- `docs/fiori/SAP_FIORI_DESIGN_GUIDELINES.md`
- `docs/fiori/SAPUI5_API_QUICK_REFERENCE.md`

---

## 📋 Tasks to Complete

### **Phase 1: Research & Extraction** (2-3 hours)

**1.1 List Controls**
- [ ] Extract all list-related controls from Fiori Design System
  - When to use List
  - When to use StandardListItem
  - When to use InputListItem
  - When to use CustomListItem (last resort scenarios)
  - When to use ObjectListItem
  - When to use DisplayListItem

**1.2 Form Controls**
- [ ] Document form-related controls
  - When to use Input
  - When to use ComboBox
  - When to use Select
  - When to use MultiComboBox
  - When to use CheckBox vs Switch

**1.3 Layout Controls**
- [ ] Document layout patterns
  - When to use Page
  - When to use Panel
  - When to use IconTabBar
  - When to use FlexBox vs Grid
  - When to use VBox vs HBox

**1.4 Navigation Controls**
- [ ] Document navigation patterns
  - When to use ShellBar
  - When to use Breadcrumbs
  - When to use Button vs Link
  - When to use Menu vs ActionSheet

---

### **Phase 2: Documentation Structure** (1 hour)

Create: `docs/fiori/FIORI_CONTROL_SELECTION_GUIDE.md`

**Format**:
```markdown
# Control Name

## When to Use
[Scenarios from Fiori guidelines]

## When NOT to Use
[Alternative controls for other scenarios]

## Example Scenario
[Real-world use case]

## Related Controls
[Similar controls and when to prefer each]

## Reference
[Link to Fiori Design System page]
```

---

### **Phase 3: Decision Trees** (1 hour)

Create decision trees for common scenarios:

**Example - Lists**:
```
Need to display a list?
├─ Read-only display? → StandardListItem
├─ With input controls (switch, checkbox)? → InputListItem
├─ Complex layout needed? → ObjectListItem
├─ Custom layout (last resort)? → CustomListItem
└─ Just text in a list? → DisplayListItem
```

**Example - Forms**:
```
Need user input?
├─ Free text? → Input
├─ Single selection from list? → ComboBox or Select
├─ Multiple selections? → MultiComboBox
├─ Date/time? → DatePicker, TimePicker
└─ Boolean (on/off)? → Switch or CheckBox
```

---

### **Phase 4: Quick Reference Table** (30 minutes)

Create quick lookup table:

| Scenario | Recommended Control | Why |
|----------|-------------------|-----|
| List with switches | InputListItem | Built-in support for input controls |
| Read-only list | StandardListItem | Standard Fiori pattern |
| Complex list item | ObjectListItem | Structured layout support |
| Custom list layout | CustomListItem | Only when others don't fit |
| ... | ... | ... |

---

## 🎯 Deliverables

1. **Main Guide**: `docs/fiori/FIORI_CONTROL_SELECTION_GUIDE.md`
   - Comprehensive documentation of WHEN to use each control
   - Organized by control category (Lists, Forms, Navigation, etc.)
   - Decision trees for common scenarios

2. **Quick Reference**: `docs/fiori/FIORI_CONTROL_QUICK_REFERENCE.md`
   - One-page cheat sheet
   - Table format for fast lookup
   - Most common scenarios covered

3. **Integration**: Update `.clinerules`
   - Add link to new guide in STEP 0
   - Reference in "Where to Find Answers" section

---

## 📊 Success Criteria

### **Documentation Quality**
- [ ] Covers 80%+ of common UI scenarios
- [ ] Clear "When to use" vs "When NOT to use" sections
- [ ] Real-world examples included
- [ ] Decision trees for complex choices

### **Usability**
- [ ] Can find answer in < 30 seconds
- [ ] Clear, actionable guidance
- [ ] Links to official Fiori pages
- [ ] Integrated into development workflow

### **Impact**
- [ ] Reduces control selection time
- [ ] Prevents CSS hacks (choose right control first)
- [ ] Prevents custom controls (unless truly needed)
- [ ] Reference example for team

---

## 🔗 Integration Points

### **Development Guidelines** (`.clinerules`)
```markdown
**STEP 0: ASK THE RIGHT QUESTION FIRST**

Before writing any code, always ask:
> "Which control should be used for this purpose?"

**Where to Find Answers**:
- Fiori Design System: https://www.sap.com/design-system/fiori-design-web/
- Project Guide: `docs/fiori/FIORI_CONTROL_SELECTION_GUIDE.md` ⭐ NEW
- Quick Reference: `docs/fiori/FIORI_CONTROL_QUICK_REFERENCE.md` ⭐ NEW
```

### **AI Assistant Workflow**
```
When user requests UI:
1. Check: FIORI_CONTROL_SELECTION_GUIDE.md
2. Find: Which control for this scenario?
3. Verify: Fiori Design System link
4. Implement: Use recommended control
5. Result: No CSS hacks needed
```

---

## 📝 Example Entry Format

```markdown
# InputListItem

## When to Use ✅
- Lists with input controls (switches, checkboxes, input fields)
- Forms presented as lists
- Settings pages with toggles
- Configuration screens

## When NOT to Use ❌
- Read-only lists → Use StandardListItem
- Complex layouts → Use ObjectListItem
- Custom layouts → Use CustomListItem (last resort)

## Example Scenario
**Feature Manager**: List of features with on/off switches
```javascript
new sap.m.InputListItem({
    label: "Feature Name",
    content: [new sap.m.Switch()]
});
```

## Benefits
- ✅ Built-in proper spacing
- ✅ Standard Fiori appearance
- ✅ No CSS hacks needed
- ✅ Responsive by default

## Related Controls
- **StandardListItem**: For read-only lists
- **ObjectListItem**: For structured content
- **CustomListItem**: For custom layouts (avoid if possible)

## Reference
- Fiori Design System: [Link to specific page]
- SAP UI5 API: https://sapui5.hana.ondemand.com/#/api/sap.m.InputListItem
```

---

## 🚀 Next Steps

1. **Research Phase**: Extract control guidance from Fiori Design System
2. **Document Phase**: Create comprehensive guide
3. **Review Phase**: Validate against real use cases
4. **Integrate Phase**: Update development guidelines
5. **Share Phase**: Make available to team

---

## 📅 Timeline

**Estimated Time**: 4-5 hours total
- Research & Extraction: 2-3 hours
- Documentation: 1 hour
- Decision Trees: 1 hour
- Quick Reference: 30 minutes

**Priority**: High (prevents CSS hacks, improves code quality)

---

## 💡 Future Enhancements

1. **Interactive Decision Tree**: Web-based tool to select controls
2. **Code Templates**: Pre-built examples for each control
3. **Video Tutorials**: Screen recordings showing control selection
4. **Common Mistakes**: Document anti-patterns to avoid

---

**This task addresses the root cause of the Feature Manager issue: Not knowing WHICH control to choose from the start.**