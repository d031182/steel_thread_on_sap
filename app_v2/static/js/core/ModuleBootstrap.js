/**
 * Module Bootstrap - Application Orchestrator
 * ============================================
 * 
 * Orchestrates app initialization with plugin architecture.
 * 
 * Responsibilities:
 * 1. Initialize core services (DI, EventBus, Registry)
 * 2. Register fallback implementations (NoOpLogger, MockDataSource)
 * 3. Discover and register real implementations (if available)
 * 4. Build navigation from module metadata
 * 5. Initialize router for module loading
 * 6. Render application shell
 * 
 * Architecture:
 * - Service Locator pattern for DI
 * - Event-driven for communication
 * - Auto-discovery for modules
 * - Graceful degradation (fallbacks)
 * 
 * Usage:
 *   const bootstrap = new ModuleBootstrap();
 *   await bootstrap.initialize();
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

class ModuleBootstrap {
    constructor() {
        // Create instances (Industry Standard pattern)
        this._container = new DependencyContainer();
        this._eventBus = new EventBus();
        this._registry = new ModuleRegistry();
        this._navBuilder = null;
        this._router = null;
        this._app = null;
    }

    /**
     * Initialize application
     * 
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            console.log('[Bootstrap] Starting application initialization...');

            // Step 1: Register fallback implementations (always available)
            this._registerFallbacks();

            // Step 2: Initialize module registry (fetch from backend)
            await this._registry.initialize();
            console.log(`[Bootstrap] Discovered ${this._registry.getModuleCount()} modules`);

            // Step 3: Register real implementations (if available)
            this._registerRealImplementations();

            // Step 4: Build navigation
            this._navBuilder = new NavigationBuilder(this._registry, this._eventBus);

            // Step 5: Create application shell
            this._app = this._createAppShell();

            // Step 6: Initialize router
            this._router = new RouterService(this._registry, this._container, this._eventBus);
            const contentContainer = this._app.getPages()[0].getContent()[0];
            this._router.initialize(contentContainer);

            // Step 7: Handle browser back/forward
            window.onpopstate = (event) => {
                if (event.state?.moduleId) {
                    this._router.handlePopState(event.state.moduleId);
                }
            };

            // Step 8: Render application
            this._app.placeAt('content');

            // Step 9: Navigate to first available module
            const modules = this._registry.getAllModules();
            if (modules.length > 0) {
                const firstModule = modules[0];
                console.log(`[Bootstrap] Navigating to first module: ${firstModule.id}`);
                await this._router.navigateTo(firstModule.id);
            }

            console.log('[Bootstrap] Application initialized successfully');

            // Publish initialization complete event
            this._eventBus.publish('app:initialized', {
                moduleCount: this._registry.getModuleCount(),
                timestamp: new Date().toISOString()
            });

        } catch (error) {
            console.error('[Bootstrap] Initialization failed:', error);
            this._showInitError(error);
            throw error;
        }
    }

    /**
     * Register fallback implementations (Null Object Pattern)
     * 
     * @private
     */
    _registerFallbacks() {
        // Logger fallback (silent, no-op)
        this._container.register('ILogger', () => new NoOpLogger());

        // DataSource fallback (mock data)
        this._container.register('IDataSource', () => new MockDataSource());

        // Cache fallback (InMemoryCache - fast, volatile)
        // Note: LocalStorageCache available if persistence needed
        this._container.register('ICache', () => new InMemoryCache());

        console.log('[Bootstrap] Fallback implementations registered');
    }

    /**
     * Register real implementations (if modules available)
     * 
     * @private
     */
    _registerRealImplementations() {
        // Check for LogManager module
        if (this._registry.hasModule('log_manager')) {
            // Real logger will be registered by log_manager module
            console.log('[Bootstrap] LogManager module available');
        }

        // Check for DataProducts V2 module
        if (this._registry.hasModule('data_products_v2')) {
            // Replace mock with real DataProductsV2Adapter
            this._container.register('IDataSource', () => new DataProductsV2Adapter({
                baseUrl: '/api/data-products',
                source: 'sqlite', // Default to SQLite for App V2
                timeout: 30000
            }));
            console.log('[Bootstrap] DataProductsV2Adapter registered (real implementation)');
        }

        console.log('[Bootstrap] Real implementations checked');
    }

    /**
     * Create application shell
     * 
     * @private
     * @returns {sap.m.App}
     */
    _createAppShell() {
        // Build navigation
        const tabBar = this._navBuilder.buildNavigation();

        // Create content container (where modules render)
        const contentContainer = new sap.ui.core.ComponentContainer({
            height: '100%',
            width: '100%'
        });

        // Create AI Assistant button for header
        const aiButton = new sap.m.Button({
            icon: 'sap-icon://collaborate',
            tooltip: 'Open AI Assistant',
            type: sap.m.ButtonType.Transparent,
            press: this._onToggleAIAssistant.bind(this)
        });

        // Create custom header with AI button
        const customHeader = new sap.m.Bar({
            contentLeft: [
                new sap.m.Title({
                    text: 'P2P Data Products',
                    level: sap.ui.core.TitleLevel.H1
                })
            ],
            contentRight: [aiButton]
        });

        // Create page with custom header and navigation
        const page = new sap.m.Page({
            customHeader: [customHeader],
            showNavButton: false,
            content: [
                tabBar,
                contentContainer
            ]
        });

        // Create app shell
        const app = new sap.m.App({
            pages: [page]
        });

        // Store references for AI Assistant
        this._aiButton = aiButton;
        this._mainPage = page;

        return app;
    }

    /**
     * Show initialization error
     * 
     * @private
     * @param {Error} error - Error that occurred
     */
    _showInitError(error) {
        // Create minimal error page without SAPUI5
        const errorHtml = `
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                font-family: Arial, sans-serif;
                padding: 20px;
                text-align: center;
            ">
                <h1 style="color: #d32f2f; margin-bottom: 20px;">
                    ⚠️ Initialization Error
                </h1>
                <p style="font-size: 18px; margin-bottom: 10px;">
                    Failed to start application
                </p>
                <p style="
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 4px;
                    font-family: monospace;
                    color: #666;
                    max-width: 600px;
                ">
                    ${error.message}
                </p>
                <button 
                    onclick="location.reload()" 
                    style="
                        margin-top: 20px;
                        padding: 10px 20px;
                        background: #1976d2;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 16px;
                    "
                >
                    Reload Application
                </button>
            </div>
        `;

        document.getElementById('content').innerHTML = errorHtml;
    }

    /**
     * Get DI container
     * 
     * @returns {DependencyContainer}
     */
    getContainer() {
        return this._container;
    }

    /**
     * Get event bus
     * 
     * @returns {EventBus}
     */
    getEventBus() {
        return this._eventBus;
    }

    /**
     * Get module registry
     * 
     * @returns {ModuleRegistry}
     */
    getRegistry() {
        return this._registry;
    }

    /**
     * Get router service
     * 
     * @returns {RouterService}
     */
    getRouter() {
        return this._router;
    }

    /**
     * Get navigation builder
     * 
     * @returns {NavigationBuilder}
     */
    getNavigationBuilder() {
        return this._navBuilder;
    }

    /**
     * Get app instance
     * 
     * @returns {sap.m.App}
     */
    getApp() {
        return this._app;
    }

    /**
     * Toggle AI Assistant overlay
     * 
     * @private
     * @param {sap.ui.base.Event} oEvent - Button press event
     */
    _onToggleAIAssistant(oEvent) {
        // ALWAYS use AI Assistant module (Phase 2+ integration)
        if (window.aiAssistant && window.aiAssistant.open) {
            window.aiAssistant.open();
        } else {
            // AI Assistant module not yet loaded
            sap.m.MessageToast.show('AI Assistant is loading... Please try again in a moment.');
            console.warn('[Bootstrap] AI Assistant module not yet initialized');
        }
    }

}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModuleBootstrap;
}