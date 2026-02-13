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
            this.currentConversationId = null;
            this.conversations = {}; // { id: { id, title, messages, created, updated } }
            
            // Load saved conversations on init
            this._loadConversations();
        }

        /**
         * Open the AI Assistant overlay
         */
        open() {
            if (!this.dialog) {
                this._createDialog();
            }
            
            // Restore last active conversation or create new
            if (!this.currentConversationId) {
                this._createNewConversation();
            } else {
                this._loadConversation(this.currentConversationId);
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
         * Clear conversation (start new)
         */
        clearConversation() {
            this._createNewConversation();
            this._renderMessages();
            this._renderHistory();
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
                <div style="display: flex; height: 600px; width: 100%; gap: 1rem;">
                    <!-- Sidebar: Conversation History -->
                    <div style="width: 200px; display: flex; flex-direction: column; border-right: 1px solid #ddd; padding-right: 1rem;">
                        <div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.9em;">Conversations</div>
                        <div id="ai-history" style="flex: 1; overflow-y: auto;">
                            <!-- History rendered here -->
                        </div>
                        <button 
                            id="ai-export" 
                            style="margin-top: 0.5rem; padding: 0.5rem; background: #f5f5f5; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; font-size: 0.85em;"
                        >
                            Export All
                        </button>
                        <button 
                            id="ai-import" 
                            style="margin-top: 0.25rem; padding: 0.5rem; background: #f5f5f5; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; font-size: 0.85em;"
                        >
                            Import
                        </button>
                        <input type="file" id="ai-import-file" accept=".json" style="display: none;" />
                    </div>
                    
                    <!-- Main Chat Area -->
                    <div style="flex: 1; display: flex; flex-direction: column;">
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
            const exportBtn = document.getElementById('ai-export');
            const importBtn = document.getElementById('ai-import');
            const importFile = document.getElementById('ai-import-file');

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

            if (exportBtn) {
                exportBtn.addEventListener('click', () => this._exportConversations());
            }

            if (importBtn) {
                importBtn.addEventListener('click', () => importFile?.click());
            }

            if (importFile) {
                importFile.addEventListener('change', (e) => this._importConversations(e));
            }

            // Render initial history
            this._renderHistory();
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
                this._saveCurrentConversation(); // Phase 3: Auto-save
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

        // ==================== Phase 3: localStorage Persistence ====================

        /**
         * Load conversations from localStorage
         * @private
         */
        _loadConversations() {
            try {
                const saved = localStorage.getItem('ai_conversations');
                if (saved) {
                    this.conversations = JSON.parse(saved);
                    // Load last active conversation ID
                    this.currentConversationId = localStorage.getItem('ai_current_conversation');
                }
            } catch (error) {
                console.error('[AIAssistantOverlay] Failed to load conversations:', error);
                this.conversations = {};
            }
        }

        /**
         * Save conversations to localStorage
         * @private
         */
        _saveConversations() {
            try {
                localStorage.setItem('ai_conversations', JSON.stringify(this.conversations));
                if (this.currentConversationId) {
                    localStorage.setItem('ai_current_conversation', this.currentConversationId);
                }
            } catch (error) {
                console.error('[AIAssistantOverlay] Failed to save conversations:', error);
            }
        }

        /**
         * Create new conversation
         * @private
         */
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

        /**
         * Load conversation by ID
         * @private
         */
        _loadConversation(id) {
            if (this.conversations[id]) {
                this.currentConversationId = id;
                this.messages = this.conversations[id].messages || [];
                this._saveConversations(); // Save last active
            }
        }

        /**
         * Save current conversation state
         * @private
         */
        _saveCurrentConversation() {
            if (!this.currentConversationId) return;
            
            const conv = this.conversations[this.currentConversationId];
            if (!conv) return;
            
            conv.messages = this.messages;
            conv.updated = new Date().toISOString();
            
            // Auto-generate title from first user message
            if (conv.title === 'New Conversation' && this.messages.length > 0) {
                const firstUserMsg = this.messages.find(m => m.type === 'user');
                if (firstUserMsg) {
                    conv.title = firstUserMsg.text.substring(0, 50) + 
                                 (firstUserMsg.text.length > 50 ? '...' : '');
                }
            }
            
            this._saveConversations();
        }

        /**
         * Delete conversation by ID
         * @private
         */
        _deleteConversation(id) {
            delete this.conversations[id];
            
            // If deleting current conversation, create new one
            if (id === this.currentConversationId) {
                this._createNewConversation();
            }
            
            this._saveConversations();
            this._renderHistory();
            this._renderMessages();
        }

        // ==================== Phase 3: Conversation History UI ====================

        /**
         * Render conversation history sidebar
         * @private
         */
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
                        onmouseover="this.style.background='${isActive ? '#e3f2fd' : '#f0f0f0'}'"
                        onmouseout="this.style.background='${isActive ? '#e3f2fd' : '#f9f9f9'}'"
                    >
                        <div style="font-weight: ${isActive ? '600' : '500'}; margin-bottom: 0.25rem; 
                                    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
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

        // ==================== Phase 3: Export/Import ====================

        /**
         * Export all conversations as JSON
         * @private
         */
        _exportConversations() {
            try {
                const data = {
                    version: '1.0',
                    exported: new Date().toISOString(),
                    conversations: this.conversations
                };

                const json = JSON.stringify(data, null, 2);
                const blob = new Blob([json], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = `joule_conversations_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                
                URL.revokeObjectURL(url);

                sap.m.MessageToast.show('Conversations exported successfully');
            } catch (error) {
                console.error('[AIAssistantOverlay] Export failed:', error);
                sap.m.MessageToast.show('Export failed: ' + error.message);
            }
        }

        /**
         * Import conversations from JSON file
         * @private
         */
        _importConversations(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    
                    // Validate structure
                    if (!data.conversations || typeof data.conversations !== 'object') {
                        throw new Error('Invalid file format');
                    }

                    // Merge conversations (keep existing, add new)
                    this.conversations = { ...this.conversations, ...data.conversations };
                    this._saveConversations();
                    this._renderHistory();

                    const count = Object.keys(data.conversations).length;
                    sap.m.MessageToast.show(`${count} conversation(s) imported successfully`);
                } catch (error) {
                    console.error('[AIAssistantOverlay] Import failed:', error);
                    sap.m.MessageToast.show('Import failed: ' + error.message);
                }
            };

            reader.readAsText(file);
            event.target.value = ''; // Reset file input
        }
    }

    // Export to window for module.js to use
    window.AIAssistantOverlay = AIAssistantOverlay;
    console.log('[AIAssistantOverlay] Class registered');

})();