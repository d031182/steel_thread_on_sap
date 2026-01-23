# Archived UI Alternative Files

**Archive Date**: January 22, 2026  
**Reason**: Consolidation to SAPUI5+Fiori standard implementation

---

## 📦 Archived Files

### From web/current/ (root level)

#### 1. index.html
**Type**: Standalone Vanilla JavaScript Application  
**Original Location**: `web/current/index.html`  
**Description**: Main application with embedded JavaScript, no SAPUI5 framework  
**Features**:
- Data Products Catalog with sample data
- HANA Connection Manager
- SQL Console with templates
- CSN Viewer
- Theme switcher
- Data Products Explorer
- Log Viewer

**Why Archived**: Not using SAPUI5 framework. Application logic mixed with presentation layer.

---

#### 2. index-ui5.html
**Type**: Alternative UI5 Implementation  
**Original Location**: `web/current/index-ui5.html`  
**Description**: UI5-based version but not following proper SAPUI5 webapp structure  
**Features**: Similar features to index.html but with some UI5 components

**Why Archived**: Not following SAP standard webapp structure with Component.js, manifest.json, MVC pattern.

---

#### 3. sapui5-demo.html
**Type**: Demo/Test File  
**Original Location**: `web/current/sapui5-demo.html`  
**Description**: SAPUI5 demonstration file for testing UI5 components  

**Why Archived**: Demo/test file, not production code.

---

### From web/current/webapp/ (SAPUI5 app directory)

#### 4. app-complete.html
**Type**: Complete Standalone SAPUI5 Application  
**Original Location**: `web/current/webapp/app-complete.html`  
**Description**: Full SAPUI5 app in a single HTML file  

**Why Archived**: Alternative entry point. Not following proper SAPUI5 MVC structure with separate Component.js and manifest.json.

---

#### 5. p2p-fiori-proper.html
**Type**: Fiori-Compliant HTML File  
**Original Location**: `web/current/webapp/p2p-fiori-proper.html`  
**Description**: Fiori design guidelines implementation  

**Why Archived**: Alternative entry point. The main index.html already follows Fiori guidelines properly.

---

#### 6. index-simple.html
**Type**: Simplified SAPUI5 Entry Point  
**Original Location**: `web/current/webapp/index-simple.html`  
**Description**: Simple version of the SAPUI5 app  

**Why Archived**: Alternative entry point. The main index.html is the standard entry point.

---

## ✅ Retained Implementation

**Primary Application**: `webapp/` directory

**Structure**:
```
webapp/
├── index.html              # Entry point
├── Component.js            # Application component
├── manifest.json           # App descriptor
├── controller/             # Controllers (MVC)
├── view/                   # Views (XML)
├── model/                  # Models
├── css/                    # Styles
├── i18n/                   # Internationalization
└── test/                   # Unit tests
```

**Reasons for Retention**:
- ✅ Follows SAP SAPUI5 best practices
- ✅ Proper MVC architecture
- ✅ manifest.json app descriptor
- ✅ Component-based structure
- ✅ SAP Fiori design guidelines compliant
- ✅ Separation of concerns
- ✅ Maintainable and scalable
- ✅ Production-ready

---


---

## 🔄 Migration Guide

If you need to reference the archived implementations:

### From index.html to webapp/
The webapp implementation provides the same features but with proper SAPUI5 structure:

| Feature | index.html | webapp/ Implementation |
|---------|-----------|----------------------|
| Data Products | Inline JS | DataProducts.controller.js |
| Views | Inline HTML | DataProducts.view.xml |
| Routing | Manual | manifest.json routing |
| Models | localStorage direct | models.js + manifest.json |
| Styles | Inline CSS | css/style.css |
| i18n | Hardcoded | i18n/i18n.properties |

### Key Differences

**index.html Approach**:
```javascript
// Everything in one file
function openDataProduct(id) {
    // Direct DOM manipulation
    document.getElementById('content').innerHTML = '...';
}
```

**webapp/ Approach**:
```javascript
// Controller
sap.ui.define([
    "sap/ui/core/mvc/Controller"
], function(Controller) {
    return Controller.extend("p2p.controller.DataProducts", {
        onProductPress: function(oEvent) {
            // Framework-managed navigation
            this.getRouter().navTo("product", {
                productId: oEvent.getSource().getBindingContext().getProperty("id")
            });
        }
    });
});
```

---

## 🔗 Related Documentation

- **SAPUI5 Migration Plan**: `../docs/migration/SAPUI5_MIGRATION_PLAN.md`
- **SAPUI5 Migration Phase 1 Complete**: `../docs/migration/SAPUI5_MIGRATION_PHASE1_COMPLETE.md`
- **Main README**: `../README.md`

---

## 🗂️ Archive Structure

```
archive-ui-alternatives-2026-01-22/
├── README.md                    # This file
│
# From web/current/ root
├── index.html                   # Standalone vanilla JS app
├── index-ui5.html              # Alternative UI5 version
├── sapui5-demo.html            # Demo file
│
# From web/current/webapp/
├── app-complete.html           # Complete SAPUI5 in one file
├── p2p-fiori-proper.html       # Fiori-compliant version
└── index-simple.html           # Simplified entry point
```

**Total Files Archived**: 6

---

## ⚠️ Important Notes

1. **No Functionality Loss**: All features from archived files are available in webapp/ implementation
2. **Better Architecture**: webapp/ follows SAP best practices
3. **Maintainability**: Proper separation of concerns makes maintenance easier
4. **Scalability**: Component-based architecture scales better
5. **Team Development**: MVC pattern supports team collaboration

---

## 🔧 Restoring Archived Files

If you need to restore any archived file:

```powershell
# Restore index.html
Copy-Item "archive-ui-alternatives-2026-01-22/index.html" "../"

# Restore index-ui5.html
Copy-Item "archive-ui-alternatives-2026-01-22/index-ui5.html" "../"

# Restore sapui5-demo.html
Copy-Item "archive-ui-alternatives-2026-01-22/sapui5-demo.html" "../"
```

---

## 📊 Statistics

- **Files Archived**: 6
  - 3 from web/current/ root
  - 3 from web/current/webapp/
- **Total Size**: ~500KB (estimated)
- **Lines of Code Archived**: ~5000+ lines
- **Features Preserved**: 100% (all features available in webapp/index.html)

---

## 🎯 Recommendation

**Use webapp/ implementation** for all new development and production deployment.

The archived files are kept for:
- Historical reference
- Migration examples
- Feature comparison
- Rollback capability (if needed)

---

**Archive Created By**: P2P MCP Team  
**Date**: January 22, 2026  
**Status**: ✅ Archive Complete
