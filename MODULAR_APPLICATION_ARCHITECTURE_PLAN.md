# Modular Application Architecture - Complete Plan

**Date**: 2026-01-24  
**Purpose**: Transform entire application into self-contained, toggleable modules  
**Status**: 📋 COMPREHENSIVE PLANNING

---

## 🎯 Vision: Module-Based Application

### Core Philosophy

**Every capability = Self-contained module**

Each module contains:
- ✅ Backend logic (APIs, services, connectors)
- ✅ Frontend UI (SAP UI5 views, controllers)
- ✅ Documentation (README, guides, examples)
- ✅ Tests (unit, integration)
- ✅ Configuration (settings, feature flags)

**Benefits**:
- 🔌 Enable/disable features on demand
- 📦 Install/uninstall modules
- 🧪 Test modules in isolation
- 📚 Self-documented capabilities
- 🚀 Deploy selectively to production

---

## 📂 Complete Application Structure

```
steel_thread_on_sap/
│
├── modules/                              # All application modules
│   │
│   ├── feature-manager/                  # ⭐ Core module: Feature toggle system
│   │   ├── backend/
│   │   │   ├── __init__.py
│   │   │   ├── feature_flags.py         # Feature flag storage
│   │   │   ├── api.py                   # Feature toggle API
│   │   │   └── config.yaml              # Default feature states
│   │   ├── frontend/
│   │   │   ├── ConfiguratorApp.view.xml # Settings dialog
│   │   │   ├── Configurator.controller.js
│   │   │   └── FeatureToggle.fragment.xml
│   │   ├── docs/
│   │   │   └── FEATURE_MANAGER.md
│   │   ├── tests/
│   │   │   ├── test_feature_flags.py
│   │   │   └── featureToggle.test.js
│   │   └── README.md
│   │
│   ├── csn-validation/                   # Module 1: CSN Validation
│   │   ├── backend/
│   │   │   ├── core/
│   │   │   │   ├── validator.py
│   │   │   │   ├── csn_parser.py
│   │   │   │   └── type_mapper.py
│   │   │   ├── sources/
│   │   │   │   ├── base.py
│   │   │   │   ├── hana_connector.py
│   │   │   │   └── sqlite_connector.py
│   │   │   ├── api.py                   # Flask routes
│   │   │   └── config.yaml
│   │   ├── frontend/
│   │   │   ├── CSNValidator.view.xml    # Validation UI
│   │   │   ├── CSNValidator.controller.js
│   │   │   └── components/
│   │   │       ├── SourceSelector.fragment.xml
│   │   │       └── ValidationResults.fragment.xml
│   │   ├── docs/
│   │   │   ├── README.md                # Module documentation
│   │   │   ├── API_REFERENCE.md
│   │   │   ├── USER_GUIDE.md
│   │   │   └── DEVELOPER_GUIDE.md
│   │   ├── tests/
│   │   │   ├── test_validator.py
│   │   │   ├── test_hana_connector.py
│   │   │   └── csnValidator.test.js
│   │   └── README.md
│   │
│   ├── data-products-viewer/             # Module 2: Data Products Viewer
│   │   ├── backend/
│   │   │   ├── data_products_api.py
│   │   │   ├── hana_client.py
│   │   │   └── config.yaml
│   │   ├── frontend/
│   │   │   ├── DataProducts.view.xml
│   │   │   ├── DataProducts.controller.js
│   │   │   └── components/
│   │   ├── docs/
│   │   │   ├── README.md
│   │   │   └── USER_GUIDE.md
│   │   ├── tests/
│   │   └── README.md
│   │
│   ├── sql-execution/                    # Module 3: SQL Execution
│   │   ├── backend/
│   │   │   ├── sql_executor.py
│   │   │   ├── result_formatter.py
│   │   │   └── query_history.py
│   │   ├── frontend/
│   │   │   ├── SQLConsole.view.xml
│   │   │   ├── SQLConsole.controller.js
│   │   │   └── components/
│   │   ├── docs/
│   │   ├── tests/
│   │   └── README.md
│   │
│   ├── hana-connection/                  # Module 4: HANA Connection Manager
│   │   ├── backend/
│   │   ├── frontend/
│   │   ├── docs/
│   │   ├── tests/
│   │   └── README.md
│   │
│   └── sqlite-fallback/                  # Module 5: SQLite Demo Mode
│       ├── backend/
│       ├── frontend/
│       ├── docs/
│       ├── tests/
│       └── README.md
│
├── core/                                 # Shared core services
│   ├── backend/
│   │   ├── app.py                       # Main Flask app
│   │   ├── config.py                    # Global config
│   │   └── logger.py                    # Application logging
│   ├── frontend/
│   │   ├── Component.js                 # Root UI component
│   │   ├── Shell.view.xml               # Application shell
│   │   └── Shell.controller.js
│   └── shared/
│       ├── utils/                       # Shared utilities
│       └── constants/                   # Shared constants
│
├── docs/                                 # Module-organized docs
│   ├── architecture/
│   │   ├── MODULAR_ARCHITECTURE.md      # This architecture
│   │   └── FEATURE_TOGGLE_DESIGN.md
│   ├── modules/                          # Module-specific docs
│   │   ├── csn-validation/
│   │   ├── data-products-viewer/
│   │   └── feature-manager/
│   └── guides/                           # Cross-module guides
│       ├── GETTING_STARTED.md
│       └── DEVELOPER_ONBOARDING.md
│
└── tests/
    ├── integration/                      # Cross-module tests
    └── e2e/                              # End-to-end tests
```

