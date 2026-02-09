/**
 * Data Products V2 Module
 * =======================
 * 
 * App V2 integration for Data Products browser
 * 
 * Features:
 * - Browse HANA Cloud data products
 * - View table structures and data
 * - CSN schema support
 * - Dependency injection ready
 * - Event-driven architecture
 * 
 * @author P2P Development Team
 * @version 2.0.0
 */

(function() {
    'use strict';

    /**
     * Data Products V2 Factory
     * 
     * Creates module instance with DI and EventBus integration
     * 
     * @param {DependencyContainer} container - DI container
     * @param {EventBus} eventBus - Event bus
     * @returns {Object} Module interface
     */
    window.DataProductsV2Factory = function(container, eventBus) {
        
        // ====================
        // DEPENDENCY RESOLUTION
        // ====================
        
        // Required: DataSource (uses DataProductsAdapter from App V2)
        if (!container.has('IDataSource')) {
            throw new Error('Data Products V2 requires IDataSource');
        }
        const dataSource = container.get('IDataSource');
        
        // Optional: Logger (fallback to console)
        const logger = container.has('ILogger') 
            ? container.get('ILogger')
            : {
                log: (msg) => console.log('[DataProductsV2]', msg),
                warn: (msg) => console.warn('[DataProductsV2]', msg),
                error: (msg) => console.error('[DataProductsV2]', msg)
              };

        // Optional: Cache
        const cache = container.has('ICache') ? container.get('ICache') : null;

        logger.log('Module factory initialized');

        // ====================
        // MODULE STATE
        // ====================
        
        let currentView = null;
        let isInitialized = false;
        let dataProducts = [];
        let currentSource = 'sqlite'; // Default to SQLite

        // ====================
        // PRIVATE METHODS
        // ====================
        
        /**
         * Switch data source and reload
         */
        async function switchSource(newSource) {
            logger.log(`Switching data source to: ${newSource}`);
            currentSource = newSource;
            
            // Re-register adapter with new source
            container.register('IDataSource', () => new DataProductsV2Adapter({
                baseUrl: '/api/v2/data-products',
                source: newSource,
                timeout: 30000
            }));
            
            // Reload data products
            await loadDataProducts();
            
            // Refresh view
            if (currentView && currentView.refresh) {
                currentView.refresh(dataProducts, currentSource);
            }
            
            sap.m.MessageToast.show(`Switched to ${newSource === 'hana' ? 'HANA Cloud' : 'SQLite'}`);
        }
        
        /**
         * Load data products from backend
         */
        async function loadDataProducts() {
            try {
                logger.log('Loading data products...');
                
                // IMPORTANT: Always get fresh adapter from container (in case source switched)
                const currentDataSource = container.get('IDataSource');
                
                // Use DataSource adapter (already handles caching)
                dataProducts = await currentDataSource.query('data_products', {
                    operation: 'list'
                });
                
                logger.log(`Loaded ${dataProducts.length} data products`);
                
                // Publish event
                eventBus.publish('data-products:loaded', {
                    count: dataProducts.length,
                    timestamp: new Date().toISOString()
                });
                
                return dataProducts;
                
            } catch (error) {
                logger.error('Failed to load data products', error);
                
                // SAP Fiori Best Practice: Use MessageBox for errors (not MessageToast)
                // Display user-friendly error with technical details
                const errorMsg = error.message || 'Unknown error occurred';
                const isHanaError = currentSource === 'hana';
                
                sap.m.MessageBox.error(
                    isHanaError 
                        ? `Failed to load data products from HANA Cloud.\n\n${errorMsg}\n\nPlease check your connection or switch to SQLite as fallback.`
                        : `Failed to load data products from SQLite.\n\n${errorMsg}`,
                    {
                        title: "Data Loading Error",
                        actions: isHanaError 
                            ? [sap.m.MessageBox.Action.OK, "Switch to SQLite"]
                            : [sap.m.MessageBox.Action.OK],
                        emphasizedAction: sap.m.MessageBox.Action.OK,
                        onClose: function(action) {
                            if (action === "Switch to SQLite" && isHanaError) {
                                // Auto-switch to SQLite as fallback
                                switchSource('sqlite').catch(fallbackError => {
                                    sap.m.MessageBox.error(
                                        `Failed to switch to SQLite: ${fallbackError.message}`,
                                        { title: "Fallback Failed" }
                                    );
                                });
                            }
                        }
                    }
                );
                
                throw error;
            }
        }

        // ====================
        // PUBLIC API
        // ====================
        
        return {
            /**
             * Get module metadata
             */
            getMetadata: function() {
                return {
                    id: 'data_products_v2',
                    name: 'Data Products V2',
                    version: '2.0.0',
                    description: 'HANA Cloud Data Products browser',
                    category: 'Data Management',
                    icon: 'sap-icon://database',
                    dependencies: {
                        required: ['IDataSource'],
                        optional: ['ILogger', 'ICache']
                    }
                };
            },

            /**
             * Initialize module (called once)
             */
            initialize: async function() {
                if (isInitialized) {
                    logger.warn('Module already initialized');
                    return;
                }

                logger.log('Initializing module...');

                try {
                    // Subscribe to relevant events
                    eventBus.subscribe('data:refreshed', async () => {
                        logger.log('Data refresh requested');
                        await loadDataProducts();
                        if (currentView && currentView.refresh) {
                            currentView.refresh(dataProducts);
                        }
                    });

                    // Load initial data
                    await loadDataProducts();
                    
                    isInitialized = true;
                    logger.log('Module initialized successfully');

                    // Publish initialization event
                    eventBus.publish('module:initialized', {
                        moduleId: 'data_products_v2',
                        timestamp: new Date().toISOString()
                    });

                } catch (error) {
                    logger.error('Module initialization failed', error);
                    
                    // SAP Fiori Best Practice: Show error with actionable guidance
                    // Note: Error already displayed in loadDataProducts() with MessageBox
                    // Just re-throw to signal failure to caller
                    throw error;
                }
            },

            /**
             * Render module view
             * 
             * @returns {sap.ui.core.Control} SAPUI5 control
             */
            render: async function() {
                logger.log('Rendering module view');

                try {
                    // Check if view factory exists
                    if (!window.createDataProductsV2Page) {
                        const error = new Error('View factory not found: createDataProductsV2Page');
                        logger.error('Render failed', error);
                        
                        // SAP Fiori Best Practice: MessageBox for critical errors
                        sap.m.MessageBox.error(
                            'Failed to render Data Products module.\n\nView factory "createDataProductsV2Page" not found.\n\nPlease ensure all module scripts are loaded correctly.',
                            { title: 'Module Render Error' }
                        );
                        
                        throw error;
                    }

                    // Create view with data
                    currentView = window.createDataProductsV2Page(dataProducts, currentSource, {
                        onProductClick: (product) => {
                            logger.log('Product clicked:', product);
                            
                            // Show detail dialog with table browser
                            // IMPORTANT: Get current adapter from container (handles source switching)
                            if (window.showDataProductDetailsV2) {
                                const currentDataSource = container.get('IDataSource');
                                window.showDataProductDetailsV2(product, currentDataSource);
                            }
                            
                            // Publish event
                            eventBus.publish('data-products:product-selected', {
                                product,
                                timestamp: new Date().toISOString()
                            });
                        },
                        onRefresh: async () => {
                            logger.log('Refresh requested');
                            
                            try {
                                await loadDataProducts();
                                if (currentView && currentView.refresh) {
                                    currentView.refresh(dataProducts, currentSource);
                                }
                                
                                // SAP Fiori Best Practice: MessageToast for SUCCESS only
                                sap.m.MessageToast.show('Data products refreshed successfully');
                                
                            } catch (refreshError) {
                                // Error already shown in loadDataProducts() via MessageBox
                                logger.error('Refresh failed', refreshError);
                            }
                        },
                        onSourceChange: async (newSource) => {
                            try {
                                await switchSource(newSource);
                            } catch (switchError) {
                                // Error already shown in loadDataProducts() via MessageBox
                                logger.error('Source switch failed', switchError);
                            }
                        }
                    });

                    // Publish render event
                    eventBus.publish('module:rendered', {
                        moduleId: 'data_products_v2',
                        timestamp: new Date().toISOString()
                    });

                    logger.log('Module rendered successfully');
                    
                    // Return control for RouterService to place
                    return currentView;

                } catch (error) {
                    logger.error('Module render failed', error);
                    throw error;
                }
            },

            /**
             * Destroy module and cleanup
             */
            destroy: function() {
                logger.log('Destroying module...');

                try {
                    if (currentView && currentView.destroy) {
                        currentView.destroy();
                        currentView = null;
                    }

                    // Clear state
                    dataProducts = [];

                    eventBus.publish('module:destroyed', {
                        moduleId: 'data_products_v2',
                        timestamp: new Date().toISOString()
                    });

                    logger.log('Module destroyed successfully');

                } catch (error) {
                    logger.error('Module destroy failed', error);
                }
            },

            /**
             * Check if module can be activated
             */
            canActivate: function() {
                // Check required dependencies
                return container.has('IDataSource');
            },

            /**
             * Get module status
             */
            getStatus: function() {
                return {
                    initialized: isInitialized,
                    hasView: currentView !== null,
                    dataProductsCount: dataProducts.length,
                    dependencies: {
                        dataSource: container.has('IDataSource'),
                        logger: container.has('ILogger'),
                        cache: container.has('ICache')
                    }
                };
            },

            /**
             * Get loaded data products
             */
            getDataProducts: function() {
                return dataProducts;
            }
        };
    };

    console.log('[DataProductsV2] Module factory registered');

})();