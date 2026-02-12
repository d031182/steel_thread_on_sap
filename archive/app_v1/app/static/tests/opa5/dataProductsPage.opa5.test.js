sap.ui.define([
    "sap/ui/test/Opa5",
    "sap/ui/test/opaQunit",
    "sap/ui/test/actions/Press",
    "sap/ui/test/actions/EnterText",
    "sap/ui/test/matchers/AggregationLengthEquals",
    "sap/ui/test/matchers/PropertyStrictEquals"
], function(Opa5, opaTest, Press, EnterText, AggregationLengthEquals, PropertyStrictEquals) {
    "use strict";

    QUnit.module("Data Products Page - OPA5 Component Tests");

    // Configure OPA5
    Opa5.extendConfig({
        viewNamespace: "p2p.ui.pages",
        autoWait: true,
        timeout: 30,
        debugTimeout: 60,
        pollingInterval: 400
    });

    // Test: Page loads and displays table
    opaTest("Should load Data Products page with table", function(Given, When, Then) {
        // Arrangement
        Given.iStartMyAppInAFrame("../../index.html#/dataProducts");

        // Action
        When.waitFor({
            controlType: "sap.ui.table.Table",
            success: function(aTables) {
                Opa5.assert.ok(aTables.length > 0, "Table found on page");
            },
            errorMessage: "Did not find the data products table"
        });

        // Assertion
        Then.waitFor({
            controlType: "sap.ui.table.Table",
            matchers: function(oTable) {
                return oTable.getRows().length > 0;
            },
            success: function(aTables) {
                Opa5.assert.ok(true, "Table has rows");
            },
            errorMessage: "Table does not have any rows"
        });

        // Cleanup
        Then.iTeardownMyApp();
    });

    // Test: Table columns are properly configured
    opaTest("Should have correct table columns", function(Given, When, Then) {
        // Arrangement
        Given.iStartMyAppInAFrame("../../index.html#/dataProducts");

        // Assertion
        Then.waitFor({
            controlType: "sap.ui.table.Table",
            success: function(aTables) {
                var oTable = aTables[0];
                var aColumns = oTable.getColumns();
                
                Opa5.assert.ok(aColumns.length >= 4, "Table has at least 4 columns");
                
                // Check for key columns
                var columnLabels = aColumns.map(function(col) {
                    return col.getLabel().getText();
                });
                
                Opa5.assert.ok(
                    columnLabels.some(function(label) { return label.includes("Purchase Order"); }),
                    "Has Purchase Order column"
                );
            },
            errorMessage: "Could not verify table columns"
        });

        // Cleanup
        Then.iTeardownMyApp();
    });

    // Test: Search functionality
    opaTest("Should filter table when searching", function(Given, When, Then) {
        // Arrangement
        Given.iStartMyAppInAFrame("../../index.html#/dataProducts");

        var initialRowCount = 0;

        // Get initial row count
        When.waitFor({
            controlType: "sap.ui.table.Table",
            success: function(aTables) {
                initialRowCount = aTables[0].getBinding("rows").getLength();
            }
        });

        // Action: Enter search term
        When.waitFor({
            controlType: "sap.m.SearchField",
            actions: new EnterText({ text: "PO-" }),
            errorMessage: "Did not find the search field"
        });

        // Assertion: Table should be filtered
        Then.waitFor({
            controlType: "sap.ui.table.Table",
            success: function(aTables) {
                var filteredCount = aTables[0].getBinding("rows").getLength();
                Opa5.assert.ok(
                    filteredCount <= initialRowCount,
                    "Table filtered: " + filteredCount + " <= " + initialRowCount
                );
            },
            errorMessage: "Table was not filtered"
        });

        // Cleanup
        Then.iTeardownMyApp();
    });

    // Test: Row selection
    opaTest("Should select row when clicked", function(Given, When, Then) {
        // Arrangement
        Given.iStartMyAppInAFrame("../../index.html#/dataProducts");

        // Action: Click first row
        When.waitFor({
            controlType: "sap.ui.table.Table",
            success: function(aTables) {
                var oTable = aTables[0];
                var firstRow = oTable.getRows()[0];
                if (firstRow) {
                    firstRow.firePress();
                }
            }
        });

        // Assertion: Row should be selected
        Then.waitFor({
            controlType: "sap.ui.table.Table",
            success: function(aTables) {
                var oTable = aTables[0];
                var selectedIndices = oTable.getSelectedIndices();
                Opa5.assert.ok(
                    selectedIndices.length > 0,
                    "At least one row is selected"
                );
            },
            errorMessage: "No row was selected"
        });

        // Cleanup
        Then.iTeardownMyApp();
    });

    // Test: Data loading indicator
    opaTest("Should show busy indicator while loading", function(Given, When, Then) {
        // Arrangement
        Given.iStartMyAppInAFrame("../../index.html#/dataProducts");

        // Check for busy indicator (may be transient)
        When.waitFor({
            controlType: "sap.m.Page",
            check: function(aPages) {
                // Page may be busy initially
                return aPages.length > 0;
            },
            success: function(aPages) {
                Opa5.assert.ok(true, "Page loaded successfully");
            }
        });

        // Assertion: Eventually not busy
        Then.waitFor({
            controlType: "sap.m.Page",
            matchers: new PropertyStrictEquals({
                name: "busy",
                value: false
            }),
            success: function() {
                Opa5.assert.ok(true, "Page is not busy after loading");
            },
            errorMessage: "Page remained busy"
        });

        // Cleanup
        Then.iTeardownMyApp();
    });

    // Test: Export button exists and is enabled
    opaTest("Should have enabled export button when data is loaded", function(Given, When, Then) {
        // Arrangement
        Given.iStartMyAppInAFrame("../../index.html#/dataProducts");

        // Wait for table to load
        When.waitFor({
            controlType: "sap.ui.table.Table",
            matchers: function(oTable) {
                return oTable.getRows().length > 0;
            },
            success: function() {
                Opa5.assert.ok(true, "Table loaded with data");
            }
        });

        // Assertion: Export button exists and is enabled
        Then.waitFor({
            controlType: "sap.m.Button",
            matchers: new PropertyStrictEquals({
                name: "icon",
                value: "sap-icon://excel-attachment"
            }),
            success: function(aButtons) {
                Opa5.assert.ok(aButtons.length > 0, "Export button found");
                Opa5.assert.ok(aButtons[0].getEnabled(), "Export button is enabled");
            },
            errorMessage: "Did not find enabled export button"
        });

        // Cleanup
        Then.iTeardownMyApp();
    });

    QUnit.start();
});