---

## 🎛️ Feature Manager Module (CORE)

### Purpose
Centralized feature toggle system that controls which modules are active.

### Backend: Feature Flag Service

```python
# modules/feature-manager/backend/feature_flags.py
import json
import os
from typing import Dict, List, Optional

class FeatureFlags:
    """
    Feature flag service with persistent storage.
    Manages enable/disable state for all application modules.
    """
    
    def __init__(self, config_file: str = 'feature-config.json'):
        self.config_file = config_file
        self.flags = self._load_flags()
    
    def _load_flags(self) -> Dict:
        """Load feature flags from storage"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._get_default_flags()
    
    def _get_default_flags(self) -> Dict:
        """Default feature states"""
        return {
            'features': {
                'csn-validation': {
                    'enabled': True,
                    'name': 'CSN Validation',
                    'description': 'Validate CSN against data sources',
                    'category': 'Development Tools',
                    'requiresHana': False
                },
                'data-products-viewer': {
                    'enabled': True,
                    'name': 'Data Products Viewer',
                    'description': 'Browse and query data products',
                    'category': 'Data Management',
                    'requiresHana': True
                },
                'sql-execution': {
                    'enabled': True,
                    'name': 'SQL Console',
                    'description': 'Execute SQL queries',
                    'category': 'Development Tools',
                    'requiresHana': True
                },
                'sqlite-fallback': {
                    'enabled': True,
                    'name': 'Demo Mode (SQLite)',
                    'description': 'Use sample data when HANA unavailable',
                    'category': 'System',
                    'requiresHana': False
                },
                'hana-connection': {
                    'enabled': True,
                    'name': 'HANA Connection Manager',
                    'description': 'Manage HANA Cloud connections',
                    'category': 'Configuration',
                    'requiresHana': False
                }
            }
        }
    
    def is_enabled(self, feature_key: str) -> bool:
        """Check if feature is enabled"""
        return self.flags.get('features', {}).get(feature_key, {}).get('enabled', False)
    
    def enable(self, feature_key: str) -> bool:
        """Enable a feature"""
        if feature_key in self.flags['features']:
            self.flags['features'][feature_key]['enabled'] = True
            self._save_flags()
            return True
        return False
    
    def disable(self, feature_key: str) -> bool:
        """Disable a feature"""
        if feature_key in self.flags['features']:
            self.flags['features'][feature_key]['enabled'] = False
            self._save_flags()
            return True
        return False
    
    def toggle(self, feature_key: str) -> bool:
        """Toggle feature state"""
        if feature_key in self.flags['features']:
            current = self.flags['features'][feature_key]['enabled']
            self.flags['features'][feature_key]['enabled'] = not current
            self._save_flags()
            return not current
        return False
    
    def get_all(self) -> Dict:
        """Get all features with their states"""
        return self.flags.get('features', {})
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled feature keys"""
        return [
            key for key, feature in self.flags.get('features', {}).items()
            if feature.get('enabled', False)
        ]
    
    def _save_flags(self):
        """Persist flags to storage"""
        with open(self.config_file, 'w') as f:
            json.dump(self.flags, f, indent=2)

# Global singleton instance
feature_flags = FeatureFlags()
```

```python
# modules/feature-manager/backend/api.py
from flask import Blueprint, jsonify, request
from .feature_flags import feature_flags

api = Blueprint('feature_manager', __name__, url_prefix='/api/features')

@api.route('/', methods=['GET'])
def get_features():
    """GET /api/features - List all features and their states"""
    return jsonify({
        'success': True,
        'features': feature_flags.get_all()
    })

@api.route('/<feature_key>', methods=['GET'])
def get_feature(feature_key):
    """GET /api/features/{key} - Check if feature is enabled"""
    return jsonify({
        'success': True,
        'feature': feature_key,
        'enabled': feature_flags.is_enabled(feature_key)
    })

@api.route('/<feature_key>/toggle', methods=['POST'])
def toggle_feature(feature_key):
    """POST /api/features/{key}/toggle - Toggle feature on/off"""
    new_state = feature_flags.toggle(feature_key)
    return jsonify({
        'success': True,
        'feature': feature_key,
        'enabled': new_state
    })

@api.route('/<feature_key>/enable', methods=['POST'])
def enable_feature(feature_key):
    """POST /api/features/{key}/enable - Enable feature"""
    success = feature_flags.enable(feature_key)
    return jsonify({
        'success': success,
        'feature': feature_key,
        'enabled': True
    })

@api.route('/<feature_key>/disable', methods=['POST'])
def disable_feature(feature_key):
    """POST /api/features/{key}/disable - Disable feature"""
    success = feature_flags.disable(feature_key)
    return jsonify({
        'success': success,
        'feature': feature_key,
        'enabled': False
    })
```

### Frontend: Application Configurator

