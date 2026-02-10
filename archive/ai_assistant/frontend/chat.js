/**
 * AI Assistant Chat Interface - Pure JavaScript Implementation
 * 
 * Uses SAPUI5 controls programmatically (no XML views)
 * Fiori-compliant, ChatGPT-like UX
 */

sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/Page",
    "sap/m/List",
    "sap/m/FeedListItem",
    "sap/m/Toolbar",
    "sap/m/TextArea",
    "sap/m/Button",
    "sap/m/ToolbarSpacer",
    "sap/m/Panel",
    "sap/m/VBox",
    "sap/m/HBox",
    "sap/m/Label",
    "sap/m/Text",
    "sap/m/MessageBox",
    "sap/m/MessageToast",
    "sap/m/BusyIndicator",
    "sap/m/CustomListItem"
], function (
    Controller,
    JSONModel,
    Page,
    List,
    FeedListItem,
    Toolbar,
    TextArea,
    Button,
    ToolbarSpacer,
    Panel,
    VBox,
    HBox,
    Label,
    Text,
    MessageBox,
    MessageToast,
    BusyIndicator,
    CustomListItem
) {
    "use strict";

    /**
     * AI Assistant Chat Controller
     */
    return Controller.extend("ai.assistant.Chat", {
        
        /**
         * Initialize the chat interface
         */
        onInit: function () {
            // Initialize view model
            const oViewModel = new JSONModel({
                messages: [],
                currentMessage: "",
                isLoading: false,
                currentDataProduct: "",
                currentSchema: "",
                currentTable: "",
                contextVisible: false
            });
            this.getView().setModel(oViewModel);
            
            // Load context from main app (if available)
            this._loadContext();
        },
        
        /**
         * Create the chat UI programmatically
         * Call this to build the interface
         */
        createUI: function (oContainer) {
            const oModel = this.getView().getModel();
            
            // Main page
            const oPage = new Page({
                title: "AI Assistant",
                showNavButton: false,
                enableScrolling: false,
                content: [
                    this._createContextPanel(),
                    this._createMessageList()
                ],
                footer: this._createInputToolbar()
            });
            
            oPage.addStyleClass("sapUiResponsiveContentPadding");
            
            if (oContainer) {
                oContainer.addContent(oPage);
            }
            
            return oPage;
        },
        
        /**
         * Create context panel (collapsible)
         */
        _createContextPanel: function () {
            const oPanel = new Panel({
                headerText: "Current Context",
                expandable: true,
                expanded: "{/contextVisible}",
                content: [
                    new VBox({
                        items: [
                            new Label({
                                text: "Data Product:",
                                class: "sapUiTinyMarginBottom"
                            }),
                            new Text({
                                text: "{/currentDataProduct}",
                                class: "sapUiSmallMarginBottom"
                            }),
                            new Label({
                                text: "Schema:",
                                class: "sapUiTinyMarginBottom"
                            }),
                            new Text({
                                text: "{/currentSchema}",
                                class: "sapUiSmallMarginBottom"
                            }),
                            new Label({
                                text: "Table:",
                                class: "sapUiTinyMarginBottom"
                            }),
                            new Text({
                                text: "{/currentTable}"
                            })
                        ]
                    })
                ]
            });
            
            oPanel.addStyleClass("sapUiResponsiveMargin");
            return oPanel;
        },
        
        /**
         * Create message list with feed items
         */
        _createMessageList: function () {
            // Create message list
            const oList = new List("messageList", {
                mode: "None",
                growing: true,
                growingThreshold: 20,
                growingScrollToLoad: true,
                noDataText: "Start a conversation with the AI Assistant...",
                items: {
                    path: "/messages",
                    template: new FeedListItem({
                        sender: "{sender}",
                        timestamp: "{timestamp}",
                        text: "{text}",
                        icon: {
                            path: "type",
                            formatter: function (sType) {
                                return sType === "user" 
                                    ? "sap-icon://person-placeholder" 
                                    : "sap-icon://collaborate";
                            }
                        },
                        iconDensityAware: false,
                        customData: [
                            new sap.ui.core.CustomData({
                                key: "messageType",
                                value: "{type}"
                            })
                        ]
                    }).addStyleClass("{= ${type} === 'user' ? 'userMessage' : 'aiMessage' }")
                }
            });
            
            oList.addStyleClass("sapUiResponsiveMargin");
            oList.addStyleClass("chatMessageList");
            
            // Add loading indicator as separate item
            const oLoadingItem = new CustomListItem({
                visible: "{/isLoading}",
                content: [
                    new HBox({
                        alignItems: "Center",
                        justifyContent: "Start",
                        items: [
                            new BusyIndicator({
                                size: "1rem"
                            }).addStyleClass("sapUiTinyMarginEnd"),
                            new Text({
                                text: "AI is thinking..."
                            }).addStyleClass("sapUiTinyMarginBegin")
                        ]
                    })
                ]
            }).addStyleClass("aiLoadingMessage");
            
            oList.addItem(oLoadingItem);
            
            return oList;
        },
        
        /**
         * Create input toolbar (footer)
         */
        _createInputToolbar: function () {
            const that = this;
            
            const oTextArea = new TextArea("messageInput", {
                value: "{/currentMessage}",
                placeholder: "Ask about data products, schemas, or request SQL generation...",
                rows: 2,
                maxLength: 2000,
                width: "100%",
                growing: true,
                growingMaxLines: 5,
                enabled: {
                    path: "/isLoading",
                    formatter: function (bLoading) {
                        return !bLoading;
                    }
                },
                liveChange: function () {
                    // Enable/disable send button based on text
                }
            });
            
            // Handle Enter key to send
            oTextArea.attachBrowserEvent("keydown", function (oEvent) {
                if (oEvent.key === "Enter" && !oEvent.shiftKey) {
                    oEvent.preventDefault();
                    that.onSendMessage();
                }
            });
            
            const oSendButton = new Button({
                text: "Send",
                type: "Emphasized",
                icon: "sap-icon://paper-plane",
                press: this.onSendMessage.bind(this),
                enabled: {
                    parts: [
                        { path: "/currentMessage" },
                        { path: "/isLoading" }
                    ],
                    formatter: function (sMessage, bLoading) {
                        return sMessage && sMessage.trim().length > 0 && !bLoading;
                    }
                }
            });
            
            const oToolbar = new Toolbar({
                content: [
                    oTextArea,
                    new ToolbarSpacer(),
                    oSendButton
                ]
            });
            
            oToolbar.addStyleClass("sapUiMediumMarginTop");
            
            return oToolbar;
        },
        
        /**
         * Handle send message button press
         */
        onSendMessage: function () {
            const oModel = this.getView().getModel();
            const sMessage = oModel.getProperty("/currentMessage").trim();
            
            if (!sMessage) {
                return;
            }
            
            // Add user message to list
            this._addMessage({
                type: "user",
                sender: "You",
                text: sMessage,
                timestamp: new Date().toLocaleTimeString()
            });
            
            // Clear input and show loading
            oModel.setProperty("/currentMessage", "");
            oModel.setProperty("/isLoading", true);
            
            // Call AI API
            this._callAIAPI(sMessage);
        },
        
        /**
         * Call AI Assistant API
         */
        _callAIAPI: function (sPrompt) {
            const oModel = this.getView().getModel();
            const oContext = this._getContext();
            
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
                    // Add AI response
                    this._addMessage({
                        type: "ai",
                        sender: "AI Assistant",
                        text: this._formatResponse(data.response),
                        timestamp: new Date().toLocaleTimeString(),
                        tokensUsed: data.tokens_used
                    });
                    
                    // Scroll to bottom
                    this._scrollToBottom();
                    
                    // Show success toast with token usage
                    if (data.tokens_used) {
                        MessageToast.show(`Response received (${data.tokens_used} tokens)`);
                    }
                } else {
                    MessageBox.error(
                        "Failed to get AI response:\n\n" + (data.error || "Unknown error"),
                        {
                            title: "AI Error"
                        }
                    );
                }
            })
            .catch(error => {
                oModel.setProperty("/isLoading", false);
                MessageBox.error(
                    "Network error:\n\n" + error.message,
                    {
                        title: "Connection Error",
                        actions: [MessageBox.Action.OK, "Retry"],
                        onClose: function (sAction) {
                            if (sAction === "Retry") {
                                this._callAIAPI(sPrompt);
                            }
                        }.bind(this)
                    }
                );
            });
        },
        
        /**
         * Add message to list
         */
        _addMessage: function (oMessage) {
            const oModel = this.getView().getModel();
            const aMessages = oModel.getProperty("/messages");
            aMessages.push(oMessage);
            oModel.setProperty("/messages", aMessages);
        },
        
        /**
         * Scroll to bottom of message list
         */
        _scrollToBottom: function () {
            setTimeout(() => {
                const oList = sap.ui.getCore().byId("messageList");
                if (oList) {
                    const aItems = oList.getItems();
                    if (aItems.length > 0) {
                        // Scroll to last item (excluding loading indicator)
                        const iLastIndex = aItems.length - 2; // -2 because last is loading indicator
                        if (iLastIndex >= 0) {
                            oList.scrollToIndex(iLastIndex);
                        }
                    }
                }
            }, 100);
        },
        
        /**
         * Get current context for AI
         */
        _getContext: function () {
            const oModel = this.getView().getModel();
            const oContext = {};
            
            const sDataProduct = oModel.getProperty("/currentDataProduct");
            const sSchema = oModel.getProperty("/currentSchema");
            const sTable = oModel.getProperty("/currentTable");
            
            if (sDataProduct) {
                oContext.data_product = sDataProduct;
            }
            if (sSchema) {
                oContext.current_schema = sSchema;
            }
            if (sTable) {
                oContext.current_table = sTable;
            }
            
            return oContext;
        },
        
        /**
         * Format AI response (remove technical wrappers)
         */
        _formatResponse: function (sResponse) {
            if (!sResponse) {
                return "No response received.";
            }
            
            // Remove AgentRunResult wrapper if present
            const match = sResponse.match(/AgentRunResult\(output='(.*)'\)/s);
            if (match) {
                return match[1];
            }
            
            return sResponse;
        },
        
        /**
         * Load context from main app (if integrated)
         */
        _loadContext: function () {
            // TODO: Integrate with main app to get current data product/schema/table
            // For now, leave empty or set dummy values for testing
            
            const oModel = this.getView().getModel();
            
            // Example: Set dummy context for testing
            // oModel.setProperty("/currentDataProduct", "SupplierInvoice");
            // oModel.setProperty("/currentSchema", "sap_s4com_supplierinvoice_v1");
            // oModel.setProperty("/currentTable", "A_SupplierInvoice");
        },
        
        /**
         * Clear conversation
         */
        onClearConversation: function () {
            MessageBox.confirm(
                "Are you sure you want to clear the conversation history?",
                {
                    title: "Clear Conversation",
                    onClose: function (sAction) {
                        if (sAction === MessageBox.Action.OK) {
                            const oModel = this.getView().getModel();
                            oModel.setProperty("/messages", []);
                            MessageToast.show("Conversation cleared");
                        }
                    }.bind(this)
                }
            );
        },
        
        /**
         * Export conversation as Markdown
         */
        onExportConversation: function () {
            const oModel = this.getView().getModel();
            const aMessages = oModel.getProperty("/messages");
            
            if (aMessages.length === 0) {
                MessageToast.show("No messages to export");
                return;
            }
            
            // Generate Markdown
            const sMarkdown = aMessages.map(msg => {
                return `**${msg.sender}** (${msg.timestamp}):\n${msg.text}\n`;
            }).join("\n---\n\n");
            
            // Add header
            const sFullMarkdown = `# AI Assistant Conversation\n\n**Date**: ${new Date().toLocaleString()}\n\n---\n\n${sMarkdown}`;
            
            // Download as file
            this._downloadFile("ai-conversation.md", sFullMarkdown);
            
            MessageToast.show("Conversation exported");
        },
        
        /**
         * Download file helper
         */
        _downloadFile: function (sFilename, sContent) {
            const blob = new Blob([sContent], { type: "text/markdown" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = sFilename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    });
});