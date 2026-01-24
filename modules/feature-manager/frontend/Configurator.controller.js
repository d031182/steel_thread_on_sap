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
            // Create view model
            var oViewModel = new JSONModel({
                features: [],
                totalFeatures: 0,
                enabledCount: 0,
                disabledCount: 0,
                currentCategory: "Infrastructure"
            });
            this.getView().setModel(oViewModel);

            // Load features
            this._loadFeatures();
        },

        /**
         * Load features from API
         * @private
         */
        _loadFeatures: function () {
            var that = this;
            
            // Call Feature Manager API
            fetch('/api/features')
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        that._processFeatures(data.features);
                    } else {
                        MessageToast.show("Error loading features: " + data.error);
                    }
                })
                .catch(function (error) {
                    MessageToast.show("Failed to load features: " + error.message);
                });
        },

        /**
         * Process and organize features by category
         * @param {object} features - Features object from API
         * @private
         */
        _processFeatures: function (features) {
            var oModel = this.getView().getModel();
            var aFeatures = [];
            var iEnabled = 0;
            var iDisabled = 0;

            // Convert features object to array and add name property
            for (var sKey in features) {
                var oFeature = Object.assign({}, features[sKey]);
                oFeature.name = sKey;
                aFeatures.push(oFeature);

                if (oFeature.enabled) {
                    iEnabled++;
                } else {
                    iDisabled++;
                }
            }

            // Update model
            oModel.setProperty("/features", aFeatures);
            oModel.setProperty("/totalFeatures", aFeatures.length);
            oModel.setProperty("/enabledCount", iEnabled);
            oModel.setProperty("/disabledCount", iDisabled);

            // Filter by current category
            this._filterByCategory(oModel.getProperty("/currentCategory"));
        },

        /**
         * Filter features by category
         * @param {string} sCategory - Category name
         * @private
         */
        _filterByCategory: function (sCategory) {
            var oModel = this.getView().getModel();
            var aAllFeatures = oModel.getProperty("/features");
            
            // Filter features
            var aFiltered = aAllFeatures.filter(function (oFeature) {
                return oFeature.category === sCategory;
            });

            // Update the corresponding list
            var sListId = this._getCategoryListId(sCategory);
            var oList = this.byId(sListId);
            
            if (oList) {
                var oListModel = new JSONModel(aFiltered);
                oList.setModel(oListModel);
                oList.bindItems({
                    path: "/",
                    template: oList.getItems()[0].clone()
                });
            }
        },

        /**
         * Get list ID for category
         * @param {string} sCategory - Category name
         * @returns {string} List ID
         * @private
         */
        _getCategoryListId: function (sCategory) {
            var mCategoryToListId = {
                "Infrastructure": "infrastructureList",
                "Business Logic": "businessLogicList",
                "Developer Tools": "devToolsList"
            };
            return mCategoryToListId[sCategory] || "infrastructureList";
        },

        /**
         * Handle category tab selection
         * @param {sap.ui.base.Event} oEvent - Selection event
         */
        onCategorySelect: function (oEvent) {
            var sCategory = oEvent.getParameter("key");
            var oModel = this.getView().getModel();
            
            oModel.setProperty("/currentCategory", sCategory);
            this._filterByCategory(sCategory);
        },

        /**
         * Handle feature toggle
         * @param {sap.ui.base.Event} oEvent - Change event
         */
        onFeatureToggle: function (oEvent) {
            var that = this;
            var oSwitch = oEvent.getSource();
            var bNewState = oEvent.getParameter("state");
            var sFeatureName = oSwitch.data("featureName");

            // Call API to toggle feature
            var sUrl = '/api/features/' + sFeatureName + '/toggle';
            
            fetch(sUrl, { method: 'POST' })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        MessageToast.show(data.message);
                        that._loadFeatures(); // Reload to update stats
                    } else {
                        MessageToast.show("Error toggling feature: " + data.error);
                        // Revert switch state
                        oSwitch.setState(!bNewState);
                    }
                })
                .catch(function (error) {
                    MessageToast.show("Failed to toggle feature: " + error.message);
                    // Revert switch state
                    oSwitch.setState(!bNewState);
                });
        },

        /**
         * Handle export button press
         */
        onExport: function () {
            var that = this;
            
            // Get export from API
            fetch('/api/features/export')
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        // Show export dialog
                        var oDialog = that.byId("exportDialog");
                        var oTextArea = that.byId("exportTextArea");
                        
                        oTextArea.setValue(data.config);
                        oDialog.open();
                    } else {
                        MessageToast.show("Error exporting: " + data.error);
                    }
                })
                .catch(function (error) {
                    MessageToast.show("Failed to export: " + error.message);
                });
        },

        /**
         * Copy exported config to clipboard
         */
        onCopyToClipboard: function () {
            var oTextArea = this.byId("exportTextArea");
            var sConfig = oTextArea.getValue();
            
            // Copy to clipboard
            navigator.clipboard.writeText(sConfig).then(function () {
                MessageToast.show("Configuration copied to clipboard");
            }).catch(function () {
                MessageToast.show("Failed to copy to clipboard");
            });
        },

        /**
         * Close export dialog
         */
        onCloseExportDialog: function () {
            this.byId("exportDialog").close();
        },

        /**
         * Handle import button press
         */
        onImport: function () {
            var oDialog = this.byId("importDialog");
            var oTextArea = this.byId("importTextArea");
            
            // Clear previous input
            oTextArea.setValue("");
            oDialog.open();
        },

        /**
         * Confirm import
         */
        onConfirmImport: function () {
            var that = this;
            var oTextArea = this.byId("importTextArea");
            var sConfig = oTextArea.getValue().trim();
            
            if (!sConfig) {
                MessageToast.show("Please paste configuration JSON");
                return;
            }
            
            // Validate JSON
            try {
                JSON.parse(sConfig);
            } catch (e) {
                MessageToast.show("Invalid JSON format");
                return;
            }
            
            // Call API to import
            fetch('/api/features/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ config: sConfig })
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        MessageToast.show(data.message);
                        that.byId("importDialog").close();
                        that._loadFeatures(); // Reload features
                    } else {
                        MessageToast.show("Error importing: " + data.error);
                    }
                })
                .catch(function (error) {
                    MessageToast.show("Failed to import: " + error.message);
                });
        },

        /**
         * Close import dialog
         */
        onCloseImportDialog: function () {
            this.byId("importDialog").close();
        },

        /**
         * Handle reset button press
         */
        onReset: function () {
            this.byId("resetDialog").open();
        },

        /**
         * Confirm reset to defaults
         */
        onConfirmReset: function () {
            var that = this;
            
            // Call API to reset
            fetch('/api/features/reset', { method: 'POST' })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        MessageToast.show(data.message);
                        that.byId("resetDialog").close();
                        that._loadFeatures(); // Reload features
                    } else {
                        MessageToast.show("Error resetting: " + data.error);
                    }
                })
                .catch(function (error) {
                    MessageToast.show("Failed to reset: " + error.message);
                });
        },

        /**
         * Close reset dialog
         */
        onCloseResetDialog: function () {
            this.byId("resetDialog").close();
        }

    });
});