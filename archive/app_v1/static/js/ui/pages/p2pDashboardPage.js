/**
 * P2P Dashboard Page Module
 * 
 * Displays comprehensive P2P KPIs with interactive visualizations:
 * - Purchase Orders (PO metrics, late tracking, processing time)
 * - Suppliers (active count, top spend, on-time delivery)
 * - Invoices (accuracy rates, pending invoices, processing time)
 * - Financial Health (cash in POs, spend by category, payment terms)
 * - Service Entry Sheets (volume, pending approvals, approval time)
 * 
 * Features:
 * - Real-time KPI updates
 * - Period filtering (last 7/30/90 days, YTD)
 * - Trend visualizations with Chart.js
 * - Drill-down into recent transactions
 * 
 * @author P2P Development Team
 * @version 1.0.0
 * @date 2026-02-07
 */

// Global state
let currentPeriod = 'last_30_days';
let currentCompanyCode = null;
let refreshInterval = null;
let kpiData = null;

/**
 * Initialize P2P Dashboard on page load
 */
export async function initializeP2PDashboard() {
    console.log('[P2P Dashboard] Initializing...');
    
    // Load dashboard data automatically
    await loadDashboard();
    
    // Set up auto-refresh (every 5 minutes)
    startAutoRefresh();
}

/**
 * Load complete dashboard data
 */
