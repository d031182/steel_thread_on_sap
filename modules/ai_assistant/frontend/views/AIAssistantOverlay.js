/**
 * AI Assistant Overlay - Simplified Clean Implementation
 * Focus: Readable text colors, streaming support, conversation history
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
            this.currentConversationId = null;
            this.conversations = {};
            
            this._loadConversations();
        }

        open() {
            if (!this.dialog) {
                this._createDialog();
            }
            
            if (!this.currentConversationId) {
                this._createNewConversation();
            } else {
                this._loadConversation(this.currentConversationId);
            }
            
            this.dialog.open();
            
            setTimeout(() => {
                const input = document.getElementById('ai-input');
                if (input) input.focus();
            }, 100);
        }

        close() {
            if (this.dialog) {
                this.dialog.close();
            }
        }

        clearConversation() {
            this._createNewConversation();
            this._renderMessages();
            this._renderHistory();
        }

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

            this.dialog.attachAfterOpen(() => {
                this._attachEventHandlers();
            });
        }

        _getDialogHTML() {
            return `
                <div style="display: flex; height: 600px; width: 100%; gap: 1rem;">
                    <!-- Sidebar -->
                    <div style="width: 200px; border-right: 1px solid #ddd; padding-right: 1rem;">
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">Conversations</div>
                        <div id="ai-history" style="flex: 1; overflow-y: auto; max-height: 550px;"></div>
                    </div>
                    
                    <!-- Chat Area -->
                    <div style="flex: 1; display: flex; flex-direction: column;">
                        <div id="ai-messages" style="flex: 1; overflow-y: auto; padding: 1rem; background: #f5f5f5; border-radius: 4px; margin-bottom: 1rem;"></div>
                        
                        <div style="display: flex; gap: 0.5rem;">
                            <textarea 
                                id="ai-input" 
                                placeholder="Ask me anything..."
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
                </div>
            `;
        }

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

            this._renderHistory();
        }

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

            input.value = '';
            input.disabled = true;
            sendBtn.disabled = true;

            // Add streaming placeholder
            this.messages.push({
                type: 'streaming',
                text: '',
                timestamp: ''
            });

            this._renderMessages();

            let streamedText = '';
            const streamStartIndex = this.messages.length - 1;

            try {
                const cleanup = this.adapter.sendMessageStream(message, {
                    onDelta: (content) => {
                        console.log('[AIAssistantOverlay] onDelta received:', content);
                        streamedText += content;
                        
                        if (this.messages[streamStartIndex]) {
                            this.messages[streamStartIndex].text = streamedText;
                            this._renderMessages();
                        }
                    },
                    
                    onDone: (response) => {
                        console.log('[AIAssistantOverlay] onDone received:', response);
                        console.log('[AIAssistantOverlay] Final accumulated text:', streamedText);
                        
                        if (this.messages[streamStartIndex]) {
                            this.messages[streamStartIndex].type = 'assistant';
                            this.messages[streamStartIndex].timestamp = new Date().toLocaleTimeString();
                        }
                        
                        this._renderMessages();
                        this._saveCurrentConversation();
                        
                        input.disabled = false;
                        sendBtn.disabled = false;
                        input.focus();
                    },
                    
                    onError: (error) => {
                        this.messages = this.messages.filter(m => m.type !== 'streaming');
                        
                        this.messages.push({
                            type: 'error',
                            text: `Error: ${error}`,
                            timestamp: new Date().toLocaleTimeString()
                        });
                        
                        this._renderMessages();
                        
                        input.disabled = false;
                        sendBtn.disabled = false;
                        input.focus();
                    }
                });

            } catch (error) {
                this.messages = this.messages.filter(m => m.type !== 'streaming');

                this.messages.push({
                    type: 'error',
                    text: `Error: ${error.message}`,
                    timestamp: new Date().toLocaleTimeString()
                });
                
                this._renderMessages();
                
                input.disabled = false;
                sendBtn.disabled = false;
                input.focus();
            }
        }

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
                const isStreaming = msg.type === 'streaming';

                // Define colors based on message type
                const bgColor = isUser ? '#0070f2' : isError ? '#ff4444' : 'white';
                const textColor = (isUser || isError) ? 'white' : '#333';

                return `
                    <div style="margin-bottom: 1rem; display: flex; justify-content: ${isUser ? 'flex-end' : 'flex-start'};">
                        <div style="
                            max-width: 70%; 
                            padding: 0.75rem; 
                            border-radius: 8px; 
                            background: ${bgColor};
                            color: ${textColor};
                            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                        ">
                            <div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.9em; color: ${textColor};">
                                ${isUser ? 'You' : isError ? 'Error' : 'Joule'}
                            </div>
                            <div style="white-space: pre-wrap; word-break: break-word; color: ${textColor};">
                                ${this._escapeHTML(msg.text || '')}
                                ${isStreaming ? '<span style="display: inline-block; width: 2px; height: 1em; background: currentColor; margin-left: 2px; animation: blink 1s infinite;"></span>' : ''}
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

            // Add blink animation if not exists
            if (!document.getElementById('blink-animation')) {
                const style = document.createElement('style');
                style.id = 'blink-animation';
                style.textContent = `
                    @keyframes blink {
                        0%, 49% { opacity: 1; }
                        50%, 100% { opacity: 0; }
                    }
                `;
                document.head.appendChild(style);
            }

            container.scrollTop = container.scrollHeight;
        }

        _escapeHTML(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // ==================== Conversation Management ====================

        _loadConversations() {
            try {
                const saved = localStorage.getItem('ai_conversations');
                if (saved) {
                    this.conversations = JSON.parse(saved);
                    this.currentConversationId = localStorage.getItem('ai_current_conversation');
                }
            } catch (error) {
                console.error('[AIAssistantOverlay] Load error:', error);
                this.conversations = {};
            }
        }

        _saveConversations() {
            try {
                localStorage.setItem('ai_conversations', JSON.stringify(this.conversations));
                if (this.currentConversationId) {
                    localStorage.setItem('ai_current_conversation', this.currentConversationId);
                }
            } catch (error) {
                console.error('[AIAssistantOverlay] Save error:', error);
            }
        }

        _createNewConversation() {
            const id = 'conv_' + Date.now();
            const now = new Date().toISOString();
            
            this.currentConversationId = id;
            this.conversations[id] = {
                id: id,
                title: 'New Conversation',
                messages: [],
                created: now,
                updated: now
            };
            
            this.messages = [];
            this._saveConversations();
        }

        _loadConversation(id) {
            if (this.conversations[id]) {
                this.currentConversationId = id;
                this.messages = this.conversations[id].messages || [];
                this._saveConversations();
            }
        }

        _saveCurrentConversation() {
            if (!this.currentConversationId) return;
            
            const conv = this.conversations[this.currentConversationId];
            if (!conv) return;
            
            conv.messages = this.messages;
            conv.updated = new Date().toISOString();
            
            if (conv.title === 'New Conversation' && this.messages.length > 0) {
                const firstUserMsg = this.messages.find(m => m.type === 'user');
                if (firstUserMsg) {
                    conv.title = firstUserMsg.text.substring(0, 50) + 
                                 (firstUserMsg.text.length > 50 ? '...' : '');
                }
            }
            
            this._saveConversations();
        }

        _deleteConversation(id) {
            delete this.conversations[id];
            
            if (id === this.currentConversationId) {
                this._createNewConversation();
            }
            
            this._saveConversations();
            this._renderHistory();
            this._renderMessages();
        }

        _renderHistory() {
            const container = document.getElementById('ai-history');
            if (!container) return;

            const convArray = Object.values(this.conversations)
                .sort((a, b) => new Date(b.updated) - new Date(a.updated));

            if (convArray.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; color: #999; font-size: 0.85em; padding: 1rem;">
                        No conversations yet
                    </div>
                `;
                return;
            }

            container.innerHTML = convArray.map(conv => {
                const isActive = conv.id === this.currentConversationId;
                const msgCount = conv.messages?.length || 0;
                const date = new Date(conv.updated).toLocaleDateString();

                return `
                    <div 
                        data-conv-id="${conv.id}"
                        style="
                            padding: 0.5rem;
                            margin-bottom: 0.25rem;
                            background: ${isActive ? '#e3f2fd' : '#f9f9f9'};
                            border: 1px solid ${isActive ? '#2196f3' : '#ddd'};
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 0.85em;
                        "
                    >
                        <div style="font-weight: ${isActive ? '600' : '500'}; margin-bottom: 0.25rem;">
                            ${this._escapeHTML(conv.title)}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #666;">
                            <span>${msgCount} msgs</span>
                            <span>${date}</span>
                        </div>
                        <button
                            data-delete-id="${conv.id}"
                            style="
                                margin-top: 0.25rem;
                                padding: 0.25rem 0.5rem;
                                background: #ff4444;
                                color: white;
                                border: none;
                                border-radius: 3px;
                                cursor: pointer;
                                font-size: 0.75em;
                                width: 100%;
                            "
                            onclick="event.stopPropagation()"
                        >
                            Delete
                        </button>
                    </div>
                `;
            }).join('');

            // Attach click handlers
            container.querySelectorAll('[data-conv-id]').forEach(el => {
                const convId = el.getAttribute('data-conv-id');
                el.addEventListener('click', (e) => {
                    if (!e.target.hasAttribute('data-delete-id')) {
                        this._loadConversation(convId);
                        this._renderMessages();
                        this._renderHistory();
                    }
                });
            });

            container.querySelectorAll('[data-delete-id]').forEach(btn => {
                const delId = btn.getAttribute('data-delete-id');
                btn.addEventListener('click', () => {
                    if (confirm('Delete this conversation?')) {
                        this._deleteConversation(delId);
                    }
                });
            });
        }
    }

    window.AIAssistantOverlay = AIAssistantOverlay;
    console.log('[AIAssistantOverlay] Simplified version loaded');

})();