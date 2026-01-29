/**
 * Main Application Module
 * 
 * Initializes the P2P Data Products application following modular architecture.
 * This file bootstraps the app and coordinates between different page modules.
 * 
 * @author P2P Development Team
 * @version 2.0.0
 */

import { openLoggingDialog } from './pages/loggingPage.js';
import { openSettingsDialog } from './pages/settingsPage.js';
import { openConnectionsDialog } from './pages/connectionsPage.js';
import { initializeDataProducts, loadDataProducts } from './pages/dataProductsPage.js';
import { createAPIPlaygroundPage, initializeAPIPlayground } from './pages/apiPlaygroundPage.js';

/**
 * Initialize the application
 */
export async function initializeApp() {
    console.log('🚀 Initializing P2P Data Products Application...');
    
    // Load feature flags
    const features = await loadFeatureFlags();
    
    // Create main application UI
    const oApp = createAppShell();
    
    // Initialize data products page (default)
    await initializeDataProducts();
    
    // Render application
    oApp.placeAt("content");
    
    console.log('✓ Application initialized successfully');
}

/**
 * Load feature flags from API
 */
async function loadFeatureFlags() {
    try {
        const response = await fetch("/api/features");
        const data = await response.json();
        if (data && data.success) {
            return data.features.features || data.features;
        }
    } catch (error) {
        console.warn("Could not load feature flags:", error);
    }
    return {};
}

/**
 * Create main application shell with SAP Fiori components
 */
function createAppShell() {
    return new sap.m.App({
        pages: [
            new sap.m.Page({
                showHeader: false,
                content: [
                    // SAP Fiori ShellBar
                    new sap.f.ShellBar({
                        title: "Procure to Pay",
                        showNavButton: false,
                        showCopilot: false,
                        showSearch: false,
                        showNotifications: false,
                        profile: new sap.f.Avatar({
                            initials: "UI"
                        })
                    }),
                    
                    // Toolbar with action buttons
                    createToolbar(),
                    
                    // Page navigation tabs
                    new sap.m.IconTabBar({
                        id: "mainTabBar",
                        select: function(oEvent) {
                            switchPage(oEvent.getParameter("key"));
                        },
                        items: [
                            new sap.m.IconTabFilter({
                                key: "dataProducts",
                                text: "Data Products",
                                icon: "sap-icon://database"
                            }),
                            new sap.m.IconTabFilter({
                                key: "apiPlayground",
                                text: "API Playground",
                                icon: "sap-icon://employee-lookup"
                            })
                        ],
                        selectedKey: "dataProducts"
                    }).addStyleClass("sapUiSmallMarginTop"),
                    
                    // Main content area (dynamically switched)
                    new sap.m.VBox({
                        id: "mainContent",
                        items: [
                            // Data Products page (default)
                            createDataProductsPageContent()
                        ]
                    }).addStyleClass("sapUiLargeMarginTop")
                ]
            })
        ]
    });
}

/**
 * Create Data Products page content
 */
function createDataProductsPageContent() {
    return new sap.m.VBox({
        id: "dataProductsPageContent",
        items: [
            new sap.m.Title({
                text: "Data Products",
                level: "H2"
            }),
            new sap.m.Text({
                id: "loadingStatus",
                text: "Click 'Load Data' button above to view data products"
            }).addStyleClass("sapUiSmallMarginTop"),
            new sap.m.FlexBox({
                id: "tilesContainer",
                wrap: "Wrap",
                justifyContent: "Start",
                alignItems: "Start"
            }).addStyleClass("sapUiSmallMarginTop")
        ]
    }).addStyleClass("sapUiContentPadding");
}

/**
 * Switch between pages
 * @param {string} pageKey - 'dataProducts' or 'apiPlayground'
 */
async function switchPage(pageKey) {
    const oMainContent = sap.ui.getCore().byId("mainContent");
    if (!oMainContent) return;
    
    console.log(`Switching to page: ${pageKey}`);
    
    // Clear current content
    oMainContent.destroyItems();
    
    // Load selected page
    if (pageKey === "dataProducts") {
        oMainContent.addItem(createDataProductsPageContent());
        // Reload data if needed
        await initializeDataProducts();
    } else if (pageKey === "apiPlayground") {
        oMainContent.addItem(createAPIPlaygroundPage());
        // Initialize API Playground
        await initializeAPIPlayground();
    }
}

/**
 * Create toolbar with navigation buttons
 */
function createToolbar() {
    return new sap.m.Toolbar({
        content: [
            new sap.m.ToolbarSpacer(),
            new sap.m.Button({
                icon: "sap-icon://refresh",
                text: "Load Data",
                press: function() {
                    // Check which page is active
                    const oTabBar = sap.ui.getCore().byId("mainTabBar");
                    if (oTabBar && oTabBar.getSelectedKey() === "dataProducts") {
                        loadDataProducts();
                    } else if (oTabBar && oTabBar.getSelectedKey() === "apiPlayground") {
                        initializeAPIPlayground();
                    }
                }
            }),
            new sap.m.Button({
                icon: "sap-icon://database",
                text: "Data Sources",
                press: function() {
                    openConnectionsDialog();
                }
            }),
            new sap.m.Button({
                icon: "sap-icon://notes",
                text: "Logging",
                press: function() {
                    openLoggingDialog();
                }
            }),
            new sap.m.Button({
                icon: "sap-icon://action-settings",
                text: "Settings",
                press: function() {
                    openSettingsDialog();
                }
            })
        ]
    });
}
