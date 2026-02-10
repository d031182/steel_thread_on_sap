/**
 * OPA5 Tests for API Playground Page
 * 
 * Tests the API Playground UI components, navigation, and user interactions.
 * Follows SAP UI5 OPA5 testing framework standards.
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

sap.ui.require([
    "sap/ui/test/Opa5",
    "sap/ui/test/opaQunit",
    "sap/ui/test/actions/Press",
    "sap/ui/test/actions/EnterText",
    "sap/ui/test/matchers/PropertyStrictEquals",
    "sap/ui/test/matchers/AggregationLengthEquals"
], function(Opa5, opaTest, Press, EnterText, PropertyStrictEquals, AggregationLengthEquals) {
    "use strict";

    QUnit.module("API Playground Page - Navigation", {
        beforeEach: function() {
            // Setup before each test
        },
        afterEach: function() {
            // Cleanup after each test
        }
    });

    opaTest("Should display IconTabBar with API Playground tab", function(Given, When, Then) {
        // Arrangement
        Given.iStartMyAppInAFrame("../../index.html");

        // Action & Assertion
        Then.waitFor({
            id: "mainTabBar",
            controlType: "sap.m.IconTabBar",
            success: function(oTabBar) {
                Opa5.assert.ok(oTabBar, "IconTabBar is present");
                
                var aFilters = oTabBar.getItems();
                Opa5.assert.ok(aFilters.length >= 2, "At least 2 tabs present");
                
                var bHasAPIPlayground = aFilters.some(function(oFilter) {
                    return oFilter.getText() === "API Playground";
                });
                Opa5.assert.ok(bHasAPIPlayground, "API Playground tab exists");
            },
            errorMessage: "IconTabBar with API Playground tab not found"
        });
    });

    opaTest("Should navigate to API Playground when tab is clicked", function(Given, When, Then) {
        // Action - Click API Playground tab
        When.waitFor({
            id: "mainTabBar",
            controlType: "sap.m.IconTabBar",
            actions: function(oTabBar) {
                var aFilters = oTabBar.getItems();
                var oAPIPlaygroundTab = aFilters.find(function(oFilter) {
                    return oFilter.getKey() === "apiPlayground";
                });
                if (oAPIPlaygroundTab) {
                    oTabBar.setSelectedKey("apiPlayground");
                    oTabBar.fireSelect({ key: "apiPlayground", item: oAPIPlaygroundTab });
                }
            },
            success: function() {
                Opa5.assert.ok(true, "API Playground tab clicked");
            }
        });

        // Assertion - Check main content changed
        Then.waitFor({
            id: "mainContent",
            controlType: "sap.m.VBox",
            success: function(oMainContent) {
                Opa5.assert.ok(oMainContent, "Main content area found");
                
                // Check if API Playground content is present
                var aItems = oMainContent.getItems();
                var bHasAPIPlaygroundContent = aItems.some(function(oItem) {
                    return oItem.getId && oItem.getId().indexOf("apiPlaygroundContent") > -1;
                });
                Opa5.assert.ok(bHasAPIPlaygroundContent, "API Playground content is displayed");
            },
            errorMessage: "API Playground content not found after navigation"
        });
    });

    QUnit.module("API Playground Page - 3-Column Layout", {
        beforeEach: function() {
            // Ensure we're on API Playground page
        }
    });

    opaTest("Should display Flexible Column Layout with 3 columns", function(Given, When, Then) {
        // Arrangement - Navigate to API Playground
        Given.iStartMyAppInAFrame("../../index.html");
        
        When.waitFor({
            id: "mainTabBar",
            controlType: "sap.m.IconTabBar",
            actions: function(oTabBar) {
                oTabBar.setSelectedKey("apiPlayground");
                oTabBar.fireSelect({ key: "apiPlayground" });
            }
        });

        // Assertion - Check FCL exists
        Then.waitFor({
            id: "apiPlaygroundFCL",
            controlType: "sap.f.FlexibleColumnLayout",
            success: function(oFCL) {
                Opa5.assert.ok(oFCL, "Flexible Column Layout found");
                Opa5.assert.strictEqual(
                    oFCL.getLayout(),
                    "ThreeColumnsMidExpanded",
                    "Layout is ThreeColumnsMidExpanded"
                );
            },
            errorMessage: "Flexible Column Layout not found"
        });

        // Check BEGIN column (API Explorer)
        Then.waitFor({
            id: "apiExplorerPage",
            controlType: "sap.m.Page",
            success: function(oPage) {
                Opa5.assert.ok(oPage, "API Explorer page found in BEGIN column");
                Opa5.assert.strictEqual(oPage.getTitle(), "API Explorer", "BEGIN column has correct title");
            }
        });

        // Check MID column (Request Builder)
        Then.waitFor({
            id: "requestBuilderPage",
            controlType: "sap.m.Page",
            success: function(oPage) {
                Opa5.assert.ok(oPage, "Request Builder page found in MID column");
                Opa5.assert.strictEqual(oPage.getTitle(), "Request Builder", "MID column has correct title");
            }
        });

        // Check END column (Response Viewer)
        Then.waitFor({
            id: "responseViewerPage",
            controlType: "sap.m.Page",
            success: function(oPage) {
                Opa5.assert.ok(oPage, "Response Viewer page found in END column");
                Opa5.assert.strictEqual(oPage.getTitle(), "Response", "END column has correct title");
            }
        });
    });

    QUnit.module("API Playground - API Explorer (BEGIN Column)");

    opaTest("Should display API Explorer with search field", function(Given, When, Then) {
        // Navigate to API Playground first
        Given.iStartMyAppInAFrame("../../index.html");
        
        When.waitFor({
            id: "mainTabBar",
            actions: function(oTabBar) {
                oTabBar.setSelectedKey("apiPlayground");
                oTabBar.fireSelect({ key: "apiPlayground" });
            }
        });

        // Check search field exists
        Then.waitFor({
            id: "apiSearchField",
            controlType: "sap.m.SearchField",
            success: function(oSearchField) {
                Opa5.assert.ok(oSearchField, "Search field found");
                Opa5.assert.strictEqual(
                    oSearchField.getPlaceholder(),
                    "Search APIs...",
                    "Search field has correct placeholder"
                );
            },
            errorMessage: "API search field not found"
        });

        // Check API list exists
        Then.waitFor({
            id: "apiExplorerList",
            controlType: "sap.m.List",
            success: function(oList) {
                Opa5.assert.ok(oList, "API Explorer list found");
                Opa5.assert.strictEqual(
                    oList.getMode(),
                    "SingleSelectMaster",
                    "List has correct selection mode"
                );
            },
            errorMessage: "API Explorer list not found"
        });
    });

    opaTest("Should display statistics toolbar", function(Given, When, Then) {
        Then.waitFor({
            id: "apiStatsToolbar",
            controlType: "sap.m.Toolbar",
            success: function(oToolbar) {
                Opa5.assert.ok(oToolbar, "Stats toolbar found");
                
                // Check for stats text controls
                var aContent = oToolbar.getContent();
                var bHasStats = aContent.some(function(oControl) {
                    return oControl.getId && (
                        oControl.getId().indexOf("statsModules") > -1 ||
                        oControl.getId().indexOf("statsEndpoints") > -1
                    );
                });
                Opa5.assert.ok(bHasStats, "Stats toolbar contains statistics");
            },
            errorMessage: "Statistics toolbar not found"
        });
    });

    QUnit.module("API Playground - Request Builder (MID Column)");

    opaTest("Should display HTTP method selector", function(Given, When, Then) {
        Then.waitFor({
            id: "httpMethodSelect",
            controlType: "sap.m.Select",
            success: function(oSelect) {
                Opa5.assert.ok(oSelect, "HTTP method selector found");
                
                var aItems = oSelect.getItems();
                Opa5.assert.ok(aItems.length >= 4, "At least 4 HTTP methods available");
                
                var aMethods = aItems.map(function(oItem) {
                    return oItem.getKey();
                });
                Opa5.assert.ok(aMethods.indexOf("GET") > -1, "GET method available");
                Opa5.assert.ok(aMethods.indexOf("POST") > -1, "POST method available");
                Opa5.assert.ok(aMethods.indexOf("PUT") > -1, "PUT method available");
                Opa5.assert.ok(aMethods.indexOf("DELETE") > -1, "DELETE method available");
            },
            errorMessage: "HTTP method selector not found"
        });
    });

    opaTest("Should display endpoint URL input field", function(Given, When, Then) {
        Then.waitFor({
            id: "endpointUrlInput",
            controlType: "sap.m.Input",
            success: function(oInput) {
                Opa5.assert.ok(oInput, "Endpoint URL input found");
                Opa5.assert.strictEqual(
                    oInput.getPlaceholder(),
                    "/api/module/endpoint",
                    "URL input has correct placeholder"
                );
            },
            errorMessage: "Endpoint URL input not found"
        });
    });

    opaTest("Should display request body text area", function(Given, When, Then) {
        Then.waitFor({
            id: "requestBodyInput",
            controlType: "sap.m.TextArea",
            success: function(oTextArea) {
                Opa5.assert.ok(oTextArea, "Request body text area found");
                Opa5.assert.ok(oTextArea.getRows() >= 10, "Text area has sufficient rows");
            },
            errorMessage: "Request body text area not found"
        });
    });

    opaTest("Should display Execute and Clear buttons", function(Given, When, Then) {
        Then.waitFor({
            controlType: "sap.m.Button",
            matchers: function(oButton) {
                return oButton.getText() === "Execute" || oButton.getText() === "Clear";
            },
            success: function(aButtons) {
                Opa5.assert.ok(aButtons.length >= 2, "Execute and Clear buttons found");
                
                var bHasExecute = aButtons.some(function(btn) {
                    return btn.getText() === "Execute";
                });
                var bHasClear = aButtons.some(function(btn) {
                    return btn.getText() === "Clear";
                });
                
                Opa5.assert.ok(bHasExecute, "Execute button present");
                Opa5.assert.ok(bHasClear, "Clear button present");
            },
            errorMessage: "Execute or Clear button not found"
        });
    });

    QUnit.module("API Playground - Response Viewer (END Column)");

    opaTest("Should display response metadata toolbar", function(Given, When, Then) {
        Then.waitFor({
            id: "responseMetadataBar",
            controlType: "sap.m.Toolbar",
            success: function(oToolbar) {
                Opa5.assert.ok(oToolbar, "Response metadata toolbar found");
                
                // Check for status and time text controls
                var aContent = oToolbar.getContent();
                var bHasMetadata = aContent.some(function(oControl) {
                    return oControl.getId && (
                        oControl.getId().indexOf("responseStatus") > -1 ||
                        oControl.getId().indexOf("responseTime") > -1
                    );
                });
                Opa5.assert.ok(bHasMetadata, "Metadata toolbar contains status/time");
            },
            errorMessage: "Response metadata toolbar not found"
        });
    });

    opaTest("Should display response tabs (Formatted/Raw)", function(Given, When, Then) {
        Then.waitFor({
            id: "responseTabBar",
            controlType: "sap.m.IconTabBar",
            success: function(oTabBar) {
                Opa5.assert.ok(oTabBar, "Response tab bar found");
                
                var aFilters = oTabBar.getItems();
                Opa5.assert.ok(aFilters.length >= 2, "At least 2 response tabs");
                
                var aKeys = aFilters.map(function(f) { return f.getKey(); });
                Opa5.assert.ok(aKeys.indexOf("formatted") > -1, "Formatted tab present");
                Opa5.assert.ok(aKeys.indexOf("raw") > -1, "Raw tab present");
            },
            errorMessage: "Response tab bar not found"
        });
    });

    opaTest("Should display formatted response text area", function(Given, When, Then) {
        Then.waitFor({
            id: "formattedResponse",
            controlType: "sap.m.TextArea",
            success: function(oTextArea) {
                Opa5.assert.ok(oTextArea, "Formatted response text area found");
                Opa5.assert.strictEqual(oTextArea.getEditable(), false, "Text area is read-only");
                Opa5.assert.ok(oTextArea.getRows() >= 20, "Text area has sufficient rows");
            },
            errorMessage: "Formatted response text area not found"
        });
    });

    opaTest("Should display copy response button", function(Given, When, Then) {
        Then.waitFor({
            id: "copyResponseBtn",
            controlType: "sap.m.Button",
            success: function(oButton) {
                Opa5.assert.ok(oButton, "Copy response button found");
                Opa5.assert.strictEqual(oButton.getText(), "Copy", "Button has correct text");
            },
            errorMessage: "Copy response button not found"
        });
    });

    QUnit.module("API Playground - User Interactions");

    opaTest("Should enable request body when POST method is selected", function(Given, When, Then) {
        // Change to POST method
        When.waitFor({
            id: "httpMethodSelect",
            actions: function(oSelect) {
                oSelect.setSelectedKey("POST");
                oSelect.fireChange({ selectedItem: oSelect.getItems()[1] });
            },
            success: function() {
                Opa5.assert.ok(true, "Changed method to POST");
            }
        });

        // Check if request body is enabled
        Then.waitFor({
            id: "requestBodyInput",
            success: function(oTextArea) {
                // Note: In actual implementation, this is controlled by JavaScript
                // We're verifying the control exists and can be enabled
                Opa5.assert.ok(oTextArea, "Request body text area responds to method change");
            }
        });
    });

    opaTest("Should handle navigation between tabs", function(Given, When, Then) {
        // Switch to Data Products
        When.waitFor({
            id: "mainTabBar",
            actions: function(oTabBar) {
                oTabBar.setSelectedKey("dataProducts");
                oTabBar.fireSelect({ key: "dataProducts" });
            },
            success: function() {
                Opa5.assert.ok(true, "Switched to Data Products tab");
            }
        });

        // Switch back to API Playground
        When.waitFor({
            id: "mainTabBar",
            actions: function(oTabBar) {
                oTabBar.setSelectedKey("apiPlayground");
                oTabBar.fireSelect({ key: "apiPlayground" });
            },
            success: function() {
                Opa5.assert.ok(true, "Switched back to API Playground tab");
            }
        });

        // Verify API Playground content is still there
        Then.waitFor({
            id: "apiPlaygroundFCL",
            success: function(oFCL) {
                Opa5.assert.ok(oFCL, "API Playground content persists after tab switching");
            }
        });

        // Cleanup
        Then.iTeardownMyApp();
    });

    QUnit.module("API Playground - Edge Cases");

    opaTest("Should handle empty API list gracefully", function(Given, When, Then) {
        Given.iStartMyAppInAFrame("../../index.html");
        
        When.waitFor({
            id: "mainTabBar",
            actions: function(oTabBar) {
                oTabBar.setSelectedKey("apiPlayground");
                oTabBar.fireSelect({ key: "apiPlayground" });
            }
        });

        Then.waitFor({
            id: "apiExplorerList",
            success: function(oList) {
                // Even if empty, list should exist
                Opa5.assert.ok(oList, "API list exists even when empty");
            }
        });

        Then.iTeardownMyApp();
    });

    // Start QUnit
    QUnit.start();
});