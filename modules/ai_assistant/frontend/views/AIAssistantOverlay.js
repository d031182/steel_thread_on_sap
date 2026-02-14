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
            this.highlightJsLoaded = false; // Phase 4.1: Track highlight.js loading
            this.searchQuery = ''; // Phase 4.3: Track search query
            
            // Load saved conversations on init
            this._loadConversations();
            
            // Phase 4.1: Load highlight.js for code syntax highlighting
            this._loadHighlightJS();
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
                        
                        <!-- Phase 4.3: Search Input -->
                        <div style="position: relative; margin-bottom: 0.5rem;">
                            <input 
                                type="text" 
                                id="ai-search" 
                                placeholder="Search conversations..."
                                style="
                                    width: 100%;
                                    padding: 0.5rem 2rem 0.5rem 0.5rem;
                                    border: 1px solid #ccc;
                                    border-radius: 4px;
                                    font-size: 0.85em;
                                    box-sizing: border-box;
                                "
                            />
                            <button
                                id="ai-search-clear"
                                style="
                                    position: absolute;
                                    right: 0.25rem;
                                    top: 50%;
                                    transform: translateY(-50%);
                                    background: none;
                                    border: none;
                                    cursor: pointer;
                                    font-size: 1.2em;
                                    color: #999;
                                    padding: 0.25rem;
                                    display: none;
                                "
                                title="Clear search"
                            >
                                ✕
                            </button>
                        </div>
                        
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

            // Phase 4.3: Search event handlers
            const searchInput = document.getElementById('ai-search');
            const searchClearBtn = document.getElementById('ai-search-clear');
            
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    this.searchQuery = e.target.value.trim().toLowerCase();
                    this._renderHistory();
                    
                    // Show/hide clear button
                    if (searchClearBtn) {
                        searchClearBtn.style.display = this.searchQuery ? 'block' : 'none';
                    }
                });
            }
            
            if (searchClearBtn) {
                searchClearBtn.addEventListener('click', () => {
                    if (searchInput) {
                        searchInput.value = '';
                        this.searchQuery = '';
                        this._renderHistory();
                        searchClearBtn.style.display = 'none';
                    }
                });
            }

            // Render initial history
            this._renderHistory();
        }

        /**
         * Send message to AI with streaming (Phase 4.4)
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

            // Add streaming message placeholder
            this.messages.push({
                type: 'streaming',
                text: '',
                timestamp: '',
                toolCalls: [] // Track tool calls during stream
            });

            this._renderMessages();

            // Accumulate streamed text
            let streamedText = '';
            const streamStartIndex = this.messages.length - 1;

            try {
                // Call streaming API (Phase 4.4)
                const cleanup = this.adapter.sendMessageStream(message, {
                    onDelta: (content) => {
                        // Accumulate text
                        streamedText += content;
                        
                        // Update streaming message
                        if (this.messages[streamStartIndex]) {
                            this.messages[streamStartIndex].text = streamedText;
                            this._renderMessages();
                        }
                    },
                    
                    onToolCall: (toolName) => {
                        console.log('[AIAssistantOverlay] Tool call:', toolName);
                        
                        // Track tool call
                        if (this.messages[streamStartIndex]) {
                            this.messages[streamStartIndex].toolCalls.push(toolName);
                            this._renderMessages();
                        }
                    },
                    
                    onDone: (response, conversationId) => {
                        console.log('[AIAssistantOverlay] Stream done:', response);
                        
                        // Convert streaming message to final assistant message
                        if (this.messages[streamStartIndex]) {
                            this.messages[streamStartIndex].type = 'assistant';
                            this.messages[streamStartIndex].timestamp = new Date().toLocaleTimeString();
                            delete this.messages[streamStartIndex].toolCalls; // Remove tool calls array
                        }
                        
                        this._renderMessages();
                        this._saveCurrentConversation();
                        
                        // Re-enable input
                        input.disabled = false;
                        sendBtn.disabled = false;
                        input.focus();
                    },
                    
                    onError: (error) => {
                        console.error('[AIAssistantOverlay] Stream error:', error);
                        
                        // Remove streaming message
                        this.messages = this.messages.filter(m => m.type !== 'streaming');
                        
                        // Add error message
                        this.messages.push({
                            type: 'error',
                            text: `Error: ${error}`,
                            timestamp: new Date().toLocaleTimeString()
                        });
                        
                        this._renderMessages();
                        
                        // Re-enable input
                        input.disabled = false;
                        sendBtn.disabled = false;
                        input.focus();
                    }
                });

            } catch (error) {
                console.error('[AIAssistantOverlay] Error:', error);

                // Remove streaming message
                this.messages = this.messages.filter(m => m.type !== 'streaming');

                // Add error message
                this.messages.push({
                    type: 'error',
                    text: `Error: ${error.message}`,
                    timestamp: new Date().toLocaleTimeString()
                });
                
                this._renderMessages();
                
                // Re-enable input
                input.disabled = false;
                sendBtn.disabled = false;
                input.focus();
            }
        }

        /**
         * Render messages (Phase 4.4: Streaming support)
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

            container.innerHTML = this.messages.map((msg, index) => {
                const isUser = msg.type === 'user';
                const isError = msg.type === 'error';
                const isStreaming = msg.type === 'streaming';
                const isAssistant = msg.type === 'assistant';

                // Phase 4.4: Show tool calls during streaming
                const toolCallsHTML = isStreaming && msg.toolCalls && msg.toolCalls.length > 0
                    ? `<div style="font-size: 0.85em; opacity: 0.8; margin-top: 0.5rem; padding: 0.5rem; background: rgba(33, 150, 243, 0.1); border-radius: 4px;">
                        🔍 ${msg.toolCalls.map(t => `Using tool: ${t}`).join(', ')}
                       </div>`
                    : '';

                return `
                    <div style="margin-bottom: 1rem; display: flex; justify-content: ${isUser ? 'flex-end' : 'flex-start'};">
                        <div class="ai-message-bubble" data-msg-index="${index}" style="
                            max-width: 70%; 
                            padding: 0.75rem; 
                            border-radius: 8px; 
                            background: ${isUser ? '#0070f2' : isError ? '#ff4444' : 'white'};
                            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                        ">
                            <div class="ai-message-label">
                                ${isUser ? 'You' : isError ? 'Error' : 'Joule'}
                                ${isStreaming ? `
                                    <span class="typing-indicator" style="display: inline-flex; gap: 3px;">
                                        <span style="width: 6px; height: 6px; background: #666; border-radius: 50%; animation: typing-dot 1.4s infinite;"></span>
                                        <span style="width: 6px; height: 6px; background: #666; border-radius: 50%; animation: typing-dot 1.4s infinite 0.2s;"></span>
                                        <span style="width: 6px; height: 6px; background: #666; border-radius: 50%; animation: typing-dot 1.4s infinite 0.4s;"></span>
                                    </span>
                                ` : ''}
                            </div>
                            <div class="ai-message-content" style="white-space: pre-wrap; word-break: break-word; ${isStreaming ? 'min-height: 1.2em;' : ''} color: ${isUser || isError ? 'white' : '#333'};">
                                ${isAssistant ? this._formatMessageText(msg.text) : this._escapeHTML(msg.text || (isStreaming ? '' : ''))}
                                ${isStreaming && msg.text ? '<span class="typing-cursor" style="display: inline-block; width: 2px; height: 1em; background: #666; margin-left: 2px; animation: blink 1s infinite;"></span>' : ''}
                            </div>
                            ${toolCallsHTML}
                            ${msg.timestamp ? `
                                <div class="ai-message-timestamp" style="font-size: 0.75em; opacity: 0.7; margin-top: 0.25rem;">
                                    ${msg.timestamp}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');

            // Phase 4.4: Add CSS animations for streaming
            if (!document.getElementById('streaming-animations')) {
                const style = document.createElement('style');
                style.id = 'streaming-animations';
                style.textContent = `
                    @keyframes typing-dot {
                        0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
                        30% { transform: translateY(-8px); opacity: 1; }
                    }
                    @keyframes blink {
                        0%, 49% { opacity: 1; }
                        50%, 100% { opacity: 0; }
                    }
                `;
                document.head.appendChild(style);
            }

            // Phase 4.2: Attach copy button event handlers
            container.querySelectorAll('.copy-code-btn').forEach(btn => {
                const codeId = btn.getAttribute('data-code-id');
                btn.addEventListener('click', () => this._copyCodeToClipboard(codeId));
            });

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
         * Phase 4.3: Includes search filtering and highlighting
         * @private
         */
        _renderHistory() {
            const container = document.getElementById('ai-history');
            if (!container) return;

            let convArray = Object.values(this.conversations)
                .sort((a, b) => new Date(b.updated) - new Date(a.updated));

            // Phase 4.3: Filter conversations by search query
            if (this.searchQuery) {
                convArray = convArray.filter(conv => {
                    // Search in title
                    if (conv.title.toLowerCase().includes(this.searchQuery)) {
                        return true;
                    }
                    
                    // Search in message content
                    if (conv.messages && conv.messages.some(msg => 
                        msg.text && msg.text.toLowerCase().includes(this.searchQuery)
                    )) {
                        return true;
                    }
                    
                    return false;
                });
            }

            if (convArray.length === 0) {
                const emptyMessage = this.searchQuery 
                    ? `No conversations match "${this._escapeHTML(this.searchQuery)}"`
                    : 'No conversations yet';
                    
                container.innerHTML = `
                    <div style="text-align: center; color: #999; font-size: 0.85em; padding: 1rem;">
                        ${emptyMessage}
                    </div>
                `;
                return;
            }

            container.innerHTML = convArray.map(conv => {
                const isActive = conv.id === this.currentConversationId;
                const msgCount = conv.messages?.length || 0;
                const date = new Date(conv.updated).toLocaleDateString();

                // Phase 4.3: Highlight matching search terms in title
                const displayTitle = this.searchQuery 
                    ? this._highlightSearchTerms(conv.title, this.searchQuery)
                    : this._escapeHTML(conv.title);

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
                            ${displayTitle}
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

        // ==================== Phase 4.3: Search Highlighting ====================

        /**
         * Highlight search terms in text
         * Phase 4.3: Wraps matching terms in <mark> tags
         * @private
         */
        _highlightSearchTerms(text, query) {
            if (!query) return this._escapeHTML(text);
            
            const escaped = this._escapeHTML(text);
            const regex = new RegExp(`(${this._escapeRegex(query)})`, 'gi');
            
            return escaped.replace(regex, '<mark style="background: #ffeb3b; padding: 0 2px;">$1</mark>');
        }

        /**
         * Escape special regex characters
         * @private
         */
        _escapeRegex(str) {
            return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
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

        // ==================== Phase 4.1: Code Syntax Highlighting ====================

        /**
         * Load highlight.js library from CDN
         * @private
         */
        _loadHighlightJS() {
            if (this.highlightJsLoaded || window.hljs) {
                this.highlightJsLoaded = true;
                return;
            }

            // Load CSS
            const cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css';
            document.head.appendChild(cssLink);

            // Load JS
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js';
            script.onload = () => {
                this.highlightJsLoaded = true;
                console.log('[AIAssistantOverlay] highlight.js loaded');
            };
            script.onerror = () => {
                console.error('[AIAssistantOverlay] Failed to load highlight.js');
            };
            document.head.appendChild(script);
        }

        /**
         * Format message text with code syntax highlighting
         * Phase 4.1: Detects ```language code blocks and applies highlighting
         * @private
         */
        _formatMessageText(text) {
            console.log('[AIAssistantOverlay] Formatting text:', text.substring(0, 200));
            
            if (!this.highlightJsLoaded || !window.hljs) {
                console.log('[AIAssistantOverlay] highlight.js not ready');
                return this._escapeHTML(text);
            }

            // Detect code blocks: ```language\n code \n```
            const codeBlockPattern = /```(\w+)?\n([\s\S]*?)```/g;
            
            // Split text into parts (code blocks and regular text)
            const parts = [];
            let lastIndex = 0;
            let match;

            // Reset regex
            codeBlockPattern.lastIndex = 0;

            // Find all code blocks
            while ((match = codeBlockPattern.exec(text)) !== null) {
                // Add text before code block (escaped)
                if (match.index > lastIndex) {
                    parts.push(this._escapeHTML(text.substring(lastIndex, match.index)));
                }

                const language = match[1] || 'plaintext';
                const code = match[2];
                
                try {
                    // Highlight code
                    const highlighted = language && window.hljs.getLanguage(language)
                        ? window.hljs.highlight(code, { language }).value
                        : window.hljs.highlightAuto(code).value;
                    
                    // Phase 4.2: Add copy button to code block
                    const codeBlockId = 'code-block-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
                    parts.push(`
                        <div class="code-block-container" style="position: relative;">
                            <button 
                                class="copy-code-btn" 
                                data-code-id="${codeBlockId}"
                                style="
                                    position: absolute;
                                    top: 0.5rem;
                                    right: 0.5rem;
                                    padding: 0.25rem 0.75rem;
                                    background: rgba(255, 255, 255, 0.9);
                                    border: 1px solid #ccc;
                                    border-radius: 4px;
                                    cursor: pointer;
                                    font-size: 0.8em;
                                    font-weight: 500;
                                    transition: all 0.2s;
                                    z-index: 10;
                                "
                                onmouseover="this.style.background='rgba(255,255,255,1)'; this.style.transform='scale(1.05)'"
                                onmouseout="this.style.background='rgba(255,255,255,0.9)'; this.style.transform='scale(1)'"
                            >
                                📋 Copy
                            </button>
                            <pre><code class="hljs language-${language}" data-code-id="${codeBlockId}">${highlighted}</code></pre>
                            <textarea 
                                id="${codeBlockId}" 
                                style="position: absolute; left: -9999px;"
                            >${this._escapeHTML(code)}</textarea>
                        </div>
                    `);
                } catch (error) {
                    console.error('[AIAssistantOverlay] Highlight error:', error);
                    // Fallback: show code without highlighting
                    const codeBlockId = 'code-block-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
                    parts.push(`
                        <div class="code-block-container" style="position: relative;">
                            <button 
                                class="copy-code-btn" 
                                data-code-id="${codeBlockId}"
                                style="
                                    position: absolute;
                                    top: 0.5rem;
                                    right: 0.5rem;
                                    padding: 0.25rem 0.75rem;
                                    background: rgba(255, 255, 255, 0.9);
                                    border: 1px solid #ccc;
                                    border-radius: 4px;
                                    cursor: pointer;
                                    font-size: 0.8em;
                                    font-weight: 500;
                                    transition: all 0.2s;
                                    z-index: 10;
                                "
                            >
                                📋 Copy
                            </button>
                            <pre><code data-code-id="${codeBlockId}">${this._escapeHTML(code)}</code></pre>
                            <textarea 
                                id="${codeBlockId}" 
                                style="position: absolute; left: -9999px;"
                            >${this._escapeHTML(code)}</textarea>
                        </div>
                    `);
                }

                lastIndex = codeBlockPattern.lastIndex;
            }

            // Add remaining text after last code block (escaped)
            if (lastIndex < text.length) {
                parts.push(this._escapeHTML(text.substring(lastIndex)));
            }

            return parts.join('');
        }

        // ==================== Phase 4.2: Copy Button ====================

        /**
         * Copy code to clipboard
         * Phase 4.2: One-click clipboard copy with visual feedback
         * @private
         */
        _copyCodeToClipboard(codeBlockId) {
            try {
                // Get the hidden textarea containing raw code
                const textarea = document.getElementById(codeBlockId);
                if (!textarea) {
                    console.error('[AIAssistantOverlay] Code block not found:', codeBlockId);
                    return;
                }

                // Get the button
                const button = document.querySelector(`button[data-code-id="${codeBlockId}"]`);

                // Copy to clipboard using Clipboard API
                navigator.clipboard.writeText(textarea.value).then(() => {
                    console.log('[AIAssistantOverlay] Code copied successfully');
                    
                    // Visual feedback: Change button text temporarily
                    if (button) {
                        const originalText = button.textContent;
                        button.textContent = '✅ Copied!';
                        button.style.background = 'rgba(76, 175, 80, 0.9)';
                        button.style.color = 'white';
                        
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.background = 'rgba(255, 255, 255, 0.9)';
                            button.style.color = '';
                        }, 2000);
                    }

                    // Toast notification
                    sap.m.MessageToast.show('Code copied to clipboard!');
                }).catch(err => {
                    console.error('[AIAssistantOverlay] Copy failed:', err);
                    sap.m.MessageToast.show('Failed to copy code: ' + err.message);
                });
            } catch (error) {
                console.error('[AIAssistantOverlay] Copy error:', error);
                sap.m.MessageToast.show('Copy error: ' + error.message);
            }
        }
    }

    // Export to window for module.js to use
    window.AIAssistantOverlay = AIAssistantOverlay;
    console.log('[AIAssistantOverlay] Class registered');

})();
