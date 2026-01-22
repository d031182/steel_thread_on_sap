# 🎯 UI Files Guide - Which One to Use?

**Date**: January 22, 2026  
**Status**: Current project structure clarified

---

## ✅ LEADING UX FILE (RECOMMENDED)

### webapp/index.html
**Location**: `web/current/webapp/index.html`  
**Type**: SAPUI5+Fiori Application (SAP Standard)  
**Status**: ✅ **PRIMARY - USE THIS ONE**

**How to Access**:
```bash
# Via Flask Backend (recommended)
cd web/current/flask-backend
python app.py
# Then open: http://localhost:5000/webapp/

# OR via Python HTTP server
cd web/current
python -m http.server 8000
# Then open: http://localhost:8000/webapp/
```

**Features**:
- ✅ **CSN Button Added**: "View CSN" button on each data product card
- ✅ SAP SAPUI5 framework
- ✅ MVC architecture (Controller, View, Model)
- ✅ manifest.json app descriptor
- ✅ Component-based structure
- ✅ SAP Fiori Horizon theme
- ✅ Professional and production-ready

**Structure**:
```
webapp/
├── index.html                    # Entry point ← START HERE
├── Component.js                  # App component
├── manifest.json                 # App configuration
├── controller/
│   └── DataProducts.controller.js  # ✅ Has onViewCSN handler
├── view/
│   └── DataProducts.view.xml      # ✅ Has "View CSN" button
└── ...
```

---

## 📦 ARCHIVED FILES (No longer active)

### archive-ui-alternatives-2026-01-22/
**Location**: `web/current/archive-ui-alternatives-2026-01-22/`  
**Status**: ⚠️ **ARCHIVED - NOT ACTIVE**

These files were moved to archive on January 22, 2026:

1. **index.html** (archived)
   - Standalone vanilla JavaScript app
   - Had CSN button implementation
   - No longer the primary file

2. **index-ui5.html** (archived)
   - Alternative UI5 version
   - Not following proper webapp structure

3. **sapui5-demo.html** (archived)
   - Demo/test file

---

## 🔍 Current Implementation Status

### CSN Button Location

**File**: `web/current/webapp/view/DataProducts.view.xml`  
**Line**: ~86-95  
**Implementation**: ✅ COMPLETE

```xml
<HBox width="100%" justifyContent="SpaceBetween" class="sapUiSmallMarginTop">
    <Button
        text="View CSN"
        type="Default"
        icon="sap-icon://document"
        press=".onViewCSN"
        customData:productId="{id}"
        xmlns:customData="http://schemas.sap.com/sapui5/extension/sap.ui.core.CustomData/1" />
    <Button
        text="View Details"
        type="Emphasized"
        press=".onViewProduct"
        customData:productId="{id}"
        xmlns:customData="http://schemas.sap.com/sapui5/extension/sap.ui.core.CustomData/1" />
</HBox>
```

### CSN Handler

**File**: `web/current/webapp/controller/DataProducts.controller.js`  
**Function**: `onViewCSN`  
**Implementation**: ✅ COMPLETE

**Features**:
- Loads CSN from local JSON files
- Displays in SAPUI5 Dialog
- Copy to clipboard functionality
- Proper error handling
- Loading indicators

---

## 🚀 How to See the CSN Button

### Step 1: Start the Application

**Option A: Flask Backend** (Recommended for full features)
```powershell
cd web\current\flask-backend
python app.py
```
Then open: http://localhost:5000/webapp/

**Option B: Python HTTP Server** (For SAPUI5 only)
```powershell
cd web\current
python -m http.server 8000
```
Then open: http://localhost:8000/webapp/

### Step 2: View the Application

1. The SAPUI5 app will load
2. You'll see 6 data product cards (Supplier, Purchase Order, etc.)
3. Each card now has TWO buttons:
   - **"View CSN"** (left button with document icon 📄)
   - **"View Details"** (right button, emphasized blue)

### Step 3: Click "View CSN"

1. Click the "View CSN" button on any data product card
2. A dialog will open showing the CSN definition
3. You can copy the CSN to clipboard using the button in the dialog

---

## ⚠️ If You Don't See the Button

### Possible Issues:

1. **Wrong File Open**: 
   - You might have an old file cached in browser
   - **Solution**: Hard refresh (Ctrl+Shift+R or Ctrl+F5)

2. **Wrong URL**:
   - Looking at archived file instead of webapp/
   - **Correct URL**: `http://localhost:8000/webapp/` (note the `/webapp/` at the end)
   - **Wrong URL**: `http://localhost:8000/` (this would try to load archived files)

3. **Browser Cache**:
   - Browser cached old version
   - **Solution**: Clear cache or use incognito mode

4. **Server Not Started**:
   - No HTTP server running
   - **Solution**: Start Python HTTP server or Flask backend

---

## 📊 File Comparison

| File | Location | Type | CSN Button | Status |
|------|----------|------|------------|--------|
| **webapp/index.html** | `web/current/webapp/` | SAPUI5+Fiori | ✅ YES | ✅ **PRIMARY** |
| index.html | `archive-ui-alternatives-2026-01-22/` | Vanilla JS | ✅ YES | ⚠️ Archived |
| index-ui5.html | `archive-ui-alternatives-2026-01-22/` | Alt UI5 | ❌ NO | ⚠️ Archived |
| sapui5-demo.html | `archive-ui-alternatives-2026-01-22/` | Demo | ❌ NO | ⚠️ Archived |

---

## 🎯 Quick Test

To verify the CSN button is working:

```powershell
# 1. Start server
cd web\current
python -m http.server 8000

# 2. Open in browser
start http://localhost:8000/webapp/

# 3. Look for the "View CSN" button on each data product card
# 4. Click it to see the CSN definition dialog
```

---

## 📝 Summary

**LEADING UX FILE**: `web/current/webapp/index.html`  
**CSN BUTTON STATUS**: ✅ **IMPLEMENTED AND READY**  
**HOW TO ACCESS**: Start HTTP server and navigate to `/webapp/` directory

The CSN button has been successfully added to the SAPUI5 webapp. If you're not seeing it, please:
1. Make sure you're accessing `/webapp/` directory
2. Hard refresh your browser (Ctrl+Shift+R)
3. Check that the server is serving from `web/current` directory

---

**Last Updated**: January 22, 2026, 2:56 PM
