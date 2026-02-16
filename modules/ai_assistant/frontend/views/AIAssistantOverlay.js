(function() {
    "use strict";

    /**
     * AI Assistant Overlay - Clean Fiori Design with Markdown Support
     * Simple chat interface using SAP Fiori best practices
     * 
     * Design Principles:
     * - Use FeedListItem for chat messages (Fiori standard for feeds/chats)
     * - Use Input (not TextArea) for single-line messaging
     * - NON-streaming API (Groq streaming doesn't work reliably)
     * - Simple VBox layout with proper spacing
     * - EXPLICIT HEIGHTS to prevent input from disappearing
     * - Markdown formatting for AI responses
     * 
     * @param {Object} adapter - AIAssistantAdapter instance
     * @param {string} datasource - Current datasource ('hana' or 'p2p_data')
     */
    window.AIAssistantOverlay = function(adapter, datasource) {
        console.log("[AIAssistantOverlay] Constructor called with datasource:", datasource);
        
        this._adapter = adapter;
        this._datasource = datasource || 'p2p_data'; // Default to SQLite
        this._dialog = null;
        this._feed = null;
        this._input = null;
        this._conversationId = null; // Track conversation ID for context persistence
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
            
            // Create input toolbar with FIXED HEIGHT (prevents disappearing)
            const inputToolbar = new sap.m.Toolbar({
                height: "60px",
                content: [
                    this._input,
                    sendButton,
                    clearButton
                ]
            });
            
            // Create messages scroll container with EXPLICIT HEIGHT (prevents overflow)
            const messagesContainer = new sap.m.ScrollContainer({
                width: "100%",
                height: "calc(100% - 60px)", // Explicit: total height minus toolbar
                vertical: true,
                horizontal: false,
                content: [feedList]
            });
            
            // Create main content area - SIMPLE, NO FLEXBOX COMPLEXITY
            const content = new sap.m.VBox({
                height: "100%",
                fitContainer: true,
                items: [
                    messagesContainer,
                    inputToolbar
                ]
            });
            
            // Create dialog with datasource indicator (disable dialog scrolling, we handle it ourselves)
            const datasourceLabel = this._datasource === 'hana' ? 'HANA Cloud' : 'Local';
            
            this._dialog = new sap.m.Dialog({
                title: "Joule AI Assistant (" + datasourceLabel + ")",
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
            
            console.log("[AIAssistantOverlay] Dialog created with explicit heights");
            console.log("[AIAssistantOverlay] - ScrollContainer: calc(100% - 60px)");
            console.log("[AIAssistantOverlay] - Toolbar: 60px fixed");
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
            
            // Build request payload with conversation ID for context persistence
            const requestPayload = {
                datasource: this._datasource
            };
            
            // If we have a conversation ID, include it to maintain context
            if (this._conversationId) {
                requestPayload.conversation_id = this._conversationId;
                console.log("[AIAssistantOverlay] Reusing conversation:", this._conversationId);
            } else {
                console.log("[AIAssistantOverlay] Starting new conversation with datasource:", this._datasource);
            }
            
            // Send to backend (NON-streaming) with datasource context
            this._adapter.sendMessage(message, requestPayload)
                .then(response => {
                    console.log("[AIAssistantOverlay] Got response:", response);
                    
                    // Store conversation ID for future messages (maintains context!)
                    if (response && response.conversation_id) {
                        this._conversationId = response.conversation_id;
                        console.log("[AIAssistantOverlay] Stored conversation ID:", this._conversationId);
                    }
                    
                    // Remove thinking indicator
                    this._feed.getParent().removeItem(thinkingFeed);
                    thinkingFeed.destroy();
                    
                    // Check for error in response (backend returns success: true even with errors)
                    if (response && response.error) {
                        // Backend returned an error
                        const errorMsg = response.error.message || response.error || "An error occurred";
                        
                        // Show error in chat
                        this._addMessage("Joule", "❌ I apologize, but I encountered an error processing your request.", true);
                        
                        // Show detailed error in MessageBox (SAP Fiori best practice)
                        sap.m.MessageBox.error(errorMsg, {
                            title: "AI Assistant Error",
                            details: response.error.details || JSON.stringify(response.error, null, 2),
                            styleClass: "sapUiSizeCompact"
                        });
                        
                        return;
                    }
                    
                    // Extract AI message from successful response
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
                    
                    // Show user-friendly error message in chat
                    this._addMessage("Joule", "❌ I'm sorry, I couldn't process your request. Please try again.", true);
                    
                    // Show detailed error in MessageBox (SAP Fiori best practice)
                    sap.m.MessageBox.error(error.message || "An unexpected error occurred", {
                        title: "Communication Error",
                        details: error.stack || error.toString(),
                        styleClass: "sapUiSizeCompact"
                    });
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
            const icon = isAI ? "sap-icon://da" : "sap-icon://person-placeholder";
            const timestamp = new Date().toLocaleTimeString();
            
            // Format markdown to HTML if MarkdownFormatter is available and message is from AI
            let formattedText = text;
            if (isAI && window.MarkdownFormatter) {
                formattedText = window.MarkdownFormatter.format(text);
                console.log("[AIAssistantOverlay] Formatted markdown text");
            } else if (!isAI) {
                // For user messages, just escape HTML and add line breaks
                formattedText = this._escapeHTML(text).replace(/\n/g, '<br>');
            }
            
            const feedItem = new sap.m.FeedListItem({
                sender: sender,
                text: formattedText,
                icon: icon,
                info: timestamp,
                showIcon: true,
                convertLinksToAnchorTags: "All"
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
         * Escape HTML to prevent XSS
         * @param {string} text - Text to escape
         * @returns {string} Escaped text
         */
        _escapeHTML: function(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
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