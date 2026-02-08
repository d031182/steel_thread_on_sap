/**
 * Router Service - Dynamic Module Routing
 * ========================================
 * 
 * Manages client-side routing and module loading.
 * 
 * Features:
 * - Route-based module activation
 * - Dynamic script loading
 * - Dependency validation before load
 * - Error handling with fallbacks
 * - History API integration
 * 
 * Architecture:
 * - Listens to navigation:moduleSelected events
 * - Validates dependencies via DependencyContainer
 * - Loads module scripts dynamically
 * - Renders module content in container
 * - Publishes routing events
 * 
 * Usage:
 *   const router = new RouterService(registry, container, eventBus);
 *   router.initialize(contentContainer);
 *   router.navigateTo('knowledge_graph_v2');
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

class RouterService {
    /**
     * Create router service
     * 
     * @param {ModuleRegistry} registry - Module registry instance
     * @param {DependencyContainer} container - DI container
     * @param {EventBus} eventBus - Event bus
     */
    constructor(registry, container, eventBus) {
        if (!registry || !registry.isInitialized()) {
            throw new Error('RouterService requires initialized ModuleRegistry');
        }
        if (!container) {
            throw new Error('RouterService requires DependencyContainer');
        }
        if (!eventBus) {
            throw new Error('RouterService requires EventBus');
        }

        this._registry = registry;
        this._container = container;
        this._eventBus = eventBus;
        this._contentContainer = null;
        this._currentModuleId = null;
        this._currentModuleInstance = null;  // Track active module instance
        this._loadedScripts = new Set();
        this._moduleInstances = new Map();   // Cache module instances
    }

    /**
     * Initialize router with content container
     * 
     * @param {sap.ui.core.Control} contentContainer - Container for module content
     */
    initialize(contentContainer) {
        this._contentContainer = contentContainer;

        // Subscribe to navigation events
        this._eventBus.subscribe('navigation:moduleSelected', (data) => {
            this.navigateTo(data.moduleId);
        });

        console.log('[RouterService] Initialized');
    }

    /**
     * Navigate to module by ID
     * 
     * @param {string} moduleId - Module identifier
     * @returns {Promise<boolean>} True if navigation successful
     */
    async navigateTo(moduleId) {
        try {
            console.log(`[RouterService] Navigating to: ${moduleId}`);

            // Get module metadata
            const module = this._registry.getModule(moduleId);
            if (!module) {
                throw new Error(`Module not found: ${moduleId}`);
            }

            // Check authentication
            if (module.frontend?.requires_auth) {
                const isAuthenticated = this._checkAuthentication();
                if (!isAuthenticated) {
                    this._showAuthError(module.name);
                    return false;
                }
            }

            // Validate dependencies
            const validation = this._registry.validateDependencies(moduleId, this._container);
            if (!validation.valid) {
                this._showDependencyError(module.name, validation.missing);
                return false;
            }

            // Load module script if not already loaded
            const entryPoint = module.frontend?.entry_point;
            if (entryPoint && typeof entryPoint === 'string') {
                await this._loadModuleScript(entryPoint);
            }

            // Render module
            await this._renderModule(module);

            // Update current module
            this._currentModuleId = moduleId;

            // Update URL (without page reload)
            const route = module.frontend?.route || `/${moduleId}`;
            window.history.pushState({ moduleId }, module.name, route);

            // Publish routing event
            this._eventBus.publish('routing:navigated', {
                moduleId,
                module,
                timestamp: new Date().toISOString()
            });

            console.log(`[RouterService] Navigation successful: ${moduleId}`);
            return true;

        } catch (error) {
            console.error(`[RouterService] Navigation failed:`, error);
            this._showError(error.message);
            return false;
        }
    }

    /**
     * Load module script dynamically
     * 
     * @private
     * @param {string} scriptPath - Path to module script
     * @returns {Promise<void>}
     */
    async _loadModuleScript(scriptPath) {
        // Skip if already loaded
        if (this._loadedScripts.has(scriptPath)) {
            console.log(`[RouterService] Script already loaded: ${scriptPath}`);
            return;
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = scriptPath;
            script.async = true;

            script.onload = () => {
                this._loadedScripts.add(scriptPath);
                console.log(`[RouterService] Script loaded: ${scriptPath}`);
                resolve();
            };

            script.onerror = () => {
                reject(new Error(`Failed to load script: ${scriptPath}`));
            };

            document.head.appendChild(script);
        });
    }

    /**
     * Render module content
     * 
     * @private
     * @param {Object} module - Module metadata
     * @returns {Promise<void>}
     */
    async _renderModule(module) {
        if (!this._contentContainer) {
            throw new Error('Content container not initialized');
        }

        // Destroy previous module instance (lifecycle management)
        if (this._currentModuleInstance && this._currentModuleInstance.destroy) {
            console.log(`[RouterService] Destroying previous module: ${this._currentModuleId}`);
            this._currentModuleInstance.destroy();
            this._currentModuleInstance = null;
        }

        // Clear previous content
        this._contentContainer.destroyContent();

        const entryPoint = module.frontend?.entry_point;

        // STRATEGY 1: Module Factory Pattern (PREFERRED - proper DI + lifecycle)
        if (typeof entryPoint === 'object' && entryPoint.factory) {
            const factoryName = entryPoint.factory;
            const factory = window[factoryName];

            if (typeof factory === 'function') {
                console.log(`[RouterService] Using module factory: ${factoryName}`);

                // Get or create module instance (singleton per module)
                let moduleInstance = this._moduleInstances.get(module.id);
                
                if (!moduleInstance) {
                    // Create module instance with DI
                    moduleInstance = factory(this._container, this._eventBus);
                    this._moduleInstances.set(module.id, moduleInstance);

                    // Initialize module (once per instance)
                    if (moduleInstance.initialize) {
                        console.log(`[RouterService] Initializing module: ${module.id}`);
                        await moduleInstance.initialize();
                    }
                }

                // Render module content
                if (moduleInstance.render) {
                    console.log(`[RouterService] Rendering module: ${module.id}`);
                    
                    // Create temp container div for render
                    const tempContainerId = `module-${module.id}-container`;
                    let tempContainer = document.getElementById(tempContainerId);
                    
                    if (!tempContainer) {
                        tempContainer = document.createElement('div');
                        tempContainer.id = tempContainerId;
                        tempContainer.style.width = '100%';
                        tempContainer.style.height = '100%';
                        document.body.appendChild(tempContainer);
                    }

                    // Module renders into temp container
                    await moduleInstance.render(tempContainerId);

                    // Move rendered content to SAPUI5 container
                    const renderedContent = tempContainer.firstChild;
                    if (renderedContent) {
                        this._contentContainer.addContent(renderedContent);
                    }

                    // Clean up temp container
                    tempContainer.remove();
                }

                // Track current module instance
                this._currentModuleInstance = moduleInstance;
                
                console.log(`[RouterService] Module loaded successfully: ${module.id}`);
                return;
            }
        }

        // STRATEGY 2: Legacy init_function (FALLBACK for backward compatibility)
        if (typeof entryPoint === 'object' && entryPoint.init_function) {
            const initFn = window[entryPoint.init_function];
            if (typeof initFn === 'function') {
                console.log(`[RouterService] Using legacy init function: ${entryPoint.init_function}`);
                const content = await initFn(this._container, this._eventBus);
                this._contentContainer.addContent(content);
                return;
            }
        }

        // STRATEGY 3: Global factory function (FALLBACK)
        const factoryName = `create${this._toPascalCase(module.id)}Page`;
        const factory = window[factoryName];

        if (typeof factory === 'function') {
            console.log(`[RouterService] Using global factory: ${factoryName}`);
            const content = await factory(this._container, this._eventBus);
            this._contentContainer.addContent(content);
            return;
        }

        // STRATEGY 4: No implementation found - show placeholder
        console.warn(`[RouterService] No implementation found for module: ${module.id}`);
        this._showPlaceholder(module);
    }

    /**
     * Convert snake_case to PascalCase
     * 
     * @private
     * @param {string} text - Input text
     * @returns {string} PascalCase text
     */
    _toPascalCase(text) {
        return text
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join('');
    }

    /**
     * Check if user is authenticated
     * 
     * @private
     * @returns {boolean}
     */
    _checkAuthentication() {
        // TODO: Implement authentication check
        // For now, return true (no auth required)
        return true;
    }

    /**
     * Show authentication error
     * 
     * @private
     * @param {string} moduleName - Module name
     */
    _showAuthError(moduleName) {
        this._contentContainer.destroyContent();
        
        const message = new sap.m.MessagePage({
            title: 'Authentication Required',
            text: `You must be logged in to access ${moduleName}`,
            icon: 'sap-icon://locked',
            description: 'Please log in and try again.'
        });

        this._contentContainer.addContent(message);
    }

    /**
     * Show dependency error
     * 
     * @private
     * @param {string} moduleName - Module name
     * @param {Array<string>} missing - Missing dependencies
     */
    _showDependencyError(moduleName, missing) {
        this._contentContainer.destroyContent();

        const message = new sap.m.MessagePage({
            title: 'Missing Dependencies',
            text: `${moduleName} requires services that are not available`,
            icon: 'sap-icon://alert',
            description: `Missing: ${missing.join(', ')}`
        });

        this._contentContainer.addContent(message);
    }

    /**
     * Show placeholder for module
     * 
     * @private
     * @param {Object} module - Module metadata
     */
    _showPlaceholder(module) {
        const placeholder = new sap.m.MessagePage({
            title: module.name,
            text: module.description || 'Module loading...',
            icon: module.icon || 'sap-icon://product',
            description: `Version: ${module.version}`
        });

        this._contentContainer.addContent(placeholder);
    }

    /**
     * Show error message
     * 
     * @private
     * @param {string} errorMessage - Error message
     */
    _showError(errorMessage) {
        if (!this._contentContainer) return;

        this._contentContainer.destroyContent();

        const message = new sap.m.MessagePage({
            title: 'Navigation Error',
            text: errorMessage,
            icon: 'sap-icon://error',
            description: 'Please try again or contact support.'
        });

        this._contentContainer.addContent(message);
    }

    /**
     * Get current module ID
     * 
     * @returns {string|null}
     */
    getCurrentModule() {
        return this._currentModuleId;
    }

    /**
     * Navigate back
     * 
     * @returns {Promise<boolean>}
     */
    async navigateBack() {
        window.history.back();
        return true;
    }

    /**
     * Navigate forward
     * 
     * @returns {Promise<boolean>}
     */
    async navigateForward() {
        window.history.forward();
        return true;
    }

    /**
     * Handle browser back/forward buttons
     * 
     * Called by window.onpopstate event
     * 
     * @param {string} moduleId - Module ID from history state
     * @returns {Promise<boolean>}
     */
    async handlePopState(moduleId) {
        if (moduleId) {
            return this.navigateTo(moduleId);
        }
        return false;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RouterService;
}