/**
 * AI Assistant Page Module
 * 
 * Chat interface for natural language queries about P2P data products.
 * Uses Pydantic AI + Groq for AI-powered analysis.
 * 
 * Pure JavaScript implementation (no XML views) for easier debugging.
 */

/**
 * Create AI Assistant page content
 * @returns {sap.m.VBox} Page content
 */
export function createAIAssistantPage() {
    // View model for chat state
    const oViewModel = new sap.ui.model.json.JSONModel({
        messages: [],
        currentMessage: "",
        isLoading: false,
        currentDataProduct: "",
        currentSchema: "",
        currentTable: "",
        contextVisible: false
    });
    
    // Store model reference for access in functions
    window.aiAssistantModel = oViewModel;
    
    // Context Panel (collapsible)
    const oContextPanel = new sap.m.Panel({
        headerText: "Current Context",
        expandable: true,
        expanded: "{/contextVisible}",
        content: [
            new sap.m.VBox({
                items: [
                    new sap.m.Label({ text: "Data Product:" }).addStyleClass("sapUiTinyMarginBottom"),
                    new sap.m.Text({ text: "{/currentDataProduct}" }).addStyleClass("sapUiSmallMarginBottom"),
                    new sap.m.Label({ text: "Schema:" }).addStyleClass("sapUiTinyMarginBottom"),
                    new sap.m.Text({ text: "{/currentSchema}" }).addStyleClass("sapUiSmallMarginBottom"),
                    new sap.m.Label({ text: "Table:" }).addStyleClass("sapUiTinyMarginBottom"),
                    new sap.m.Text({ text: "{/currentTable}" })
                ]
            })
        ]
    }).addStyleClass("sapUiResponsiveMargin contextPanel");
    
    oContextPanel.setModel(oViewModel);
    
    // Message List
    const oMessageList = new sap.m.List("aiMessageList", {
        mode: "None",
        growing: true,
        growingThreshold: 20,
        growingScrollToLoad: true,
        noDataText: "Start a conversation with the AI Assistant...",
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
            // Apply styling after list updates
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
    }).addStyleClass("sapUiResponsiveMargin chatMessageList");
    
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
    
    // Input Area
    const oTextArea = new sap.m.TextArea("aiMessageInput", {
        value: "{/currentMessage}",
        placeholder: "Ask about data products, schemas, or request SQL generation...",
        rows: 2,
        maxLength: 2000,
        width: "100%",
        growing: true,
        growingMaxLines: 5
    });
    
    oTextArea.setModel(oViewModel);
    
    // Bind enabled property after model is set
    oTextArea.bindProperty("enabled", {
        path: "/isLoading",
        formatter: function (bLoading) {
            return Boolean(!bLoading);  // Explicit boolean coercion
        }
    });
    
    // Handle Enter key
    oTextArea.attachBrowserEvent("keydown", function (oEvent) {
        if (oEvent.key === "Enter" && !oEvent.shiftKey) {
            oEvent.preventDefault();
            handleSendMessage();
        }
    });
    
    const oSendButton = new sap.m.Button({
        text: "Send",
        type: "Emphasized",
        icon: "sap-icon://paper-plane",
        press: handleSendMessage
    });
    
    oSendButton.setModel(oViewModel);
    
    // Bind enabled property after model is set
    oSendButton.bindProperty("enabled", {
        parts: [
            { path: "/currentMessage" },
            { path: "/isLoading" }
        ],
        formatter: function (sMessage, bLoading) {
            return Boolean(sMessage && sMessage.trim().length > 0 && !bLoading);  // Explicit boolean coercion
        }
    });
    
    const oInputToolbar = new sap.m.Toolbar({
        content: [
            oTextArea,
            new sap.m.ToolbarSpacer(),
            oSendButton
        ]
    }).addStyleClass("chatInputToolbar");
    
    // Header buttons
    const oClearButton = new sap.m.Button({
        icon: "sap-icon://delete",
        tooltip: "Clear Conversation",
        press: function() {
            sap.m.MessageBox.confirm(
                "Are you sure you want to clear the conversation?",
                {
                    onClose: function(sAction) {
                        if (sAction === sap.m.MessageBox.Action.OK) {
                            oViewModel.setProperty("/messages", []);
                            sap.m.MessageToast.show("Conversation cleared");
                        }
                    }
                }
            );
        }
    });
    
    const oExportButton = new sap.m.Button({
        icon: "sap-icon://download",
        tooltip: "Export Conversation",
        press: function() {
            const aMessages = oViewModel.getProperty("/messages");
            
            if (aMessages.length === 0) {
                sap.m.MessageToast.show("No messages to export");
                return;
            }
            
            const sMarkdown = aMessages.map(msg => {
                return `**${msg.sender}** (${msg.timestamp}):\n${msg.text}\n`;
            }).join("\n---\n\n");
            
            const sFullMarkdown = `# AI Assistant Conversation\n\n**Date**: ${new Date().toLocaleString()}\n\n---\n\n${sMarkdown}`;
            
            // Download
            const blob = new Blob([sFullMarkdown], { type: "text/markdown" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "ai-conversation.md";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            sap.m.MessageToast.show("Conversation exported");
        }
    });
    
    // Main container
    const oContainer = new sap.m.VBox({
        items: [
            new sap.m.HBox({
                justifyContent: "SpaceBetween",
                alignItems: "Center",
                items: [
                    new sap.m.Title({
                        text: "AI Assistant",
                        level: "H2"
                    }),
                    new sap.m.HBox({
                        items: [oClearButton, oExportButton]
                    })
                ]
            }).addStyleClass("sapUiSmallMarginBottom"),
            oContextPanel,
            oMessageList,
            oInputToolbar
        ]
    }).addStyleClass("sapUiContentPadding");
    
    return oContainer;
}

/**
 * Initialize AI Assistant (called when page loads)
 */
export async function initializeAIAssistant() {
    console.log('🤖 Initializing AI Assistant...');
    
    // Load CSS (only once)
    if (!document.querySelector('link[href*="chat.css"]')) {
        loadCSS('/modules/ai_assistant/frontend/chat.css');
    }
    
    // Check API status
    try {
        const response = await fetch('/api/ai-assistant/status');
        const data = await response.json();
        
        if (data && data.ready) {
            console.log('✓ AI Assistant ready:', data.model);
        } else {
            console.warn('⚠ AI Assistant not ready');
        }
    } catch (error) {
        console.error('Error checking AI Assistant status:', error);
    }
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
    const oModel = window.aiAssistantModel;
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
    const oModel = window.aiAssistantModel;
    if (!oModel) return;
    
    const aMessages = oModel.getProperty("/messages");
    aMessages.push(oMessage);
    oModel.setProperty("/messages", aMessages);
}

/**
 * Call AI Assistant API
 */
function callAIAPI(sPrompt) {
    const oModel = window.aiAssistantModel;
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
                sender: "AI Assistant",
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
    const oModel = window.aiAssistantModel;
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
    // Handle both single and double quotes
    let match = sResponse.match(/AgentRunResult\(output="(.*)"\)/s);
    if (!match) {
        match = sResponse.match(/AgentRunResult\(output='(.*)'\)/s);
    }
    
    if (match && match[1]) {
        // Unescape the content
        let cleaned = match[1];
        // Replace escaped newlines with actual newlines
        cleaned = cleaned.replace(/\\n/g, '\n');
        // Replace escaped tabs with actual tabs
        cleaned = cleaned.replace(/\\t/g, '\t');
        // Replace escaped quotes
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
        const oList = sap.ui.getCore().byId("aiMessageList");
        if (oList) {
            const aItems = oList.getItems();
            if (aItems.length > 1) {
                const iLastIndex = aItems.length - 2; // -2 for loading indicator
                if (iLastIndex >= 0) {
                    oList.scrollToIndex(iLastIndex);
                }
            }
        }
    }, 100);
}