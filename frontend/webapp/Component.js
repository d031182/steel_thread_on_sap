sap.ui.define([
    "sap/ui/core/UIComponent",
    "sap/ui/model/json/JSONModel",
    "p2p/dataproducts/model/models"
], function (UIComponent, JSONModel, models) {
    "use strict";

    return UIComponent.extend("p2p.dataproducts.Component", {
        metadata: {
            manifest: "json"
        },

        /**
         * The component is initialized by UI5 automatically during the startup of the app and calls the init method once.
         * @public
         * @override
         */
        init: function () {
            // Call the base component's init function
            UIComponent.prototype.init.apply(this, arguments);

            // Set the device model
            this.setModel(models.createDeviceModel(), "device");

            // Create and set the app data model
            var oAppModel = new JSONModel({
                // Data Products
                dataProducts: [
                    {
                        id: "supplier",
                        name: "Supplier",
                        subtitle: "Vendor Master Data",
                        icon: "sap-icon://supplier",
                        description: "Vendor master data definition including contact information, banking details, and payment terms",
                        type: "Master Data",
                        tablesCount: 1,
                        samplesCount: 3
                    },
                    {
                        id: "purchaseOrder",
                        name: "Purchase Order",
                        subtitle: "Procurement Documents",
                        icon: "sap-icon://sales-order",
                        description: "Purchase order header and item definitions with supplier confirmation tracking",
                        type: "Transaction",
                        tablesCount: 2,
                        samplesCount: 5
                    },
                    {
                        id: "serviceEntry",
                        name: "Service Entry Sheet",
                        subtitle: "Service Confirmations",
                        icon: "sap-icon://wrench",
                        description: "Service confirmation documents with acceptance workflow",
                        type: "Transaction",
                        tablesCount: 2,
                        samplesCount: 4
                    },
                    {
                        id: "supplierInvoice",
                        name: "Supplier Invoice",
                        subtitle: "Accounts Payable Documents",
                        icon: "sap-icon://money-bills",
                        description: "Invoice header and item definitions with variance tracking and payment status",
                        type: "Transaction",
                        tablesCount: 2,
                        samplesCount: 7
                    },
                    {
                        id: "paymentTerms",
                        name: "Payment Terms",
                        subtitle: "Payment Conditions",
                        icon: "sap-icon://payment-approval",
                        description: "Payment terms master data with discount structures",
                        type: "Master Data",
                        tablesCount: 1,
                        samplesCount: 3
                    },
                    {
                        id: "journalEntry",
                        name: "Journal Entry Header",
                        subtitle: "Financial Accounting Documents",
                        icon: "sap-icon://activity-items",
                        description: "Financial accounting documents with GL postings for invoice posting and payment clearing",
                        type: "Transaction",
                        tablesCount: 2,
                        samplesCount: 5
                    }
                ],
                // Explorer state
                explorer: {
                    installedProducts: [],
                    selectedProduct: null,
                    selectedTable: null,
                    tableData: [],
                    loading: false
                },
                // HANA Connection state
                hanaConnection: {
                    instances: [],
                    selectedInstance: null,
                    sqlQuery: "",
                    queryResults: [],
                    queryStatus: null,
                    templates: {
                        check_user: "-- Check if P2P_DP_USER exists\nSELECT USER_NAME, CREATOR, CREATE_TIME, USER_DEACTIVATED\nFROM SYS.USERS \nWHERE USER_NAME = 'P2P_DP_USER';",
                        list_schemas: "-- List all schemas\nSELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME\nFROM SYS.SCHEMAS\nORDER BY SCHEMA_NAME;",
                        list_tables: "-- List tables in P2P_DATA_PRODUCTS schema\nSELECT TABLE_NAME, TABLE_TYPE\nFROM SYS.TABLES\nWHERE SCHEMA_NAME = 'P2P_DATA_PRODUCTS'\nORDER BY TABLE_NAME;",
                        check_privileges: "-- Check P2P_DP_USER privileges\nSELECT GRANTEE, PRIVILEGE, OBJECT_TYPE, IS_GRANTABLE\nFROM SYS.GRANTED_PRIVILEGES\nWHERE GRANTEE = 'P2P_DP_USER'\nORDER BY OBJECT_TYPE, PRIVILEGE;"
                    }
                }
            });
            this.setModel(oAppModel);

            // Initialize APIs (will be loaded from existing js/api/ folder)
            this._initializeAPIs();

            // Create the views based on the url/hash
            this.getRouter().initialize();
        },

        /**
         * Initialize existing APIs for use in SAPUI5 controllers
         * Reuses existing API-first implementation
         * @private
         */
        _initializeAPIs: function() {
            // APIs will be dynamically imported in controllers as needed
            // This preserves the API-first architecture
            this._apis = {
                sqlExecution: null,  // Loaded on demand
                dataProducts: null,   // Loaded on demand
                hanaConnection: null, // Loaded on demand
                resultFormatter: null // Loaded on demand
            };
        },

        /**
         * Get API instance (lazy loading)
         * @param {string} apiName - Name of the API
         * @returns {Object} API instance
         * @public
         */
        getAPI: function(apiName) {
            return this._apis[apiName];
        },

        /**
         * Set API instance
         * @param {string} apiName - Name of the API
         * @param {Object} apiInstance - API instance
         * @public
         */
        setAPI: function(apiName, apiInstance) {
            this._apis[apiName] = apiInstance;
        },

        /**
         * Get content density class for responsive design
         * @returns {string} CSS class for content density
         * @public
         */
        getContentDensityClass: function() {
            if (!this._sContentDensityClass) {
                if (!sap.ui.Device.support.touch) {
                    this._sContentDensityClass = "sapUiSizeCompact";
                } else {
                    this._sContentDensityClass = "sapUiSizeCozy";
                }
            }
            return this._sContentDensityClass;
        }
    });
});