```xml
<!-- modules/feature-manager/frontend/Configurator.view.xml -->
<mvc:View
    controllerName="modules.feature-manager.controller.Configurator"
    xmlns:mvc="sap.ui.core.mvc"
    xmlns="sap.m"
    xmlns:l="sap.ui.layout"
    xmlns:f="sap.ui.layout.form">
    
    <Page
        title="Application Configuration"
        showNavButton="true"
        navButtonPress="onNavBack">
        
        <content>
            <!-- Module Categories -->
            <IconTabBar
                id="categoryTabs"
                select="onCategorySelect"
                class="sapUiResponsiveContentPadding">
                
                <items>
                    <IconTabFilter
                        key="all"
                        text="All Modules"
                        count="{/totalCount}"/>
                    
                    <IconTabFilter
                        key="development"
                        text="Development Tools"
                        icon="sap-icon://developer-settings"
                        count="{/devCount}"/>
                    
                    <IconTabFilter
                        key="data"
                        text="Data Management"
                        icon="sap-icon://database"
                        count="{/dataCount}"/>
                    
                    <IconTabFilter
                        key="system"
                        text="System"
                        icon="sap-icon://settings"
                        count="{/systemCount}"/>
                    
                    <IconTabFilter
                        key="config"
                        text="Configuration"
                        icon="sap-icon://action-settings"
                        count="{/configCount}"/>
                </items>
                
                <content>
                    <!-- Module List -->
                    <List
                        id="moduleList"
                        mode="None"
                        items="{
                            path: '/features',
                            sorter: {
                                path: 'name'
                            }
                        }">
                        
                        <CustomListItem>
                            <HBox
                                justifyContent="SpaceBetween"
                                alignItems="Center"
                                class="sapUiSmallMargin">
                                
                                <!-- Module Info -->
                                <VBox class="sapUiSmallMarginEnd">
                                    <Title text="{name}" level="H4"/>
                                    <Text text="{description}" class="sapUiTinyMarginTop"/>
                                    <HBox class="sapUiTinyMarginTop">
                                        <ObjectStatus
                                            text="{category}"
                                            state="Information"
                                            class="sapUiTinyMarginEnd"/>
                                        <ObjectStatus
                                            text="{= ${requiresHana} ? 'Requires HANA' : 'Standalone' }"
                                            state="{= ${requiresHana} ? 'Warning' : 'Success' }"
                                            visible="{requiresHana}"/>
                                    </HBox>
                                </VBox>
                                
                                <!-- Toggle Switch (Fiori Best Practice) -->
                                <Switch
                                    state="{enabled}"
                                    customTextOn="ON"
                                    customTextOff="OFF"
                                    change="onFeatureToggle"
                                    tooltip="{= ${enabled} ? 'Disable this module' : 'Enable this module' }"/>
                            </HBox>
                        </CustomListItem>
                    </List>
                </content>
            </IconTabBar>
            
            <!-- Actions -->
            <Toolbar class="sapUiMediumMarginTop">
                <ToolbarSpacer/>
                <Button
                    text="Reset to Defaults"
                    icon="sap-icon://undo"
                    press="onResetDefaults"
                    type="Emphasized"/>
                <Button
                    text="Export Configuration"
                    icon="sap-icon://download"
                    press="onExportConfig"/>
                <Button
                    text="Import Configuration"
                    icon="sap-icon://upload"
                    press="onImportConfig"/>
            </Toolbar>
        </content>
        
        <footer>
            <OverflowToolbar>
                <ToolbarSpacer/>
                <Button
                    text="Close"
                    press="onClose"/>
            </OverflowToolbar>
        </footer>
    </Page>
</mvc:View>
```

