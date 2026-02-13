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
         * Send chat message (Phase 2: Single endpoint)
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
    }

    // Export to window for module.js to use
    window.AIAssistantAdapter = AIAssistantAdapter;
    console.log('[AIAssistantAdapter] Class registered');

})();