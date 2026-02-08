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

            // Step 9: Navigate to first module (if available)
            const modules = this._registry.getAllModules();
            if (modules.length > 0) {
                await this._router.navigateTo(modules[0].id);
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

        // Cache fallback (localStorage)
        this._container.register('ICache', () => ({
            get: (key) => localStorage.getItem(key),
            set: (key, value) => localStorage.setItem(key, value),
            delete: (key) => localStorage.removeItem(key),
            has: (key) => localStorage.getItem(key) !== null,
            clear: () => localStorage.clear()
        }));

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

        // Check for DataProducts module
        if (this._registry.hasModule('data_products')) {
            // Real data source will be registered by data_products module
            console.log('[Bootstrap] DataProducts module available');
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

        // Create page with navigation
        const page = new sap.m.Page({
            title: 'P2P Data Products',
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
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModuleBootstrap;
}