```javascript
// modules/feature-manager/frontend/Configurator.controller.js
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast",
    "sap/m/MessageBox"
], function(Controller, JSONModel, MessageToast, MessageBox) {
    "use strict";

    return Controller.extend("modules.feature-manager.controller.Configurator", {
        
        onInit: function() {
            this._loadFeatures();
        },
        
        async _loadFeatures() {
            try {
                const response = await fetch('/api/features');
                const data = await response.json();
                
                if (data.success) {
                    // Transform features object to array for binding
                    const featuresArray = Object.entries(data.features).map(([key, feature]) => ({
                        key: key,
                        ...feature
                    }));
                    
                    // Set model
                    const model = new JSONModel({
                        features: featuresArray,
                        totalCount: featuresArray.length,
                        devCount: featuresArray.filter(f => f.category === 'Development Tools').length,
                        dataCount: featuresArray.filter(f => f.category === 'Data Management').length,
                        systemCount: featuresArray.filter(f => f.category === 'System').length,
                        configCount: featuresArray.filter(f => f.category === 'Configuration').length
                    });
                    
                    this.getView().setModel(model);
                } else {
                    MessageBox.error('Failed to load feature configuration');
                }
            } catch (error) {
                MessageBox.error('Error loading features: ' + error.message);
            }
        },
        
        async onFeatureToggle(oEvent) {
            const switchControl = oEvent.getSource();
            const context = switchControl.getBindingContext();
            const feature = context.getObject();
            const newState = oEvent.getParameter('state');
            
            try {
                // Call API to toggle feature
                const response = await fetch(`/api/features/${feature.key}/toggle`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    MessageToast.show(
                        `${feature.name} ${data.enabled ? 'enabled' : 'disabled'}`
                    );
                    
                    // Notify shell to reload if needed
                    this._notifyFeatureChange(feature.key, data.enabled);
                } else {
                    // Revert switch state
                    switchControl.setState(!newState);
                    MessageBox.error('Failed to toggle feature');
                }
            } catch (error) {
                // Revert switch state
                switchControl.setState(!newState);
                MessageBox.error('Error: ' + error.message);
            }
        },
        
        onCategorySelect(oEvent) {
            const key = oEvent.getParameter('key');
            const list = this.byId('moduleList');
            const binding = list.getBinding('items');
            
            if (key === 'all') {
                binding.filter([]);
            } else {
                const categoryMap = {
                    'development': 'Development Tools',
                    'data': 'Data Management',
                    'system': 'System',
                    'config': 'Configuration'
                };
                binding.filter([
                    new sap.ui.model.Filter('category', 'EQ', categoryMap[key])
                ]);
            }
        },
        
        onResetDefaults() {
            MessageBox.confirm(
                'Reset all features to default settings?',
                {
                    onClose: async (action) => {
                        if (action === MessageBox.Action.OK) {
                            await this._resetToDefaults();
                        }
                    }
                }
            );
        },
        
        async _resetToDefaults() {
            try {
                const response = await fetch('/api/features/reset', {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    MessageToast.show('Configuration reset to defaults');
                    this._loadFeatures(); // Reload
                }
            } catch (error) {
                MessageBox.error('Error resetting: ' + error.message);
            }
        },
        
        onExportConfig() {
            // Export current configuration as JSON
            const model = this.getView().getModel();
            const config = model.getData();
            
            const blob = new Blob([JSON.stringify(config, null, 2)], {
                type: 'application/json'
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'feature-config.json';
            a.click();
            URL.revokeObjectURL(url);
            
            MessageToast.show('Configuration exported');
        },
        
        onImportConfig() {
            // Create file input
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            
            input.onchange = (e) => {
                const file = e.target.files[0];
                const reader = new FileReader();
                
                reader.onload = async (event) => {
                    try {
                        const config = JSON.parse(event.target.result);
                        await this._importConfiguration(config);
                    } catch (error) {
                        MessageBox.error('Invalid configuration file');
                    }
                };
                
                reader.readAsText(file);
            };
            
            input.click();
        },
        
        async _importConfiguration(config) {
            try {
                const response = await fetch('/api/features/import', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });
                const data = await response.json();
                
                if (data.success) {
                    MessageToast.show('Configuration imported successfully');
                    this._loadFeatures();
                } else {
                    MessageBox.error('Failed to import configuration');
                }
            } catch (error) {
                MessageBox.error('Error importing: ' + error.message);
            }
        },
        
        _notifyFeatureChange(featureKey, enabled) {
            // Emit event for shell to handle
            const eventBus = sap.ui.getCore().getEventBus();
            eventBus.publish("app", "featureToggled", {
                feature: featureKey,
                enabled: enabled
            });
        },
        
        onNavBack() {
            window.history.back();
        },
        
        onClose() {
            // Close dialog or navigate back
            this.onNavBack();
        }
    });
});
```

### Integration with Shell/Main App

```javascript
// core/frontend/Shell.controller.js
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel"
], function(Controller, JSONModel) {
    "use strict";

    return Controller.extend("core.controller.Shell", {
        
        onInit: function() {
            this._loadFeatureStates();
            
            // Listen for feature toggle events
            const eventBus = sap.ui.getCore().getEventBus();
            eventBus.subscribe("app", "featureToggled", this._onFeatureToggled, this);
        },
        
        async _loadFeatureStates() {
            try {
                const response = await fetch('/api/features');
                const data = await response.json();
                
                if (data.success) {
                    const model = new JSONModel(data.features);
                    this.getView().setModel(model, "features");
                    
                    // Show/hide navigation items based on feature flags
                    this._updateNavigation(data.features);
                }
            } catch (error) {
                console.error('Error loading features:', error);
            }
        },
        
        _updateNavigation(features) {
            // Show/hide navigation items based on enabled features
            const navList = this.byId("navigationList");
            
            navList.getItems().forEach(item => {
                const featureKey = item.data("feature");
                if (featureKey && features[featureKey]) {
                    item.setVisible(features[featureKey].enabled);
                }
            });
        },
        
        _onFeatureToggled(channel, event, data) {
            // Reload navigation when feature toggled
            this._loadFeatureStates();
            
            // Show notification
            sap.m.MessageToast.show(
                `${data.feature} ${data.enabled ? 'enabled' : 'disabled'} - Please refresh to see changes`
            );
        },
        
        onOpenConfigurator() {
            // Open configurator dialog
            if (!this._configuratorDialog) {
                this._configuratorDialog = sap.ui.xmlfragment(
                    "modules.feature-manager.view.Configurator",
                    this
                );
                this.getView().addDependent(this._configuratorDialog);
            }
            this._configuratorDialog.open();
        }
    });
});
```

### Shell Navigation with Feature Flags

