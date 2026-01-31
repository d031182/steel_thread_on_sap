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
import { createAPIPlaygroundPageSimple, initializeAPIPlaygroundSimple } from './pages/apiPlaygroundPageSimple.js';
import { createKnowledgeGraphPage, initializeKnowledgeGraph } from './pages/knowledgeGraphPage.js';

/**UI5 
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
    
    // Load current user and update ShellBar
    await loadCurrentUser();
    
    console.log('✓ Application initialized successfully');
}

/**
 * Load current user from login manager and update ShellBar
 */
async function loadCurrentUser() {
    try {
        const response = await fetch('/api/login-manager/current-user');
        const data = await response.json();
        
        if (data && data.success && data.user) {
            const user = data.user;
            const shellBar = sap.ui.getCore().byId("appShellBar");
            
            if (shellBar) {
                // Update avatar initials only (no secondTitle)
                const avatar = shellBar.getProfile();
                if (avatar && user.username) {
                    const initials = user.username.substring(0, 2).toUpperCase();
                    avatar.setInitials(initials);
                    
                    // Set tooltip for avatar to show full user info
                    avatar.setTooltip(`${user.username} (${user.role})`);
                }
                
                console.log('✓ Logged in as:', user.username, `(${user.role})`);
            }
        }
    } catch (error) {
        console.error('Error loading current user:', error);
    }
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
                    // SAP Fiori ShellBar with logo (non-clickable)
                    new sap.f.ShellBar({
                        id: "appShellBar",
                        title: "Procure to Pay",
                        homeIcon: "images/sap-logo.png",
                        showNavButton: false,
                        showCopilot: false,
                        showSearch: false,
                        showNotifications: false,
                        showProductSwitcher: false,
                        profile: new sap.f.Avatar({
                            initials: "UI"
                        }),
                        additionalContent: [
                            new sap.m.Button({
                                icon: "sap-icon://notes",
                                tooltip: "Logging",
                                press: function() {
                                    openLoggingDialog();
                                }
                            }),
                            new sap.m.Button({
                                icon: "sap-icon://action-settings",
                                tooltip: "Settings",
                                press: function() {
                                    openSettingsDialog();
                                }
                            })
                        ]
                        // No homeIconPressed event = logo not clickable
                    }),
                    
                    // Page navigation tabs with standard TabContainer (Fiori compliant)
                    new sap.m.IconTabBar({
                        id: "mainTabBar",
                        upperCase: false,
                        headerMode: "Inline",
                        headerBackgroundDesign: "Transparent",
                        backgroundDesign: "Transparent",
                        select: function(oEvent) {
                            switchPage(oEvent.getParameter("key"));
                        },
                        items: [
                            new sap.m.IconTabFilter({
                                key: "dataProducts",
                                icon: "sap-icon://database",
                                text: "Data Products",
                                design: "Horizontal"
                            }),
                            new sap.m.IconTabFilter({
                                key: "knowledgeGraph",
                                icon: "sap-icon://org-chart",
                                text: "Knowledge Graph",
                                design: "Horizontal"
                            }),
                            new sap.m.IconTabFilter({
                                key: "apiPlayground",
                                icon: "sap-icon://employee-lookup",
                                text: "API Playground",
                                design: "Horizontal"
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
 * Create Data Products page content with two-column layout
 */
function createDataProductsPageContent() {
    // Left panel: Data source configuration (fixed width)
    const sourcePanel = new sap.m.VBox({
        width: "320px",
        items: [
            new sap.m.Title({
                text: "Data Source",
                level: "H3"
            }),
            
            // Source selection
            new sap.m.VBox({
                items: [
                    new sap.m.Label({ text: "Active Source:" }).addStyleClass("sapUiTinyMarginTop"),
                    new sap.m.Select({
                        id: "dataSourceSelect",
                        selectedKey: localStorage.getItem('selectedDataSource') || 'sqlite',
                        width: "100%",
                        items: [
                            new sap.ui.core.Item({ key: "sqlite", text: "Local SQLite" }),
                            new sap.ui.core.Item({ key: "hana", text: "HANA Cloud" })
                        ],
                        change: function(oEvent) {
                            const newSource = oEvent.getParameter("selectedItem").getKey();
                            localStorage.setItem('selectedDataSource', newSource);
                            loadDataProducts();
                        }
                    })
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            
            // Quick actions
            new sap.m.VBox({
                items: [
                    new sap.m.Label({ text: "Quick Actions:" }).addStyleClass("sapUiSmallMarginTop"),
                    new sap.m.Button({
                        text: "Refresh Data",
                        icon: "sap-icon://refresh",
                        type: "Emphasized",
                        width: "100%",
                        press: function() {
                            loadDataProducts();
                        }
                    }).addStyleClass("sapUiTinyMarginTop"),
                    new sap.m.Button({
                        text: "Manage Connections",
                        icon: "sap-icon://database",
                        width: "100%",
                        press: function() {
                            openConnectionsDialog();
                        }
                    }).addStyleClass("sapUiTinyMarginTop")
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            
            // Connection status
            new sap.m.Panel({
                headerText: "Connection Status",
                expandable: true,
                expanded: true,
                content: [
                    new sap.m.VBox({
                        items: [
                            new sap.m.HBox({
                                justifyContent: "SpaceBetween",
                                items: [
                                    new sap.m.Label({ text: "SQLite:" }),
                                    new sap.m.ObjectStatus({
                                        id: "sqliteStatus",
                                        text: "Ready",
                                        state: "Success"
                                    })
                                ]
                            }),
                            new sap.m.HBox({
                                justifyContent: "SpaceBetween",
                                items: [
                                    new sap.m.Label({ text: "HANA Cloud:" }),
                                    new sap.m.ObjectStatus({
                                        id: "hanaStatus",
                                        text: "Not Connected",
                                        state: "None"
                                    })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop")
                        ]
                    }).addStyleClass("sapUiSmallMargin")
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            
            // Stats
            new sap.m.Panel({
                headerText: "Statistics",
                expandable: true,
                expanded: false,
                content: [
                    new sap.m.VBox({
                        items: [
                            new sap.m.HBox({
                                justifyContent: "SpaceBetween",
                                items: [
                                    new sap.m.Label({ text: "Data Products:" }),
                                    new sap.m.Text({ id: "productCount", text: "0" })
                                ]
                            }),
                            new sap.m.HBox({
                                justifyContent: "SpaceBetween",
                                items: [
                                    new sap.m.Label({ text: "Total Tables:" }),
                                    new sap.m.Text({ id: "tableCount", text: "0" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop")
                        ]
                    }).addStyleClass("sapUiSmallMargin")
                ]
            }).addStyleClass("sapUiSmallMarginTop")
        ]
    }).addStyleClass("sapUiContentPadding");
    
    // Right panel: Data product tiles (flexible width)
    const tilesPanel = new sap.m.VBox({
        items: [
            new sap.m.Title({
                text: "Data Products",
                level: "H3"
            }),
            new sap.m.Text({
                id: "loadingStatus",
                text: "Loading data products..."
            }).addStyleClass("sapUiTinyMarginTop"),
            new sap.m.FlexBox({
                id: "tilesContainer",
                wrap: "Wrap",
                justifyContent: "Start",
                alignItems: "Start"
            }).addStyleClass("sapUiSmallMarginTop")
        ]
    }).addStyleClass("sapUiContentPadding");
    
    // Two-column layout: Source config left (fixed), Tiles right (flexible)
    return new sap.m.HBox({
        id: "dataProductsPageContent",
        items: [
            sourcePanel,
            new sap.m.VBox({ width: "1rem" }), // Spacer
            tilesPanel
        ]
    });
}

/**
 * Switch between pages
 * @param {string} pageKey - 'dataProducts' or 'apiPlayground'
 */
async function switchPage(pageKey) {
    try {
        const oMainContent = sap.ui.getCore().byId("mainContent");
        if (!oMainContent) {
            console.error('mainContent not found');
            return;
        }
        
        console.log(`Switching to page: ${pageKey}`);
        
        // Clear current content
        oMainContent.destroyItems();
        
        // Load selected page
        if (pageKey === "dataProducts") {
            oMainContent.addItem(createDataProductsPageContent());
            // Reload data if needed
            await initializeDataProducts();
        } else if (pageKey === "knowledgeGraph") {
            console.log('Loading Knowledge Graph...');
            oMainContent.addItem(createKnowledgeGraphPage());
            await initializeKnowledgeGraph();
        } else if (pageKey === "apiPlayground") {
            console.log('Loading API Playground (Simple)...');
            // Use simple vanilla JS version (no iframe)
            oMainContent.addItem(createAPIPlaygroundPageSimple());
            await initializeAPIPlaygroundSimple();
        }
    } catch (error) {
        console.error('Error switching page:', error);
        sap.m.MessageBox.error('Error loading page: ' + error.message);
    }
}

