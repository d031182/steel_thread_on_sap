(function() {
    "use strict";

    /**
     * AI Assistant Overlay - Clean Fiori Design
     * Simple chat interface using SAP Fiori best practices
     * 
     * Design Principles:
     * - Use FeedListItem for chat messages (Fiori standard for feeds/chats)
     * - Use Input (not TextArea) for single-line messaging
     * - NON-streaming API (Groq streaming doesn't work reliably)
     * - Simple VBox layout with proper spacing
     * 
     * @param {Object} adapter - AIAssistantAdapter instance
     */
    window.AIAssistantOverlay = function(adapter) {
        console.log("[AIAssistantOverlay] Constructor called");
        
        this._adapter = adapter;
        this._dialog = null;
        this._feed = null;
        this._input = null;
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
         * Clear conversation
         */
        clearConversation: function() {
            console.log("[AIAssistantOverlay] Clearing conversation");
            if (this._feed) {
                this._feed.destroyItems();
            }
        },

        /**
         * Create the dialog structure
         * Simple, clean Fiori design
         */
        _createDialog: function() {
            console.log("[AIAssistantOverlay] _createDialog() called");
            
            // Create feed list for messages (Fiori standard for chat)
            this._feed = new sap.m.FeedListItem({
                showIcon: false,
                text: "👋 Hello! I'm Joule, your P2P data analysis assistant. Ask me anything about suppliers, invoices, or data products."
            });
            
            const feedList = new sap.m.List({
                items: [this._feed],
                noDataText: "Start a conversation..."
            }).addStyleClass("sapUiSmallMargin");
            
            // Create input field (single line, Fiori standard)
            this._input = new sap.m.Input({
                placeholder: "Ask about your P2P data...",
                width: "100%",
                submit: this._handleSendMessage.bind(this)
            });
            
            // Create send button
            const sendButton = new sap.m.Button({
                text: "Send",
                type: "Emphasized",
                icon: "sap-icon://paper-plane",
                press: this._handleSendMessage.bind(this)
            });
            
            // Create clear button
            const clearButton = new sap.m.Button({
                icon: "sap-icon://delete",
                tooltip: "Clear conversation",
                type: "Transparent",
                press: this.clearConversation.bind(this)
            });
            
            // Create input toolbar
            const inputToolbar = new sap.m.Toolbar({
                content: [
                    this._input,
                    sendButton,
                    clearButton
                ]
            });
            
            // Create messages scroll container (calculated height to avoid overlap with toolbar)
            const messagesContainer = new sap.m.ScrollContainer({
                width: "100%",
                vertical: true,
                horizontal: false,
                content: [feedList]
            });
            
            // Create main content area with flexbox layout (Fiori pattern)
            const content = new sap.m.VBox({
                height: "100%",
                fitContainer: true,
                items: [
                    messagesContainer,
                    inputToolbar
                ]
            });
            
            // Apply flexbox styling to make messages scrollable and input fixed
            content.addEventDelegate({
                onAfterRendering: function() {
                    console.log("[AIAssistantOverlay] onAfterRendering called");
                    const vboxDom = content.getDomRef();
                    console.log("[AIAssistantOverlay] VBox DOM:", vboxDom);
                    
                    if (vboxDom) {
                        // VBox: flex column layout
                        vboxDom.style.display = "flex";
                        vboxDom.style.flexDirection = "column";
                        vboxDom.style.height = "100%";
                        console.log("[AIAssistantOverlay] Applied flex layout to VBox");
                        
                        // Messages container: flex-grow to fill space with visible scrollbar
                        const scrollDom = messagesContainer.getDomRef();
                        console.log("[AIAssistantOverlay] ScrollContainer DOM:", scrollDom);
                        if (scrollDom) {
                            scrollDom.style.flex = "1 1 auto";
                            scrollDom.style.minHeight = "0"; // Critical for flex children
                            scrollDom.style.overflowY = "auto"; // Force vertical scrollbar when needed
                            scrollDom.style.overflowX = "hidden";
                            
                            // Ensure inner scroll area is styled
                            const scrollArea = scrollDom.querySelector('.sapMScrollCont');
                            if (scrollArea) {
                                scrollArea.style.overflowY = "auto";
                                scrollArea.style.height = "100%";
                            }
                            console.log("[AIAssistantOverlay] Applied flex-grow to messages");
                        }
                        
                        // Input toolbar: fixed at bottom
                        const toolbarDom = inputToolbar.getDomRef();
                        console.log("[AIAssistantOverlay] Toolbar DOM:", toolbarDom);
                        if (toolbarDom) {
                            toolbarDom.style.flex = "0 0 auto";
                            toolbarDom.style.borderTop = "1px solid #e0e0e0";
                            toolbarDom.style.boxShadow = "0 -2px 4px rgba(0, 0, 0, 0.05)";
                            toolbarDom.style.backgroundColor = "#ffffff";
                            toolbarDom.style.padding = "0.5rem";
                            console.log("[AIAssistantOverlay] Applied fixed positioning to toolbar");
                        } else {
                            console.error("[AIAssistantOverlay] Toolbar DOM not found!");
                        }
                    } else {
                        console.error("[AIAssistantOverlay] VBox DOM not found!");
                    }
                }
            });
            
            console.log("[AIAssistantOverlay] Created content with items:", content.getItems().length);
            console.log("[AIAssistantOverlay] Item 0 (messagesContainer):", content.getItems()[0]);
            console.log("[AIAssistantOverlay] Item 1 (inputToolbar):", content.getItems()[1]);
            
            // Create dialog (disable dialog scrolling, we handle it ourselves)
            this._dialog = new sap.m.Dialog({
                title: "Joule AI Assistant",
                contentWidth: "700px",
                contentHeight: "600px",
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
         * Handle send message
         */
        _handleSendMessage: function() {
            const message = this._input.getValue().trim();
            
            if (!message) {
                sap.m.MessageToast.show("Please enter a message");
                return;
            }
            
            console.log("[AIAssistantOverlay] Sending message:", message);
            
            // Add user message
            this._addMessage("You", message, false);
            
            // Clear input
            this._input.setValue("");
            
            // Show thinking indicator
            const thinkingFeed = this._addMessage("Joule", "Thinking...", true);
            
            // Send to backend (NON-streaming)
            this._adapter.sendMessage(message)
                .then(response => {
                    console.log("[AIAssistantOverlay] Got response:", response);
                    
                    // Remove thinking indicator
                    this._feed.getParent().removeItem(thinkingFeed);
                    thinkingFeed.destroy();
                    
                    // Extract AI message from response
                    let aiMessage = "No response";
                    
                    if (response && response.response && response.response.message) {
                        aiMessage = response.response.message;
                    } else if (response && response.message) {
                        aiMessage = response.message;
                    } else {
                        console.warn("[AIAssistantOverlay] Unexpected response:", response);
                        aiMessage = JSON.stringify(response);
                    }
                    
                    // Add AI response
                    this._addMessage("Joule", aiMessage, true);
                })
                .catch(error => {
                    console.error("[AIAssistantOverlay] Error:", error);
                    
                    // Remove thinking indicator
                    this._feed.getParent().removeItem(thinkingFeed);
                    thinkingFeed.destroy();
                    
                    // Show error
                    this._addMessage("System", "Error: " + error.message, false);
                    sap.m.MessageToast.show("Failed to get response");
                });
        },

        /**
         * Add a message to the feed
         * @param {string} sender - Message sender
         * @param {string} text - Message text
         * @param {boolean} isAI - True if from AI
         * @returns {sap.m.FeedListItem} The created feed item
         */
        _addMessage: function(sender, text, isAI) {
            const icon = isAI ? "sap-icon://collaborate" : "sap-icon://person-placeholder";
            const timestamp = new Date().toLocaleTimeString();
            
            const feedItem = new sap.m.FeedListItem({
                sender: sender,
                text: text,
                icon: icon,
                info: timestamp,
                showIcon: true
            });
            
            const feedList = this._feed.getParent();
            feedList.addItem(feedItem);
            
            // Scroll to bottom
            setTimeout(() => {
                const scrollContainer = feedList.getParent();
                const domRef = scrollContainer.getDomRef();
                if (domRef) {
                    const scrollArea = domRef.querySelector('.sapMScrollCont');
                    if (scrollArea) {
                        scrollArea.scrollTop = scrollArea.scrollHeight;
                    }
                }
            }, 100);
            
            return feedItem;
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