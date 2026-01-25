sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/m/MessageToast"
], function (Controller, MessageToast) {
    "use strict";

    return Controller.extend("p2p.dataproducts.controller.DataProducts", {
        /**
         * Called when the controller is instantiated.
         * @public
         */
        onInit: function () {
            // Controller initialization
            var oRouter = this.getOwnerComponent().getRouter();
            oRouter.getRoute("dataProducts").attachPatternMatched(this._onObjectMatched, this);
        },

        /**
         * Pattern matched handler
         * @param {sap.ui.base.Event} oEvent - Pattern matched event
         * @private
         */
        _onObjectMatched: function (oEvent) {
            // Page loaded - could load additional data here
        },

        /**
         * View product details
         * @param {sap.ui.base.Event} oEvent - Button press event
         * @public
         */
        onViewProduct: function (oEvent) {
            var oButton = oEvent.getSource();
            var sProductId = oButton.data("productId");
            
            MessageToast.show("Viewing details for: " + sProductId);
            
            // Navigate to product detail (when implemented)
            // var oRouter = this.getOwnerComponent().getRouter();
            // oRouter.navTo("productDetail", {
            //     productId: sProductId
            // });
        },

        /**
         * View CSN definition for a data product
         * @param {sap.ui.base.Event} oEvent - Button press event
         * @public
         */
        onViewCSN: function (oEvent) {
            var oButton = oEvent.getSource();
            var sProductId = oButton.data("productId");
            
            // Map product IDs to CSN file paths
            var mCsnFiles = {
                "Supplier": "../../data-products/sap-s4com-Supplier-v1.en.json",
                "PurchaseOrder": "../../data-products/sap-s4com-PurchaseOrder-v1.en.json",
                "ServiceEntry": "../../data-products/sap-s4com-ServiceEntrySheet-v1.en.json",
                "SupplierInvoice": "../../data-products/sap-s4com-SupplierInvoice-v1.en-complete.json",
                "PaymentTerms": "../../data-products/sap-s4com-PaymentTerms-v1.en.json",
                "JournalEntry": "../../data-products/sap-s4com-JournalEntryHeader-v1.en.json"
            };
            
            var sCsnFile = mCsnFiles[sProductId];
            
            if (!sCsnFile) {
                MessageToast.show("CSN file not available for this product");
                return;
            }
            
            // Load CSN file and display in dialog
            this._loadAndDisplayCSN(sProductId, sCsnFile);
        },

        /**
         * Load and display CSN definition
         * @param {string} sProductId - Product ID
         * @param {string} sCsnFile - Path to CSN file
         * @private
         */
        _loadAndDisplayCSN: function (sProductId, sCsnFile) {
            var that = this;
            
            // Show loading message
            sap.ui.core.BusyIndicator.show(0);
            
            // Fetch CSN file
            fetch(sCsnFile)
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error("HTTP error! status: " + response.status);
                    }
                    return response.json();
                })
                .then(function (oCsnData) {
                    sap.ui.core.BusyIndicator.hide();
                    that._showCSNDialog(sProductId, oCsnData);
                })
                .catch(function (oError) {
                    sap.ui.core.BusyIndicator.hide();
                    MessageToast.show("Error loading CSN: " + oError.message);
                    console.error("CSN loading error:", oError);
                });
        },

        /**
         * Show CSN definition in a dialog
         * @param {string} sProductId - Product ID
         * @param {object} oCsnData - CSN data object
         * @private
         */
        _showCSNDialog: function (sProductId, oCsnData) {
            var that = this;
            
            // Format JSON with syntax highlighting
            var sFormattedJson = JSON.stringify(oCsnData, null, 2);
            
            // Get product name from model
            var oModel = this.getView().getModel();
            var aProducts = oModel.getProperty("/dataProducts");
            var oProduct = aProducts.find(function(p) { return p.id === sProductId; });
            var sProductName = oProduct ? oProduct.name : sProductId;
            
            // Create dialog if it doesn't exist
            if (!this._oCsnDialog) {
                this._oCsnDialog = new sap.m.Dialog({
                    title: "CSN Definition - " + sProductName,
                    contentWidth: "90%",
                    contentHeight: "80%",
                    resizable: true,
                    draggable: true,
                    content: [
                        new sap.m.VBox({
                            items: [
                                new sap.m.Text({
                                    text: "Core Schema Notation",
                                    class: "sapUiSmallMarginBottom"
                                }).addStyleClass("sapUiTinyMarginTop"),
                                new sap.m.TextArea({
                                    id: "csnTextArea",
                                    value: sFormattedJson,
                                    rows: 25,
                                    width: "100%",
                                    editable: false
                                }).addStyleClass("sapUiMonospaceFont")
                            ]
                        }).addStyleClass("sapUiSmallMargin")
                    ],
                    beginButton: new sap.m.Button({
                        text: "Copy to Clipboard",
                        icon: "sap-icon://copy",
                        press: function () {
                            that._copyCSNToClipboard();
                        }
                    }),
                    endButton: new sap.m.Button({
                        text: "Close",
                        press: function () {
                            that._oCsnDialog.close();
                        }
                    })
                });
                
                this.getView().addDependent(this._oCsnDialog);
            } else {
                // Update existing dialog
                this._oCsnDialog.setTitle("CSN Definition - " + sProductName);
                sap.ui.getCore().byId("csnTextArea").setValue(sFormattedJson);
            }
            
            this._oCsnDialog.open();
            MessageToast.show("CSN definition loaded successfully");
        },

        /**
         * Copy CSN to clipboard
         * @private
         */
        _copyCSNToClipboard: function () {
            var oTextArea = sap.ui.getCore().byId("csnTextArea");
            var sText = oTextArea.getValue();
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(sText)
                    .then(function () {
                        MessageToast.show("CSN copied to clipboard!");
                    })
                    .catch(function (err) {
                        MessageToast.show("Failed to copy: " + err.message);
                    });
            } else {
                MessageToast.show("Clipboard not available in this browser");
            }
        },

        /**
         * Navigate to Data Products
         * @public
         */
        onNavToDataProducts: function () {
            var oRouter = this.getOwnerComponent().getRouter();
            oRouter.navTo("dataProducts");
        },

        /**
         * Navigate to Explorer
         * @public
         */
        onNavToExplorer: function () {
            MessageToast.show("Explorer page coming soon!");
            // var oRouter = this.getOwnerComponent().getRouter();
            // oRouter.navTo("explorer");
        },

        /**
         * Navigate to HANA Connection
         * @public
         */
        onNavToHanaConnection: function () {
            MessageToast.show("HANA Connection page coming soon!");
            // var oRouter = this.getOwnerComponent().getRouter();
            // oRouter.navTo("hanaConnection");
        },

        /**
         * Switch to custom theme (navigate to old app)
         * @public
         */
        onSwitchTheme: function () {
            MessageToast.show("Switching to custom HTML version...");
            // Navigate to the custom HTML version
            window.location.href = "index.html";
        }
    });
});
