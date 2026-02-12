sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast",
    "sap/m/MessageBox"
], function (Controller, JSONModel, MessageToast, MessageBox) {
    "use strict";

    return Controller.extend("modules.feature_manager.frontend.Configurator", {

        /**
         * Controller initialization
         */
        onInit: function () {
            // Create JSON model for features
            this.oModel = new JSONModel({
                features: [],
                stats: {
                    total: 0,
                    enabled: 0,
                    disabled: 0,
                    categories: 0
                }
            });
            this.getView().setModel(this.oModel);

            // Load features from backend
            this._loadFeatures();
        },

        /**
         * Load features from backend API
         * @private
         */
        _loadFeatures: function () {
            const that = this;
            
            // Show busy indicator
            this.getView().setBusy(true);

            // Call backend API
            fetch("/api/features")
                .then(response => response.json())
                .then(data => {
                    console.log("API Response:", data);
                    
                    if (data.success) {
                        // Handle nested structure: data.features.features or data.features
                        const featuresObj = data.features.features || data.features;
                        
                        // Transform features object to array for binding
                        const featuresArray = [];
                        for (const [key, feature] of Object.entries(featuresObj)) {
                            featuresArray.push({
                                key: key,
                                displayName: feature.displayName || key,
                                description: feature.description || "No description available",
                                category: feature.category || "Uncategorized",
                                enabled: feature.enabled || false
                            });
                        }

                        console.log("Features array:", featuresArray);

                        // Update model
                        that.oModel.setProperty("/features", featuresArray);
                        that._updateStatistics(featuresArray);

                        MessageToast.show(`${featuresArray.length} features loaded successfully`);
                    } else {
                        MessageBox.error("Failed to load features: " + (data.error || "Unknown error"));
                    }
                })
                .catch(error => {
                    MessageBox.error("Error loading features: " + error.message);
                    console.error("Feature load error:", error);
                })
                .finally(() => {
                    that.getView().setBusy(false);
                });
        },

        /**
         * Update statistics in the model
         * @param {Array} features - Array of feature objects
         * @private
         */
        _updateStatistics: function (features) {
            const stats = {
                total: features.length,
                enabled: features.filter(f => f.enabled).length,
                disabled: features.filter(f => !f.enabled).length,
                categories: [...new Set(features.map(f => f.category))].length
            };
            this.oModel.setProperty("/stats", stats);
        },

        /**
         * Handle feature toggle
         * @param {sap.ui.base.Event} oEvent - The event object
         */
        onFeatureToggle: function (oEvent) {
            const oSwitch = oEvent.getSource();
            const oBindingContext = oSwitch.getBindingContext();
            const sFeatureKey = oBindingContext.getProperty("key");
            const sFeatureName = oBindingContext.getProperty("displayName");
            const bNewState = oEvent.getParameter("state");

            // Show loading on switch (not whole page)
            oSwitch.setBusy(true);

            // Call backend API to toggle
            fetch(`/api/features/${sFeatureKey}/toggle`, {
                method: "POST"
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update model with new state
                        oBindingContext.setProperty("enabled", data.enabled);
                        
                        // Update statistics
                        const features = this.oModel.getProperty("/features");
                        this._updateStatistics(features);

                        // Show success message
                        this._showMessage(
                            "success",
                            `${sFeatureName} ${data.enabled ? "enabled" : "disabled"} successfully`
                        );
                    } else {
                        // Revert switch state on error
                        oSwitch.setState(!bNewState);
                        this._showMessage(
                            "error",
                            `Failed to toggle ${sFeatureName}: ${data.error || "Unknown error"}`
                        );
                    }
                })
                .catch(error => {
                    // Revert switch state on error
                    oSwitch.setState(!bNewState);
                    this._showMessage(
                        "error",
                        `Error toggling ${sFeatureName}: ${error.message}`
                    );
                    console.error("Feature toggle error:", error);
                })
                .finally(() => {
                    oSwitch.setBusy(false);
                });
        },

        /**
         * Show success or error message
         * @param {string} sType - Message type ("success" or "error")
         * @param {string} sText - Message text
         * @private
         */
        _showMessage: function (sType, sText) {
            const sMessageId = sType === "success" ? "successMessage" : "errorMessage";
            const oMessage = this.byId(sMessageId);
            
            if (oMessage) {
                oMessage.setText(sText);
                oMessage.setVisible(true);
                
                // Auto-hide after 3 seconds
                setTimeout(function () {
                    oMessage.setVisible(false);
                }, 3000);
            }
        },

        /**
         * Handle category tab selection
         * @param {sap.ui.base.Event} oEvent - The event object
         */
        onCategorySelect: function (oEvent) {
            const sKey = oEvent.getParameter("key");
            MessageToast.show(`Viewing ${sKey === "all" ? "all features" : sKey + " features"}`);
        },

        /**
         * Export configuration to JSON file
         */
        onExport: function () {
            this.getView().setBusy(true);

            fetch("/api/features/export")
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Create downloadable JSON file
                        const jsonString = JSON.stringify(data.config, null, 2);
                        const blob = new Blob([jsonString], { type: "application/json" });
                        const url = URL.createObjectURL(blob);
                        
                        // Create temporary download link
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `feature_flags_${new Date().toISOString().split('T')[0]}.json`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);

                        MessageToast.show("Configuration exported successfully");
                    } else {
                        MessageBox.error("Failed to export configuration: " + (data.error || "Unknown error"));
                    }
                })
                .catch(error => {
                    MessageBox.error("Error exporting configuration: " + error.message);
                    console.error("Export error:", error);
                })
                .finally(() => {
                    this.getView().setBusy(false);
                });
        },

        /**
         * Import configuration from JSON file
         */
        onImport: function () {
            const that = this;

            // Create file input element
            const fileInput = document.createElement("input");
            fileInput.type = "file";
            fileInput.accept = "application/json";
            
            fileInput.onchange = function (event) {
                const file = event.target.files[0];
                if (!file) return;

                const reader = new FileReader();
                reader.onload = function (e) {
                    try {
                        const config = JSON.parse(e.target.result);
                        
                        // Confirm import
                        MessageBox.confirm(
                            "This will replace your current configuration. Continue?",
                            {
                                title: "Confirm Import",
                                onClose: function (action) {
                                    if (action === MessageBox.Action.OK) {
                                        that._performImport(config);
                                    }
                                }
                            }
                        );
                    } catch (error) {
                        MessageBox.error("Invalid JSON file: " + error.message);
                    }
                };
                reader.readAsText(file);
            };

            fileInput.click();
        },

        /**
         * Perform the actual import
         * @param {Object} config - Configuration object
         * @private
         */
        _performImport: function (config) {
            this.getView().setBusy(true);

            fetch("/api/features/import", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ config: config })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        MessageToast.show("Configuration imported successfully");
                        this._loadFeatures(); // Reload features
                    } else {
                        MessageBox.error("Failed to import configuration: " + (data.error || "Unknown error"));
                    }
                })
                .catch(error => {
                    MessageBox.error("Error importing configuration: " + error.message);
                    console.error("Import error:", error);
                })
                .finally(() => {
                    this.getView().setBusy(false);
                });
        },

        /**
         * Reset all features to default values
         */
        onReset: function () {
            const that = this;

            MessageBox.confirm(
                "This will reset all features to their default values. Continue?",
                {
                    title: "Confirm Reset",
                    onClose: function (action) {
                        if (action === MessageBox.Action.OK) {
                            that._performReset();
                        }
                    }
                }
            );
        },

        /**
         * Perform the actual reset
         * @private
         */
        _performReset: function () {
            this.getView().setBusy(true);

            fetch("/api/features/reset", {
                method: "POST"
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        MessageToast.show("Configuration reset to defaults");
                        this._loadFeatures(); // Reload features
                    } else {
                        MessageBox.error("Failed to reset configuration: " + (data.error || "Unknown error"));
                    }
                })
                .catch(error => {
                    MessageBox.error("Error resetting configuration: " + error.message);
                    console.error("Reset error:", error);
                })
                .finally(() => {
                    this.getView().setBusy(false);
                });
        },

        /**
         * Refresh features from server
         */
        onRefresh: function () {
            this._loadFeatures();
        }
    });
});