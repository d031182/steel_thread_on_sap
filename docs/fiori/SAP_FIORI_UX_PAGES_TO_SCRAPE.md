# SAP Fiori Design Guidelines - Priority UX Pages to Scrape

**Date Created**: 2026-01-20  
**Purpose**: Identify and track the most essential UX pages for improving P2P application design  
**Base URL**: https://www.sap.com/design-system/fiori-design-web/

---

## Priority 1: Layout & Structure (Critical for P2P App)

### 1. Floorplans - List Report
**URL**: `https://www.sap.com/design-system/fiori-design-web/patterns/list-report`  
**Priority**: ⭐⭐⭐⭐⭐ (CRITICAL)  
**Why Essential**: 
- Standard pattern for displaying P2P data (invoices, POs, suppliers)
- Defines table layout, filters, and actions
- Most common floorplan for transactional apps

**Key Topics to Extract**:
- List report structure
- Filter bar design
- Table toolbar actions
- Multi-select behavior
- Search functionality
- Sort and group patterns

---

### 2. Floorplans - Object Page
**URL**: `https://www.sap.com/design-system/fiori-design-web/patterns/object-page`  
**Priority**: ⭐⭐⭐⭐⭐ (CRITICAL)  
**Why Essential**:
- Display detailed invoice, PO, or supplier information
- Section-based layout for complex data
- Header with KPIs and actions

**Key Topics to Extract**:
- Object page header design
- Section layout and navigation
- Dynamic header behavior
- Action placement in object pages
- Related objects display

---

### 3. Dynamic Page Layout
**URL**: `https://www.sap.com/design-system/fiori-design-web/patterns/dynamic-page`  
**Priority**: ⭐⭐⭐⭐⭐ (CRITICAL)  
**Why Essential**:
- Foundation for most Fiori pages
- Header, content, footer structure
- Responsive behavior

**Key Topics to Extract**:
- Dynamic page structure
- Header toolbar design
- Footer toolbar usage
- Scrolling behavior
- Responsive breakpoints

---

## Priority 2: Navigation & Information Architecture

### 4. Navigation Patterns
**URL**: `https://www.sap.com/design-system/fiori-design-web/patterns/navigation`  
**Priority**: ⭐⭐⭐⭐ (HIGH)  
**Why Essential**:
- Fiori Launchpad integration
- App-to-app navigation
- Breadcrumb usage
- Back button behavior

**Key Topics to Extract**:
- Navigation best practices
- Cross-app navigation
- Breadcrumb guidelines
- Shell bar navigation
- Hierarchical navigation

---

### 5. Shell Bar / Header
**URL**: `https://www.sap.com/design-system/fiori-design-web/components/shell-bar`  
**Priority**: ⭐⭐⭐⭐ (HIGH)  
**Why Essential**:
- Application shell structure
- Global actions placement
- Notifications and user menu
- Search integration

**Key Topics to Extract**:
- Shell bar structure
- Logo and branding
- Global search
- Notifications
- User profile menu

---

## Priority 3: Data Display Components

### 6. Tables & Lists
**URL**: `https://www.sap.com/design-system/fiori-design-web/components/table`  
**Priority**: ⭐⭐⭐⭐⭐ (CRITICAL)  
**Why Essential**:
- Core component for P2P data display
- Responsive table behavior
- Column design and sizing
- Row actions and selection

**Key Topics to Extract**:
- Table types (responsive, grid, tree)
- Column header design
- Sort and filter in tables
- Row actions and navigation
- Multi-select behavior
- Pagination
- Empty state handling
- Loading states

---

### 7. Forms & Input Controls
**URL**: `https://www.sap.com/design-system/fiori-design-web/patterns/forms`  
**Priority**: ⭐⭐⭐⭐⭐ (CRITICAL)  
**Why Essential**:
- Invoice creation and editing
- Data entry patterns
- Field validation
- Form layout

**Key Topics to Extract**:
- Form layout patterns
- Field grouping
- Label placement
- Required field indicators
- Inline validation
- Error message display
- Input field types
- Date/time pickers
- Value help dialogs

---

## Priority 4: Visual Design Elements

### 8. Typography System
**URL**: `https://www.sap.com/design-system/fiori-design-web/foundations/typography`  
**Priority**: ⭐⭐⭐⭐ (HIGH)  
**Why Essential**:
- Font family (SAP 72)
- Text sizes and scales
- Line heights
- Text color usage

**Key Topics to Extract**:
- Font specifications
- Type scale (sizes)
- Font weights
- Line heights
- Text colors
- Accessibility requirements

---

