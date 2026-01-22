# Data Products Explorer Detail Page Enhancement

**Status:** 📋 Specification  
**Priority:** Medium  
**Estimated Effort:** 30-45 minutes

## Current Behavior

### Explorer Tab (🗄️)
1. Shows list of data products from HANA
2. Click on data product → Shows tables inline in same panel
3. Click on table → Shows structure/data inline
4. Everything stays in one page

### Data Products Catalog Tab (📦)  
1. Shows cards of mock data products
2. Click on card → Navigates to separate detail page
3. Back button returns to catalog
4. Clean page-to-page navigation

## Desired Behavior

User wants Explorer tab to work like the Catalog tab:

1. ✅ Go to Explorer tab
2. ✅ See list of data products (SalesOrder)
3. ❌ Click on SalesOrder → **Open detailed page/popup**
4. ❌ Detail page shows:
   - Product name, metadata
   - List of 2 tables (SalesOrder, SalesOrderItem)
   - For each table:
     - Table name
     - Record count
     - Buttons: "View Structure", "View Data"
5. ❌ Click "View Structure" → Shows column definitions
6. ❌ Click "View Data" → Shows paginated table data
7. ❌ Back button returns to Explorer list

## Implementation Plan

### Option 1: Reuse Existing Navigation Pattern (Recommended)

Modify Explorer to use the same page navigation as Data Products Catalog:

**Files to modify:**
- `index.html` - Add `explorerDetailPage` section
- `js/ui/pages/dataProductsExplorer.js` - Add navigation functions

**Changes needed:**
1. Add new page section for Explorer detail view (copy from objectPage pattern)
2. Modify `selectDataProduct()` to navigate to detail page instead of inline display
3. Add back button to return to Explorer list
4. Reuse existing table display functions

**Pros:**
- Consistent UI pattern across app
- Reuses proven navigation code
- Clean separation of concerns

**Cons:**
- Requires HTML structure changes

### Option 2: Modal Dialog/Popup

Show detail in a modal dialog:

**Changes needed:**
1. Create large modal dialog template
2. Load data product details into dialog
3. Show/hide dialog on click

**Pros:**
- Stays on same page
- No navigation needed
- Can dim background

**Cons:**
- Different pattern than Catalog
- Modal might be too small for large tables
- Accessibility concerns

## Recommended Approach: Option 1

Use page navigation to match the existing Data Products Catalog behavior.

## Implementation Steps

### 1. Add Detail Page HTML Structure
```html
<!-- Explorer Detail Page -->
<div class="sapPage" id="explorerDetailPage">
    <div class="sapObjectPage">
        <div class="objectPageHeader" id="explorerDetailHeader">
            <!-- Populated by JS -->
        </div>
        <div class="objectPageContent" id="explorerDetailContent">
            <!-- Tables list -->
        </div>
    </div>
</div>
```

### 2. Modify dataProductsExplorer.js

Add navigation functions:
```javascript
export function openDataProductDetail(schemaName) {
    // Hide explorer list page
    document.getElementById('dataProductsExplorerPage').classList.remove('active');
    // Show detail page  
    document.getElementById('explorerDetailPage').classList.add('active');
    // Load and display tables
    loadDataProductDetail(schemaName);
}

export function closeDataProductDetail() {
    // Hide detail page
    document.getElementById('explorerDetailPage').classList.remove('active');
    // Show explorer list
    document.getElementById('dataProductsExplorerPage').classList.add('active');
}
```

### 3. Update Click Handlers

Change from inline display to navigation:
```javascript
// OLD: selectDataProduct() shows inline
// NEW: selectDataProduct() navigates to detail page
```

### 4. Add Back Button

In detail page header:
```html
<button class="sapButton sapButtonTransparent" onclick="window.closeDataProductDetail()">
    ← Back to Explorer
</button>
```

### 5. Reuse Table Display Functions

Use existing functions for structure and data views:
- `viewTableStructure()`
- `viewTableData()`

## Testing Checklist

- [ ] Click on SalesOrder in Explorer → Navigates to detail page
- [ ] Detail page shows product name and metadata
- [ ] Detail page lists 2 tables with record counts
- [ ] Click "View Structure" → Shows column definitions
- [ ] Click "View Data" → Shows table data with pagination
- [ ] Pagination works (Next/Previous buttons)
- [ ] Back button returns to Explorer list
- [ ] No JavaScript errors in console
- [ ] API calls work correctly
- [ ] Loading states display properly

## Current Status

- ✅ Backend API working perfectly
- ✅ Explorer shows data product list
- ✅ Explorer can load tables inline
- ❌ **Missing:** Detail page navigation
- ❌ **Missing:** Back button to return to list
- ❌ **Missing:** Clean page-to-page flow

## Files Currently Working

- `flask-backend/app.py` - All APIs functional
- `js/api/dataProductsAPI.js` - API client working
- `js/ui/pages/dataProductsExplorer.js` - Loads data correctly

## What User Sees Now vs. What They Want

**Now:**
```
Explorer Tab
├── Data Product List
│   └── SalesOrder [click]
│       └── Tables appear inline below
│           ├── SalesOrder table
│           └── SalesOrderItem table
```

**Want:**
```
Explorer Tab
├── Data Product List
│   └── SalesOrder [click] → Navigate to Detail Page

Detail Page (new)
├── [← Back] SalesOrder
├── Metadata (name, version, etc.)
└── Tables List
    ├── SalesOrder (492,653 rows) [View Structure] [View Data]
    └── SalesOrderItem (6,663 rows) [View Structure] [View Data]
```

## Next Steps

1. Implement Option 1 (page navigation)
2. Test with SalesOrder data product
3. Verify all functionality works
4. Update documentation

---

**Note:** This enhancement will make the Explorer tab consistent with the Data Products Catalog tab, providing a better user experience.
