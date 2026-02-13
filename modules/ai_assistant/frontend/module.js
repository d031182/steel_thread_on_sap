sap.ui.define([
    "modules/ai_assistant/frontend/adapters/AIAssistantAdapter",
    "modules/ai_assistant/frontend/views/AIAssistantOverlay"
], function(AIAssistantAdapter, AIAssistantOverlay) {
    "use strict";

    /**
     * AI Assistant v2 Module
     * 
     * Registers with app_v2 modular architecture
     */
    return {
        id: "ai_assistant",
        name: "AI Assistant",
        version: "1.0.0",

        /**
         * Initialize module
         * 
         * @param {Object} container - Dependency container
         */
        init: function(container) {
            console.log("[AI Assistant v2] Initializing...");

            // Create adapter (will use real API when backend ready)
            const adapter = new AIAssistantAdapter();

            // Create overlay instance
            const overlay = new AIAssistantOverlay(adapter);

            // Register with global namespace for shell button access
            window.aiAssistant = {
                open: () => overlay.open(),
                close: () => overlay.close(),
                clear: () => overlay.clearConversation()
            };

            // Register keyboard shortcut (Ctrl+Shift+A)
            document.addEventListener("keydown", (event) => {
                if (event.ctrlKey && event.shiftKey && event.key === "A") {
                    event.preventDefault();
                    overlay.open();
                }
            });

            console.log("[AI Assistant v2] Initialized successfully");
            console.log("[AI Assistant v2] Press Ctrl+Shift+A to open");

            return {
                adapter: adapter,
                overlay: overlay
            };
        },

        /**
         * Get module routes (none needed for overlay)
         */
        getRoutes: function() {
            return [];
        },

        /**
         * Get shell actions (button in app header)
         */
        getShellActions: function() {
            return [
                {
                    id: "open_ai_assistant",
                    icon: "sap-icon://collaborate",
                    text: "AI Assistant",
                    tooltip: "Open Joule AI Assistant (Ctrl+Shift+A)",
                    press: function() {
                        if (window.aiAssistant) {
                            window.aiAssistant.open();
                        }
                    }
                }
            ];
        }
    };
});