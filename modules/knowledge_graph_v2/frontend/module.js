/**
 * Knowledge Graph V2 Module Entry Point
 * ======================================
 * 
 * App V2 Module Integration:
 * - Declares dependencies via DependencyContainer
 * - Publishes events via EventBus
 * - Follows SAPUI5 + Clean Architecture patterns
 * 
 * Architecture: MVP (Model-View-Presenter) + Adapter Pattern
 * Dependencies: ILogger (optional), IDataSource (optional)
 * 
 * @module knowledge_graph_v2
 * @version 2.1.0
 * @author P2P Development Team
 * @date 2026-02-08
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
    window.KnowledgeGraphV2Module = function(container, eventBus) {
        
        // ====================
        // DEPENDENCY RESOLUTION
        // ====================
        
        const logger = container.has('ILogger') 
            ? container.get('ILogger')
            : { 
                log: (msg) => console.log('[KnowledgeGraphV2]', msg),
                warn: (msg) => console.warn('[KnowledgeGraphV2]', msg),
                error: (msg) => console.error('[KnowledgeGraphV2]', msg)
              };
        
        const dataSource = container.has('IDataSource')
            ? container.get('IDataSource')
            : null;

        logger.log('Module initialized with dependencies', {
            hasLogger: container.has('ILogger'),
            hasDataSource: container.has('IDataSource')
        });

        // ====================
        // MODULE STATE
        // ====================
        
        let currentView = null;
        let currentPresenter = null;
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
                    id: 'knowledge_graph_v2',
                    name: 'Knowledge Graph v2',
                    version: '2.1.0',
                    description: 'CSN Schema visualization with Clean Architecture',
                    category: 'Analytics',
                    icon: 'sap-icon://org-chart',
                    dependencies: {
                        required: [],
                        optional: ['ILogger', 'IDataSource']
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

                logger.log('Initializing Knowledge Graph V2 module...');

                try {
                    // Subscribe to relevant events
                    eventBus.subscribe('app:theme-changed', (data) => {
                        logger.log('Theme changed', data);
                        // Could refresh graph visualization with new theme
                    });

                    eventBus.subscribe('data:schema-updated', async (data) => {
                        logger.log('Schema updated, refreshing graph', data);
                        if (currentPresenter) {
                            await currentPresenter.refresh();
                        }
                    });

                    isInitialized = true;
                    logger.log('Module initialized successfully');

                    // Publish initialization complete event
                    eventBus.publish('module:initialized', {
                        moduleId: 'knowledge_graph_v2',
                        timestamp: new Date().toISOString()
                    });

                } catch (error) {
                    logger.error('Module initialization failed', error);
                    throw error;
                }
            },

            /**
             * Create and render the module view
             * Called when user navigates to this module
             * 
             * @returns {sap.m.VBox} SAPUI5 control to be rendered
             */
            render: async function() {
                logger.log('Rendering module...');

                try {
                    // Create view (uses existing SAPUI5 implementation)
                    if (!window.createKnowledgeGraphPageV2) {
                        throw new Error('View factory not loaded: createKnowledgeGraphPageV2');
                    }

                    currentView = window.createKnowledgeGraphPageV2();
                    
                    // Initialize view if needed
                    if (window.initializeKnowledgeGraphV2) {
                        await window.initializeKnowledgeGraphV2();
                    }

                    // Publish render complete event
                    eventBus.publish('module:rendered', {
                        moduleId: 'knowledge_graph_v2',
                        timestamp: new Date().toISOString()
                    });

                    logger.log('Module rendered successfully');

                    // Return SAPUI5 control for RouterService to place
                    return currentView;

                } catch (error) {
                    logger.error('Module render failed', error);
                    
                    // Return error message page
                    return new sap.m.MessagePage({
                        title: 'Failed to load Knowledge Graph V2',
                        text: error.message,
                        icon: 'sap-icon://error',
                        description: 'Please try again or contact support.'
                    });
                }
            },

            /**
             * Destroy module and cleanup resources
             * Called when navigating away or app shutdown
             */
            destroy: function() {
                logger.log('Destroying module...');

                try {
                    // Destroy view
                    if (currentView && currentView.destroy) {
                        currentView.destroy();
                        currentView = null;
                    }

                    // Cleanup presenter
                    if (currentPresenter && currentPresenter.destroy) {
                        currentPresenter.destroy();
                        currentPresenter = null;
                    }

                    // Publish destroy event
                    eventBus.publish('module:destroyed', {
                        moduleId: 'knowledge_graph_v2',
                        timestamp: new Date().toISOString()
                    });

                    logger.log('Module destroyed successfully');

                } catch (error) {
                    logger.error('Module destroy failed', error);
                }
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
                    hasView: currentView !== null,
                    dependencies: {
                        logger: container.has('ILogger'),
                        dataSource: container.has('IDataSource')
                    }
                };
            }
        };
    };

    console.log('[KnowledgeGraphV2] Module factory registered');

})();