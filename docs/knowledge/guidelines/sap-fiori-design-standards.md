# SAP Fiori Design Standards

**Type**: Guideline  
**Category**: Design & UX  
**Created**: 2026-01-20  
**Updated**: 2026-01-25  
**Source**: SAP Design System (https://www.sap.com/design-system/fiori-design-web/)

## Overview

Comprehensive SAP Fiori design principles and guidelines for creating engaging, intuitive web applications. These standards ensure consistency, usability, and professional appearance across all P2P project interfaces.

## Related Documentation

- [[SAP UI5 Common Pitfalls]] - Technical implementation pitfalls to avoid
- [[HANA Connection UI]] - Example implementation following these standards
- [[Modular Architecture]] - Architecture supporting Fiori components

## Core Design Principles

### 1. **Role-Based**
Design for specific user roles and tasks
- Tailor interface to user needs
- Show only relevant information
- Context-appropriate actions

### 2. **Adaptive** 
Responsive across all devices and screen sizes
- Mobile-first approach
- Flexible layouts (Grid, Flexbox)
- Breakpoints: Mobile (768px), Tablet (1024px)

### 3. **Simple**
Clean, focused, and uncluttered interfaces
- Minimize cognitive load
- Clear visual hierarchy
- Essential information only

### 4. **Coherent**
Consistent look, feel, and behavior
- Use standard components
- Follow spacing system
- Semantic color palette

### 5. **Delightful**
Engaging and enjoyable user experience
- Smooth animations (0.2s - 0.3s)
- Immediate feedback
- Professional polish

## Visual Design Foundations

### Theming

**Current Themes (Horizon)**:
- **Morning Horizon** (Light mode) - Recommended
- **Evening Horizon** (Dark mode)
- High-Contrast Black/White (Accessibility)

**Legacy Themes**:
- Quartz Light/Dark (deprecated)

### Color Palette

**Semantic Colors**:
```css
Success (Green):  #107e3e  /* Positive actions, completed states */
Warning (Orange): #e9730c  /* Caution, potential issues */
Error (Red):      #b00     /* Errors, failed validation */
Information (Blue): #0070f2 /* Guidance, recommendations */
```

**UI Colors**:
```css
Primary Blue:   #0070f2  /* Primary actions, links */
Shell Dark:     #354a5f  /* Navigation background */
Background:     #f5f6f7  /* Page background */
Text Primary:   #32363a  /* Body text */
Text Secondary: #6a6d70  /* Secondary text */
```

### Typography

**Font Family**: '72' (SAP proprietary)
- Optimized for all devices
- Enhanced readability
- Professional appearance

**Font Sizes**:
- Headings: 1.5rem - 2rem
- Body: 0.875rem - 1rem
- Small: 0.75rem

### Spacing System

**8px Grid System**:
```css
sapUiTinyMargin:        0.25rem (4px)   /* Fine adjustments */
sapUiSmallMargin:       0.5rem (8px)    /* Small gaps */
sapUiMediumMargin:      1rem (16px)     /* Medium gaps */
sapUiLargeMargin:       2rem (32px)     /* Large gaps */
sapUiContentPadding:    1rem (16px)     /* Content areas */
sapUiResponsiveMargin:  Variable        /* Responsive margins */
```

## Component States

Every component has ONE state at a time:

### 1. Enabled (Default)
- Interactive, focusable, visible, editable
- **Use**: Component can currently be used
- **Appearance**: Standard colors, hover effects

### 2. Disabled
- Non-interactive, grayed out
- **Use**: Can't be used now, but obvious how to enable
- **DON'T use**: If user can never enable (hide instead)
- **Appearance**: Opacity 50%, no hover effects

### 3. Read-Only
- Visible in edit mode but not editable
- Value can be selected but not changed
- **Use**: Page in edit mode, field not editable
- **Appearance**: No input affordance, selectable text

### 4. Hidden
- Not visible, not focusable
- **Use**: No authorization, responsive behavior, missing context
- **Implementation**: `display: none` or remove from DOM

## Action Placement

### Core Principles
1. Place actions **close to information** they affect
2. Use **toolbars** to organize actions
3. **Right-align** all toolbar actions
4. **ONE primary action** per page only

### Header Toolbar

**Purpose**: Global actions affecting entire page

**Action Groups (left to right)**:
1. **Business Actions**: Create, Post, Submit
2. **Manage Content**: Add, Edit, Delete
3. **Manage Layout**: Filter, Sort, Group
4. **Generic Actions**: Share, Download, Print

**Properties**:
- Always visible ("sticky")
- Right-aligned actions
- Icon + text or icon only (responsive)

### Footer Toolbar

**Purpose**: Workflow and finalizing actions

**Action Order (left to right)**:
1. **Forward Path**: Post, Submit, Save
2. **Alternative Path**: Save as Draft, Return
3. **Negative Path**: Cancel, Close

**Properties**:
- Appears at page bottom
- Sticky on scroll
- Clear primary action

### Content Toolbars

**Table Toolbar**:
- Add, Edit, Delete (left)
- Filter, Sort, Search (right)
- Above table content

**Chart Toolbar**:
- Switch views, personalization
- Zoom, download
- Context-specific actions

### Action Types & Styling

| Type | Purpose | Examples | Button Style |
|------|---------|----------|--------------|
| **Primary** | Most important | Save, Submit | Emphasized (blue) |
| **Semantic** | Positive/Negative | Approve/Reject | Green/Red |
| **Secondary** | Other actions | Copy, Delete | Standard (gray) |
| **Negative Path** | Navigate away | Cancel, Close | Transparent |

## UI Text Guidelines

### Application Names

**Transactional Apps** (verb + plural object):
- ✅ Create Billing Documents
- ✅ Manage Purchase Orders  
- ✅ Approve Supplier Invoices
- ❌ Billing Document Creation

**Analytical Apps** (noun-based):
- ✅ Cash Flow
- ✅ Supplier Performance
- ❌ Cash Flow Analysis (avoid "analysis")

### Text Formatting

**Currencies**: Use ISO codes
- ✅ EUR, USD, GBP
- ❌ €, $, £

**Case Rules**:
- **Title Case**: Labels, headings, buttons
- **Sentence case**: Messages, descriptions, tooltips

**Colons**: Use after labels when visually separate from value

**Periods**: Use only for complete sentences

**Quotation Marks**: Use double quotes ("") for variables in text

### Critical Action Labels

| Action | When to Use | Example |
|--------|-------------|---------|
| **Approve** | Grant permission | Approve Invoice |
| **Reject** | Refuse permission | Reject Purchase Order |
| **Create** | Save NEW object | Create Supplier Invoice |
| **Save** | Save changes to EXISTING | Save Changes |
| **Submit** | Submit to workflow | Submit for Approval |
| **Cancel** | Stop system function | Cancel Operation |
| **Post** | Finalize document | Post Invoice |

### Validation Messages

**Form Validation Format**:
```
✅ Good: "Select a supplier"
❌ Bad:  "Invalid entry"
```

**Required Field Message**:
```
"<Field Label> is a required field (*)."
Example: "Supplier is a required field (*)."
```

**Message Box Headings**:
- Use standard: Error, Warning, Information, Success
- Use action verbs for confirmation buttons
- Use "Close" (not "OK") for errors

### Table Guidelines

**Column Headings**:
- Use slash with spaces: `Price / Currency`
- Use singular if one entry per row
- Title Case

**Empty Fields**: Leave blank
- ❌ Don't use: hyphens, "N/A", dashes

## Value States

Semantic meaning for UI elements:

### 1. None (Default/Neutral)
- No semantic meaning
- **Use**: Before/after successful validation
- **Color**: Standard (gray/black)

### 2. Positive (Success)
- Action/validation successful
- **Use**: Confirmation, completion
- **Color**: Green (#107e3e)
- **Icon**: ✓ checkmark

### 3. Negative (Error)
- Prevents continuation
- **Use**: Validation failed, must fix
- **Color**: Red (#b00)
- **Icon**: ✗ error

### 4. Warning (Critical)
- Can continue but might error later
- **Use**: Potential issues to consider
- **Color**: Orange (#e9730c)
- **Icon**: ⚠ warning

### 5. Information
- AI suggestions, recommendations
- **Use**: Draw attention, helpful info
- **Color**: Blue (#0070f2)
- **Icon**: ℹ info

### 6. Custom
- Special business use cases
- **Use**: When standard states don't fit
- **Color**: Custom (project-specific)

## Empty States

When there's no content to display:

### 1. No Data (First Use)
**When**: First-time use, no activities yet

**Structure**:
```
Headline: "No Purchase Orders"
Description: "Create your first purchase order to start 
             the procurement process."
Action: [Create Purchase Order] (button)
```

### 2. User Action (Filtered Results)
**When**: No search/filter results

**Structure**:
```
Headline: "No Invoices Found"
Description: "No invoices match your search criteria. 
             Try adjusting your filters."
Action: "Clear Filters" (link)
```

### 3. Errors (System Issues)
**When**: Unable to load, missing permissions

**Structure**:
```
Headline: "Unable to Load Data"
Description: "The system is currently unavailable. 
             Please try again in a few moments."
Action: None (system issue)
```

### Best Practices

**Message Writing**:
- **Primary**: Single line (reason)
- **Description**: Context + next steps (3 lines max)
- Use simple, clear language

**Illustrations**:
- Use when space allows
- Must enhance communication
- Not for small UI (tiles, toasts)

**Call to Action**:
- Include when clear next step exists
- Use secondary button or text link
- DON'T use primary action button

## Wrapping vs Truncation

### Use Wrapping When:
- Information is crucial
- User must read full text
- Uncertain about importance
- Displaying numbers in continuous text
- Labels, status, links, titles

### Use Truncation When:
- Component designed to save vertical space
- Text contains secondary information only
- Column is resizable (user can expand)

### Use Combination When:
- Text is a teaser (define max lines)
- Component saves space with limited lines
- Example: 2 lines visible, then "Show More"

### Display Mechanisms

1. **Built-In**: Component reveals full text automatically
   - Example: Dropdown shows full text when opened

2. **Detail View**: Full text on navigation
   - Example: Card teaser → Full text on detail page

3. **Expandable Text**: Custom "Show More" link
   - **In Place**: Expands inline
   - **Popover**: Opens overlay with full text

## P2P-Specific Applications

### Status Indicators

Use semantic colors for P2P statuses:

**Purchase Orders**:
- Created (Blue) → Released (Green) → Received (Green) → Closed (Gray)

**Supplier Invoices**:
- Parked (Yellow) → Posted (Green) → Held (Red) → Paid (Green)

**Service Entry Sheets**:
- Created (Blue) → Accepted (Green) / Rejected (Red)

**Payments**:
- Proposed (Blue) → Released (Green) → Executed (Green) → Cancelled (Red)

### Validation Messages

**Error (Red - Blocking)**:
```
"Supplier is a required field (*)"
"Invoice amount must be greater than 0"
"Invoice date cannot be in the future"
```

**Warning (Orange - Can Continue)**:
```
"Price variance detected: Invoice 460 EUR vs PO 450 EUR"
"Quantity variance: Invoiced 110 units vs received 100"
"Payment terms expire in 2 days"
```

**Success (Green - Confirmation)**:
```
"Invoice 2024001 successfully posted"
"Payment released for 5 invoices"
"Service entry sheet approved"
```

**Information (Blue - Guidance)**:
```
"Cash discount available if paid within 10 days"
"3-way match in progress"
"Document forwarded to John Doe for approval"
```

### Application Naming

**Transactional**:
- Create Supplier Invoice
- Manage Purchase Orders
- Process Service Entry Sheets
- Approve Supplier Invoices

**Analytical**:
- Purchase Order Analysis
- Invoice Processing Metrics
- Supplier Performance Dashboard

### Action Labels

**Creation**:
- Create Purchase Order
- Create Supplier Invoice
- Copy from Purchase Order

**Processing**:
- Post Invoice
- Hold Invoice
- Release Purchase Order
- Approve Service Entry Sheet

**Workflow**:
- Forward to Approver
- Return to Supplier
- Block for Payment
- Release Payment

## Fiori Floorplans

### List Report
**Purpose**: Entry point, browse/search objects

**Components**:
- Filter bar (top)
- Table or card grid
- Action toolbar
- Navigation to Object Page

### Object Page
**Purpose**: Display/edit single object

**Components**:
- Header (title, image, metadata)
- Action toolbar (Edit, Delete, Share)
- Tabbed sections
- Footer toolbar (Save, Cancel)

### Master-Detail
**Purpose**: Side-by-side navigation

**Components**:
- Master list (left/top)
- Detail view (right/bottom)
- Independent scrolling
- Responsive collapse

### Wizard
**Purpose**: Multi-step process

**Components**:
- Step indicator
- Navigation (Next, Previous)
- Review step
- Confirmation

## Quick Reference

### Design Tokens
- Font: '72'
- Primary Color: #0070f2
- Success: #107e3e
- Warning: #e9730c
- Error: #b00
- Grid: 8px base

### Spacing
- Tiny: 4px
- Small: 8px
- Medium: 16px
- Large: 32px

### Actions
- Primary: Blue, emphasized
- Secondary: Gray, standard
- Negative: Transparent
- ONE primary per page

### States
- Default: Enabled
- Disabled: 50% opacity
- Read-only: No input affordance
- Hidden: display: none

## Resources

### Official Documentation
- **Main Site**: https://www.sap.com/design-system/fiori-design-web/
- **Version**: 1.142 (current)
- **Theme**: Horizon (Morning/Evening)

### Related Project Docs
- **Technical Implementation**: [[SAP UI5 Common Pitfalls]]
- **Example Application**: [[HANA Connection UI]]
- **Compliance Audit**: `docs/archive/SAP_FIORI_COMPLIANCE_AUDIT.md`

### Extended Guidelines
Additional comprehensive references:
- `docs/fiori/FIORI_DESIGN_EXTENDED_GUIDELINES.md` (44KB)
- `docs/fiori/SAPUI5_DEVELOPER_REFERENCE.md` (42KB)
- `docs/fiori/SAP_HELP_PORTAL_BEST_PRACTICES.md` (39KB)

## Status

✅ **ACTIVE GUIDELINES** - Apply to all P2P UI development

**Last Updated**: 2026-01-25  
**Source Scraped**: 2026-01-20 (8 comprehensive pages)  
**Compliance**: Required for all frontend development