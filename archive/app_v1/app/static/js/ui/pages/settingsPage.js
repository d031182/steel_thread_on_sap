/**
 * Settings Page Module
 * 
 * Handles the application settings dialog for managing feature flags.
 * Provides toggle controls for enabling/disabling application features.
 * 
 * @author P2P Development Team
 * @version 2.0.0
 */

/**
 * Open the settings dialog
 */
export async function openSettingsDialog() {
    sap.ui.core.BusyIndicator.show(0);
    
    try {
        // Fetch features from API
        const response = await fetch("/api/features");
        const data = await response.json();
        
        if (!data || !data.success) {
            throw new Error(data?.error || "Failed to load features");
        }
        
        const featuresObj = data.features.features || data.features;
        
        // Create settings dialog
        const oSettingsDialog = createSettingsDialog(featuresObj);
        oSettingsDialog.open();
        
    } catch (error) {
        sap.m.MessageBox.error("Error loading settings: " + error.message);
    } finally {
        sap.ui.core.BusyIndicator.hide();
    }
}

/**
 * Create the settings dialog UI
 */
function createSettingsDialog(features) {
    return new sap.m.Dialog({
        title: "Settings",
        contentWidth: "600px",
        contentHeight: "500px",
        resizable: true,
        draggable: true,
        content: [
            new sap.m.VBox({
                items: [
                    new sap.m.MessageStrip({
                        text: "Enable or disable features. Changes take effect immediately.",
                        type: "Information",
                        showIcon: true
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    createFeaturesList(features)
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
 * Create list of features with toggle switches
 */
function createFeaturesList(features) {
    const oList = new sap.m.List({
        headerText: "Application Features",
        mode: "None"
    });
    
    for (const [key, feature] of Object.entries(features)) {
        const oSwitch = new sap.m.Switch({
            state: feature.enabled || false,
            customTextOn: "ON",
            customTextOff: "OFF",
            change: async function(oEvent) {
                const bState = oEvent.getParameter("state");
                await toggleFeature(key, feature.displayName, bState, oSwitch);
            }
        });
        
        const oItem = new sap.m.InputListItem({
            label: feature.displayName || key,
            content: [oSwitch]
        });
        
        if (feature.description) {
            oItem.setTooltip(feature.description);
        }
        
        oList.addItem(oItem);
    }
    
    return oList;
}

/**
 * Toggle a feature on/off
 */
async function toggleFeature(key, name, state, oSwitch) {
    oSwitch.setBusy(true);
    
    try {
        const response = await fetch(`/api/features/${key}/toggle`, {
            method: "POST"
        });
        const data = await response.json();
        
        if (data && data.success) {
            sap.m.MessageToast.show(`${name} ${data.enabled ? "enabled" : "disabled"}`);
        } else {
            sap.m.MessageToast.show(`Failed to toggle ${name}`);
            oSwitch.setState(!state);
        }
    } catch (error) {
        sap.m.MessageToast.show(`Error: ${error.message}`);
        oSwitch.setState(!state);
    } finally {
        oSwitch.setBusy(false);
    }
}