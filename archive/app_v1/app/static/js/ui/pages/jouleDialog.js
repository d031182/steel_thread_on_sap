/**
 * Joule-Style AI Assistant Dialog
 * 
 * SAP Joule-inspired popup dialog with purple gradient branding.
 * Opens as overlay window, doesn't replace main content.
 */

import { initializeAIAssistant } from './aiAssistantPage.js';

let jouleDialog = null;

/**
 * Open Joule AI Assistant Dialog
 */
export function openJouleDialog() {
    // Create dialog if it doesn't exist
    if (!jouleDialog) {
        jouleDialog = createJouleDialog();
    }
    
    // Open dialog
    jouleDialog.open();
}

/**
 * Create Joule-style Dialog
 */
function createJouleDialog() {
    // View model for chat state
    const oViewModel = new sap.ui.model.json.JSONModel({
        messages: [],
        currentMessage: "",
        isLoading: false,
        currentDataProduct: "",
        currentSchema: "",
        currentTable: ""
    });
    
    // Store model reference
    window.jouleModel = oViewModel;
    
    // Purple gradient header with diamond logo
    const oHeader = new sap.m.VBox({
        items: [
            new sap.m.HBox({
                justifyContent: "Center",
                alignItems: "Center",
                items: [
                    new sap.ui.core.Icon({
                        src: "sap-icon://rhombus-milestone",
                        size: "3rem",
                        color: "#ffffff"
                    }).addStyleClass("jouleDiamond")
                ]
            }).addStyleClass("jouleHeader"),
            new sap.m.Title({
                text: "How can I help you?",
                level: "H2",
                textAlign: "Center"
            }).addStyleClass("jouleGreeting")
        ]
    }).addStyleClass("jouleHeaderContainer");
    
    // Message List
    const oMessageList = new sap.m.List("jouleMessageList", {
        mode: "None",
        growing: true,
        growingThreshold: 20,
        growingScrollToLoad: true,
        noDataText: "Talk to me naturally. For example, 'I want to view suppliers'",
        items: {
            path: "/messages",
            template: new sap.m.FeedListItem({
                sender: "{sender}",
                timestamp: "{timestamp}",
                text: "{text}",
                icon: {
                    path: "type",
                    formatter: function (sType) {
                        return sType === "user" 
                            ? "sap-icon://person-placeholder" 
                            : "sap-icon://rhombus-milestone";
                    }
                },
                iconDensityAware: false
            })
        },
        updateFinished: function() {
            const aItems = this.getItems();
            aItems.forEach((oItem) => {
                if (oItem instanceof sap.m.FeedListItem) {
                    const oBinding = oItem.getBinding("text");
                    if (oBinding) {
                        const oContext = oBinding.getContext();
                        if (oContext) {
                            const sType = oContext.getProperty("type");
                            oItem.removeStyleClass("userMessage");
                            oItem.removeStyleClass("aiMessage");
                            oItem.addStyleClass(sType === "user" ? "userMessage" : "aiMessage");
                        }
                    }
                }
            });
        }
    }).addStyleClass("jouleMessageList");
    
    oMessageList.setModel(oViewModel);
    
    // Loading indicator
    const oLoadingItem = new sap.m.CustomListItem({
        visible: "{/isLoading}",
        content: [
            new sap.m.HBox({
                alignItems: "Center",
                justifyContent: "Start",
                items: [
                    new sap.m.BusyIndicator({ size: "1rem" }).addStyleClass("sapUiTinyMarginEnd"),
                    new sap.m.Text({ text: "AI is thinking..." }).addStyleClass("sapUiTinyMarginBegin")
                ]
            })
        ]
    }).addStyleClass("aiLoadingMessage");
    
    oLoadingItem.setModel(oViewModel);
    oMessageList.addItem(oLoadingItem);
    
    // Input Area - Use sap.m.TextArea with growing (like Joule)
    const oTextArea = new sap.m.TextArea("jouleMessageInput", {
        value: "{/currentMessage}",
        placeholder: "Message Joule...",
        width: "100%",
        rows: 1,
        growing: true,
        growingMaxLines: 5,
        valueLiveUpdate: true
    });
    
    oTextArea.setModel(oViewModel);
    
    // Bind enabled property
    oTextArea.bindProperty("enabled", {
        path: "/isLoading",
        formatter: function (bLoading) {
            return Boolean(!bLoading);
        }
    });
    
    // Handle Enter key to send (Shift+Enter for newline)
    oTextArea.attachBrowserEvent("keypress", function (oEvent) {
        if (oEvent.key === "Enter" && !oEvent.shiftKey) {
            oEvent.preventDefault();
            handleSendMessage();
        }
    });
    
    const oSendButton = new sap.m.Button({
        icon: "sap-icon://paper-plane",
        type: "Emphasized",
        press: handleSendMessage,
        tooltip: "Send"
    });
    
    oSendButton.setModel(oViewModel);
    
    // Bind enabled property
    oSendButton.bindProperty("enabled", {
        parts: [
            { path: "/currentMessage" },
            { path: "/isLoading" }
        ],
        formatter: function (sMessage, bLoading) {
            return Boolean(sMessage && sMessage.trim().length > 0 && !bLoading);
        }
    });
    
    // Use sap.m.Bar (standard Fiori footer bar)
    // contentMiddle takes most space, contentRight for button
    const oInputBar = new sap.m.Bar({
        contentMiddle: [oTextArea],
        contentRight: [oSendButton]
    });
    
    // Dialog
    const oDialog = new sap.m.Dialog({
        title: "Joule",
        icon: "sap-icon://rhombus-milestone",
        contentWidth: "600px",
        contentHeight: "700px",
        resizable: true,
        draggable: true,
        content: [
            oHeader,
            oMessageList,
            oInputBar
        ],
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterOpen: async function() {
            // Load CSS
            if (!document.querySelector('link[href*="joule.css"]')) {
                loadCSS('/modules/ai_assistant/frontend/joule.css');
            }
            
            // Initialize AI
            await initializeAIAssistant();
        }
    }).addStyleClass("jouleDialog");
    
    return oDialog;
}

