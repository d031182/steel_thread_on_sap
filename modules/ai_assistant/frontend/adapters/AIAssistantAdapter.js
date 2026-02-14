/**
 * AI Assistant API Adapter
 * 
 * Handles communication with backend AI assistant conversation API
 * Phase 2: Real AI integration with Groq
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
         * @returns {Promise<Object>} API response with assistant message
         */
        async sendMessage(message) {
            try {
                const response = await fetch(`${this.baseUrl}/api/ai-assistant/chat`, {
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
    }

    // Export to window for module.js to use
    window.AIAssistantAdapter = AIAssistantAdapter;
    console.log('[AIAssistantAdapter] Class registered');

})();