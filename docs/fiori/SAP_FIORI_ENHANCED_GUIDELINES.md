# SAP Fiori Design Guidelines - Enhanced Edition

**Project**: P2P MCP - UX Enhancement Initiative  
**Date Created**: January 20, 2026  
**Last Updated**: January 20, 2026  
**Purpose**: Comprehensive SAP Fiori design guidelines for P2P application development  
**Guideline Version**: 1.142 (Latest - 2024/2025)  
**Theme**: Horizon (Morning & Evening modes)

---

## Table of Contents

1. [Core Design Principles](#core-design-principles)
2. [Floorplans](#floorplans)
3. [Components](#components)
4. [Visual Design Foundations](#visual-design-foundations)
5. [Best Practices for P2P Applications](#best-practices-for-p2p-applications)
6. [Implementation Guidelines](#implementation-guidelines)

---

## Core Design Principles

SAP Fiori adheres to five fundamental principles that guide all design decisions:

### 1. **Role-Based** 🎯
- Tailor applications to specific user roles and tasks
- Focus on what users need to accomplish their work efficiently
- Avoid information overload by showing only relevant data
- **P2P Example**: Show different views for AP clerks vs. finance managers

### 2. **Simple** ✨
- Focus on essentials and remove unnecessary complexity
- Clear visual hierarchy with minimal cognitive load
- One task per screen principle
- Flat design with micro-interactions
- **P2P Example**: Simplified invoice approval with clear status indicators

### 3. **Coherent** 🔄
- Unified patterns and consistent behavior across applications
- Standard components and interactions
- Predictable navigation and workflows
- **P2P Example**: Consistent table layouts across PO, Invoice, and Payment views

### 4. **Adaptive** 📱
- Responsive design across all devices (desktop, tablet, mobile)
- Graceful degradation for different screen sizes
- Touch-optimized for mobile devices
- **P2P Example**: Responsive tables that adapt from desktop to mobile views

### 5. **Delightful** 😊
- Intuitive and pleasurable user experience
- Smooth animations and transitions
- Helpful feedback and guidance
- **P2P Example**: Success animations after invoice posting, helpful error messages

---

## Floorplans

### 1. List Report Floorplan ⭐⭐⭐⭐⭐

**Purpose**: Standard pattern for displaying lists of business objects (invoices, POs, suppliers)

#### Overall Structure
- **Dynamic page layout** with header, content area, and footer
- **Filter bar** at the top for quick filtering
- **Responsive table** as primary display (or grid table for complex data)
- **Table toolbar** with actions (create, export, etc.)

#### Three Content Layouts

**A. Simple Content Layout** (Default)
- Single business object type in one responsive table
- Automatic data loading
- One table toolbar
- Object creation via dialog
- **Use for**: Standard invoice list, supplier list, PO list

**B. Multiple View Layout**
- Multiple pre-filtered table views (e.g., "Open Invoices", "Blocked", "Paid")
- Switched via segmented button (2-3 views) or select control (4+ views)
- Row count display for each view
- One toolbar shared across views
- **Use for**: Invoice status views, PO approval stages

**C. Multiple Content Layout**
- Multiple business object types/tables
- Switched via icon tab bar (text-only tabs)
- Different tables per view (e.g., Invoices tab, Deliveries tab, Payments tab)
- Different toolbars per view
- Requires object page for creation (no dialog)
- **Use for**: P2P dashboard showing multiple document types

#### Key Components

**Filter Bar**
- Positioned at top of content area
- Retains state changes (position, removal)
- Quick filtering across all views
- Smart value help for fields

**Responsive Table**
- Automatically adapts to screen size
- Supports sorting, filtering, grouping
- Multi-select for batch actions
- Row actions menu
- **Mobile**: Stacks columns vertically

**Table Toolbar**
- Primary actions (Create, Export, etc.)
- Semantic button styles (Emphasized, Primary)
- "Add Card to Insights" option (configurable)
- View settings (columns, sort, group)

#### Responsive Design
- **Desktop**: Full table with all columns
- **Tablet**: Reduced columns, prioritized data
- **Mobile**: Stacked card view with key info

#### 2024 Guidelines (v1.120+)
- Enhanced mandatory field handling (red asterisk on headers)
- Insights card creation support
- Improved error message strips
- Better draft handling

**Example P2P Use Cases**:
- Supplier Invoice List with status filters
- Purchase Order tracking with approval views
- Payment Run overview with multi-select

---

### 2. Object Page Floorplan ⭐⭐⭐⭐⭐

**Purpose**: Display detailed information about a single business object (invoice details, PO details, supplier profile)

#### Mandatory Structure
- **Always use dynamic page header** (required for SAP Fiori Elements)
- **Shell bar title**: Set to business object name (e.g., "Invoice 2024001")
- **Header facets**: Display critical business data
- **Sections**: Organize related information

#### Dynamic Page Header
- **Snapping behavior**: Header collapses on scroll, expands on scroll up
- **Expansion**: Can be expanded/collapsed by user
- **Key information**: Title, subtitle, status, key KPIs
- **Actions**: Toolbar with primary actions (Edit, Delete, Approve, etc.)

#### Header Facets
- Display critical object details (amounts, dates, statuses)
- Adapt dynamically in display vs. edit mode
- Support contact facets with Microsoft Teams integration
- **P2P Example**: Invoice amount, due date, payment status, variance indicators

#### Sections and Subsections
- Organize related information logically
- Support sub-sections for complex data
- Can contain tables, forms, charts
- **Empty sections**: Show empty state with helpful message

#### Actions and Toolbar
- **Header toolbar**: Primary actions (Save, Edit, Delete, Approve, Reject)
- **Table toolbars**: Section-specific actions
- **Unsaved changes**: Warning dialog with options:
  - Save changes
  - Keep draft
  - Discard changes
  - Cancel navigation

#### Edit Mode Features
- **Mandatory fields**: Red asterisk (*) on field labels
- **Error messages**: Clear error strips with guidance
- **Draft handling**: Auto-save after 20s focus shift (V2)
- **Validation**: Inline validation with immediate feedback

#### Table in Object Page
- **Grid table** or **responsive table**
- **Copy functionality**: Multiple rows/cells (except responsive table)
- **Empty row**: For creation with mandatory field guidance
- **Multi-input**: Editable in V4

#### Message Handling
- **Discard toast**: "Changes discarded" (V2) or "Draft discarded" (V4)
- **No toast**: If no changes were made
- **Error strips**: Guide user to issues

**Example P2P Use Cases**:
- Invoice Detail Page with line items, GL postings, payment info
- Purchase Order with items, delivery schedule, approval history
- Supplier Profile with contact info, payment terms, performance metrics

---

### 3. Dynamic Page Layout ⭐⭐⭐⭐⭐

**Purpose**: Foundation layout for most SAP Fiori pages (except overview pages)

#### Structure
- **Header**: Dynamic header with title, actions, and key info
- **Content Area**: Main content (tables, forms, charts)
- **Footer**: Optional footer toolbar for page-level actions

#### Header Behavior
- **Snapping**: Header collapses on scroll to maximize content space
- **Expansion**: User can expand/collapse header manually
- **Contextual**: Shows relevant information based on page context

#### Content Area
- Flexible to accommodate various content types
- Supports scrolling with header snapping
- Can contain multiple sections

#### Footer Toolbar
- Page-level actions (Save, Cancel, Submit)
- Sticky footer stays visible during scroll
- **Semantic actions**: Clear primary action

#### Responsive Behavior
- Adapts to screen size
- **Desktop**: Full layout with all areas
- **Tablet**: Optimized spacing
- **Mobile**: Simplified with prioritized content

**Example P2P Use Cases**:
- Invoice Entry Form with dynamic header showing draft status
- Payment Run Configuration with footer actions
- Report View with collapsible header filters

---

## Components

### Tables and Lists

#### 1. Responsive Table ⭐⭐⭐⭐⭐
**Best for**: Most P2P data displays, mobile-first scenarios

**Features**:
- Automatically adapts to screen size
- **Desktop**: Traditional table with all columns
- **Tablet**: Reduced columns
- **Mobile**: Card view with stacked information
- Supports sorting, filtering, grouping
- Multi-select for batch operations
- Row actions (inline actions, navigation)

**Column Design**:
- **Priority columns**: Always visible
- **Low priority**: Hidden on smaller screens
- **Column headers**: Clear, concise labels
- **Sorting**: Clickable headers with sort indicators

**States**:
- Loading state with skeleton
- Empty state with helpful message
- Error state with recovery action

**P2P Examples**:
- Invoice list with amounts, dates, statuses
- Supplier list with contact info, payment terms
- Line item tables with quantities, prices

#### 2. Grid Table ⭐⭐⭐⭐
**Best for**: Complex data with many columns, desktop-focused

**Features**:
- Fixed column layout
- Horizontal scrolling if needed
- Better for data-heavy scenarios
- Copy/paste functionality
- Excel-like behavior

**When to Use**:
- Financial data with many columns
- Reporting scenarios
- Power user applications

**P2P Examples**:
- GL postings with account, amount, currency, cost center
- Payment proposal with complex calculations
- Detailed line item analysis

#### 3. Table Toolbar ⭐⭐⭐⭐⭐
**Purpose**: Actions and settings for table content

**Components**:
- **Primary actions**: Create, Export, Delete
- **View settings**: Column selection, sort, filter, group
- **Search**: Quick search within table
- **Row count**: Shows total and selected rows

**Action Guidelines**:
- Max 3 primary actions before overflow
- Emphasized button for primary action
- Transparent buttons for secondary actions
- Overflow menu for less common actions

**P2P Examples**:
- "Create Invoice" (primary action)
- "Export to Excel" (secondary action)
- "Post Selected" (batch action)

---

### Forms and Input Controls

#### Form Layout Guidelines ⭐⭐⭐⭐⭐

**Principles**:
- Logical grouping of related fields
- Clear label placement (top-aligned or left-aligned)
- Consistent spacing between fields
- Responsive layout (1, 2, or 3 columns based on screen size)

**Field Groups**:
- Use **sections** to group related fields
- Section headers for clear organization
- Collapsible sections for optional details

**Label Design**:
- **Required fields**: Red asterisk (*) after label
- **Optional fields**: "(Optional)" text or no indicator if most fields required
- **Helper text**: Below field for additional guidance
- **Placeholder**: In field for format example

**Validation**:
- **Inline validation**: Immediate feedback on field blur
- **Error messages**: Clear, specific, actionable
- **Error state**: Red border, error icon, error text
- **Success state**: Green checkmark for valid entries

#### Input Controls

**1. Input Field**
- Single-line text entry
- Value help button for lookups
- Clear button to reset
- Character counter for limited fields

**2. Text Area**
- Multi-line text entry
- Resizable or fixed height
- Character counter

**3. Date Picker**
- Calendar popup
- Manual entry support
- Min/max date constraints
- Disabled dates

**4. Select / Dropdown**
- Single selection from list
- Search/filter for long lists
- Grouping for categories

**5. Multi-Input**
- Multiple value selection
- Token display for selected values
- Value help for suggestions

**6. Checkbox**
- Boolean selection
- Use for optional settings
- Group related checkboxes

**7. Radio Button**
- Single selection from options
- Use for mutually exclusive choices
- Max 5-7 options

**8. Switch**
- On/off toggle
- Use for settings that take effect immediately
- Clear on/off labels

**P2P Form Examples**:
- Invoice Header Form: Vendor, Date, Amount, Payment Terms
- Line Item Entry: Material, Quantity, Price, GL Account
- Approval Form: Approve/Reject with comments

---

## Visual Design Foundations

### Typography

#### Font Family: SAP 72 ⭐⭐⭐⭐⭐

**Font Specifications**:
- **Primary**: SAP 72 Regular
- **Bold**: SAP 72 Bold (for headers, emphasized text)
- **Light**: SAP 72 Light (rarely used)

#### Type Scale

**Headers**:
- **H1**: 2.5rem (40px) - Bold - Page titles
- **H2**: 2rem (32px) - Bold - Section headers
- **H3**: 1.5rem (24px) - Bold - Subsection headers
- **H4**: 1.25rem (20px) - Bold - Group headers
- **H5**: 1.125rem (18px) - Bold - Card titles
- **H6**: 1rem (16px) - Bold - List headers

**Body Text**:
- **Large**: 1rem (16px) - Regular - Primary body text
- **Medium**: 0.875rem (14px) - Regular - Secondary text
- **Small**: 0.75rem (12px) - Regular - Helper text, footnotes

**Special**:
- **Link**: Underline on hover, $sapLinkColor
- **Code**: Monospace font for technical text
- **Label**: 0.875rem (14px) - Regular - Form labels

#### Line Heights
- **Headers**: 1.2-1.3 (tighter)
- **Body**: 1.4-1.6 (comfortable reading)
- **Small text**: 1.4 (readable at small size)

#### Text Colors
- **Primary**: $sapTextColor (#32363A - almost black)
- **Secondary**: $sapContent_LabelColor (#6A6D70 - dark gray)
- **Disabled**: $sapContent_DisabledTextColor (#CCCCCC - light gray)
- **Link**: $sapLinkColor (#0070F2 - SAP blue)
- **Success**: $sapPositiveTextColor (#107E3E - green)
- **Error**: $sapNegativeTextColor (#BB0000 - red)
- **Warning**: $sapCriticalTextColor (#E9730C - orange)

#### Best Practices
- Use consistent type scale throughout app
- Maintain clear hierarchy with font sizes
- Ensure sufficient contrast (WCAG AA minimum)
- Don't use ALL CAPS except for buttons
- Limit to 2-3 font sizes per screen

**P2P Typography Examples**:
- **Dashboard title**: H1 - "Procure-to-Pay Overview"
- **Card title**: H5 - "Outstanding Invoices"
- **Table header**: Body Medium - "Invoice Number"
- **Amount**: Body Large Bold - "$1,234.56"
- **Helper text**: Small - "Payment due in 5 days"

---

### Spacing and Layout Grid

#### Spacing Scale ⭐⭐⭐⭐⭐

SAP Fiori uses a consistent **0.5rem (8px) base unit** for spacing:

**Scale**:
- **0.25rem** (4px) - Tiny - Between closely related elements
- **0.5rem** (8px) - Small - Standard spacing
- **1rem** (16px) - Medium - Between sections
- **1.5rem** (24px) - Large - Major sections
- **2rem** (32px) - XLarge - Page margins
- **3rem** (48px) - XXLarge - Major page divisions

#### Layout Grid

**12-Column Grid System**:
- **Desktop**: 12 columns
- **Tablet**: 8 columns (or 12 with smaller gutters)
- **Mobile**: 4 columns (or full-width with padding)

**Gutters**:
- **Desktop**: 1rem (16px) or 2rem (32px)
- **Tablet**: 1rem (16px)
- **Mobile**: 1rem (16px)

**Margins**:
- **Desktop**: 3rem (48px) or 2rem (32px)
- **Tablet**: 2rem (32px)
- **Mobile**: 1rem (16px)

#### Container Patterns

**Card Spacing**:
- **Padding**: 1rem (16px) inside cards
- **Gap**: 1rem (16px) between cards
- **Margin**: 0.5rem (8px) between card sections

**Form Spacing**:
- **Field gap**: 1rem (16px) vertical between fields
- **Section gap**: 1.5rem (24px) between sections
- **Label gap**: 0.25rem (4px) between label and input

**Table Spacing**:
- **Row height**: 2.75rem (44px) - Standard
- **Row height**: 3rem (48px) - Comfortable
- **Cell padding**: 0.5rem (8px) horizontal, 0.75rem (12px) vertical

#### Responsive Breakpoints

**Breakpoints**:
- **S** (Small): 0-599px - Phone portrait
- **M** (Medium): 600-1023px - Phone landscape / Tablet portrait
- **L** (Large): 1024-1439px - Tablet landscape / Small desktop
- **XL** (XLarge): 1440px+ - Desktop

**Design Tokens** (CSS Variables):
- `--sapUiContentPadding`: 1rem
- `--sapUiResponsiveMargin`: Responsive margin
- `--sapUiGridGap`: 0.5rem

#### Best Practices
- Use consistent spacing throughout
- Align to 8px grid for precision
- Maintain visual rhythm with consistent gaps
- More space = more emphasis
- Group related elements with less space

**P2P Spacing Examples**:
- **Dashboard cards**: 1rem gap between cards
- **Form fields**: 1rem vertical gap
- **Section headers**: 1.5rem margin-bottom
- **Page margins**: 2rem on desktop, 1rem on mobile

---

### Iconography

#### SAP Icon Font ⭐⭐⭐⭐⭐

**Icon Library**: `sap-icon://`

#### Icon Sizes

**Standard Sizes**:
- **1rem** (16px) - Standard / Inline with text
- **1.25rem** (20px) - Buttons
- **1.5rem** (24px) - App icons / Large buttons
- **2rem** (32px) - Header icons
- **3rem** (48px) - Empty state icons
- **4rem** (64px) - Illustration icons

#### Icon Types

**1. UI Icons** (Functional)
- Actions: save, delete, edit, approve, reject
- Navigation: arrow-right, arrow-left, nav-back
- Status: accept, decline, alert, information
- **Use**: Buttons, headers, status indicators

**2. Action Icons**
- Specific to business actions
- Examples: invoice, purchase-order, supplier, payment
- **Use**: Object identifiers, business action buttons

**3. Status Icons**
- Success: accept (green checkmark)
- Error: decline (red X), alert (red exclamation)
- Warning: alert (orange exclamation)
- Info: information (blue i)
- **Use**: Message states, status indicators

#### Common P2P Icons

**Documents**:
- `sap-icon://document` - Generic document
- `sap-icon://invoice` - Supplier invoice
- `sap-icon://sales-order` - Purchase order
- `sap-icon://receipt` - Payment receipt
- `sap-icon://monitor-payments` - Payment monitoring

**Actions**:
- `sap-icon://create` - Create new
- `sap-icon://edit` - Edit
- `sap-icon://delete` - Delete
- `sap-icon://save` - Save
- `sap-icon://post` - Post document

**Status**:
- `sap-icon://accept` - Approved / Success
- `sap-icon://decline` - Rejected / Error
- `sap-icon://alert` - Warning / Attention needed
- `sap-icon://pending` - Pending approval
- `sap-icon://locked` - Blocked

**Navigation**:
- `sap-icon://navigation-right-arrow` - Forward
- `sap-icon://navigation-left-arrow` - Back
- `sap-icon://drill-down` - See details
- `sap-icon://search` - Search

#### Icon Colors

**Semantic Colors**:
- **Neutral**: $sapIconColor (#0854A0 - SAP blue)
- **Success**: $sapPositiveColor (#107E3E - green)
- **Error**: $sapNegativeColor (#BB0000 - red)
- **Warning**: $sapCriticalColor (#E9730C - orange)
- **Information**: $sapInformativeColor (#0070F2 - blue)

#### Best Practices
- Always pair icons with text labels (accessibility)
- Use consistent icons for same actions
- Don't create custom icons unless necessary
- Ensure icon meanings are clear
- Size icons appropriately for context
- Use semantic colors for status icons

**P2P Icon Examples**:
- Invoice list row: `sap-icon://invoice` (neutral)
- Approved status: `sap-icon://accept` (green)
- Blocked invoice: `sap-icon://locked` (red)
- Post action: `sap-icon://post` with "Post" label

---

### Colors and Horizon Theme

#### Horizon Theme ⭐⭐⭐⭐⭐

**Theme Modes**:
- **Morning Horizon** (Light mode) - Default
- **Evening Horizon** (Dark mode) - Optional

#### Core Color Palette

**Primary Blue** (SAP Blue):
- **Light**: #0070F2
- **Dark**: #0854A0
- **Usage**: Primary actions, links, focus states

**Background Colors**:
- **Page background**: #F5F6F7 (light gray)
- **Card background**: #FFFFFF (white)
- **Shell background**: #354A5F (dark blue-gray)

**Text Colors**:
- **Primary text**: #32363A (almost black)
- **Secondary text**: #6A6D70 (dark gray)
- **Disabled text**: #CCCCCC (light gray)
- **Link text**: #0070F2 (SAP blue)

#### Semantic Colors

**Success** (Positive):
- **Background**: #F5FAEA
- **Border**: #107E3E
- **Text**: #107E3E
- **Icon**: #107E3E
- **Usage**: Successful operations, approved items

**Error** (Negative):
- **Background**: #FFEBEB
- **Border**: #BB0000
- **Text**: #BB0000
- **Icon**: #BB0000
- **Usage**: Errors, rejected items, blocked documents

**Warning** (Critical):
- **Background**: #FEF7F1
- **Border**: #E9730C
- **Text**: #E9730C
- **Icon**: #E9730C
- **Usage**: Warnings, items needing attention

**Information**:
- **Background**: #EBF8FF
- **Border**: #0070F2
- **Text**: #0070F2
- **Icon**: #0070F2
- **Usage**: Informational messages, tips

**Neutral**:
- **Background**: #F5F6F7
- **Border**: #89919A
- **Text**: #32363A
- **Icon**: #0854A0
- **Usage**: Default state, pending items

#### Status Colors for P2P

**Invoice Status Colors**:
- **Draft**: Gray (#6A6D70)
- **Pending Approval**: Orange (#E9730C)
- **Approved**: Green (#107E3E)
- **Posted**: Blue (#0070F2)
- **Paid**: Green (#107E3E)
- **Blocked**: Red (#BB0000)
- **Parked**: Yellow (#E76500)

**Payment Status Colors**:
- **Not Due**: Gray
- **Due Soon**: Orange
- **Overdue**: Red
- **Paid**: Green

**Variance Colors**:
- **No Variance**: Green
- **Minor Variance**: Orange (within tolerance)
- **Major Variance**: Red (requires approval)

#### Design Tokens (CSS Variables)

**Background**:
- `--sapBackgroundColor`: #F5F6F7
- `--sapTile_Background`: #FFFFFF
- `--sapShellColor`: #354A5F

**Text**:
- `--sapTextColor`: #32363A
- `--sapContent_LabelColor`: #6A6D70
- `--sapLinkColor`: #0070F2

**Semantic**:
- `--sapPositiveColor`: #107E3E
- `--sapNegativeColor`: #BB0000
- `--sapCriticalColor`: #E9730C
- `--sapInformativeColor`: #0070F2
- `--sapNeutralColor`: #6A6D70

#### Accessibility

**Contrast Requirements**:
- **Text on background**: Minimum 4.5:1 (WCAG AA)
- **Large text**: Minimum 3:1
- **Icons and graphics**: Minimum 3:1

**Color Blindness**:
- Don't rely on color alone
- Use icons + text + color
- Ensure patterns are distinguishable without color

#### Best Practices
- Use semantic colors consistently
- Follow Horizon theme guidelines
- Test in both light and dark modes
- Ensure sufficient contrast
- Use design tokens for theming support
- Don't create custom colors without design review

**P2P Color Examples**:
- **Approved invoice card**: Green left border, green status icon
- **Blocked invoice card**: Red left border, red alert icon
- **Warning message**: Orange background, orange icon
- **Primary action button**: Blue background, white text
- **Amount with variance**: Red text, red icon

---

## Best Practices for P2P Applications

### 1. Data Display Optimization

#### For Invoice Lists
- **Priority columns**: Invoice Number, Vendor, Amount, Due Date, Status
- **Secondary columns**: Invoice Date, PO Reference, Payment Terms
- **Mobile view**: Show Invoice Number, Amount, Status only
- **Sorting**: Default by Due Date (oldest first)
- **Filtering**: Pre-filters for "Open", "Blocked", "Overdue"

#### For Amount Display
- **Always show currency**: $1,234.56 USD
- **Alignment**: Right-align amounts
- **Negative amounts**: Red color, parentheses: ($1,234.56)
- **Large amounts**: Use thousand separators
- **Zero amounts**: Show as $0.00 (not blank)

#### For Date Display
- **Format**: Short date (MM/DD/YYYY or DD/MM/YYYY based on locale)
- **Relative dates**: "Today", "Yesterday", "3 days ago" for recent dates
- **Due dates**: Highlight overdue in red
- **Date ranges**: "Jan 1 - Jan 31, 2024"

#### For Status Indicators
- **Use semantic colors**: Green for success, Red for error, Orange for warning
- **Pair with icons**: Always show icon + text
- **Status badges**: Pill-shaped with background color
- **Quick scan**: Enable users to quickly identify status

### 2. Form Design

#### Invoice Entry Form
- **Logical sections**: Header (Vendor, Date, Terms), Line Items, Totals, GL Posting
- **Required fields**: Vendor*, Invoice Date*, Amount*, Payment Terms*
- **Value helps**: Vendor lookup, GL Account lookup, Cost Center lookup
- **Calculations**: Auto-calculate tax, totals, due date
- **Validation**: Check for duplicate invoices, PO matching

#### Three-Way Match Display
- **Visual comparison**: Side-by-side PO quantity vs. GR quantity vs. Invoice quantity
- **Variance highlight**: Red border for mismatches
- **Tolerance check**: Show if within acceptable variance
- **Action required**: Clear message if approval needed

#### Approval Workflow Form
- **Approval decision**: Radio buttons - Approve / Reject
- **Comments**: Required for rejection, optional for approval
- **Supporting docs**: Link to view invoice PDF, PO, GR documents
- **Approval history**: Show previous approvers and comments
- **Submit action**: Emphasized button - "Submit Approval Decision"

### 3. Navigation Patterns

#### Hub and Spoke
- **Fiori Launchpad**: Central hub with app tiles
- **List to Detail**: Click invoice row → Navigate to invoice detail page
- **Back navigation**: Clear back button to return to list
- **Breadcrumbs**: Home > Invoices > Invoice 2024001

#### Object Page Navigation
- **Section anchors**: Quick navigation to sections (Header, Line Items, Posting, History)
- **Related objects**: Links to related PO, GR, Supplier, Payment
- **Action outcomes**: After posting, navigate to document display

### 4. Error Handling and Validation

#### Error Messages
- **Clear and specific**: "Invoice number already exists" not "Invalid input"
- **Actionable**: "Please enter a valid vendor number" not "Error in vendor field"
- **Location**: Show errors at the field level and in a message strip
- **Recovery**: Provide clear path to fix the error

#### Validation Timing
- **Real-time**: Validate format as user types (e.g., email format)
- **On blur**: Validate business rules when field loses focus
- **On submit**: Final validation before processing
- **Prevent submission**: Disable submit button if errors exist

#### Warning Messages
- **Tolerance exceeded**: "Invoice amount exceeds PO amount by 5%"
- **Duplicate check**: "Similar invoice found: INV-2024-001 from same vendor"
- **Approval required**: "This invoice requires manager approval due to variance"

### 5. Performance Optimization

#### Lazy Loading
- **Tables**: Load first page, fetch more on scroll
- **Filters**: Load filter values on demand
- **Details**: Load object details only when accessed

#### Caching
- **Master data**: Cache vendors, GL accounts, cost centers
- **User preferences**: Cache table settings, filter selections
- **Lookups**: Cache value help results

#### Responsive Images
- **Use appropriate sizes**: Don't load high-res images for mobile
- **Lazy load images**: Load images as they come into viewport

---

## Implementation Guidelines

### SAP UI5 Framework

#### Standard Controls to Use

**Layout**:
- `sap.f.DynamicPage` - For page layout
- `sap.uxap.ObjectPageLayout` - For object pages
- `sap.m.FlexBox` - For flexible layouts
- `sap.ui.layout.Grid` - For responsive grid

**Tables**:
- `sap.m.Table` - Responsive table for most uses
- `sap.ui.table.Table` - Grid table for complex data
- `sap.ui.table.AnalyticalTable` - For aggregations

**Forms**:
- `sap.ui.layout.form.Form` - Standard form layout
- `sap.m.Input` - Text input
- `sap.m.DatePicker` - Date selection
- `sap.m.Select` - Dropdown selection
- `sap.m.MultiInput` - Multiple value selection

**Actions**:
- `sap.m.Button` - Standard button
- `sap.m.MenuButton` - Button with menu
- `sap.m.OverflowToolbar` - Toolbar with overflow

**Display**:
- `sap.m.ObjectStatus` - Status badges
- `sap.m.ObjectNumber` - Formatted numbers
- `sap.m.Title` - Page/section titles
- `sap.m.Label` - Form labels

#### CSS Classes to Use

**Spacing**:
- `sapUiTinyMargin` - 0.5rem margin
- `sapUiSmallMargin` - 1rem margin
- `sapUiMediumMargin` - 2rem margin
- `sapUiContentPadding` - Standard content padding
- `sapUiResponsiveMargin` - Responsive margins

**Containers**:
- `sapUiNoContentPadding` - Remove padding
- `sapUiResponsivePadding` - Responsive padding

**Text**:
- `sapMTextRenderWhitespace` - Preserve whitespace
- `sapMTextRenderBold` - Bold text

### Development Best Practices

#### 1. Use SAP Fiori Elements When Possible
- Reduces custom code
- Ensures design consistency
- Automatic updates with new guidelines
- Faster development

#### 2. Follow MVC Pattern
- Separate view (XML), controller (JS), and model (data)
- Use data binding for dynamic updates
- Implement formatters for data transformation

#### 3. Responsive Design
- Test on desktop, tablet, and mobile
- Use responsive controls (sap.m.*)
- Implement device-specific behaviors if needed

#### 4. Performance
- Use lazy loading for data
- Implement pagination for large lists
- Optimize images and assets
- Minimize DOM manipulations

#### 5. Accessibility
- Use semantic HTML
- Provide ARIA labels
- Ensure keyboard navigation
- Test with screen readers
- Maintain proper contrast ratios

#### 6. Testing
- Unit tests for business logic
- OPA5 tests for UI interactions
- Visual regression testing
- Performance testing

---

## Checklist for P2P Application Design

### Visual Design ✅
- [ ] Using SAP 72 font family
- [ ] Consistent spacing using 0.5rem base unit
- [ ] Proper color usage (Horizon theme)
- [ ] Semantic colors for statuses
- [ ] Sufficient contrast (WCAG AA minimum)
- [ ] Clear visual hierarchy
- [ ] Consistent iconography

### Layout ✅
- [ ] Dynamic page layout for standard pages
- [ ] Object page layout for detail views
- [ ] Responsive grid (12/8/4 columns)
- [ ] Proper margins and gutters
- [ ] Responsive breakpoints implemented
- [ ] Mobile-friendly layouts

### Components ✅
- [ ] Responsive tables for lists
- [ ] Grid tables for complex data (if needed)
- [ ] Table toolbars with proper actions
- [ ] Forms with logical grouping
- [ ] Input controls with proper validation
- [ ] Filter bars for data filtering
- [ ] Proper button types and styles

### Navigation ✅
- [ ] Clear breadcrumbs
- [ ] Back navigation implemented
- [ ] Related object links
- [ ] Section anchors in object pages
- [ ] Consistent navigation patterns

### Content ✅
- [ ] Clear, concise labels
- [ ] Helpful field descriptions
- [ ] Proper status indicators
- [ ] Empty states with guidance
- [ ] Error messages (clear, actionable)
- [ ] Success confirmations

### Interaction ✅
- [ ] Proper button states (hover, active, disabled)
- [ ] Loading indicators
- [ ] Unsaved changes warnings
- [ ] Confirmation dialogs for destructive actions
- [ ] Inline editing where appropriate
- [ ] Batch actions for efficiency

### Accessibility ✅
- [ ] ARIA labels for screen readers
- [ ] Keyboard navigation support
- [ ] Sufficient color contrast
- [ ] Focus indicators visible
- [ ] Icons paired with text
- [ ] Meaningful alt text for images

### Performance ✅
- [ ] Lazy loading implemented
- [ ] Pagination for large lists
- [ ] Efficient data binding
- [ ] Optimized images
- [ ] Minimal re-renders

---

## Resources and References

### Official Documentation
- **SAP Fiori Design System**: https://www.sap.com/design-system/fiori-design-web/
- **SAP UI5 SDK**: https://ui5.sap.com/
- **SAP Fiori Apps Library**: https://fioriappslibrary.hana.ondemand.com
- **SAP Fiori for Web Guidelines**: https://www.sap.com/design-system/fiori-design-web/

### Design Resources
- **Figma Libraries**: SAP Fiori Design Kit for Figma
- **Icon Library**: https://ui5.sap.com/test-resources/sap/m/demokit/iconExplorer/
- **Color Palette**: Horizon Theme colors
- **Typography**: SAP 72 Font Family

### Development Tools
- **SAP Business Application Studio**: Cloud IDE
- **SAP Web IDE**: Legacy IDE
- **UI5 Tooling**: https://sap.github.io/ui5-tooling/
- **UI5 Inspector**: Browser extension for debugging

### Community
- **SAP Community**: https://community.sap.com/
- **Stack Overflow**: Tag [sapui5]
- **GitHub**: SAP OpenUI5 repositories

---

## Version History

### Version 1.0 (January 20, 2026)
- Initial comprehensive guidelines document
- Coverage of List Report, Object Page, Dynamic Page floorplans
- Complete component library
- Visual design foundations
- P2P-specific best practices
- Implementation guidelines

### Future Enhancements
- Additional floorplan patterns (Overview Page, Analytical List Page)
- Mobile-specific guidelines
- Advanced component usage patterns
- Industry-specific examples
- Video tutorials and demos

---

## Contact and Support

For questions about implementing these guidelines in the P2P project:
- Review official SAP Fiori Design System documentation
- Consult SAP UI5 SDK for technical implementation
- Engage with SAP community for best practices

---

**Document Status**: ✅ Complete - Ready for Implementation  
**Last Review**: January 20, 2026  
**Next Review**: Quarterly updates with new guideline versions