```xml
<!-- core/frontend/Shell.view.xml -->
<mvc:View
    controllerName="core.controller.Shell"
    xmlns:mvc="sap.ui.core.mvc"
    xmlns="sap.m"
    xmlns:f="sap.f">
    
    <f:ShellBar
        title="P2P Data Products"
        homeIcon="sap-icon://home"
        showCopilot="false"
        showSearch="false"
        showNotifications="false"
        showProductSwitcher="false">
        
        <f:profile>
            <Avatar
                initials="DB"
                displaySize="XS"
                press="onUserMenuPress"/>
        </f:profile>
        
        <f:additionalContent>
            <!-- Settings/Configurator Button -->
            <Button
                icon="sap-icon://action-settings"
                tooltip="Application Configuration"
                press="onOpenConfigurator"
                type="Transparent"/>
        </f:additionalContent>
    </f:ShellBar>
    
    <Page showHeader="false">
        <content>
            <SplitApp id="splitApp">
                <masterPages>
                    <!-- Navigation Menu -->
                    <Page title="Modules">
                        <List
                            id="navigationList"
                            mode="SingleSelectMaster"
                            selectionChange="onNavigate">
                            
                            <!-- Data Products Module -->
                            <StandardListItem
                                title="Data Products"
                                icon="sap-icon://database"
                                type="Navigation"
                                data:feature="data-products-viewer"
                                visible="{features>/data-products-viewer/enabled}"/>
                            
                            <!-- SQL Console Module -->
                            <StandardListItem
                                title="SQL Console"
                                icon="sap-icon://syntax"
                                type="Navigation"
                                data:feature="sql-execution"
                                visible="{features>/sql-execution/enabled}"/>
                            
                            <!-- CSN Validation Module -->
                            <StandardListItem
                                title="CSN Validation"
                                icon="sap-icon://validate"
                                type="Navigation"
                                data:feature="csn-validation"
                                visible="{features>/csn-validation/enabled}"/>
                            
                            <!-- HANA Connection Module -->
                            <StandardListItem
                                title="HANA Connections"
                                icon="sap-icon://connected"
                                type="Navigation"
                                data:feature="hana-connection"
                                visible="{features>/hana-connection/enabled}"/>
                            
                            <!-- Settings (Always Visible) -->
                            <StandardListItem
                                title="Settings"
                                icon="sap-icon://action-settings"
                                type="Navigation"
                                press="onOpenConfigurator"/>
                        </List>
                    </Page>
                </masterPages>
                
                <detailPages>
                    <!-- Dynamic content loaded based on selection -->
                    <Page id="detailPage" title="Select a module">
                        <content>
                            <mvc:XMLView id="moduleContent"/>
                        </content>
                    </Page>
                </detailPages>
            </SplitApp>
        </content>
    </Page>
</mvc:View>
```

---

## 📚 Module-Based Documentation Structure

```
docs/
├── README.md                          # Documentation index
│
├── architecture/                      # Architecture docs
│   ├── MODULAR_ARCHITECTURE.md       # This document
│   ├── FEATURE_TOGGLE_DESIGN.md      # Feature flag system
│   └── MODULE_DEVELOPMENT_GUIDE.md   # How to create modules
│
├── modules/                           # Per-module documentation
│   │
│   ├── feature-manager/
│   │   ├── README.md                 # Module overview
│   │   ├── API_REFERENCE.md          # Backend API docs
│   │   ├── UI_GUIDE.md               # Frontend usage
│   │   └── DEVELOPER_GUIDE.md        # Development guide
│   │
│   ├── csn-validation/
│   │   ├── README.md                 # CSN validation overview
│   │   ├── API_REFERENCE.md          # Backend API
│   │   ├── CLI_REFERENCE.md          # CLI commands
│   │   ├── UI_GUIDE.md               # Frontend UI
│   │   ├── ADDING_CONNECTORS.md      # Extend with new sources
│   │   └── DEVELOPER_GUIDE.md        # Development guide
│   │
│   ├── data-products-viewer/
│   │   ├── README.md
│   │   ├── API_REFERENCE.md
│   │   ├── UI_GUIDE.md
│   │   └── DEVELOPER_GUIDE.md
│   │
│   ├── sql-execution/
│   │   ├── README.md
│   │   └── ...
│   │
│   └── [other modules]/
│
├── guides/                            # Cross-cutting guides
│   ├── GETTING_STARTED.md            # New user onboarding
│   ├── DEVELOPER_ONBOARDING.md       # Developer setup
│   ├── DEPLOYMENT_GUIDE.md           # Production deployment
│   └── TROUBLESHOOTING.md            # Common issues
│
├── api/                               # Global API documentation
│   ├── REST_API_OVERVIEW.md          # All endpoints
│   └── AUTHENTICATION.md             # Auth/security
│
└── reference/                         # Reference materials
    ├── HANA_CLOUD_SETUP.md
    ├── SAP_FIORI_GUIDELINES.md
    └── GIT_WORKFLOW.md
```

### Documentation Index (docs/README.md)