/**
 * Load CSS dynamically
 */
function loadCSS(href) {
    try {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        document.head.appendChild(link);
        console.log('✓ Loaded CSS:', href);
    } catch (error) {
        console.error('Error loading CSS:', error);
    }
}

/**
 * Handle send message
 */
function handleSendMessage() {
    const oModel = window.jouleModel;
    if (!oModel) return;
    
    const sMessage = oModel.getProperty("/currentMessage").trim();
    
    if (!sMessage) {
        return;
    }
    
    // Add user message
    addMessage({
        type: "user",
        sender: "You",
        text: sMessage,
        timestamp: new Date().toLocaleTimeString()
    });
    
    // Clear input and show loading
    oModel.setProperty("/currentMessage", "");
    oModel.setProperty("/isLoading", true);
    
    // Call AI API
    callAIAPI(sMessage);
}

/**
 * Add message to list
 */
function addMessage(oMessage) {
    const oModel = window.jouleModel;
    if (!oModel) return;
    
    const aMessages = oModel.getProperty("/messages");
    aMessages.push(oMessage);
    oModel.setProperty("/messages", aMessages);
}

/**
 * Call AI Assistant API
 */
function callAIAPI(sPrompt) {
    const oModel = window.jouleModel;
    if (!oModel) return;
    
    const oContext = getContext();
    
    fetch("/api/ai-assistant/query", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            prompt: sPrompt,
            context: oContext
        })
    })
    .then(response => response.json())
    .then(data => {
        oModel.setProperty("/isLoading", false);
        
        if (data.success) {
            addMessage({
                type: "ai",
                sender: "Joule",
                text: formatResponse(data.response),
                timestamp: new Date().toLocaleTimeString(),
                tokensUsed: data.tokens_used
            });
            
            scrollToBottom();
            
            if (data.tokens_used) {
                sap.m.MessageToast.show(`Response received (${data.tokens_used} tokens)`);
            }
        } else {
            sap.m.MessageBox.error(
                "Failed to get AI response:\n\n" + (data.error || "Unknown error"),
                { title: "AI Error" }
            );
        }
    })
    .catch(error => {
        oModel.setProperty("/isLoading", false);
        const errorMsg = error && error.message ? error.message : String(error || 'Unknown error');
        sap.m.MessageBox.error(
            "Network error:\n\n" + errorMsg,
            {
                title: "Connection Error",
                actions: [sap.m.MessageBox.Action.OK, "Retry"],
                onClose: function (sAction) {
                    if (sAction === "Retry") {
                        callAIAPI(sPrompt);
                    }
                }
            }
        );
    });
}

/**
 * Get current context
 */
function getContext() {
    const oModel = window.jouleModel;
    if (!oModel) return {};
    
    const oContext = {};
    
    const sDataProduct = oModel.getProperty("/currentDataProduct");
    const sSchema = oModel.getProperty("/currentSchema");
    const sTable = oModel.getProperty("/currentTable");
    
    if (sDataProduct) oContext.data_product = sDataProduct;
    if (sSchema) oContext.current_schema = sSchema;
    if (sTable) oContext.current_table = sTable;
    
    return oContext;
}

/**
 * Format AI response (remove technical wrappers)
 */
function formatResponse(sResponse) {
    if (!sResponse) {
        return "No response received.";
    }
    
    // Remove AgentRunResult wrapper if present
    let match = sResponse.match(/AgentRunResult\(output="(.*)"\)/s);
    if (!match) {
        match = sResponse.match(/AgentRunResult\(output='(.*)'\)/s);
    }
    
    if (match && match[1]) {
        let cleaned = match[1];
        cleaned = cleaned.replace(/\\n/g, '\n');
        cleaned = cleaned.replace(/\\t/g, '\t');
        cleaned = cleaned.replace(/\\"/g, '"');
        cleaned = cleaned.replace(/\\'/g, "'");
        return cleaned;
    }
    
    return sResponse;
}

/**
 * Scroll to bottom of message list
 */
function scrollToBottom() {
    setTimeout(() => {
        const oList = sap.ui.getCore().byId("jouleMessageList");
        if (oList) {
            const aItems = oList.getItems();
            if (aItems.length > 1) {
                const iLastIndex = aItems.length - 2;
                if (iLastIndex >= 0) {
                    oList.scrollToIndex(iLastIndex);
                }
            }
        }
    }, 100);
}