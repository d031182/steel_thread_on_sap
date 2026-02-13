sap.ui.define([
    "sap/m/Dialog",
    "sap/m/VBox",
    "sap/m/HBox",
    "sap/m/Button",
    "sap/m/TextArea",
    "sap/m/Text",
    "sap/m/ScrollContainer",
    "sap/m/BusyIndicator",
    "sap/m/CustomListItem",
    "sap/m/List",
    "sap/ui/core/Icon",
    "sap/ui/model/json/JSONModel"
], function(Dialog, VBox, HBox, Button, TextArea, Text, ScrollContainer, BusyIndicator, CustomListItem, List, Icon, JSONModel) {
    "use strict";

    /**
     * AI Assistant Overlay - ChatGPT-style conversational UI
     * 
     * Features:
     * - Resizable/draggable overlay window
     * - Message history with user/AI distinction
     * - Typing indicator during AI processing
     * - Auto-scroll to latest message
     * - Industry-standard chatbot UX
     * 
     * @class AIAssistantOverlay
     */
    class AIAssistantOverlay {
        constructor(adapter) {
            this.adapter = adapter;
            this.dialog = null;
            this.model = new JSONModel({
                messages: [],
                currentMessage: "",
                isLoading: false,
                conversationId: this._generateConversationId()
            });
        }

        /**
         * Open the AI Assistant overlay
         */
        open() {
            if (!this.dialog) {
                this._createDialog();
            }
            
            this.dialog.open();
            
            // Focus input after dialog opens
            setTimeout(() => {
                const input = this.dialog.getContent()[0].getItems()[1].getItems()[0];
                input.focus();
            }, 100);
        }

        /**
         * Close the AI Assistant overlay
         */
        close() {
            if (this.dialog) {
                this.dialog.close();
            }
        }

        /**
         * Create the main dialog structure
         * @private
         */
        _createDialog() {
            this.dialog = new Dialog({
                title: "Joule AI Assistant",
                contentWidth: "600px",
                contentHeight: "700px",
                resizable: true,
                draggable: true,
                modal: false,  // Allow app interaction
                content: [
                    new VBox({
                        width: "100%",
                        height: "100%",
                        items: [
                            // Chat history (scrollable)
                            this._createMessageList(),
                            
                            // Input area
                            this._createInputArea()
                        ]
                    })
                ],
                endButton: new Button({
                    text: "Close",
                    press: () => this.close()
                })
            }).addStyleClass("aiAssistantDialog");

            this.dialog.setModel(this.model);
        }

        /**
         * Create message list container
         * @private
         */
        _createMessageList() {
            const list = new List({
                id: "aiMessageList",
                mode: "None",
                growing: false,
                noDataText: "Start a conversation with Joule...",
                items: {
                    path: "/messages",
                    template: this._createMessageItem()
                }
            }).addStyleClass("aiMessageList");

            return new ScrollContainer({
                height: "550px",
                width: "100%",
                vertical: true,
                horizontal: false,
                content: [list]
            });
        }

        /**
         * Create message item template
         * @private
         */
        _createMessageItem() {
            return new CustomListItem({
                content: [
                    new HBox({
                        width: "100%",
                        justifyContent: "{= ${type} === 'user' ? 'End' : 'Start'}",
                        items: [
                            new VBox({
                                items: [
                                    new HBox({
                                        items: [
                                            new Icon({
                                                src: "{= ${type} === 'user' ? 'sap-icon://person-placeholder' : 'sap-icon://collaborate'}",
                                                size: "1rem"
                                            }).addStyleClass("sapUiTinyMarginEnd"),
                                            new Text({
                                                text: "{sender}",
                                                class: "sapUiSmallMarginBottom"
                                            }).addStyleClass("messageHeader")
                                        ]
                                    }),
                                    new Text({
                                        text: "{message}",
                                        renderWhitespace: true
                                    }).addStyleClass("messageText"),
                                    new Text({
                                        text: "{timestamp}",
                                        class: "sapUiTinyMarginTop"
                                    }).addStyleClass("messageTimestamp"),
                                    // Show sources if available
                                    new VBox({
                                        visible: "{= ${sources} && ${sources}.length > 0}",
                                        items: [
                                            new Text({
                                                text: "Sources:",
                                                class: "sapUiTinyMarginTop"
                                            }).addStyleClass("messageSourcesLabel"),
                                            new Text({
                                                text: "{= ${sources} ? ${sources}.join(', ') : ''}",
                                                class: "sapUiTinyMarginTop"
                                            }).addStyleClass("messageSourcesText")
                                        ]
                                    })
                                ]
                            }).addStyleClass("{= ${type} === 'user' ? 'userMessageBubble' : 'aiMessageBubble'}")
                        ]
                    })
                ]
            }).addStyleClass("messageItem");
        }

        /**
         * Create input area with send button
         * @private
         */
        _createInputArea() {
            const inputArea = new TextArea({
                value: "{/currentMessage}",
                placeholder: "Ask me anything about P2P data...",
                rows: 3,
                maxLength: 2000,
                width: "100%",
                growing: true,
                growingMaxLines: 5,
                enabled: "{= !${/isLoading}}",
                liveChange: this._onInputChange.bind(this)
            }).addStyleClass("aiInputArea");

            // Handle Enter key (send message)
            inputArea.attachBrowserEvent("keydown", (event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    this._sendMessage();
                }
            });

            const sendButton = new Button({
                icon: "sap-icon://paper-plane",
                type: "Emphasized",
                enabled: "{= ${/currentMessage}.length > 0 && !${/isLoading}}",
                press: this._sendMessage.bind(this),
                tooltip: "Send message (Enter)"
            }).addStyleClass("aiSendButton");

            return new HBox({
                width: "100%",
                alignItems: "End",
                justifyContent: "SpaceBetween",
                items: [
                    inputArea,
                    sendButton
                ]
            }).addStyleClass("aiInputContainer sapUiMediumMarginTop");
        }

        /**
         * Handle input change
         * @private
         */
        _onInputChange(event) {
            // Optional: Add typing indicator for multi-user (future)
        }

        /**
         * Send message to AI
         * @private
         */
        async _sendMessage() {
            const message = this.model.getProperty("/currentMessage").trim();
            
            if (!message || this.model.getProperty("/isLoading")) {
                return;
            }

            // Add user message to UI
            this._addMessage({
                type: "user",
                sender: "You",
                message: message,
                timestamp: this._getTimestamp(),
                sources: []
            });

            // Clear input
            this.model.setProperty("/currentMessage", "");
            this.model.setProperty("/isLoading", true);

            // Show typing indicator
            this._showTypingIndicator();

            try {
                // Call API
                const response = await this.adapter.sendMessage({
                    message: message,
                    conversation_id: this.model.getProperty("/conversationId"),
                    context: {
                        datasource: "p2p_data"
                    }
                });

                // Remove typing indicator
                this._hideTypingIndicator();

                if (response.success) {
                    // Add AI response
                    this._addMessage({
                        type: "assistant",
                        sender: "Joule",
                        message: response.response.message,
                        timestamp: this._getTimestamp(),
                        sources: response.response.sources || [],
                        confidence: response.response.confidence
                    });
                } else {
                    throw new Error(response.error || "Unknown error");
                }

            } catch (error) {
                console.error("AI Assistant error:", error);
                
                // Remove typing indicator
                this._hideTypingIndicator();

                // Show error message
                this._addMessage({
                    type: "error",
                    sender: "System",
                    message: `Sorry, I encountered an error: ${error.message}. Please try again.`,
                    timestamp: this._getTimestamp(),
                    sources: []
                });
            } finally {
                this.model.setProperty("/isLoading", false);
            }
        }

        /**
         * Add message to conversation
         * @private
         */
        _addMessage(messageData) {
            const messages = this.model.getProperty("/messages");
            messages.push(messageData);
            this.model.setProperty("/messages", messages);

            // Auto-scroll to bottom
            setTimeout(() => this._scrollToBottom(), 100);
        }

        /**
         * Show typing indicator
         * @private
         */
        _showTypingIndicator() {
            this._addMessage({
                type: "typing",
                sender: "Joule",
                message: "typing...",
                timestamp: "",
                sources: []
            });
        }

        /**
         * Hide typing indicator
         * @private
         */
        _hideTypingIndicator() {
            const messages = this.model.getProperty("/messages");
            const filtered = messages.filter(msg => msg.type !== "typing");
            this.model.setProperty("/messages", filtered);
        }

        /**
         * Scroll to bottom of message list
         * @private
         */
        _scrollToBottom() {
            const scrollContainer = this.dialog.getContent()[0].getItems()[0];
            const domRef = scrollContainer.getDomRef();
            if (domRef) {
                domRef.scrollTop = domRef.scrollHeight;
            }
        }

        /**
         * Get formatted timestamp
         * @private
         */
        _getTimestamp() {
            const now = new Date();
            return now.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
        }

        /**
         * Generate unique conversation ID
         * @private
         */
        _generateConversationId() {
            return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }

        /**
         * Clear conversation history
         */
        clearConversation() {
            this.model.setProperty("/messages", []);
            this.model.setProperty("/conversationId", this._generateConversationId());
        }
    }

    return AIAssistantOverlay;
});