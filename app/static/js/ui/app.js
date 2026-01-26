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

/**
 * Initialize the application
 */
export async function initializeApp() {
    console.log('🚀 Initializing P2P Data Products Application...');
    
    // Load feature flags
    const features = await loadFeatureFlags();
    
    // Create main application UI
    const oApp = createAppShell();
    
    // Initialize data products page
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
                    
                    // Main content area (managed by dataProductsPage)
                    new sap.m.VBox({
                        id: "mainContent",
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
                    }).addStyleClass("sapUiContentPadding sapUiLargeMarginTop")
                ]
            })
        ]
    });
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
                    loadDataProducts();
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