```markdown
# P2P Data Products - Documentation Index

## 🚀 Quick Start

**New User?** Start here:
1. [Getting Started Guide](guides/GETTING_STARTED.md)
2. [Application Overview](../README.md)

**Developer?** Start here:
1. [Developer Onboarding](guides/DEVELOPER_ONBOARDING.md)
2. [Module Development Guide](architecture/MODULE_DEVELOPMENT_GUIDE.md)

## 📦 Module Documentation

### Core System
- [Feature Manager](modules/feature-manager/README.md) - Feature toggle system ⭐

### Development Tools
- [CSN Validation](modules/csn-validation/README.md) - Validate CSN against sources
- [SQL Execution](modules/sql-execution/README.md) - SQL console and query tools
- [HANA Connection Manager](modules/hana-connection/README.md) - Manage connections

### Data Management
- [Data Products Viewer](modules/data-products-viewer/README.md) - Browse data products
- [SQLite Fallback](modules/sqlite-fallback/README.md) - Demo mode with sample data

## 🏗️ Architecture

- [Modular Architecture](architecture/MODULAR_ARCHITECTURE.md) - Overall design
- [Feature Toggle Design](architecture/FEATURE_TOGGLE_DESIGN.md) - Feature flags
- [Module Development Guide](architecture/MODULE_DEVELOPMENT_GUIDE.md) - Creating modules

## 📖 User Guides

- [Getting Started](guides/GETTING_STARTED.md)
- [Using the Configurator](modules/feature-manager/UI_GUIDE.md)
- [Troubleshooting](guides/TROUBLESHOOTING.md)

## 🔧 API Documentation

- [REST API Overview](api/REST_API_OVERVIEW.md)
- [Feature Manager API](modules/feature-manager/API_REFERENCE.md)
- [CSN Validation API](modules/csn-validation/API_REFERENCE.md)
- [Data Products API](modules/data-products-viewer/API_REFERENCE.md)

## 📚 Reference

- [HANA Cloud Setup](reference/HANA_CLOUD_SETUP.md)
- [SAP Fiori Guidelines](reference/SAP_FIORI_GUIDELINES.md)
- [Git Workflow](reference/GIT_WORKFLOW.md)
```

---

## 🎨 SAP Fiori Best Practices for Settings

### Control Selection: Switch vs Checkbox

**Fiori Recommendation**: Use `sap.m.Switch` for feature toggles ✅

**Why Switch over Checkbox:**
1. ✅ More intuitive for on/off states
2. ✅ Clearer visual feedback
3. ✅ Better for mobile touch interfaces
4. ✅ SAP Fiori design pattern for settings
5. ✅ Shows both states explicitly (ON/OFF labels)

**When to Use Checkbox:**
- Multiple independent selections
- Form data entry
- List item selection

**When to Use Switch:**
- ✅ Feature enable/disable (our use case)
- ✅ Settings toggles
- ✅ Boolean preferences
- ✅ System configuration

### Layout Best Practices

```xml
<!-- Fiori-Compliant Settings List -->
<List>
    <CustomListItem>
        <HBox justifyContent="SpaceBetween" alignItems="Center">
            <VBox>
                <Title text="Feature Name"/>
                <Text text="Feature description"/>
                <ObjectStatus text="Category" state="Information"/>
            </VBox>
            <Switch state="{enabled}" change="onToggle"/>
        </HBox>
    </CustomListItem>
</List>
```

**Spacing:**
- Use `sapUiSmallMargin` between list items
- Use `sapUiTinyMargin` for internal spacing
- Use `HBox` with `justifyContent="SpaceBetween"` for alignment

---

## 🔄 Module Lifecycle Management

### Module Metadata

```json
// modules/[module-name]/module.json
{
  "name": "csn-validation",
  "displayName": "CSN Validation",
  "version": "1.0.0",
  "description": "Validate CSN definitions against data sources",
  "category": "Development Tools",
  "author": "P2P Team",
  "requiresHana": false,
  "dependencies": [
    "feature-manager"  // This module requires feature-manager
  ],
  "backend": {
    "entryPoint": "backend/api.py",
    "routes": "/api/csn-validation/*"
  },
  "frontend": {
    "views": [
      "CSNValidator.view.xml"
    ],
    "navigation": {
      "title": "CSN Validation",
      "icon": "sap-icon://validate",
      "route": "csn-validation"
    }
  },
  "docs": [
    "docs/README.md",
    "docs/API_REFERENCE.md"
  ],
  "enabled": true
}
```

### Module Registry

