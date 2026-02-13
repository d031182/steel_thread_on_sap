/**
 * AI Assistant V2 Module Entry Point
 * ===================================
 * 
 * App V2 Module Integration:
 * - Uses DependencyContainer pattern
 * - Publishes events via EventBus
 * - Shell overlay pattern (no routes needed)
 * 
 * Architecture: Adapter Pattern + Shell Overlay
 * Dependencies: None (standalone)
 * 
 * @module ai_assistant
 * @version 1.0.0
 * @author P2P Development Team
 * @date 2026-02-13
 */

(function() {
    'use strict';

    /**
     * Module factory function
     * Called by ModuleRegistry to create module instance
     * 
     * @param {Object} container - DependencyContainer instance
     * @param {Object} eventBus - EventBus instance
     * @returns {Object} Module interface
     */
    window.AIAssistantModule = function(container, eventBus) {
        
        // ====================
        // DEPENDENCY RESOLUTION
        // ====================
        
        const logger = container.has('ILogger') 
            ? container.get('ILogger')
            : { 
                log: (msg) => console.log('[AIAssistant]', msg),
                warn: (msg) => console.warn('[AIAssistant]', msg),
                error: (msg) => console.error('[AIAssistant]', msg)
              };

        logger.log('Module initialized');

        // ====================
        // MODULE STATE
        // ====================
        
        let adapter = null;
        let overlay = null;
        let isInitialized = false;

        // ====================
        // PUBLIC API
        // ====================
        
        return {
            /**
             * Get module metadata
             */
            getMetadata: function() {
                return {
                    id: 'ai_assistant',
                    name: 'AI Assistant',
                    version: '1.0.0',
                    description: 'Joule AI Assistant powered by Groq',
                    category: 'Productivity',
                    icon: 'sap-icon://collaborate',
                    dependencies: {
                        required: [],
                        optional: ['ILogger']
                    }
                };
            },

            /**
             * Initialize module
             * Called once when module is first loaded
             */
            initialize: async function() {
                if (isInitialized) {
                    logger.warn('Module already initialized');
                    return;
                }

                logger.log('Initializing AI Assistant module...');

                try {
                    // Load adapter and overlay classes
                    if (!window.AIAssistantAdapter || !window.AIAssistantOverlay) {
                        throw new Error('AI Assistant classes not loaded');
                    }

                    // Create adapter (will use real API)
                    adapter = new window.AIAssistantAdapter();

                    // Create overlay instance
                    overlay = new window.AIAssistantOverlay(adapter);

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

                    isInitialized = true;
                    logger.log('Module initialized successfully');
                    logger.log('Press Ctrl+Shift+A to open AI Assistant');

                    // Publish initialization complete event
                    eventBus.publish('module:initialized', {
                        moduleId: 'ai_assistant',
                        timestamp: new Date().toISOString()
                    });

                } catch (error) {
                    logger.error('Module initialization failed', error);
                    throw error;
                }
            },

            /**
             * Get shell actions (button in app header)
             * 
             * @returns {Array} Shell action definitions
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
            },

            /**
             * Check if module can be activated
             * Returns false if required dependencies missing
             */
            canActivate: function() {
                // No required dependencies, always can activate
                return true;
            },

            /**
             * Get module status
             */
            getStatus: function() {
                return {
                    initialized: isInitialized,
                    hasAdapter: adapter !== null,
                    hasOverlay: overlay !== null
                };
            },

            /**
             * Destroy module and cleanup resources
             * Called when navigating away or app shutdown
             */
            destroy: function() {
                logger.log('Destroying module...');

                try {
                    // Cleanup overlay
                    if (overlay && overlay.close) {
                        overlay.close();
                        overlay = null;
                    }

                    // Cleanup adapter
                    adapter = null;

                    // Remove global reference
                    if (window.aiAssistant) {
                        delete window.aiAssistant;
                    }

                    // Publish destroy event
                    eventBus.publish('module:destroyed', {
                        moduleId: 'ai_assistant',
                        timestamp: new Date().toISOString()
                    });

                    logger.log('Module destroyed successfully');

                } catch (error) {
                    logger.error('Module destroy failed', error);
                }
            }
        };
    };

    console.log('[AIAssistant] Module factory registered');

})();