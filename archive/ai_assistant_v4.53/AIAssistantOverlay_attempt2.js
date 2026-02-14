(function() {
    "use strict";

    /**
     * AI Assistant Overlay - Clean Implementation  
     * Simple dialog that works with module.js factory pattern
     * 
     * @param {Object} adapter - AIAssistantAdapter instance
     */
    window.AIAssistantOverlay = function(adapter) {
        console.log("[AIAssistantOverlay] Constructor called");
        
        this._adapter = adapter;
        this._dialog = null;
    };

    /**
     * AI Assistant Overlay Prototype
     */
    window.AIAssistantOverlay.prototype = {
        /**
         * Open the dialog
         */
        open: function() {
            console.log("[AIAssistantOverlay] open() called");
            
            if (!this._dialog) {
                console.log("[AIAssistantOverlay] Creating dialog for first time...");
                this._createDialog();
            }
            
            this._dialog.open();
            console.log("[AIAssistantOverlay] Dialog opened successfully");
        },

        /**
         * Close the dialog
         */
        close: function() {
            if (this._dialog) {
                this._dialog.close();
            }
        },

        /**
         * Clear conversation (placeholder for module.js compatibility)
         */
        clearConversation: function() {
            console.log("[AIAssistantOverlay] Clear conversation (not yet implemented)");
        },

        /**
         * Create the dialog structure
         * SAP Fiori compliant chat interface
         */
        _createDialog: function() {
            console.log("[AIAssistantOverlay] _createDialog() called");
            
            // Create message display area with proper styling
            this._messageList = new sap.m.List({
                id: "aiAssistantMessageList",
                noDataText: "Ask me anything about your P2P data...",
                mode: "None",
                backgroundDesign: "Solid"
            }).addStyleClass("sapUiSmallMargin");
            
            // Create input field with Fiori styling
            this._inputField = new sap.m.TextArea({
                id: "aiAssistantInput",
                placeholder: "Ask about suppliers, invoices, or data products...",
                rows: 2,
                width: "100%",
                maxLength: 1000,
                showExceededText: true,
                valueLiveUpdate: true
            });
            
            // Create send button (Emphasized = primary action)
            this._sendButton = new sap.m.Button({
                text: "Send",
                type: "Emphasized",
                icon: "sap-icon://paper-plane",
                press: this._handleSendMessage.bind(this)
            });
            
            // Create clear chat button
            this._clearButton = new sap.m.Button({
                icon: "sap-icon://delete",
                tooltip: "Clear conversation",
                type: "Transparent",
                press: this._handleClearChat.bind(this)
            });
            
            // Create input bar using standard Fiori Bar pattern
            const inputBar = new sap.m.Bar({
                contentMiddle: [
                    new sap.m.HBox({
                        width: "100%",
                        items: [
                            this._inputField,
                            this._sendButton
                        ]
                    })
                ],
                contentRight: [this._clearButton]
            });
            
            // Create header with subtitle
            const header = new sap.m.Bar({
                contentLeft: [
                    new sap.m.Label({
                        text: "Joule AI Assistant",
                        design: "Bold"
                    })
                ],
                contentRight: [
                    new sap.m.Text({
                        text: "Powered by Groq"
                    }).addStyleClass("sapUiTinyMarginEnd")
                ]
            });
            
            // Create main layout (Fiori: content area + toolbar at bottom)
            const content = new sap.m.VBox({
                height: "100%",
                fitContainer: true,
                items: [
                    // Message area (takes all available space)
                    new sap.m.ScrollContainer({
                        height: "100%",
                        width: "100%",
                        vertical: true,
                        horizontal: false,
                        content: [this._messageList]
                    }),
                    // Input bar at bottom (Fiori pattern for chat)
                    inputBar
                ]
            });
            
            this._dialog = new sap.m.Dialog({
                customHeader: header,
                contentWidth: "800px",
                contentHeight: "650px",
                resizable: true,
                draggable: true,
                verticalScrolling: false,
                horizontalScrolling: false,
                content: [content],
                endButton: new sap.m.Button({
                    text: "Close",
                    press: this.close.bind(this)
                })
            });
            
            console.log("[AIAssistantOverlay] Dialog created successfully");
        },

        /**
         * Handle clear chat button
         */
        _handleClearChat: function() {
            console.log("[AIAssistantOverlay] Clearing chat");
            this._messageList.removeAllItems();
        },

        /**
         * Handle send message button click
         */
        _handleSendMessage: function() {
            const message = this._inputField.getValue().trim();
            
            if (!message) {
                console.log("[AIAssistantOverlay] Empty message, ignoring");
                return;
            }
            
            console.log("[AIAssistantOverlay] Sending message:", message);
            
            // Add user message to display
            this._addMessageToList("You", message, false);
            
            // Clear input
            this._inputField.setValue("");
            
            // Show "AI is thinking..." message
            const thinkingItem = this._addMessageToList("AI Assistant", "Thinking...", true);
            
            // Send to backend via adapter
            this._adapter.sendMessage(message)
                .then(response => {
                    console.log("[AIAssistantOverlay] Got response:", response);
                    
                    // Remove "thinking" message
                    this._messageList.removeItem(thinkingItem);
                    
                    // Extract AI message from nested response structure
                    // API returns: { success: true, response: { message: "..." } }
                    let aiMessage = "No response";
                    
                    if (response && response.response && response.response.message) {
                        aiMessage = response.response.message;
                    } else if (response && response.message) {
                        // Fallback for different response format
                        aiMessage = response.message;
                    } else {
                        console.warn("[AIAssistantOverlay] Unexpected response structure:", response);
                        aiMessage = JSON.stringify(response);
                    }
                    
                    // Add AI response
                    this._addMessageToList("AI Assistant", aiMessage, true);
                })
                .catch(error => {
                    console.error("[AIAssistantOverlay] Error:", error);
                    
                    // Remove "thinking" message
                    this._messageList.removeItem(thinkingItem);
                    
                    // Show error
                    this._addMessageToList("System", "Error: " + error.message, true);
                });
        },

        /**
         * Add a message to the message list
         * @param {string} sender - Message sender name
         * @param {string} text - Message text
         * @param {boolean} isAI - True if message is from AI
         * @returns {sap.m.StandardListItem} The created list item
         */
        _addMessageToList: function(sender, text, isAI) {
            const item = new sap.m.StandardListItem({
                title: sender,
                description: text,
                icon: isAI ? "sap-icon://collaborate" : "sap-icon://person-placeholder"
            });
            
            this._messageList.addItem(item);
            
            // Scroll to bottom
            setTimeout(() => {
                const listDomRef = this._messageList.getDomRef();
                if (listDomRef) {
                    listDomRef.scrollTop = listDomRef.scrollHeight;
                }
            }, 100);
            
            return item;
        },

        /**
         * Clean up resources
         */
        destroy: function() {
            console.log("[AIAssistantOverlay] destroy() called");
            if (this._dialog) {
                this._dialog.destroy();
                this._dialog = null;
            }
        }
    };

    console.log("[AIAssistantOverlay] Class registered on window object");

})();
