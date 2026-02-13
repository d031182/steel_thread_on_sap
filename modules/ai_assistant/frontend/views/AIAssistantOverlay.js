/**
 * AI Assistant Overlay - Simple Chat UI
 * 
 * Phase 2: Real AI integration with Groq
 * Simplified single-endpoint design
 * 
 * @class AIAssistantOverlay
 */
(function() {
    'use strict';

    class AIAssistantOverlay {
        constructor(adapter) {
            this.adapter = adapter;
            this.dialog = null;
            this.messages = [];
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
                const input = document.getElementById('ai-input');
                if (input) input.focus();
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
         * Clear conversation
         */
        clearConversation() {
            this.messages = [];
            this._renderMessages();
        }

        /**
         * Create the main dialog structure
         * @private
         */
        _createDialog() {
            this.dialog = new sap.m.Dialog({
                title: "Joule AI Assistant",
                contentWidth: "600px",
                contentHeight: "700px",
                resizable: true,
                draggable: true,
                content: [
                    new sap.ui.core.HTML({
                        content: this._getDialogHTML()
                    })
                ],
                beginButton: new sap.m.Button({
                    text: "Clear",
                    icon: "sap-icon://delete",
                    press: () => this.clearConversation()
                }),
                endButton: new sap.m.Button({
                    text: "Close",
                    press: () => this.close()
                })
            });

            // Attach event handlers after dialog renders
            this.dialog.attachAfterOpen(() => {
                this._attachEventHandlers();
            });
        }

        /**
         * Get dialog HTML structure
         * @private
         */
        _getDialogHTML() {
            return `
                <div style="display: flex; flex-direction: column; height: 600px; width: 100%;">
                    <!-- Message List -->
                    <div id="ai-messages" style="flex: 1; overflow-y: auto; padding: 1rem; background: #f5f5f5; border-radius: 4px; margin-bottom: 1rem;">
                        <div style="text-align: center; color: #666; padding: 2rem;">
                            Start a conversation with Joule...
                        </div>
                    </div>
                    
                    <!-- Input Area -->
                    <div style="display: flex; gap: 0.5rem; align-items: flex-end;">
                        <textarea 
                            id="ai-input" 
                            placeholder="Ask me anything about data products..."
                            style="flex: 1; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; resize: vertical; min-height: 60px;"
                        ></textarea>
                        <button 
                            id="ai-send" 
                            style="padding: 0.75rem 1.5rem; background: #0070f2; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500;"
                        >
                            Send
                        </button>
                    </div>
                </div>
            `;
        }

        /**
         * Attach event handlers
         * @private
         */
        _attachEventHandlers() {
            const input = document.getElementById('ai-input');
            const sendBtn = document.getElementById('ai-send');

            if (sendBtn) {
                sendBtn.addEventListener('click', () => this._sendMessage());
            }

            if (input) {
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this._sendMessage();
                    }
                });
            }
        }

        /**
         * Send message to AI
         * @private
         */
        async _sendMessage() {
            const input = document.getElementById('ai-input');
            const sendBtn = document.getElementById('ai-send');
            const message = input?.value.trim();

            if (!message) return;

            // Add user message
            this.messages.push({
                type: 'user',
                text: message,
                timestamp: new Date().toLocaleTimeString()
            });

            // Clear input and disable
            input.value = '';
            input.disabled = true;
            sendBtn.disabled = true;

            // Show typing indicator
            this.messages.push({
                type: 'typing',
                text: 'Joule is typing...',
                timestamp: ''
            });

            this._renderMessages();

            try {
                // Call real AI
                const response = await this.adapter.sendMessage(message);

                // Remove typing indicator
                this.messages = this.messages.filter(m => m.type !== 'typing');

                // Add AI response (Phase 2: simplified response structure)
                const aiText = typeof response.response === 'string' 
                    ? response.response 
                    : response.response?.message || JSON.stringify(response.response) || 'No response';
                
                this.messages.push({
                    type: 'assistant',
                    text: aiText,
                    timestamp: new Date().toLocaleTimeString()
                });

            } catch (error) {
                console.error('[AIAssistantOverlay] Error:', error);

                // Remove typing indicator
                this.messages = this.messages.filter(m => m.type !== 'typing');

                // Add error message
                this.messages.push({
                    type: 'error',
                    text: `Error: ${error.message}`,
                    timestamp: new Date().toLocaleTimeString()
                });
            } finally {
                this._renderMessages();
                input.disabled = false;
                sendBtn.disabled = false;
                input.focus();
            }
        }

        /**
         * Render messages
         * @private
         */
        _renderMessages() {
            const container = document.getElementById('ai-messages');
            if (!container) return;

            if (this.messages.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; color: #666; padding: 2rem;">
                        Start a conversation with Joule...
                    </div>
                `;
                return;
            }

            container.innerHTML = this.messages.map(msg => {
                const isUser = msg.type === 'user';
                const isError = msg.type === 'error';
                const isTyping = msg.type === 'typing';

                return `
                    <div style="margin-bottom: 1rem; display: flex; justify-content: ${isUser ? 'flex-end' : 'flex-start'};">
                        <div style="
                            max-width: 70%; 
                            padding: 0.75rem; 
                            border-radius: 8px; 
                            background: ${isUser ? '#0070f2' : isError ? '#ff4444' : isTyping ? '#f0f0f0' : 'white'};
                            color: ${isUser || isError ? 'white' : '#333'};
                            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                        ">
                            <div style="font-weight: 500; margin-bottom: 0.25rem; font-size: 0.9em;">
                                ${isUser ? 'You' : isTyping ? 'Joule' : isError ? 'Error' : 'Joule'}
                            </div>
                            <div style="white-space: pre-wrap; word-break: break-word;">
                                ${this._escapeHTML(msg.text)}
                            </div>
                            ${msg.timestamp ? `
                                <div style="font-size: 0.75em; opacity: 0.7; margin-top: 0.25rem;">
                                    ${msg.timestamp}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');

            // Auto-scroll to bottom
            container.scrollTop = container.scrollHeight;
        }

        /**
         * Escape HTML
         * @private
         */
        _escapeHTML(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    // Export to window for module.js to use
    window.AIAssistantOverlay = AIAssistantOverlay;
    console.log('[AIAssistantOverlay] Class registered');

})();