```python
# core/backend/module_registry.py
import os
import json
from typing import Dict, List

class ModuleRegistry:
    """
    Central registry of all application modules.
    Auto-discovers modules by scanning modules/ directory.
    """
    
    def __init__(self, modules_dir: str = 'modules'):
        self.modules_dir = modules_dir
        self.modules = self._discover_modules()
    
    def _discover_modules(self) -> Dict:
        """Auto-discover all modules with module.json"""
        modules = {}
        
        if not os.path.exists(self.modules_dir):
            return modules
        
        for module_name in os.listdir(self.modules_dir):
            module_path = os.path.join(self.modules_dir, module_name)
            manifest_path = os.path.join(module_path, 'module.json')
            
            if os.path.isdir(module_path) and os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    module_config = json.load(f)
                    modules[module_name] = {
                        'path': module_path,
                        'config': module_config
                    }
        
        return modules
    
    def get_enabled_modules(self, feature_flags) -> List[str]:
        """Get list of enabled modules based on feature flags"""
        enabled = []
        
        for module_name, module_info in self.modules.items():
            if feature_flags.is_enabled(module_name):
                enabled.append(module_name)
        
        return enabled
    
    def get_module_config(self, module_name: str) -> Dict:
        """Get configuration for specific module"""
        return self.modules.get(module_name, {}).get('config', {})
    
    def list_modules(self) -> List[Dict]:
        """List all modules with metadata"""
        return [
            {
                'name': name,
                **info['config']
            }
            for name, info in self.modules.items()
        ]

# Global instance
module_registry = ModuleRegistry()
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1)

**1.1 Feature Manager Module**
- [ ] Create `modules/feature-manager/` structure
- [ ] Implement `FeatureFlags` service (backend)
- [ ] Create REST API endpoints
- [ ] Build Configurator UI (SAP UI5)
- [ ] Write unit tests
- [ ] Document in `docs/modules/feature-manager/`

**1.2 Module Registry System**
- [ ] Create `core/backend/module_registry.py`
- [ ] Define `module.json` schema
- [ ] Implement auto-discovery
- [ ] Create loader utilities

**1.3 Shell Integration**
- [ ] Update `core/frontend/Shell.view.xml`
- [ ] Add configurator button to ShellBar
- [ ] Implement dynamic navigation (show/hide based on flags)
- [ ] Add feature toggle event handling

**Time**: 5 days

### Phase 2: Migrate Existing Features (Week 2-3)

**2.1 CSN Validation Module**
- [ ] Create `modules/csn-validation/` structure
- [ ] Move and refactor code from `backend/validate_csn_against_hana.py`
- [ ] Create module.json
- [ ] Build UI view (validation interface)
- [ ] Write module-specific docs
- [ ] Add to feature flags

**2.2 Data Products Viewer Module**
- [ ] Create `modules/data-products-viewer/` structure
- [ ] Extract existing data products code
- [ ] Create module.json
- [ ] Build standalone UI view
- [ ] Write docs
- [ ] Add to feature flags

**2.3 SQL Execution Module**
- [ ] Create `modules/sql-execution/` structure
- [ ] Extract SQL execution code
- [ ] Create module.json
- [ ] Build SQL console UI
- [ ] Write docs
- [ ] Add to feature flags

**2.4 HANA Connection Module**
- [ ] Create `modules/hana-connection/` structure
- [ ] Extract connection management code
- [ ] Create module.json
- [ ] Build connection manager UI
- [ ] Write docs
- [ ] Add to feature flags

**2.5 SQLite Fallback Module**
- [ ] Create `modules/sqlite-fallback/` structure
- [ ] Implement fallback logic
- [ ] Create module.json
- [ ] Build demo mode UI
- [ ] Write docs
- [ ] Add to feature flags

**Time**: 10 days

### Phase 3: Documentation Reorganization (Week 3)

**3.1 Module Documentation**
- [ ] Create `docs/modules/` structure
- [ ] Move relevant docs to module folders
- [ ] Create module-specific READMEs
- [ ] Write API references
- [ ] Write user guides

**3.2 Architecture Documentation**
- [ ] Create `docs/architecture/` folder
- [ ] Write modular architecture guide
- [ ] Document feature toggle system
- [ ] Create module development guide

**3.3 Consolidated Guides**
- [ ] Update main README.md
- [ ] Create documentation index
- [ ] Write getting started guide
- [ ] Create troubleshooting guide

**Time**: 3 days

### Phase 4: Testing & Refinement (Week 4)

**4.1 Integration Testing**
- [ ] Test module enable/disable flows
- [ ] Test inter-module dependencies
- [ ] Test navigation with feature flags
- [ ] Test configuration import/export

**4.2 UX Polish**
- [ ] Review Fiori compliance
- [ ] Test responsive design
- [ ] Add loading states
- [ ] Improve error messages

**4.3 Performance**
- [ ] Optimize module loading
- [ ] Test with many modules disabled
- [ ] Profile feature flag checks

**Time**: 5 days

---

## 📊 Module Development Template

### Creating a New Module (Checklist)

**Step 1: Create Structure**
```bash
mkdir -p modules/my-module/{backend,frontend,docs,tests}
```

**Step 2: Create module.json**
```json
{
  "name": "my-module",
  "displayName": "My Module",
  "version": "1.0.0",
  "description": "What this module does",
  "category": "Development Tools",
  "requiresHana": false,
  "backend": {
    "entryPoint": "backend/api.py"
  },
  "frontend": {
    "views": ["MyModule.view.xml"]
  },
  "enabled": true
}
```

**Step 3: Implement Backend**
- Create API endpoints
- Implement business logic
- Add to Flask app blueprint

**Step 4: Implement Frontend**
- Create SAP UI5 view
- Create controller
- Add navigation entry

**Step 5: Documentation**
- Write module README
- Document APIs
- Write user guide

**Step 6: Tests**
- Unit tests (backend)
- Unit tests (frontend)
- Integration tests

**Step 7: Register**
- Module auto-discovered via module.json
- Add to default feature flags
- Update documentation index

---

## 🎯 Success Criteria

### Module Compliance Checklist

Each module must have:
- [ ] `module.json` metadata file
- [ ] Backend API implementation
- [ ] Frontend UI (SAP UI5)
- [ ] Module README.md
- [ ] API reference documentation
- [ ] User guide
- [ ] Unit tests (80%+ coverage)
- [ ] Feature flag integration
- [ ] No dependencies on other modules (except feature-manager)

### Application Quality

- [ ] All modules independently toggleable
- [ ] Navigation updates dynamically
- [ ] Configuration persists across sessions
- [ ] Import/export configuration works
- [ ] No console errors when modules disabled
- [ ] Fiori-compliant settings UI
- [ ] Mobile-responsive configurator

---

## 🔧 Technical Implementation Details

### Backend: Dynamic Route Registration

```python
# core/backend/app.py
from flask import Flask
from core.backend.module_registry import module_registry
from modules.feature_manager.backend.feature_flags import feature_flags

