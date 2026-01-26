/**
 * Logging Page Module
 * 
 * Handles the application logging dialog with filtering, refresh, and debug mode.
 * Displays logs from backend with color-coded levels and performance metrics.
 * 
 * @author P2P Development Team
 * @version 2.0.0
 */

import { LogViewerAPI } from '../../api/logViewerAPI.js';

// Create API instance
const logViewerAPI = new LogViewerAPI();

/**
 * Open the logging dialog
 */
export async function openLoggingDialog() {
    sap.ui.core.BusyIndicator.show(0);
    
    try {
        // Fetch logs from API
        const result = await logViewerAPI.getLogs({ limit: 100 });
        
        if (!result.success) {
            throw new Error(result.error?.message || "Failed to load logs");
        }
        
        const logs = result.logs || [];
        
        // Calculate statistics
        const stats = calculateStats(logs);
        
        // Check current debug mode state
        const debugMode = localStorage.getItem('debugMode') === 'true';
        
        // Create and open dialog
        const oLogDialog = createLoggingDialog(logs, stats, debugMode);
        oLogDialog.open();
        
    } catch (error) {
        sap.m.MessageBox.error("Error loading logs: " + error.message);
    } finally {
        sap.ui.core.BusyIndicator.hide();
    }
}

/**
 * Calculate log statistics
 */
function calculateStats(logs) {
    return {
        total: logs.length,
        INFO: logs.filter(l => l.level === 'INFO').length,
        WARNING: logs.filter(l => l.level === 'WARNING').length,
        ERROR: logs.filter(l => l.level === 'ERROR').length
    };
}

/**
 * Create the logging dialog UI
 */
function createLoggingDialog(logs, stats, debugMode) {
    return new sap.m.Dialog({
        title: "Application Logs",
        contentWidth: "80%",
        contentHeight: "70%",
        resizable: true,
        draggable: true,
        content: [
            new sap.m.VBox({
                items: [
                    createDebugModeToolbar(debugMode),
                    createFilterToolbar(stats),
                    createLogsTable(logs)
                ]
            })
        ],
        beginButton: new sap.m.Button({
            text: "Close",
            press: function() {
                this.getParent().close();
            }
        }),
        afterClose: function() {
            this.destroy();
        }
    });
}

/**
 * Create debug mode toggle toolbar
 */
function createDebugModeToolbar(debugMode) {
    return new sap.m.Toolbar({
        content: [
            new sap.m.Label({ 
                text: "Debug Mode:",
                design: "Bold"
            }),
            new sap.m.Switch({
                state: debugMode,
                customTextOn: "ON",
                customTextOff: "OFF",
                change: function(oEvent) {
                    const bState = oEvent.getParameter("state");
                    if (bState) {
                        localStorage.setItem('debugMode', 'true');
                        console.log("[Debug Mode] Enabled");
                    } else {
                        localStorage.removeItem('debugMode');
                        console.log("[Debug Mode] Disabled");
                    }
                    sap.m.MessageToast.show("Debug Mode " + (bState ? "enabled" : "disabled") + " - Refresh page to apply");
                }
            }).addStyleClass("sapUiTinyMarginBegin"),
            new sap.m.ToolbarSpacer(),
            new sap.m.Text({
                text: "Enable for detailed browser console logging"
            })
        ]
    }).addStyleClass("sapUiTinyMarginBottom");
}

/**
 * Create filter toolbar
 */
function createFilterToolbar(stats) {
    return new sap.m.OverflowToolbar({
        content: [
            new sap.m.Title({
                text: "Logs (" + stats.total + ")",
                level: "H2"
            }),
            new sap.m.ToolbarSpacer(),
            new sap.m.Label({ text: "Filter:" }),
            new sap.m.SegmentedButton({
                selectedKey: "ALL",
                selectionChange: async function(oEvent) {
                    const level = oEvent.getParameter("item").getKey();
                    await refreshLogs(level);
                },
                items: [
                    new sap.m.SegmentedButtonItem({
                        key: "ALL",
                        text: "All (" + stats.total + ")"
                    }),
                    new sap.m.SegmentedButtonItem({
                        key: "INFO",
                        text: "Info (" + stats.INFO + ")"
                    }),
                    new sap.m.SegmentedButtonItem({
                        key: "WARNING",
                        text: "Warning (" + stats.WARNING + ")"
                    }),
                    new sap.m.SegmentedButtonItem({
                        key: "ERROR",
                        text: "Error (" + stats.ERROR + ")"
                    })
                ]
            }),
            new sap.m.Button({
                icon: "sap-icon://refresh",
                tooltip: "Refresh",
                press: async function() {
                    await refreshLogs("ALL");
                }
            })
        ]
    });
}

