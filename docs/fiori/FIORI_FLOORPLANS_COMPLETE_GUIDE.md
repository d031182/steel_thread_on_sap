# SAP Fiori Floorplans - Complete Guide

**Purpose**: Comprehensive guide to SAP Fiori floorplans for building enterprise applications  
**Version**: 1.0  
**Last Updated**: January 24, 2026  
**Source**: Scraped from SAP Fiori Design Guidelines via Perplexity MCP

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [List Report Floorplan](#list-report-floorplan)
3. [Worklist Floorplan](#worklist-floorplan)
4. [Object Page Floorplan](#object-page-floorplan)
5. [Choosing the Right Floorplan](#choosing-the-right-floorplan)
6. [Best Practices](#best-practices)

---

## Overview

SAP Fiori floorplans are **predefined templates** for common application use cases, providing consistent UX patterns and reducing development time.

### What are Floorplans?

**Floorplans** are standardized page layouts that define:
- Structure and components
- Navigation patterns
- Interaction behaviors
- Responsive design rules
- Accessibility requirements

### Available Floorplans

| Floorplan | Primary Use | When to Use |
|-----------|-------------|-------------|
| **List Report** | Search, filter, analyze large datasets | Complex queries, editing, navigation to details |
| **Worklist** | Process/approve simple item lists | Quick decisions on numerous items without complex filters |
| **Object Page** | Display/edit single object details | View/create/edit all information about one object |
| **Initial Page** | Navigate to single object | Single input field access point |
| **Overview Page** | Dashboard with cards | Multiple data sources, KPIs, quick actions |

This guide covers the **three most common**: List Report, Worklist, and Object Page.

---

## List Report Floorplan

### Overview

The **List Report** displays large datasets of the same object type in a flat, filterable list, often paired with an Object Page for details. Best for **non-analytical data** on desktop or responsive devices.

### Structure

The floorplan divides into key areas:

```
┌─────────────────────────────────────────┐
│         Header Content                   │
│  (Title, Breadcrumb, Global Actions)    │
├─────────────────────────────────────────┤
│         Filter Bar                       │
│  (Search, Filters, Grouping)            │
├─────────────────────────────────────────┤
│         Table / Grid                     │
│  (Main content area with data)          │
│  • Columns configured via @UI.lineItem  │
│  • Toolbar with actions                 │
│  • Line-item actions per row            │
├─────────────────────────────────────────┤
│         Footer Toolbar (optional)        │
│  (Bulk operations, Save/Cancel)         │
└─────────────────────────────────────────┘
```

#### 1. Header Content
- **Includes**: Title, breadcrumb, global actions
- **Configuration**: `@UI.headerInfo` annotations
  - `typeName`: Singular object name (e.g., "Customer")
  - `typeNamePlural`: Plural (e.g., "Customers")
  - `title`: Field for title display

#### 2. Filter Bar
- **Purpose**: Search, filter, group data
- **Features**:
  - Search bar (with barcode scanner on mobile)
  - Multiple filters (defined in CDS views)
  - Grouping capabilities
  - Variants for saving filter configurations

#### 3. Table
- **Core content** displaying data rows
- **Table Types**:
  - **Grid Table**: Desktop, large datasets with filtering/selection
  - **Responsive Table**: Mobile/tablet adaptation
  - **Analytical Table**: For analytics (use different floorplan)
- **Configuration**: `@UI.lineItem` annotation
  ```
  @UI.lineItem: [
    { position: 10, importance: #HIGH, label: 'Customer ID' },
    { position: 20, importance: #HIGH, label: 'Name' },
    { position: 30, importance: #MEDIUM, label: 'City' }
  ]
  ```

#### 4. Toolbar
- **Global actions** (header-level): Create, Edit table
- **Table actions** (toolbar-level): Sort, Group, Column settings
- **Line-item actions** (per-row): View, Edit, Delete

#### 5. Footer Toolbar (optional)
- **Purpose**: Bulk operations
- **Actions**: Save, Cancel, Messages
- **Visibility**: Appears for mass edits

### Properties and Annotations

**Key CDS/UI Annotations**:

```javascript
// Header Info
@UI.headerInfo: {
  typeName: 'Customer',
  typeNamePlural: 'Customers',
  title: { value: 'CustomerName' }
}

// Line Item (Table Columns)
@UI.lineItem: [
  { 
    position: 10, 
    importance: #HIGH, 
    label: 'Customer ID',
    type: #STANDARD
  },
  { 
    position: 20, 
    importance: #HIGH, 
    label: 'Name' 
  },
  { 
    position: 30, 
    importance: #MEDIUM, 
    label: 'City' 
  }
]

// Selection Fields (Filters)
@UI.selectionFields: [
  { name: 'Country' },
  { name: 'Status' }
]
```

**Annotation Locations**:
- **Backend (CDS views)**: Preferred for field definitions
- **Local XML**: For complex cases, customer extensions
- **Priority**: Customer layer > Extension layer > Core

### Responsive Behavior

| Device | Table Type | Features |
|--------|-----------|----------|
| **Desktop** | Grid Table | High data volume, many columns, filtering |
| **Tablet** | Responsive Table | Adaptive columns, touch-friendly |
| **Mobile** | Responsive Table/Chart | Barcode scanner, fewer columns |

**Adaptation**:
- Automatically adjusts to device size
- Grid table for desktop-heavy apps
- Responsive tables for mobile scenarios
- Search bar features require physical devices for barcode

### Navigation

**Pattern**: List → Object Page
- Click on table row navigates to Object Page
- Shows detailed information for selected item
- Back navigation returns to List Report

### When to Use

✅ **Use List Report when**:
- Users need to search and filter large datasets
- Multiple views/variants required
- Data needs personalization (sorting, grouping)
- Navigation to Object Page for details
- Analytical data NOT primary focus

❌ **Don't use for**:
- Analytical data (use Analytical List Page)
- Simple task processing (use Worklist)
- Single object access (use Initial Page)

### Best Practices

1. **Annotations**:
   - Define basic in CDS views (backend-preferred)
   - Use local XML for advanced cases
   - Test across annotation layers

2. **Table Selection**:
   - Grid table for desktop with many items/columns
   - Responsive table for mobile/tablet
   - Limit to non-analytical lists

3. **Filtering**:
   - Provide meaningful filter options
   - Use variants for common searches
   - Enable grouping for subsets

4. **Performance**:
   - Implement backend paging
   - Lazy loading for large datasets
   - Optimize CDS views

5. **Testing**:
   - Check metadata extensions
   - Verify responsive behavior
   - Test on actual devices

### Example Implementation

**CDS View with Annotations**:
```abap
@UI.headerInfo: {
  typeName: 'Sales Order',
  typeNamePlural: 'Sales Orders',
  title: { value: 'SalesOrderID' }
}

@UI.lineItem: [
  { position: 10, importance: #HIGH, label: 'Order ID' },
  { position: 20, importance: #HIGH, label: 'Customer' },
  { position: 30, importance: #MEDIUM, label: 'Amount' },
  { position: 40, importance: #LOW, label: 'Status' }
]

define view C_SalesOrder as select from SalesOrder {
  key SalesOrderID,
  CustomerName,
  TotalAmount,
  Status
}
```

**Result**: Professional list with search, filter, sort, and navigation to detail pages.

---

## Worklist Floorplan

### Overview

The **Worklist** displays a collection of items for user processing (approving, rejecting tasks) **without** needing advanced filtering. Uses **dynamic page layout** ideal for straightforward workflows.

### Structure

```
┌─────────────────────────────────────────┐
│         Dynamic Page Header             │
│  • Title (mandatory)                    │
│  • Optional KPIs                        │
│  • Global Actions (Create, Edit)        │
├─────────────────────────────────────────┤
│         Content Area                    │
│  ┌───────────────────────────────────┐  │
│  │ Tabs (optional)                   │  │
│  │ • Open  • In Process  • Complete │  │
│  ├───────────────────────────────────┤  │
│  │ KPI Tags (optional)               │  │
│  ├───────────────────────────────────┤  │
│  │ Responsive Table                  │  │
│  │ • Title/Count in toolbar          │  │
│  │ • Sort/Group/Column settings      │  │
│  │ • Line item actions (Approve etc) │  │
│  │ • Navigation indicators (chevrons)│  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│     Footer Toolbar (optional)           │
│  • Save/Cancel for mass edits          │
│  • Message popover                     │
└─────────────────────────────────────────┘
```

### Key Components

#### 1. Header
- **Mandatory**: Title/variant
- **Optional**: KPIs, global action toolbar
- **Actions**: Create, Edit table (global level)

#### 2. Content Area
- **Primary**: Responsive table (recommended)
- **Optional**: Tabs for views (Open/In Process/Complete)
- **Optional**: KPI tags for prioritization
- **Table Toolbar**: 
  - Title and item count
  - Sort, Group, Column settings (via dialogs)
  - Personalization options

#### 3. Footer Toolbar (optional)
- **Purpose**: Finalizing actions and mass edits
- **Contains**: Save, Cancel, Message popover
- **Appears**: When editing or performing table-wide changes

### Table Features

**Recommended**: Responsive table for flexibility

**Features**:
- Navigation indicators (chevrons) for item details
- No-data text with explanation
- Line item actions (per row)
- Personalization (sorting, grouping, columns)
- Item counts in toolbar

### Variants

1. **Simple**: Plain table, no tabs/KPIs
2. **With Tabs**: Multiple views (e.g., Open, In Process)
3. **With KPIs**: Priority indicators for task processing

### Actions Placement

| Location | Purpose | Examples |
|----------|---------|----------|
| **Header Toolbar** | Global (all items) | Create, Edit table settings |
| **Table Toolbar** | Table-specific | Sort, Group, Columns, Search |
| **Line Item** | Per-item | Approve, Reject, Navigate, View |
| **Footer Toolbar** | Finalizing/mass operations | Save, Cancel, Messages |

**Action Guidelines**:
- Hide unavailable actions
- Group via menus for many actions
- Prioritize Add/Edit in toolbars
- Replace Edit with Save/Cancel in footer during mass edit

### Worklist vs List Report

| Aspect | Worklist | List Report |
|--------|----------|-------------|
| **Primary Use** | Process/approve simple lists | Search, filter, analyze large datasets |
| **Filtering** | Minimal/none; tabs for views | Full filter bar, variants, sorting |
| **Table Focus** | Action-oriented (review + act) | Data exploration (multi-views, KPIs) |
| **Structure** | Header + table + footer; tabs optional | List + Object Page navigation |
| **Complexity** | Simple workflow | Sophisticated queries |
| **When to Use** | Numerous items needing quick decisions | Complex filtering, editing, navigation |

### When to Use

✅ **Use Worklist when**:
- Task-heavy scenarios (approvals, reviews)
- Users need to process many items quickly
- Direct actions on items (approve/reject)
- Minimal filtering needed
- Prioritization via tabs/KPIs

❌ **Don't use for**:
- Complex search and filtering requirements
- Advanced data analysis
- Need for personalization and variants
- Multi-step editing workflows

### Responsive Behavior

- **Desktop**: Full table with all features
- **Tablet**: Adapted table, touch-friendly actions
- **Mobile**: Simplified view, essential actions only

### Best Practices

1. **Table Choice**:
   - Always use responsive table
   - Enable line navigation with chevrons
   - Add item counts for context

2. **Actions**:
   - Place contextually (hide unavailable)
   - Use footer toolbar for mass edits
   - Provide clear action labels

3. **Empty States**:
   - Explain why list is empty
   - Provide next steps
   - Offer "Create" action if applicable

4. **Personalization**:
   - Add table settings sparingly
   - Focus on processing flow
   - Avoid over-filtering

5. **Performance**:
   - Load initial items quickly
   - Implement paging for large lists
   - Show loading indicators

### Example Use Cases

**Approval Workflows**:
- Leave requests awaiting approval
- Purchase orders to review
- Invoice processing queue

**Task Management**:
- Support tickets to assign
- Defects to triage
- Work orders to complete

### Implementation Notes

**Configuration**: Define in Fiori Elements via annotations or freestyle with dynamic page layout.

**Table Setup**:
```javascript
// Responsive table with worklist pattern
var oTable = new sap.m.Table({
    headerText: "Work Items ({count})",
    mode: "None",
    growing: true,
    growingThreshold: 20,
    items: {
        path: "/workItems",
        template: oItemTemplate
    }
});
```

---

## Object Page Floorplan

### Overview

The **Object Page** displays and categorizes **all relevant information** about a single object, enabling:
- Quick navigation via anchor/tab bars
- Switching between display and edit modes
- Creation of new objects
- Flexible responsive layout

**Mandatory**: Uses **dynamic page header** (replaces old object page header).

### Structure

```
┌─────────────────────────────────────────────────┐
│      Dynamic Page Header                        │
│  • Title, Breadcrumb                            │
│  • Global Actions                               │
│  • Collapsed/Expanded states                    │
├─────────────────────────────────────────────────┤
│      Navigation Bar (Anchor Bar)                │
│  [Section 1] [Section 2] [Section 3] ...       │
├─────────────────────────────────────────────────┤
│      Content Area (Sections + Subsections)     │
│  ┌───────────────────────────────────────────┐ │
│  │ Section 1 (First section, no title)      │ │
│  │   ├─ Subsection 1.1 (Form)               │ │
│  │   └─ Subsection 1.2 (Table)              │ │
│  ├───────────────────────────────────────────┤ │
│  │ Section 2: Details (Optional item count) │ │
│  │   └─ Subsection 2.1 (Form)               │ │
│  ├───────────────────────────────────────────┤ │
│  │ Section 3: Related Items                 │ │
│  │   ├─ Subsection 3.1 (Table with Show All)│ │
│  │   └─ Subsection 3.2 (Blocks)             │ │
│  └───────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│      Footer Toolbar (edit mode)                 │
│  • Save, Cancel actions                         │
└─────────────────────────────────────────────────┘
```

### Key Components

#### 1. Dynamic Page Header (Mandatory)

**Replaces**: Old object page header (deprecated)

**Features**:
- **Collapsed/Expanded states**: Header content can expand/collapse
- **Title**: Object name, subtitle
- **Breadcrumbs**: Navigation path
- **Global Actions**: Edit, Delete, Share, etc.
- **Header Content**: KPIs, status, key fields
- **Footer Toolbar**: Save/Cancel in edit mode

**Why Mandatory**:
- Consistency across applications
- Flexibility for simple/complex objects
- Fixable issues (old header deprecated)
- Better responsive behavior

#### 2. Navigation Bar (Anchor Bar)

**Purpose**: Quick access to sections

**Behavior**:
- Derives from sections/subsections
- Uses subsection title if section has only one subsection
- No submenu for single subsections
- Scrolls to section on click

#### 3. Sections and Subsections

**Sections**:
- **Containers** for subsections
- First section: No title (implied "General Information")
- Other sections: Title with optional item counter
- **Cannot contain controls directly** (only subsections)

**Subsections**:
- **Hold actual content**: Forms, tables, blocks
- Title becomes section name if single subsection
- Can have local action toolbars

**Content Types**:
1. **Forms**:
   - One form per subsection (recommended)
   - Title from subsection header
   - Responsive columns (see Responsive Behavior)

2. **Tables**:
   - Remove redundant title if sole content
   - Add "Show All (x)" link for navigation
   - Top N items with link to full list

3. **Blocks**:
   - Use "Show More/Show Less" toggles
   - Avoid panel containers
   - Group related information

### Responsive Behavior

**Fully responsive across screen sizes**:

#### Default Fiori Elements Form Columns

| Screen Size | Columns | Use Case |
|-------------|---------|----------|
| **S (Small/Phone)** | 1 | Mobile devices |
| **M (Medium/Tablet)** | 3 | Tablets portrait |
| **L (Large/Desktop)** | 4 | Desktop standard |
| **XL (Extra Large)** | 6 | Wide screens |

#### Earlier Form Columns (older apps)

| Screen Size | Columns |
|-------------|---------|
| **S** | 1 |
| **M** | 2 |
| **L** | 3 |
| **XL** | 4 |

**Tables/Forms**:
- Adapt columns automatically
- Reduce vertical space for single tables
- Stack on smaller screens

### Sections Structure Guidelines

**Section Organization**:
- First section: Most important, no title
- Subsequent sections: Categorized content
- Section titles: Clear, concise
- Item counters: For collections (optional)

**Subsection Guidelines**:
- Title subsection as section if single
- One form per subsection
- No multiple forms unless titled
- Tables: Top N with "Show All" link
- Local actions: Toolbar at subsection level

**Example**:
```
Section 1 (no title shown)
  └─ General Information (form)

Section 2: Contact Details  
  └─ Contact Info (form)

Section 3: Orders (12)
  ├─ Recent Orders (table with "Show All")
  └─ Order Statistics (blocks)
```

### Actions

**Action Levels**:

| Level | Location | Purpose | Examples |
|-------|----------|---------|----------|
| **Global** | Header/Shell bar | Object-wide | Edit, Delete, Share, Copy |
| **Section** | N/A | Not allowed | (Sections can't have direct actions) |
| **Subsection** | Toolbar | Content-specific | Add Item, Export, Refresh |
| **Line Item** | Table rows | Per-record | View, Edit, Remove |

**Footer Actions** (Edit Mode):
- Save, Cancel
- Validation messages
- Additional workflow actions

### Editing Modes

**Modes**:
1. **Display**: Read-only view of object
2. **Edit**: Modify existing object
3. **Create**: Enter data for new object

**Behavior**:
- Switch via global "Edit" action
- Forms become editable
- Footer toolbar appears (Save/Cancel)
- Header content can move to sections (preferred)

**Best Practice**:
- Minimize editable header content
- Keep most fields in sections
- Use inline edit for subobjects (<8 fields)
- Use dialog for complex subobject creation

### Dynamic Page Layout

**Properties**:
- **Header Expanded**: Controls initial state
- **Header Pinned**: Keeps header visible while scrolling
- **Toggle on Title Click**: Expand/collapse header
- **Preserve State**: Maintains header state on scroll

**Advantages**:
- Adaptable to simple/complex objects
- Consistent with Fiori design
- Better than old object page header
- Built-in responsive behavior

### Facets (Content Organization)

**Facets** appear as sections/subsections following column-based responsive design:
- Categorized navigation via anchor bar
- Hierarchical organization (section → subsection → content)
- Responsive adaptation

### When to Use

✅ **Use Object Page when**:
- Displaying complete object information
- Multiple categories of data
- Edit/create object functionality needed
- Navigation from List Report/Worklist
- Complex or simple objects (adaptable)

❌ **Don't use for**:
- Lists or collections (use List Report/Worklist)
- Dashboard (use Overview Page)
- Wizard-style creation (use Wizard floorplan)

### Best Practices

1. **Always Use Dynamic Page Header**:
   - Don't use old object page header
   - Avoid "page variant" in current Fiori Elements
   - Mandatory for consistency

2. **Section Organization**:
   - First section: Most critical info, no title
   - Multiple sections for complex objects
   - Fewer sections for simple objects
   - Meaningful section titles

3. **Subsections**:
   - One subsection per form
   - No multiple forms unless titled
   - Tables: Top N items with "Show All"
   - No redundant titles if table is sole content

4. **Forms**:
   - Use Fiori Elements default columns
   - Responsive design automatic
   - Group related fields
   - Clear labels

5. **Subobjects**:
   - <8 fields: Inline edit or dialog
   - Complex: Separate Object Page
   - Simple: Avoid navigation overhead

6. **Edit Mode**:
   - Move header content to sections if editable
   - Use footer toolbar for Save/Cancel
   - Validate before save
   - Clear error messages

7. **Resources**:
   - SAPUI5 Object Page samples
   - Fiori Elements developer guides
   - SAP Fiori Design Guidelines

### Implementation

**Fiori Elements** (Annotation-based):
```javascript
// CDS View annotations
@UI.headerInfo: {
  typeName: 'Sales Order',
  typeNamePlural: 'Sales Orders',
  title: { value: 'SalesOrderID' }
}

@UI.facets: [
  {
    id: 'GeneralInfo',
    purpose: #STANDARD,
    type: #IDENTIFICATION_REFERENCE,
    label: 'General Information'
  },
  {
    id: 'Items',
    purpose: #STANDARD,
    type: #LINEITEM_REFERENCE,
    label: 'Items',
    targetElement: 'ItemSet'
  }
]
```

**Freestyle** (sap.f.DynamicPage):
```javascript
// Use sap.f.DynamicPage control
var oObjectPage = new sap.f.DynamicPage({
    headerTitle: new sap.f.DynamicPageTitle({...}),
    headerContent: [...],
    content: new sap.uxap.ObjectPageLayout({...})
});
```

### Guidelines Version

- Guidelines from **v1.84 – v1.136**
- Check latest SAPUI5 Demo Kit for updates
- Follow Fiori Elements documentation for implementation

---

## Choosing the Right Floorplan

### Decision Tree

```
Start: What is your primary use case?

├─ Search, filter, analyze large dataset
│  └─ → LIST REPORT
│
├─ Process/approve many items quickly
│  └─ → WORKLIST
│
├─ Display/edit single object details
│  └─ → OBJECT PAGE
│
├─ Dashboard with KPIs and cards
│  └─ → OVERVIEW PAGE
│
└─ Wizard-style multi-step process
   └─ → WIZARD FLOORPLAN
```

### Comparison Matrix

| Criteria | List Report | Worklist | Object Page |
|----------|-------------|----------|-------------|
| **Data Volume** | Large (100s-1000s) | Medium (10s-100s) | Single object |
| **Filtering** | Complex, full bar | Minimal, tabs | N/A (one object) |
| **Actions** | View, navigate | Approve, process | Edit, view all |
| **Navigation** | To Object Page | To detail optional | From List/Worklist |
| **Editing** | Via Object Page | Inline or dialog | Full edit mode |
| **Variants** | Yes, personalization | Limited, tabs | No (one object) |
| **Complexity** | High | Low-Medium | Variable |

### Use Case Examples

**List Report**:
- Customer list with search and filters
- Product catalog with personalization
- Sales orders with variants
- Employee directory with grouping

**Worklist**:
- Leave approvals
- Invoice processing
- Support ticket triage
- Purchase order reviews

**Object Page**:
- Customer details and history
- Product specifications
- Sales order complete view
- Employee profile and records

---

## Best Practices

### General Guidelines

1. **Follow Fiori Design Principles**:
   - Role-Based: Clear purpose for each floorplan
   - Responsive: Mobile, tablet, desktop support
   - Simple: Minimal cognitive load
   - Coherent: Consistent patterns
   - Delightful: Professional appearance

2. **Choose Appropriate Floorplan**:
   - Match use case to floorplan strengths
   - Don't force-fit (e.g., Worklist for complex filtering)
   - Consider user workflow
   - Test with actual users

3. **Responsive Design**:
   - Test on all device sizes
   - Adaptive layouts work automatically
   - Mobile-first thinking
   - Touch-friendly interactions

4. **Performance**:
   - Backend paging for large datasets
   - Lazy loading where applicable
   - Optimize CDS views/OData services
   - Monitor load times

5. **Accessibility**:
   - SAP UI5 controls provide ARIA support
   - Test with screen readers
   - Keyboard navigation
   - Color contrast compliance

### Annotation Best Practices

**CDS Views** (Backend):
- ✅ Define field-level annotations
- ✅ Basic UI structure
- ✅ Reusable across apps
- ✅ Version controlled

**Local XML** (Frontend):
- ✅ Complex UI configurations
- ✅ Customer-specific extensions
- ✅ Override backend annotations
- ⚠️ Test layer priority (customer > extension > core)

### Navigation Patterns

**List Report → Object Page**:
```
User Journey:
1. Search/filter in List Report
2. Select item from table
3. Navigate to Object Page
4. View details, edit if needed
5. Back to List Report
```

**Worklist → Action → Worklist**:
```
User Journey:
1. View items in Worklist
2. Approve/Reject directly
3. Item removed/updated
4. Continue with next item
```

### Testing Checklist

**Functional**:
- [ ] All actions work
- [ ] Navigation correct
- [ ] Filters apply properly
- [ ] Edit/Create save successfully
- [ ] Validations trigger

**Responsive**:
- [ ] Phone (S) layout correct
- [ ] Tablet (M) layout correct
- [ ] Desktop (L/XL) layout correct
- [ ] Touch interactions work

**Performance**:
- [ ] Initial load < 3 seconds
- [ ] Paging works smoothly
- [ ] No memory leaks
- [ ] Smooth scrolling

**Accessibility**:
- [ ] Keyboard navigation
- [ ] Screen reader compatible
- [ ] Color contrast compliant
- [ ] Focus indicators visible

---

## Resources

### Official Documentation

- **SAP Fiori Design**: https://experience.sap.com/fiori-design-web/
- **SAPUI5 SDK**: https://sapui5.hana.ondemand.com/sdk/
- **Fiori Elements**: https://sapui5.hana.ondemand.com (Fiori Elements section)

### Project Documentation

- **This Guide**: `docs/fiori/FIORI_FLOORPLANS_COMPLETE_GUIDE.md`
- **SAPUI5 Reference**: `docs/fiori/SAPUI5_DEVELOPER_REFERENCE.md`
- **API Quick Reference**: `docs/fiori/SAPUI5_API_QUICK_REFERENCE.md`
- **Fiori Design Report**: `docs/fiori/FIORI_DESIGN_SCRAPING_REPORT.md`

### Learning Resources

- SAPUI5 Tutorials (Demo Kit)
- SAP Community blogs
- YouTube SAP Fiori tutorials
- SAP Learning Hub courses

---

## Summary

### Key Takeaways

1. **List Report** = Search + Filter + Large datasets → Object Page
2. **Worklist** = Process + Approve + Simple lists → Quick actions
3. **Object Page** = Display + Edit + Single object → Complete view

4. **All use**:
   - SAP UI5 controls
   - SAP Horizon theme
   - Responsive design
   - Dynamic Page layout (Object Page, Worklist)

5. **Best Practice**:
   - Choose floorplan matching use case
   - Follow Fiori guidelines
   - Test responsively
   - Use annotations where possible

### Next Steps

1. ✅ Read this guide completely
2. ✅ Review SAPUI5 Developer Reference
3. ✅ Check project examples in `modules/feature-manager/`
4. ✅ Build prototype using appropriate floorplan
5. ✅ Test on devices
6. ✅ Get user feedback

---

**Status**: ✅ Complete Guide - Ready for Production Use

**Version**: 1.0

**Source**: Scraped from SAP Fiori Design Guidelines (January 24, 2026)

This guide provides comprehensive coverage of the three most common Fiori floorplans. Use as reference for building enterprise-grade SAP Fiori applications.