export async function loadDashboard() {
    const dashboardContainer = sap.ui.getCore().byId("dashboardContainer");
    const loadingText = sap.ui.getCore().byId("dashboardStatus");
    
    if (!dashboardContainer || !loadingText) {
        console.error("[P2P Dashboard] Required UI elements not found");
        return;
    }
    
    loadingText.setText(`Loading P2P Dashboard (${getPeriodDisplayName(currentPeriod)})...`);
    dashboardContainer.setBusy(true);
    
    try {
        // Build API URL with parameters
        let url = `/api/p2p-dashboard/kpis?period=${currentPeriod}`;
        if (currentCompanyCode) {
            url += `&company_code=${currentCompanyCode}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Failed to load dashboard data");
        }
        
        kpiData = data.data;
        
        // Update status
        const timestamp = new Date(kpiData.timestamp).toLocaleTimeString();
        loadingText.setText(`Last updated: ${timestamp} | Period: ${getPeriodDisplayName(currentPeriod)}`);
        
        // Clear and rebuild dashboard
        dashboardContainer.destroyContent();
        
        // Create dashboard layout
        const dashboardContent = createDashboardLayout(kpiData);
        dashboardContainer.addContent(dashboardContent);
        
        dashboardContainer.setBusy(false);
        
    } catch (error) {
        console.error("[P2P Dashboard] Error loading data:", error);
        const errorMessage = error.message || error.toString() || "Unknown error";
        loadingText.setText("Error loading dashboard: " + errorMessage);
        dashboardContainer.setBusy(false);
        sap.m.MessageToast.show("Failed to load dashboard: " + errorMessage);
    }
}

/**
 * Create complete dashboard layout
 */
function createDashboardLayout(data) {
    const kpis = data.kpis;
    
    return new sap.m.VBox({
        items: [
            // Header with controls
            createDashboardHeader(),
            
            // KPI Cards Grid
            new sap.m.Title({
                text: "Key Performance Indicators",
                level: "H2"
            }).addStyleClass("sapUiMediumMarginTop"),
            
            createKPICardsGrid(kpis),
            
            // Trend Charts Section
            new sap.m.Title({
                text: "Trends & Analytics",
                level: "H2"
            }).addStyleClass("sapUiLargeMarginTop"),
            
            createTrendsSection(),
            
            // Recent Transactions Section
            new sap.m.Title({
                text: "Recent Transactions",
                level: "H2"
            }).addStyleClass("sapUiLargeMarginTop"),
            
            createRecentTransactionsSection()
        ]
    });
}

/**
 * Create dashboard header with period selector and refresh
 */
function createDashboardHeader() {
    return new sap.m.HBox({
        justifyContent: "SpaceBetween",
        alignItems: "Center",
        items: [
            new sap.m.Title({
                text: "P2P Dashboard",
                level: "H1"
            }),
            new sap.m.HBox({
                items: [
                    new sap.m.SegmentedButton({
                        selectedKey: currentPeriod,
                        selectionChange: function(oEvent) {
                            currentPeriod = oEvent.getParameter("item").getKey();
                            loadDashboard();
                        },
                        items: [
                            new sap.m.SegmentedButtonItem({
                                key: "last_7_days",
                                text: "7 Days"
                            }),
                            new sap.m.SegmentedButtonItem({
                                key: "last_30_days",
                                text: "30 Days"
                            }),
                            new sap.m.SegmentedButtonItem({
                                key: "last_90_days",
                                text: "90 Days"
                            }),
                            new sap.m.SegmentedButtonItem({
                                key: "ytd",
                                text: "YTD"
                            })
                        ]
                    }).addStyleClass("sapUiTinyMarginEnd"),
                    new sap.m.Button({
                        icon: "sap-icon://refresh",
                        text: "Refresh",
                        press: function() {
                            loadDashboard();
                        }
                    })
                ]
            })
        ]
    }).addStyleClass("sapUiSmallMarginBottom");
}

/**
 * Create KPI cards grid (5 categories)
 */
function createKPICardsGrid(kpis) {
    return new sap.m.FlexBox({
        wrap: "Wrap",
        items: [
            createPOKPICard(kpis.purchase_orders),
            createSupplierKPICard(kpis.suppliers),
            createInvoiceKPICard(kpis.invoices),
            createFinancialKPICard(kpis.financial),
            createServiceSheetKPICard(kpis.service_sheets)
        ]
    });
}

/**
 * Create Purchase Order KPI Card
 */
function createPOKPICard(po) {
    const poCount = po.po_count || 0;
    const totalValue = po.total_value || 0;
    const lateCount = po.late_po_count || 0;
    const avgProcessing = po.avg_processing_days || 0;
    
    // Calculate health indicator
    const latePercentage = poCount > 0 ? (lateCount / poCount * 100) : 0;
    const healthState = latePercentage < 5 ? sap.m.ValueColor.Good : latePercentage < 15 ? sap.m.ValueColor.Critical : sap.m.ValueColor.Error;
    
    return new sap.m.GenericTile({
        frameType: "TwoByOne",
        header: "Purchase Orders",
        subheader: `${poCount.toLocaleString()} Orders`,
        press: function() {
            showPODetails(po);
        },
        tileContent: [
            new sap.m.TileContent({
                footer: `${lateCount} Late | Avg ${avgProcessing.toFixed(1)} days`,
                content: [
                    new sap.m.NumericContent({
                        value: (totalValue / 1000000).toFixed(1),
                        scale: "M€",
                        valueColor: healthState,
                        icon: "sap-icon://cart",
                        withMargin: false
                    })
                ]
            })
        ]
    }).addStyleClass("sapUiTinyMargin dashboardTile");
}

/**
 * Create Supplier KPI Card
 */
function createSupplierKPICard(suppliers) {
    const activeCount = suppliers.active_count || 0;
    const blockedCount = suppliers.blocked_count || 0;
    const topSuppliers = suppliers.top_suppliers || [];
    
    const healthState = blockedCount === 0 ? sap.m.ValueColor.Good : blockedCount < 5 ? sap.m.ValueColor.Critical : sap.m.ValueColor.Error;
    
    return new sap.m.GenericTile({
        frameType: "TwoByOne",
        header: "Suppliers",
        subheader: `${activeCount} Active`,
        press: function() {
            showSupplierDetails(suppliers);
        },
        tileContent: [
            new sap.m.TileContent({
                footer: `${blockedCount} Blocked | ${topSuppliers.length} Top Performers`,
                content: [
                    new sap.m.NumericContent({
                        value: activeCount,
                        valueColor: healthState,
                        icon: "sap-icon://supplier",
                        withMargin: false
                    })
                ]
            })
        ]
    }).addStyleClass("sapUiTinyMargin dashboardTile");
}

/**
 * Create Invoice KPI Card
 */
function createInvoiceKPICard(invoices) {
    const invoiceCount = invoices.invoice_count || 0;
    const totalValue = invoices.total_value || 0;
    const pendingCount = invoices.pending_count || 0;
    const accuracyRate = invoices.accuracy_rate || 0;
    
    const healthState = accuracyRate >= 95 ? sap.m.ValueColor.Good : accuracyRate >= 85 ? sap.m.ValueColor.Critical : sap.m.ValueColor.Error;
    
    return new sap.m.GenericTile({
        frameType: "TwoByOne",
        header: "Invoices",
        subheader: `${invoiceCount.toLocaleString()} Processed`,
        press: function() {
            showInvoiceDetails(invoices);
        },
        tileContent: [
            new sap.m.TileContent({
                footer: `${pendingCount} Pending | ${accuracyRate.toFixed(1)}% Accurate`,
                content: [
                    new sap.m.NumericContent({
                        value: (totalValue / 1000000).toFixed(1),
                        scale: "M€",
                        valueColor: healthState,
                        icon: "sap-icon://invoice",
                        withMargin: false
                    })
                ]
            })
        ]
    }).addStyleClass("sapUiTinyMargin dashboardTile");
}

/**
 * Create Financial KPI Card
 */
function createFinancialKPICard(financial) {
    const cashInPOs = financial.cash_tied_in_pos || 0;
    const topCategories = financial.spend_by_category || [];
    
    return new sap.m.GenericTile({
        frameType: "TwoByOne",
        header: "Financial Health",
        subheader: "Cash Flow Analysis",
        press: function() {
            showFinancialDetails(financial);
        },
        tileContent: [
            new sap.m.TileContent({
                footer: `${topCategories.length} Spend Categories`,
                content: [
                    new sap.m.NumericContent({
                        value: (cashInPOs / 1000000).toFixed(1),
                        scale: "M€ in POs",
                        valueColor: sap.m.ValueColor.Neutral,
                        icon: "sap-icon://money-bills",
                        withMargin: false
                    })
                ]
            })
        ]
    }).addStyleClass("sapUiTinyMargin dashboardTile");
}

/**
 * Create Service Entry Sheet KPI Card
 */
function createServiceSheetKPICard(sheets) {
    const sheetCount = sheets.sheet_count || 0;
    const totalValue = sheets.total_value || 0;
    const pendingCount = sheets.pending_count || 0;
    const avgApproval = sheets.avg_approval_days || 0;
    
    const healthState = pendingCount < 10 ? sap.m.ValueColor.Good : pendingCount < 30 ? sap.m.ValueColor.Critical : sap.m.ValueColor.Error;
    
    return new sap.m.GenericTile({
        frameType: "TwoByOne",
        header: "Service Entry Sheets",
        subheader: `${sheetCount} Sheets`,
        press: function() {
            showServiceSheetDetails(sheets);
        },
        tileContent: [
            new sap.m.TileContent({
                footer: `${pendingCount} Pending | Avg ${avgApproval.toFixed(1)} days`,
                content: [
                    new sap.m.NumericContent({
                        value: (totalValue / 1000).toFixed(0),
                        scale: "K€",
                        valueColor: healthState,
                        icon: "sap-icon://document",
                        withMargin: false
                    })
                ]
            })
        ]
    }).addStyleClass("sapUiTinyMargin dashboardTile");
}

/**
 * Create trends section with placeholder for charts
 */
function createTrendsSection() {
    return new sap.m.VBox({
        items: [
            new sap.m.Text({
                text: "Trend charts will be loaded here (Chart.js integration)"
            }).addStyleClass("sapUiSmallMargin"),
            new sap.m.Button({
                text: "View PO Trends",
                press: function() {
                    showTrendChart('po');
                }
            }).addStyleClass("sapUiTinyMarginEnd"),
            new sap.m.Button({
                text: "View Invoice Trends",
                press: function() {
                    showTrendChart('invoice');
                }
            })
        ]
    }).addStyleClass("sapUiSmallMargin");
}

/**
 * Create recent transactions section
 */
function createRecentTransactionsSection() {
    return new sap.m.HBox({
        items: [
            new sap.m.Button({
                text: "Recent POs",
                icon: "sap-icon://cart",
                press: function() {
                    showRecentTransactions('pos');
                }
            }).addStyleClass("sapUiTinyMarginEnd"),
            new sap.m.Button({
                text: "Recent Invoices",
                icon: "sap-icon://invoice",
                press: function() {
                    showRecentTransactions('invoices');
                }
            }).addStyleClass("sapUiTinyMarginEnd"),
            new sap.m.Button({
                text: "Recent Service Sheets",
                icon: "sap-icon://document",
                press: function() {
                    showRecentTransactions('service_sheets');
                }
            })
        ]
    }).addStyleClass("sapUiSmallMargin");
}

/**
 * Show Purchase Order details dialog
 */
function showPODetails(po) {
    const oDialog = new sap.m.Dialog({
        title: "Purchase Orders - Details",
        contentWidth: "600px",
        contentHeight: "400px",
        content: [
            new sap.m.VBox({
                items: [
                    createDetailItem("Total Orders", po.po_count),
                    createDetailItem("Total Value", `€${(po.total_value || 0).toLocaleString()}`),
                    createDetailItem("Average Value", `€${(po.avg_value || 0).toLocaleString()}`),
                    createDetailItem("Completed Orders", po.completed_count),
                    createDetailItem("Cancelled Orders", po.cancelled_count),
                    createDetailItem("Late Orders", po.late_po_count),
                    createDetailItem("Late Value", `€${(po.late_po_value || 0).toLocaleString()}`),
                    createDetailItem("Avg Processing Time", `${(po.avg_processing_days || 0).toFixed(1)} days`)
                ]
            }).addStyleClass("sapUiSmallMargin")
        ],
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    oDialog.open();
}

/**
 * Show Supplier details dialog
 */
function showSupplierDetails(suppliers) {
    const topSuppliers = suppliers.top_suppliers || [];
    
    const oDialog = new sap.m.Dialog({
        title: "Suppliers - Details",
        contentWidth: "700px",
        contentHeight: "500px",
        content: [
            new sap.m.VBox({
                items: [
                    createDetailItem("Active Suppliers", suppliers.active_count),
                    createDetailItem("Blocked Suppliers", suppliers.blocked_count),
                    new sap.m.Title({
                        text: "Top Suppliers by Spend",
                        level: "H3"
                    }).addStyleClass("sapUiMediumMarginTop"),
                    new sap.m.Table({
                        columns: [
                            new sap.m.Column({ header: new sap.m.Label({ text: "Supplier" }) }),
                            new sap.m.Column({ header: new sap.m.Label({ text: "Total Spend" }), hAlign: "Right" }),
                            new sap.m.Column({ header: new sap.m.Label({ text: "PO Count" }), hAlign: "Right" })
                        ],
                        items: topSuppliers.map(s => new sap.m.ColumnListItem({
                            cells: [
                                new sap.m.Text({ text: s.SupplierName || s.Supplier }),
                                new sap.m.Text({ text: `€${(s.total_spend || 0).toLocaleString()}`, textAlign: "End" }),
                                new sap.m.Text({ text: s.po_count, textAlign: "End" })
                            ]
                        }))
                    })
                ]
            }).addStyleClass("sapUiSmallMargin")
        ],
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    oDialog.open();
}

/**
 * Show Invoice details dialog
 */
function showInvoiceDetails(invoices) {
    const oDialog = new sap.m.Dialog({
        title: "Invoices - Details",
        contentWidth: "600px",
        contentHeight: "400px",
        content: [
            new sap.m.VBox({
                items: [
                    createDetailItem("Total Invoices", invoices.invoice_count),
                    createDetailItem("Total Value", `€${(invoices.total_value || 0).toLocaleString()}`),
                    createDetailItem("Pending Invoices", invoices.pending_count),
                    createDetailItem("Pending Value", `€${(invoices.pending_value || 0).toLocaleString()}`),
                    createDetailItem("Accuracy Rate", `${(invoices.accuracy_rate || 0).toFixed(1)}%`),
                    createDetailItem("Avg Processing Time", `${(invoices.avg_processing_days || 0).toFixed(1)} days`)
                ]
            }).addStyleClass("sapUiSmallMargin")
        ],
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    oDialog.open();
}

/**
 * Show Financial details dialog
 */
function showFinancialDetails(financial) {
    const spendByCategory = financial.spend_by_category || [];
    
    const oDialog = new sap.m.Dialog({
        title: "Financial Health - Details",
        contentWidth: "700px",
        contentHeight: "500px",
        content: [
            new sap.m.VBox({
                items: [
                    createDetailItem("Cash Tied in Open POs", `€${(financial.cash_tied_in_pos || 0).toLocaleString()}`),
                    new sap.m.Title({
                        text: "Spend by Category",
                        level: "H3"
                    }).addStyleClass("sapUiMediumMarginTop"),
                    new sap.m.Table({
                        columns: [
                            new sap.m.Column({ header: new sap.m.Label({ text: "Material Group" }) }),
                            new sap.m.Column({ header: new sap.m.Label({ text: "Total Spend" }), hAlign: "Right" }),
                            new sap.m.Column({ header: new sap.m.Label({ text: "PO Count" }), hAlign: "Right" })
                        ],
                        items: spendByCategory.map(c => new sap.m.ColumnListItem({
                            cells: [
                                new sap.m.Text({ text: c.MaterialGroup }),
                                new sap.m.Text({ text: `€${(c.total_spend || 0).toLocaleString()}`, textAlign: "End" }),
                                new sap.m.Text({ text: c.po_count, textAlign: "End" })
                            ]
                        }))
                    })
                ]
            }).addStyleClass("sapUiSmallMargin")
        ],
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    oDialog.open();
}

/**
 * Show Service Sheet details dialog
 */
function showServiceSheetDetails(sheets) {
    const oDialog = new sap.m.Dialog({
        title: "Service Entry Sheets - Details",
        contentWidth: "600px",
        contentHeight: "400px",
        content: [
            new sap.m.VBox({
                items: [
                    createDetailItem("Total Sheets", sheets.sheet_count),
                    createDetailItem("Total Value", `€${(sheets.total_value || 0).toLocaleString()}`),
                    createDetailItem("Pending Sheets", sheets.pending_count),
                    createDetailItem("Pending Value", `€${(sheets.pending_value || 0).toLocaleString()}`),
                    createDetailItem("Avg Approval Time", `${(sheets.avg_approval_days || 0).toFixed(1)} days`)
                ]
            }).addStyleClass("sapUiSmallMargin")
        ],
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    oDialog.open();
}

/**
 * Show trend chart (placeholder - needs Chart.js integration)
 */
async function showTrendChart(metric) {
    sap.m.MessageToast.show(`Loading trend chart for ${metric}... (Chart.js integration pending)`);
    
    // TODO: Implement Chart.js integration
    // fetch(`/api/p2p-dashboard/trends/${metric}?period=${currentPeriod}`)
}

/**
 * Show recent transactions
 */
async function showRecentTransactions(type) {
    const oDialog = new sap.m.Dialog({
        title: `Recent ${type.toUpperCase()}`,
        contentWidth: "90%",
        contentHeight: "70%",
        content: [
            new sap.m.Text({
                text: "Loading recent transactions..."
            }).addStyleClass("sapUiSmallMargin")
        ],
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    oDialog.open();
    
    try {
        const response = await fetch(`/api/p2p-dashboard/transactions/recent?type=${type}&limit=20`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Failed to load transactions");
        }
        
        const transactions = data.data.transactions || [];
        
        // Create table
        const oTable = new sap.m.Table({
            growing: false,
            columns: Object.keys(transactions[0] || {}).map(key => 
                new sap.m.Column({ header: new sap.m.Label({ text: key }) })
            ),
            items: transactions.map(tx => 
                new sap.m.ColumnListItem({
                    cells: Object.values(tx).map(value => 
                        new sap.m.Text({ text: String(value || '-') })
                    )
                })
            )
        });
        
        oDialog.removeAllContent();
        oDialog.addContent(oTable);
        
    } catch (error) {
        console.error("Error loading transactions:", error);
        sap.m.MessageToast.show("Error: " + error.message);
    }
}

/**
 * Create detail item (label + value)
 */
function createDetailItem(label, value) {
    return new sap.m.HBox({
        justifyContent: "SpaceBetween",
        items: [
            new sap.m.Label({ text: label + ":" }),
            new sap.m.Text({ text: String(value || 0) })
        ]
    }).addStyleClass("sapUiTinyMarginBottom");
}

/**
 * Get display name for period
 */
function getPeriodDisplayName(period) {
    const names = {
        'last_7_days': 'Last 7 Days',
        'last_30_days': 'Last 30 Days',
        'last_90_days': 'Last 90 Days',
        'ytd': 'Year to Date'
    };
    return names[period] || period;
}

/**
 * Start auto-refresh (every 5 minutes)
 */
function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    refreshInterval = setInterval(() => {
        console.log('[P2P Dashboard] Auto-refresh triggered');
        loadDashboard();
    }, 5 * 60 * 1000); // 5 minutes
}

/**
 * Stop auto-refresh
 */
export function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

/**
 * Cleanup when leaving page
 */
export function cleanup() {
    stopAutoRefresh();
}