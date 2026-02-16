/**
 * AI Assistant API Adapter
 * 
 * Handles communication with backend AI assistant conversation API
 * Phase 2: Real AI integration with Groq
 * Phase 4.7: SQL Execution UI support
 * 
 * @class AIAssistantAdapter
 */
(function() {
    'use strict';

    class AIAssistantAdapter {
        constructor(baseUrl = "") {
            this.baseUrl = baseUrl || "";
        }

        /**
         * Send chat message (Phase 2: Single endpoint - non-streaming)
         * 
         * @param {string} message - User message
         * @param {Object} context - Optional conversation context
         *   - datasource: 'hana' | 'p2p_data' (required for correct data routing)
         *   - conversation_id: string (optional, for multi-turn conversations)
         * @returns {Promise<Object>} API response with assistant message
         */
        async sendMessage(message, context) {
            try {
                // Build request body
                const requestBody = {
                    message
                };
                
                // Add conversation_id if provided (for context persistence)
                if (context && context.conversation_id) {
                    requestBody.conversation_id = context.conversation_id;
                }
                
                // Add context with datasource (for correct data routing)
                if (context && context.datasource) {
                    requestBody.context = {
                        datasource: context.datasource
                    };
                }
                
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/chat`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(requestBody)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();

            } catch (error) {
                console.error("[AIAssistantAdapter] Failed to send message:", error);
                throw error;
            }
        }

        /**
         * Send chat message with streaming response (Phase 4.4)
         * 
         * Uses Server-Sent Events (SSE) for real-time streaming responses
         * 
         * @param {string} message - User message
         * @param {Object} callbacks - Event callbacks
         * @param {Function} callbacks.onDelta - Called for each text chunk (content)
         * @param {Function} callbacks.onToolCall - Called when agent uses P2P tools (tool_name)
         * @param {Function} callbacks.onDone - Called when stream completes (response, conversation_id)
         * @param {Function} callbacks.onError - Called on error (error)
         * @returns {Function} Cleanup function to close EventSource
         */
        sendMessageStream(message, callbacks) {
            const {
                onDelta = () => {},
                onToolCall = () => {},
                onDone = () => {},
                onError = () => {}
            } = callbacks;

            // Create EventSource for SSE
            const url = `${this.baseUrl}/api/ai-assistant/chat/stream`;
            
            // Use fetch with POST for request body, then get readable stream
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                // Read stream
                const readChunk = () => {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            console.log('[AIAssistantAdapter] Stream complete');
                            return;
                        }

                        // Decode chunk and add to buffer
                        buffer += decoder.decode(value, { stream: true });

                        // Process complete SSE messages (split by \n\n)
                        const messages = buffer.split('\n\n');
                        buffer = messages.pop(); // Keep incomplete message in buffer

                        messages.forEach(msg => {
                            if (!msg.trim()) return;

                            // Parse SSE format: "data: {json}"
                            const match = msg.match(/^data: (.+)$/m);
                            if (!match) return;

                            const dataStr = match[1];
                            
                            // Check for completion signal
                            if (dataStr === '[DONE]') {
                                return;
                            }

                            try {
                                const event = JSON.parse(dataStr);

                                switch (event.type) {
                                    case 'delta':
                                        onDelta(event.content);
                                        break;
                                    
                                    case 'tool_call':
                                        onToolCall(event.tool_name);
                                        break;
                                    
                                    case 'done':
                                        onDone(event.response, event.conversation_id);
                                        break;
                                    
                                    case 'error':
                                        onError(event.error);
                                        break;
                                }
                            } catch (e) {
                                console.error('[AIAssistantAdapter] Failed to parse SSE event:', e);
                            }
                        });

                        // Continue reading
                        readChunk();
                    }).catch(error => {
                        console.error('[AIAssistantAdapter] Stream read error:', error);
                        onError(error.message);
                    });
                };

                readChunk();
            })
            .catch(error => {
                console.error('[AIAssistantAdapter] Failed to start stream:', error);
                onError(error.message);
            });

            // Return cleanup function (no-op for fetch streams)
            return () => {
                console.log('[AIAssistantAdapter] Stream cleanup requested');
            };
        }

        /**
         * Execute SQL query (Phase 4.7)
         * 
         * @param {string} query - SQL query to execute
         * @param {string} database - Database name ('p2p_data' or 'p2p_graph')
         * @returns {Promise<Object>} Execution result with rows, columns, metadata
         */
        async executeSQL(query, database = 'p2p_data') {
            try {
                const startTime = Date.now();
                
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/sql/execute`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ 
                        sql: query.trim(),
                        datasource: database
                    })
                });

                const data = await response.json();
                const executionTime = Date.now() - startTime;

                if (!response.ok) {
                    throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                // Add execution time to result
                return {
                    ...data,
                    execution_time_ms: executionTime
                };

            } catch (error) {
                console.error("[AIAssistantAdapter] Failed to execute SQL:", error);
                throw error;
            }
        }

        /**
         * Create new conversation (Phase 3)
         * 
         * @param {string} title - Optional conversation title
         * @returns {Promise<Object>} Created conversation with id
         */
        async createConversation(title = null) {
            try {
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/conversations`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ title })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();

            } catch (error) {
                console.error("[AIAssistantAdapter] Failed to create conversation:", error);
                throw error;
            }
        }

        /**
         * Load all conversations (Phase 3)
         * 
         * @returns {Promise<Array>} List of conversations with metadata
         */
        async loadConversations() {
            try {
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/conversations`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                return data.conversations || [];

            } catch (error) {
                console.error("[AIAssistantAdapter] Failed to load conversations:", error);
                throw error;
            }
        }

        /**
         * Get conversation by ID (Phase 3)
         * 
         * @param {string} conversationId - Conversation ID
         * @returns {Promise<Object>} Conversation with full message history
         */
        async getConversation(conversationId) {
            try {
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/conversations/${conversationId}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();

            } catch (error) {
                console.error("[AIAssistantAdapter] Failed to get conversation:", error);
                throw error;
            }
        }

        /**
         * Send message to specific conversation (Phase 3)
         * 
         * @param {string} conversationId - Conversation ID
         * @param {string} message - User message
         * @returns {Promise<Object>} API response with assistant message
         */
        async sendMessageToConversation(conversationId, message) {
            try {
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/conversations/${conversationId}/messages`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();

            } catch (error) {
                console.error("[AIAssistantAdapter] Failed to send message to conversation:", error);
                throw error;
            }
        }

        /**
         * Delete conversation (Phase 3)
         * 
         * @param {string} conversationId - Conversation ID to delete
         * @returns {Promise<Object>} Deletion confirmation
         */
        async deleteConversation(conversationId) {
            try {
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/conversations/${conversationId}`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();

            } catch (error) {
                console.error("[AIAssistantAdapter] Failed to delete conversation:", error);
                throw error;
            }
        }

        /**
         * Get conversation context (Phase 4.6)
         * 
         * @param {string} conversationId - Conversation ID
         * @returns {Promise<Object>} Conversation context and metadata
         */
        async getConversationContext(conversationId) {
            try {
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/conversations/${conversationId}/context`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();

            } catch (error) {
                console.error("[AIAssistantAdapter] Failed to get conversation context:", error);
                throw error;
            }
        }
    }

    // Export to window for module.js to use
    window.AIAssistantAdapter = AIAssistantAdapter;
    console.log('[AIAssistantAdapter] Class registered with SQL execution support');

})();