### 9. Iconography
**URL**: `https://www.sap.com/design-system/fiori-design-web/foundations/icons`  
**Priority**: ⭐⭐⭐⭐ (HIGH)  
**Why Essential**:
- Standard icon library
- Action icons
- Status icons
- Icon sizing

**Key Topics to Extract**:
- Icon library overview
- UI vs action icons
- Icon sizes
- Icon colors
- Custom icons guidelines
- Accessibility

---

### 10. Spacing & Layout Grid
**URL**: `https://www.sap.com/design-system/fiori-design-web/foundations/layout`  
**Priority**: ⭐⭐⭐⭐ (HIGH)  
**Why Essential**:
- Consistent spacing system
- Grid structure
- Responsive breakpoints
- Container usage

**Key Topics to Extract**:
- Spacing scale (0.5rem, 1rem, etc.)
- Grid system (12-column)
- Breakpoints (S, M, L, XL)
- Container patterns
- Margin and padding standards

---

## Additional High-Value Pages (Priority 2)

### 11. Buttons & Actions
**URL**: `https://www.sap.com/design-system/fiori-design-web/components/button`  
**Priority**: ⭐⭐⭐⭐ (HIGH)  
**Why Essential**: Action button types, placement, states

### 12. Messages & Notifications
**URL**: `https://www.sap.com/design-system/fiori-design-web/patterns/messaging`  
**Priority**: ⭐⭐⭐⭐ (HIGH)  
**Why Essential**: Error messages, success messages, message toast, message box

### 13. Dialogs & Popovers
**URL**: `https://www.sap.com/design-system/fiori-design-web/components/dialog`  
**Priority**: ⭐⭐⭐ (MEDIUM)  
**Why Essential**: Modal dialogs, confirmation dialogs, value help

### 14. Colors
**URL**: `https://www.sap.com/design-system/fiori-design-web/foundations/colors`  
**Priority**: ⭐⭐⭐⭐ (HIGH)  
**Why Essential**: Color palette, semantic colors, status colors

### 15. Cards
**URL**: `https://www.sap.com/design-system/fiori-design-web/components/card`  
**Priority**: ⭐⭐⭐ (MEDIUM)  
**Why Essential**: Dashboard and overview displays

---

## Scraping Strategy

### Phase 1: Critical Foundation (Top 3)
1. List Report Floorplan
2. Object Page Floorplan  
3. Dynamic Page Layout

**Rationale**: These define the fundamental page structure for P2P applications

### Phase 2: Data Display (Items 6-7)
4. Tables & Lists
5. Forms & Input Controls

**Rationale**: Core components for displaying and entering P2P data

### Phase 3: Visual System (Items 8-10)
6. Typography
7. Iconography
8. Spacing & Layout Grid

**Rationale**: Ensures visual consistency and proper implementation

### Phase 4: Navigation & Interaction (Items 4-5, 11-12)
9. Navigation Patterns
10. Shell Bar
11. Buttons & Actions
12. Messages & Notifications

**Rationale**: Completes the interaction model

---

## Expected Outcomes

After scraping these 10+ pages, we will have comprehensive guidance on:

✅ **Layout**: How to structure list views and detail pages  
✅ **Components**: Proper usage of tables, forms, buttons  
✅ **Visual Design**: Typography, icons, spacing, colors  
✅ **Navigation**: How users move through the application  
✅ **Interactions**: Actions, validations, messages  
✅ **Responsive**: How designs adapt to different screens  
✅ **Accessibility**: ARIA labels, keyboard navigation  

---

## Implementation Plan

### Option 1: Manual Browser Scraping
- Use browser_action to navigate to each page
- Capture screenshots and content
- Document key patterns and examples

### Option 2: Automated Scraping (Preferred)
- Fix and restart scrapy MCP server
- Use scrape_multiple_urls to batch process
- Extract structured content automatically

### Option 3: Hybrid Approach
- Use Perplexity for context and understanding
- Manually document key patterns
- Reference official documentation

---

## Success Metrics

✅ **Coverage**: All 10 priority pages documented  
✅ **Depth**: Key patterns and examples extracted  
✅ **Applicability**: Direct application to P2P viewer improvements  
✅ **Completeness**: Guidelines cover layout, components, interactions, visual design  

---

## Next Actions

1. ✅ Created priority list with URLs
2. ⏳ Scrape top 10 pages (awaiting scrapy server restart OR use browser)
3. ⏳ Extract and document key UX patterns
4. ⏳ Update SAP_FIORI_DESIGN_GUIDELINES.md with new content
5. ⏳ Apply learnings to p2p-data-products-ui5-fiori.html
6. ⏳ Update PROJECT_TRACKER_REFACTORED.md

---

*Document created: 2026-01-20*  
*Last updated: 2026-01-20*  
*Status: Ready for scraping*