app = Flask(__name__)

# Register enabled module routes
def register_module_routes():
    enabled_modules = module_registry.get_enabled_modules(feature_flags)
    
    for module_name in enabled_modules:
        module_config = module_registry.get_module_config(module_name)
        
        if 'backend' in module_config:
            # Dynamically import and register module blueprint
            backend_path = module_config['backend']['entryPoint']
            module_path = f"modules.{module_name}.{backend_path.replace('/', '.').replace('.py', '')}"
            
            try:
                module = __import__(module_path, fromlist=['api'])
                app.register_blueprint(module.api)
                print(f"✅ Registered module: {module_name}")
            except Exception as e:
                print(f"⚠️  Failed to load module {module_name}: {e}")

register_module_routes()
```

### Frontend: Dynamic View Loading

```javascript
// core/frontend/Shell.controller.js
onNavigate: function(oEvent) {
    const item = oEvent.getParameter('listItem');
    const featureKey = item.data('feature');
    
    // Check if feature is enabled
    const featureModel = this.getView().getModel('features');
    const feature = featureModel.getProperty(`/${featureKey}`);
    
    if (!feature || !feature.enabled) {
        sap.m.MessageToast.show('This feature is currently disabled');
        return;
    }
    
    // Load module view
    const moduleConfig = this._getModuleConfig(featureKey);
    if (moduleConfig && moduleConfig.frontend) {
        const viewName = moduleConfig.frontend.views[0];
        this._loadModuleView(viewName);
    }
}
```

---

## 📖 Documentation Templates

### Module README Template

```markdown
# [Module Name]

**Version**: 1.0.0  
**Category**: [Category]  
**Status**: ✅ Active

## Overview

Brief description of what this module does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Quick Start

### Enable Module
1. Open Application Configurator (⚙️ icon in top right)
2. Find "[Module Name]" in the list
3. Toggle switch to ON

### Using the Module
[Usage instructions]

## Documentation

- [API Reference](API_REFERENCE.md) - Backend API endpoints
- [UI Guide](UI_GUIDE.md) - Frontend usage
- [Developer Guide](DEVELOPER_GUIDE.md) - Extending this module

## Dependencies

- Requires: [list dependencies]
- Optional: [list optional dependencies]

## Configuration

[Configuration options]

## Troubleshooting

[Common issues and solutions]
```

---

## 🎓 Benefits of This Architecture

### For Users
- ✅ **Customizable experience** - Enable only needed features
- ✅ **Faster load times** - Disabled modules don't load
- ✅ **Less clutter** - Hide unused capabilities
- ✅ **Easy discovery** - Configurator shows all available features

### For Developers
- ✅ **Clear boundaries** - Each module is self-contained
- ✅ **Parallel development** - Teams can work on different modules
- ✅ **Easier testing** - Test modules in isolation
- ✅ **Safer changes** - Changes to one module don't affect others

### For Operations
- ✅ **Selective deployment** - Deploy only needed modules
- ✅ **Feature flags** - Enable/disable without code changes
- ✅ **A/B testing** - Test features with subset of users
- ✅ **Gradual rollout** - Enable features incrementally

---

## 📝 Next Steps for Implementation

### Immediate Actions Needed

1. **Review & Approve This Plan**
   - Architecture approach
   - Module structure
   - Feature toggle design
   - Documentation structure
   - Timeline (4 weeks)

2. **Start Phase 1** (If Approved)
   - Create feature-manager module (Week 1)
   - Implement backend feature flags
   - Build configurator UI
   - Test toggle functionality

3. **Plan Phase 2** Details
   - Prioritize which modules to migrate first
   - Identify module boundaries
   - Plan data migration if needed

### Questions for You

1. **Priority order** - Which module to migrate first?
   - Option A: CSN Validation (newest, clearest boundaries)
   - Option B: Data Products Viewer (most used)
   - Option C: Feature Manager first, then others

2. **Timeline flexibility** - 4 weeks realistic? Or faster/slower?

3. **Documentation depth** - How detailed should module docs be?

4. **Testing requirements** - What test coverage % is acceptable?

**Status**: ✅ COMPREHENSIVE PLAN READY - Awaiting your review and decisions