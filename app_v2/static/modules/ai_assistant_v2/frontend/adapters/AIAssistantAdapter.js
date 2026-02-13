sap.ui.define([], function() {
    "use strict";

    /**
     * AI Assistant API Adapter
     * 
     * Handles communication with backend AI assistant API
     * 
     * @class AIAssistantAdapter
     */
    class AIAssistantAdapter {
        constructor(baseUrl = "") {
            this.baseUrl = baseUrl || "";
            this.apiEndpoint = "/api/ai-assistant/chat";
        }

        /**
         * Send message to AI assistant
         * 
         * @param {Object} payload - Message payload
         * @param {string} payload.message - User message
         * @param {string} [payload.conversation_id] - Conversation ID
         * @param {Object} [payload.context] - Additional context
         * @returns {Promise<Object>} API response
         */
        async sendMessage(payload) {
            try {
                const response = await fetch(this.baseUrl + this.apiEndpoint, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                return data;

            } catch (error) {
                console.error("AI Assistant API error:", error);
                throw error;
            }
        }

        /**
         * Get conversation history
         * 
         * @param {string} conversationId - Conversation ID
         * @returns {Promise<Object>} Conversation history
         */
        async getConversationHistory(conversationId) {
            try {
                const response = await fetch(
                    `${this.baseUrl}/api/ai-assistant/conversation/${conversationId}`,
                    {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();

            } catch (error) {
                console.error("Failed to load conversation history:", error);
                throw error;
            }
        }

        /**
         * Export conversation as markdown
         * 
         * @param {Array} messages - Message array
         * @returns {string} Markdown formatted conversation
         */
        exportConversation(messages) {
            let markdown = "# AI Assistant Conversation\n\n";
            markdown += `*Exported: ${new Date().toLocaleString()}*\n\n`;
            markdown += "---\n\n";

            messages.forEach(msg => {
                if (msg.type === "typing") return;  // Skip typing indicators

                markdown += `### ${msg.sender} (${msg.timestamp})\n\n`;
                markdown += `${msg.message}\n\n`;

                if (msg.sources && msg.sources.length > 0) {
                    markdown += `*Sources: ${msg.sources.join(", ")}*\n\n`;
                }

                if (msg.confidence) {
                    markdown += `*Confidence: ${(msg.confidence * 100).toFixed(1)}%*\n\n`;
                }

                markdown += "---\n\n";
            });

            return markdown;
        }

        /**
         * Download conversation as file
         * 
         * @param {Array} messages - Message array
         * @param {string} [filename] - Output filename
         */
        downloadConversation(messages, filename = "conversation.md") {
            const markdown = this.exportConversation(messages);
            const blob = new Blob([markdown], { type: "text/markdown" });
            const url = URL.createObjectURL(blob);

            const link = document.createElement("a");
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            URL.revokeObjectURL(url);
        }
    }

    return AIAssistantAdapter;
});