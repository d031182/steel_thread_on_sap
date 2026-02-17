/**
 * Log Viewer Overlay
 * ==================
 * Full-screen overlay for viewing application logs
 * 
 * Pattern: Shell Overlay (same as AI Assistant)
 * - Triggered by ShellBar button
 * - Full-screen modal with 60px top offset (shellbar height)
 * - No navigation tab needed
 * 
 * Features:
 * - View logs with filtering (level, category, time range)
 * - Real-time log streaming (Flight Recorder mode)
 * - Export logs
 * - Mode switching (Default ↔ Flight Recorder)
 */

(function() {
    'use strict';

    window.LogViewerOverlay = {
        _dialog: null,
        _logsTable: null,
        _isOpen: false,
        _pollInterval: null,

        /**
         * Open the log viewer overlay
         */
        open: function() {
            if (this._isOpen) {
                return; // Already open
            }

            console.log('[LogViewerOverlay] Opening...');
            this._createDialog();
            this._dialog.open();
            this._isOpen = true;
            
            // Load initial logs
            this._loadLogs();
            
            // Start polling if Flight Recorder mode
            this._startPollingIfNeeded();
        },

        /**
         * Close the log viewer overlay
         */
        close: function() {
            if (!this._isOpen) {
                return;
            }

            console.log('[LogViewerOverlay] Closing...');
            
            // Stop polling
            if (this._pollInterval) {
                clearInterval(this._pollInterval);
                this._pollInterval = null;
            }
            
            if (this._dialog) {
                this._dialog.close();
                this._dialog.destroy();
                this._dialog = null;
            }
            
            this._isOpen = false;
        },

        /**
         * Create the log viewer dialog
         */
        _createDialog: function() {
            const self = this;

            // Create dialog
            this._dialog = new sap.m.Dialog({
                title: "Log Viewer",
                icon: "sap-icon://log",
                contentWidth: "calc(100vw - 120px)",
                contentHeight: "calc(100vh - 120px)",
                draggable: true,
                resizable: true,
                verticalScrolling: false,
                content: this._createContent(),
                beginButton: new sap.m.Button({
                    text: "Refresh",
                    icon: "sap-icon://refresh",
                    press: function() {
                        self._loadLogs();
                    }
                }),
                endButton: new sap.m.Button({
                    text: "Close",
                    press: function() {
                        self.close();
                    }
                }),
                afterClose: function() {
                    self._isOpen = false;
                }
            }).addStyleClass('logViewerDialog');

            // Add custom CSS for full-screen effect
            this._addCustomStyles();
        },

        /**
         * Create dialog content
         */
        _createContent: function() {
            const self = this;

            // Create toolbar with filters and mode toggle
            const toolbar = new sap.m.Toolbar({
                content: [
                    new sap.m.Label({
                        text: "Level:",
                        labelFor: "logLevelFilter"
                    }),
                    new sap.m.Select({
                        id: "logLevelFilter",
                        width: "120px",
                        items: [
                            new sap.ui.core.Item({ key: "ALL", text: "All Levels" }),
                            new sap.ui.core.Item({ key: "ERROR", text: "ERROR" }),
                            new sap.ui.core.Item({ key: "WARN", text: "WARN" }),
                            new sap.ui.core.Item({ key: "INFO", text: "INFO" })
                        ],
                        change: function() {
                            self._loadLogs();
                        }
                    }),
                    new sap.m.ToolbarSpacer({ width: "1rem" }),
                    new sap.m.Label({
                        text: "Category:",
                        labelFor: "logCategoryFilter"
                    }),
                    new sap.m.Select({
                        id: "logCategoryFilter",
                        width: "150px",
                        items: [
                            new sap.ui.core.Item({ key: "ALL", text: "All Categories" }),
                            new sap.ui.core.Item({ key: "API", text: "API" }),
                            new sap.ui.core.Item({ key: "CLICK", text: "Click" }),
                            new sap.ui.core.Item({ key: "CONSOLE", text: "Console" }),
                            new sap.ui.core.Item({ key: "ERROR", text: "Error" }),
                            new sap.ui.core.Item({ key: "SAPUI5", text: "SAPUI5" })
                        ],
                        change: function() {
                            self._loadLogs();
                        }
                    }),
                    new sap.m.ToolbarSpacer(),
                    this._createModeToggle(),
                    new sap.m.Button({
                        text: "Export",
                        icon: "sap-icon://download",
                        press: function() {
                            self._exportLogs();
                        }
                    }),
                    new sap.m.Button({
                        icon: "sap-icon://clear-all",
                        tooltip: "Clear Filters",
                        press: function() {
                            sap.ui.getCore().byId("logLevelFilter").setSelectedKey("ALL");
                            sap.ui.getCore().byId("logCategoryFilter").setSelectedKey("ALL");
                            self._loadLogs();
                        }
                    })
                ]
            });

            // Create logs table
            this._logsTable = new sap.m.Table({
                id: "logsTable",
                growing: true,
                growingScrollToLoad: true,
                width: "100%",
                columns: [
                    new sap.m.Column({
                        width: "150px",
                        header: new sap.m.Text({ text: "Timestamp" })
                    }),
                    new sap.m.Column({
                        width: "80px",
                        header: new sap.m.Text({ text: "Level" })
                    }),
                    new sap.m.Column({
                        width: "120px",
                        header: new sap.m.Text({ text: "Category" })
                    }),
                    new sap.m.Column({
                        hAlign: "Left",
                        header: new sap.m.Text({ text: "Message" })
                    })
                ]
            });

            // Create page with toolbar and table
            const page = new sap.m.Page({
                showHeader: false,
                content: [toolbar, this._logsTable]
            });

            return page;
        },

        /**
         * Create mode toggle button
         */
        _createModeToggle: function() {
            const self = this;

            return new sap.m.SegmentedButton({
                id: "logModeToggle",
                items: [
                    new sap.m.SegmentedButtonItem({
                        key: "default",
                        text: "Default"
                    }),
                    new sap.m.SegmentedButtonItem({
                        key: "flight_recorder",
                        text: "Flight Recorder"
                    })
                ],
                selectionChange: function(oEvent) {
                    const selectedKey = oEvent.getParameter("item").getKey();
                    self._setLoggingMode(selectedKey);
                }
            });
        },

        /**
         * Load logs from backend
         */
        _loadLogs: async function() {
            try {
                // Get filter values
                const levelFilter = sap.ui.getCore().byId("logLevelFilter")?.getSelectedKey() || "ALL";
                const categoryFilter = sap.ui.getCore().byId("logCategoryFilter")?.getSelectedKey() || "ALL";

                // Build query params
                const params = new URLSearchParams({
                    limit: 100,
                    offset: 0
                });

                if (levelFilter !== "ALL") {
                    params.append("level", levelFilter);
                }
                if (categoryFilter !== "ALL") {
                    params.append("category", categoryFilter);
                }

                // Fetch logs
                const response = await fetch(`/api/logger/logs?${params}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                if (data.status === 'success') {
                    this._displayLogs(data.data.logs || []);
                    
                    // Show message if no logs yet
                    if (data.data.message) {
                        sap.m.MessageToast.show(data.data.message);
                    }
                } else {
                    throw new Error(data.message || 'Failed to load logs');
                }

            } catch (error) {
                console.error('[LogViewerOverlay] Failed to load logs:', error);
                sap.m.MessageBox.error(`Failed to load logs: ${error.message}`);
            }
        },

        /**
         * Display logs in table
         */
        _displayLogs: function(logs) {
            this._logsTable.removeAllItems();

            logs.forEach(log => {
                const item = new sap.m.ColumnListItem({
                    cells: [
                        new sap.m.Text({ 
                            text: this._formatTimestamp(log.timestamp) 
                        }),
                        new sap.m.ObjectStatus({
                            text: log.level,
                            state: this._getLevelState(log.level)
                        }),
                        new sap.m.Text({ text: log.category }),
                        new sap.m.Text({ 
                            text: log.message,
                            maxLines: 2
                        })
                    ]
                });

                this._logsTable.addItem(item);
            });

            // If no logs, show message
            if (logs.length === 0) {
                const emptyItem = new sap.m.ColumnListItem({
                    cells: [
                        new sap.m.Text({ text: "" }),
                        new sap.m.Text({ text: "" }),
                        new sap.m.Text({ text: "" }),
                        new sap.m.Text({ 
                            text: "No logs available. Logs are stored in logs/ directory.",
                            renderWhitespace: true
                        })
                    ]
                });
                this._logsTable.addItem(emptyItem);
            }
        },

        /**
         * Set logging mode
         */
        _setLoggingMode: async function(mode) {
            try {
                const response = await fetch('/api/logger/mode', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();

                if (data.status === 'success') {
                    sap.m.MessageToast.show(`Logging mode changed to ${mode}`);
                    
                    // Refresh logs
                    this._loadLogs();
                    
                    // Update polling
                    this._startPollingIfNeeded();
                } else {
                    throw new Error(data.message || 'Failed to set mode');
                }

            } catch (error) {
                console.error('[LogViewerOverlay] Failed to set mode:', error);
                sap.m.MessageBox.error(`Failed to set logging mode: ${error.message}`);
            }
        },

        /**
         * Start polling for new logs if Flight Recorder mode
         */
        _startPollingIfNeeded: async function() {
            const self = this;

            // Clear existing interval
            if (this._pollInterval) {
                clearInterval(this._pollInterval);
                this._pollInterval = null;
            }

            // Check current mode
            try {
                const response = await fetch('/api/logger/mode');
                const data = await response.json();

                if (data.data.mode === 'flight_recorder') {
                    // Poll every 5 seconds in Flight Recorder mode
                    this._pollInterval = setInterval(() => {
                        self._loadLogs();
                    }, 5000);
                    
                    console.log('[LogViewerOverlay] Started polling (Flight Recorder mode)');
                }
            } catch (error) {
                console.error('[LogViewerOverlay] Failed to check mode:', error);
            }
        },

        /**
         * Export logs to JSON file
         */
        _exportLogs: async function() {
            try {
                const response = await fetch('/api/logger/logs?limit=10000');
                const data = await response.json();

                if (data.status === 'success') {
                    const logs = data.data.logs;
                    const json = JSON.stringify(logs, null, 2);
                    const blob = new Blob([json], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `logs_${new Date().toISOString().replace(/:/g, '-')}.json`;
                    a.click();
                    
                    URL.revokeObjectURL(url);
                    
                    sap.m.MessageToast.show('Logs exported successfully');
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                console.error('[LogViewerOverlay] Failed to export:', error);
                sap.m.MessageBox.error(`Failed to export logs: ${error.message}`);
            }
        },

        /**
         * Format timestamp for display
         */
        _formatTimestamp: function(timestamp) {
            if (!timestamp) return '';
            
            try {
                const date = new Date(timestamp);
                return date.toLocaleString('en-US', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                });
            } catch (e) {
                return timestamp;
            }
        },

        /**
         * Get status state based on log level
         */
        _getLevelState: function(level) {
            const stateMap = {
                'ERROR': 'Error',
                'WARN': 'Warning',
                'INFO': 'Success'
            };
            return stateMap[level] || 'None';
        },

        /**
         * Add custom styles for full-screen overlay
         */
        _addCustomStyles: function() {
            if (document.getElementById('logViewerStyles')) {
                return; // Already added
            }

            const style = document.createElement('style');
            style.id = 'logViewerStyles';
            style.textContent = `
                /* Log Viewer Overlay Styles */
                .logViewerDialog {
                    z-index: 10000 !important;
                }

                .logViewerDialog .sapMDialogScroll {
                    padding: 0 !important;
                }

                .logViewerDialog .sapMDialog {
                    top: 60px !important;  /* ShellBar height */
                    max-height: calc(100vh - 80px) !important;
                }

                /* Table styling */
                #logsTable {
                    margin-top: 1rem;
                }

                #logsTable .sapMListTblCell {
                    vertical-align: top;
                    padding: 0.5rem;
                }
            `;
            document.head.appendChild(style);
        }
    };

    console.log('✓ LogViewerOverlay registered globally');
})();