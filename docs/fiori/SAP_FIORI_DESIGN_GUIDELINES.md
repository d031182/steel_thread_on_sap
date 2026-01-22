# SAP Fiori Design Guidelines for Web - Comprehensive Reference

> **Source**: https://www.sap.com/design-system/fiori-design-web/  
> **Scraped**: 2026-01-20  
> **Pages Scraped**: 8 comprehensive guideline pages  
> **Purpose**: Complete reference document for SAP Fiori design principles and guidelines for P2P project

---

## Table of Contents

1. [Overview](#overview)
2. [Visual Design Foundations](#visual-design-foundations)
3. [Interaction Design](#interaction-design)
4. [Action Placement](#action-placement)
5. [UI Text Guidelines](#ui-text-guidelines)
6. [Value States](#value-states)
7. [Empty States](#empty-states)
8. [Wrapping and Truncation](#wrapping-and-truncation)
9. [P2P-Specific Guidelines](#p2p-specific-guidelines)
10. [Quick Reference](#quick-reference)

---

## Overview

The SAP Fiori user interface for web apps. Learn how to design engaging and intuitive apps that can run on any device.

### Core Fiori Design Principles

1. **Role-Based**: Designed for specific user roles and tasks
2. **Adaptive**: Responsive across all devices and screen sizes
3. **Simple**: Clean, focused, and uncluttered interfaces
4. **Coherent**: Consistent look, feel, and behavior
5. **Delightful**: Engaging and enjoyable user experience

---

## Visual Design Foundations

Visual design plays a key role in how users perceive and recognize a product.

### 1. Design Tokens
- Central repository for all design values
- Consistent across all SAP technologies
- Clear, meaningful naming conventions

### 2. Theming
**Available Themes:**
- **Morning Horizon** (Light mode) - Latest
- **Evening Horizon** (Dark mode) - Latest
- High-Contrast Black/White
- Quartz Light/Dark (Legacy)

### 3. Colors
- **Semantic Colors**: Success, warning, error, information
- **Primary Colors**: Main brand colors
- **Accent Colors**: Highlight and emphasis

### 4. Typography
- "72" font family
- Enhanced readability
- Optimized for all devices

### 5. Iconography & Illustrations
- Grid system specifications
- Four responsive sizes
- Theme-specific variations

---

## Interaction Design

### Component States

A component can have only ONE state at a time:

#### 1. Enabled (Default)
- Component is interactive, focusable, visible, editable
- **Use when**: Component can currently be used

#### 2. Disabled
- **Use when**: Can't currently be used, but obvious how to enable it
- **Don't use when**: User can never enable it (hide instead)

#### 3. Read-Only
- Visible in edit mode but not editable
- Value can be recognized and selected but not changed
- **Use when**: Page in edit mode, component currently not editable

#### 4. Hidden
- Not visible, not focusable, not editable
- **Use when**: User lacks authorization, responsive behavior, context not available

---

## Action Placement

Actions trigger functions such as saving or deleting a business object.

### Core Principles
1. Place actions **close to the information** they act upon
2. Use **toolbars** to organize actions
3. **Right-align** all toolbar actions
4. ONE primary action per page only

### Toolbars

#### Header Toolbar
- Global actions (Edit, Delete, Filter, Share)
- Always visible ("sticky")
- **Action Groups (left to right)**:
  1. Business actions
  2. Manage content
  3. Manage layout
  4. Generic actions

#### Footer Toolbar
- Workflow/finalizing actions
- **Action Order (left to right)**:
  1. Forward path (Post, Submit)
  2. Alternative path (Return)
  3. Negative path (Cancel, Close)

#### Content Toolbars
- Table toolbar: Add, Edit, Delete, Filter, Sort
- Chart toolbar: Switch views, personalization

### Action Types

| Type | Use | Examples | Style |
|------|-----|----------|-------|
| **Primary** | Most important | Save, Submit | Emphasized |
| **Semantic** | Positive/Negative pairs | Approve/Reject | Semantic styling |
| **Secondary** | Other actions | Copy, Delete | Standard |
| **Negative Path** | Navigate away | Cancel, Close | Transparent |

---

## UI Text Guidelines

### Application Names

**Transactional**: Start with verb + plural object
- ✅ Create Billing Documents
- ✅ Manage Purchase Orders
- ✅ Approve Supplier Invoices

**Analytical**: Noun-based, avoid "analysis"
- ✅ Cash Flow
- ❌ Cash Flow Analysis

### Formatting

**Currencies**: EUR, USD (not €, $)

**Case**:
- **Title Case**: Labels, headings
- **Sentence Case**: Messages, explanations

**Colons**: Place after field labels when visually separate

**Periods**: Use for complete sentences only

**Quotation Marks**: Use double quotes ("") for variables

### Critical Action Labels

| Action | Description |
|--------|-------------|
| **Approve** | Grant permission |
| **Reject** | Refuse permission |
| **Create** | Save NEW object |
| **Save** | Save changes to EXISTING objects |
| **Submit** | Submit to workflow |
| **Cancel** | Stop system function |
| **Post** | Finalize document |

### Messages

**Form Validation**:
- ✅ Select a supplier
- ❌ Invalid entry

**Required Fields**:
`<Field Label> is a required field (*).`

**Message Box**:
- Use standard headings: Error, Warning, Information, Success
- Use action verbs for confirmation buttons
- Use Close (not OK) for errors

### Tables

**Column Headings**:
- Use slash with spaces: Price / Currency
- Use singular if one entry per row

**Empty Fields**: Leave blank (no hyphens, no N/A)

---

## Value States

Value states show semantic meaning of UI elements.

### 1. None (Default/Neutral)
- No semantic meaning assigned
- **Use**: Before/after successful validation

### 2. Positive (Success)
- **Use**: Action/validation successful
- **Color**: Green

### 3. Negative (Error)
- Prevents user from continuing
- **Use**: Validation failed, must be fixed
- **Color**: Red

### 4. Warning (Critical)
- Minor problem, can continue but might error later
- **Use**: Potential issues that should be considered
- **Color**: Orange/Yellow

### 5. Information
- AI suggestions, highlighted elements, info messages
- **Use**: Draw attention, recommendations available
- **Color**: Blue

### 6. Custom
- For special business use cases
- **Use**: When standard states don't fit

### P2P Examples

**Error States**:
- Missing required fields (Supplier, Amount, Date)
- Invalid format (Date, Currency)
- Duplicate invoice number

**Warning States**:
- Price variance detected
- Quantity variance detected
- Payment terms expiring soon

**Success States**:
- Invoice successfully posted
- Payment released
- Document approved

---

## Empty States

Empty states occur when there's no content to display.

### Types

#### 1. No Data
- **When**: First-time use, no activities yet
- **Guidance**: Explain what will appear when data is added
- **Example**: "No invoices yet. Create your first invoice to get started."

#### 2. User Action
- **When**: No search/filter results, process completed
- **Guidance**: Help understand situation, indicate next step
- **Example**: "No invoices match your filters. Try adjusting your search criteria."

#### 3. Errors
- **When**: Unable to load, missing permissions
- **Guidance**: Explain problem, corrective actions
- **Example**: "Unable to load invoices. Check your network connection or contact support."

### Best Practices

**Message Writing**:
- **Primary Message**: Single line explaining reason
- **Description**: Context and next steps (3 lines max)

**Call to Action**:
- Include action when clear next step exists
- Use secondary button or text link
- Don't use primary action button

**Illustration**:
- Use when space allows
- Must enhance message communication
- Not for small UI elements (tiles, toasts)

### P2P Examples

**No Purchase Orders**:
- Headline: "No Purchase Orders"
- Description: "Create your first purchase order to start the procurement process."
- Action: "Create Purchase Order" (button)

**No Search Results**:
- Headline: "No Invoices Found"
- Description: "No invoices match your search criteria. Try adjusting your filters or search term."
- Action: "Clear Filters" (link)

**Error State**:
- Headline: "Unable to Load Data"
- Description: "The system is currently unavailable. Please try again in a few moments."
- No action (system issue)

---

## Wrapping and Truncation

Defines how text behaves when it exceeds available space.

### When to Use

#### Use Wrapping When:
- Information is crucial
- User required to read full text
- Uncertain about importance
- Displaying numbers in continuous text
- Labels, object status, links, titles

#### Use Truncation When:
- Component designed to save vertical space
- Text contains only secondary information
- Column is resizable

#### Use Combination When:
- Text is a teaser (define max lines)
- Component saves space with limited lines

### Display Options

#### 1. Built-In Mechanism
Component reveals full text automatically
- Example: Dropdown list shows full text when opened

#### 2. Detail View
Full text visible after navigation
- Example: Card shows full text on detail page

#### 3. Expandable Text
Custom solution with Show More/Less link
- **In Place**: Expands text inline
- **Popover**: Opens popover with full text

### P2P Examples

**Wrap**:
- Invoice description (crucial info)
- Error messages
- Terms and conditions

**Truncate**:
- Supplier name in table (column resizable)
- Long material descriptions (secondary info)
- Notes field in list view

**Combination**:
- Purchase order items (2 lines, then truncate)
- Invoice line item descriptions (3 lines max)

---

## P2P-Specific Guidelines

### Components for P2P Workflow

#### 1. Tables
- Responsive tables with proper column headings
- Actions in table toolbar
- Semantic colors for status

#### 2. Forms
- Actions next to affected fields
- Proper labels with colons
- Form field validation

#### 3. Object Pages
- Header toolbar: Edit, Delete
- Footer toolbar: Save, Post, Submit
- Grouped sections

#### 4. Status Indicators
Use semantic colors:
- **Posted** (Green): Successfully posted
- **Held** (Red): Blocked due to variance
- **Parked** (Yellow): Draft, awaiting approval
- **Paid** (Green): Payment executed

### Application Naming

**Transactional**:
- Create Supplier Invoice
- Manage Purchase Orders
- Process Service Entry Sheets
- Approve Supplier Invoices

**Analytical**:
- Purchase Order Analysis
- Invoice Processing Metrics
- Supplier Performance

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

### Status Examples

**Purchase Orders**: Created → Released → Partially Received → Fully Received → Closed

**Supplier Invoices**: Parked → Posted → Held (Variance) → Paid

**Service Entry Sheets**: Created → Accepted/Rejected → Cancelled

**Payments**: Proposed → Released → Executed → Cancelled

### Validation Messages

**Error (Red - Prevents Action)**:
- "Supplier is a required field (*)"
- "Invoice amount must be greater than 0"
- "Invoice date cannot be in the future"

**Warning (Orange - Can Continue)**:
- "Price variance detected: Invoice price (460 EUR) differs from PO price (450 EUR)"
- "Quantity variance: Invoiced 110 units vs. received 100 units"
- "Payment terms expire in 2 days"

**Success (Green - Confirmation)**:
- "Invoice 2024001 successfully posted"
- "Payment released for 5 invoices"
- "Service entry sheet approved"

**Information (Blue - Guidance)**:
- "Cash discount available if paid within 10 days"
- "3-way match in progress"
- "Document forwarded to John Doe for approval"

### Empty State Examples

**No Invoices**:
- "No Supplier Invoices"
- "Create your first invoice or upload invoice data to get started."
- [Create Invoice] button

**No Variances**:
- "All Invoices Match"
- "Great! No price or quantity variances detected."
- No action needed

**Error Loading**:
- "Unable to Load Purchase Orders"
- "The system is temporarily unavailable. Please try again in a few moments."

---

## Quick Reference

### Key Resources
- **Official Site**: https://www.sap.com/design-system/fiori-design-web/
- **Guidelines Version**: 1.142 (Latest)
- **Current Theme**: Horizon (Morning & Evening modes)

### Pages Scraped (8 Total)
1. ✅ Main Landing Page
2. ✅ Visual Design Foundations (7 areas)
3. ✅ Component States (4 states)
4. ✅ UI Text Guidelines (40+ rules)
5. ✅ Action Placement (toolbars, buttons)
6. ✅ Value States (6 states)
7. ✅ Empty States (no-data scenarios)
8. ✅ Wrapping and Truncation

### Compliance
See `SAP_FIORI_COMPLIANCE_AUDIT.md` for complete checklist

---

## Notes

**Total Content**: ~70,000 words of design guidelines  
**Last Updated**: 2026-01-20  
**Maintained for**: P2P MCP Project  

For the most up-to-date specifications, always refer to the official SAP Design System website.