/**
 * Create logs table
 */
function createLogsTable(logs) {
    return new sap.m.Table({
        id: "logsTable",
        growing: true,
        growingThreshold: 50,
        columns: [
            new sap.m.Column({
                header: new sap.m.Label({ text: "Time" }),
                width: "160px"
            }),
            new sap.m.Column({
                header: new sap.m.Label({ text: "Level" }),
                width: "100px",
                hAlign: "Center"
            }),
            new sap.m.Column({
                header: new sap.m.Label({ text: "Duration" }),
                width: "120px",
                hAlign: "Right"
            }),
            new sap.m.Column({
                header: new sap.m.Label({ text: "Message" })
            })
        ],
        items: logs.map(log => createLogItem(log))
    });
}

/**
 * Create a single log item
 */
function createLogItem(log) {
    const { state, icon } = getLogLevelFormat(log.level);
    const { durationText, durationState } = formatDuration(log.duration_ms);
    
    return new sap.m.ColumnListItem({
        cells: [
            new sap.m.Text({
                text: logViewerAPI.formatTimestamp(log.timestamp)
            }),
            new sap.m.ObjectStatus({
                text: log.level,
                state: state,
                icon: icon
            }),
            new sap.m.ObjectStatus({
                text: durationText,
                state: durationState
            }),
            new sap.m.Text({
                text: log.message,
                wrapping: true
            })
        ]
    });
}

/**
 * Get format for log level
 */
function getLogLevelFormat(level) {
    const formats = {
        'ERROR': { state: 'Error', icon: 'sap-icon://message-error' },
        'WARNING': { state: 'Warning', icon: 'sap-icon://message-warning' },
        'INFO': { state: 'Information', icon: 'sap-icon://message-information' }
    };
    return formats[level] || { state: 'None', icon: 'sap-icon://message-information' };
}

/**
 * Format duration with color coding
 */
function formatDuration(duration_ms) {
    if (duration_ms === null || duration_ms === undefined) {
        return { durationText: '-', durationState: 'None' };
    }
    
    const durationText = duration_ms.toFixed(2) + 'ms';
    let durationState = 'Success';  // Green for fast (<200ms)
    
    if (duration_ms > 1000) {
        durationState = 'Error';  // Red for slow (>1s)
    } else if (duration_ms > 500) {
        durationState = 'Warning';  // Orange for medium (>500ms)
    } else if (duration_ms > 200) {
        durationState = 'Information';  // Blue for acceptable (>200ms)
    }
    
    return { durationText, durationState };
}

/**
 * Refresh logs with optional filter
 */
async function refreshLogs(level) {
    sap.ui.core.BusyIndicator.show(0);
    
    try {
        const fetchLevel = (level === 'ALL') ? null : level;
        const result = await logViewerAPI.getLogs({ level: fetchLevel, limit: 100 });
        
        if (!result.success) {
            throw new Error(result.error?.message || "Failed to refresh logs");
        }
        
        const logs = result.logs || [];
        
        // Update table
        const oTable = sap.ui.getCore().byId("logsTable");
        if (oTable) {
            oTable.destroyItems();
            logs.forEach(log => oTable.addItem(createLogItem(log)));
        }
        
        sap.m.MessageToast.show("Logs refreshed (" + logs.length + " entries)");
        
    } catch (error) {
        sap.m.MessageBox.error("Error refreshing logs: " + error.message);
    } finally {
        sap.ui.core.BusyIndicator.hide();
    }
}