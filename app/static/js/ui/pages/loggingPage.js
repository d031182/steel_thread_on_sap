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
        
        // Fetch statistics from API (not calculated locally)
        const statsResult = await logViewerAPI.getLogStats();
        const stats = statsResult.success ? statsResult.stats : calculateStats(logs);
        
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
 * Calculate log statistics (fallback if API call fails)
 * Returns lowercase keys to match API format
 */
function calculateStats(logs) {
    return {
        total: logs.length,
        info: logs.filter(l => l.level === 'INFO').length,
        warning: logs.filter(l => l.level === 'WARNING').length,
        error: logs.filter(l => l.level === 'ERROR').length
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
 * Create Flight Recorder mode switcher toolbar (simplified)
 */
function createDebugModeToolbar(debugMode) {
    // Get current Flight Recorder mode from window.LoggingMode (async)
    let flightRecorderActive = false;
    if (window.LoggingMode && window.LoggingMode.getCurrentMode) {
        flightRecorderActive = window.LoggingMode.getCurrentMode() === 'flight_recorder';
    }
    
    return new sap.m.Toolbar({
        content: [
            new sap.m.Label({ 
                text: "Flight Recorder:",
                design: "Bold"
            }),
            new sap.m.Switch({
                id: "flightRecorderSwitch",
                state: flightRecorderActive,
                customTextOn: "ON",
                customTextOff: "OFF",
                change: async function(oEvent) {
                    const bState = oEvent.getParameter("state");
                    const newMode = bState ? 'flight_recorder' : 'default';
                    
                    sap.ui.core.BusyIndicator.show(0);
                    try {
                        if (window.LoggingMode && window.LoggingMode.switchMode) {
                            // Flight Recorder controls Debug Mode automatically
                            if (bState) {
                                localStorage.setItem('debugMode', 'true');
                                console.log("[Flight Recorder] Enabling full tracing (backend + console)");
                            } else {
                                localStorage.removeItem('debugMode');
                                console.log("[Flight Recorder] Disabling tracing");
                            }
                            
                            const success = await window.LoggingMode.switchMode(newMode);
                            if (success) {
                                sap.m.MessageToast.show("Flight Recorder " + (bState ? "enabled" : "disabled") + " - Page will reload...");
                            } else {
                                // Revert localStorage on failure
                                oEvent.getSource().setState(!bState);
                                if (bState) {
                                    localStorage.removeItem('debugMode');
                                } else {
                                    localStorage.setItem('debugMode', 'true');
                                }
                                sap.m.MessageBox.error("Failed to switch Flight Recorder mode");
                            }
                        } else {
                            sap.m.MessageBox.error("Flight Recorder system not available");
                            oEvent.getSource().setState(!bState);
                        }
                    } catch (error) {
                        sap.m.MessageBox.error("Error switching mode: " + error.message);
                        oEvent.getSource().setState(!bState);
                    } finally {
                        sap.ui.core.BusyIndicator.hide();
                    }
                }
            }).addStyleClass("sapUiTinyMarginBegin"),
            new sap.m.ToolbarSpacer(),
            new sap.m.Text({
                text: flightRecorderActive 
                    ? "🔴 Capturing all activities: clicks, API calls, errors, console output"
                    : "Enable to capture and trace all application activities"
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
                        text: "Info (" + stats.info + ")"
                    }),
                    new sap.m.SegmentedButtonItem({
                        key: "WARNING",
                        text: "Warning (" + stats.warning + ")"
                    }),
                    new sap.m.SegmentedButtonItem({
                        key: "ERROR",
                        text: "Error (" + stats.error + ")"
                    })
                ]
            }),
            new sap.m.Button({
                icon: "sap-icon://refresh",
                tooltip: "Refresh",
                press: async function() {
                    await refreshLogs("ALL");
                }
            }),
            new sap.m.Button({
                icon: "sap-icon://delete",
                text: "Clear All Logs",
                type: "Reject",
                press: async function() {
                    await clearAllLogs();
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
 * Clear all logs
 */
async function clearAllLogs() {
    // Confirm with user - use Dialog instead of MessageBox (more reliable)
    const confirmDialog = new sap.m.Dialog({
        title: "Clear All Logs",
        type: "Message",
        state: "Warning",
        content: new sap.m.Text({
            text: "Are you sure you want to clear all logs? This action cannot be undone."
        }),
        beginButton: new sap.m.Button({
            text: "Yes",
            type: "Emphasized",
            press: async function() {
                confirmDialog.close();
                await executeClearLogs();
            }
        }),
        endButton: new sap.m.Button({
            text: "No",
            press: function() {
                confirmDialog.close();
            }
        }),
        afterClose: function() {
            confirmDialog.destroy();
        }
    });
    
    confirmDialog.open();
}

/**
 * Execute the clear logs operation
 */
async function executeClearLogs() {
    
    sap.ui.core.BusyIndicator.show(0);
    
    try {
        const result = await logViewerAPI.clearLogs();
        
        if (!result.success) {
            throw new Error(result.error?.message || "Failed to clear logs");
        }
        
        // Refresh the table to show empty state
        await refreshLogs("ALL");
        
        sap.m.MessageToast.show("✓ All logs cleared successfully");
        
    } catch (error) {
        sap.m.MessageBox.error("Error clearing logs: " + error.message);
    } finally {
        sap.ui.core.BusyIndicator.hide();
    }
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