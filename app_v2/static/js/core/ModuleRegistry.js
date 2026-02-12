/**
 * Module Registry - Frontend Auto-Discovery
 * ==========================================
 * 
 * Fetches module metadata from backend API and provides registry for:
 * - Module lookup by ID
 * - Module filtering by category
 * - Dependency resolution
 * - Module availability checks
 * 
 * Architecture:
 * - Consumes /api/modules/frontend-registry endpoint
 * - Caches module metadata locally
 * - Provides synchronous access after initialization
 * - Supports force refresh
 * 
 * Usage:
 *   const registry = new ModuleRegistry();
 *   await registry.initialize();
 *   const modules = registry.getAllModules();
 *   const module = registry.getModule('knowledge_graph_v2');
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

class ModuleRegistry {
    constructor() {
        this._modules = new Map(); // module_id -> module_metadata
        this._categories = new Map(); // category -> module_ids[]
        this._initialized = false;
        this._apiUrl = '/api/modules/frontend-registry';
    }

    /**
     * Initialize registry by fetching module metadata from API
     * 
     * @param {boolean} forceRefresh - Force API cache refresh
     * @returns {Promise<void>}
     * @throws {Error} If API fetch fails
     */
    async initialize(forceRefresh = false) {
        try {
            // Build URL with optional force_refresh parameter
            const params = new URLSearchParams();
            if (forceRefresh) {
                params.append('force_refresh', 'true');
            }
            
            const url = params.toString() ? `${this._apiUrl}?${params.toString()}` : this._apiUrl;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch modules: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(`API error: ${data.error || 'Unknown error'}`);
            }

            // Clear existing data
            this._modules.clear();
            this._categories.clear();

            // Index modules by ID
            for (const module of data.modules) {
                this._modules.set(module.id, module);

                // Index by category
                const category = module.category || 'general';
                if (!this._categories.has(category)) {
                    this._categories.set(category, []);
                }
                this._categories.get(category).push(module.id);
            }

            this._initialized = true;

            console.log(`[ModuleRegistry] Initialized with ${data.count} modules`);
            
        } catch (error) {
            console.error('[ModuleRegistry] Initialization failed:', error);
            throw error;
        }
    }

    /**
     * Get all modules
     * 
     * @returns {Array<Object>} Array of module metadata objects
     * @throws {Error} If not initialized
     */
    getAllModules() {
        this._ensureInitialized();
        return Array.from(this._modules.values());
    }

    /**
     * Get module by ID
     * 
     * @param {string} moduleId - Module identifier
     * @returns {Object|null} Module metadata or null if not found
     */
    getModule(moduleId) {
        this._ensureInitialized();
        return this._modules.get(moduleId) || null;
    }

    /**
     * Check if module exists
     * 
     * @param {string} moduleId - Module identifier
     * @returns {boolean}
     */
    hasModule(moduleId) {
        this._ensureInitialized();
        return this._modules.has(moduleId);
    }

    /**
     * Get modules by category
     * 
     * @param {string} category - Category name
     * @returns {Array<Object>} Array of module metadata objects
     */
    getModulesByCategory(category) {
        this._ensureInitialized();
        const moduleIds = this._categories.get(category) || [];
        return moduleIds.map(id => this._modules.get(id));
    }

    /**
     * Get all categories
     * 
     * @returns {Array<string>} Array of category names
     */
    getCategories() {
        this._ensureInitialized();
        return Array.from(this._categories.keys());
    }

    /**
     * Get modules with backend availability
     * 
     * @returns {Array<Object>} Modules with backend.available === true
     */
    getModulesWithBackend() {
        this._ensureInitialized();
        return this.getAllModules().filter(m => m.backend?.available);
    }

    /**
     * Get modules with specific dependency
     * 
     * @param {string} dependency - Dependency name (e.g., 'ILogger')
     * @returns {Array<Object>} Modules that depend on the specified service
     */
    getModulesWithDependency(dependency) {
        this._ensureInitialized();
        return this.getAllModules().filter(m => 
            m.frontend?.dependencies?.includes(dependency)
        );
    }

    /**
     * Check if registry is initialized
     * 
     * @returns {boolean}
     */
    isInitialized() {
        return this._initialized;
    }

    /**
     * Get module count
     * 
     * @returns {number}
     */
    getModuleCount() {
        this._ensureInitialized();
        return this._modules.size;
    }

    /**
     * Get registry statistics
     * 
     * @returns {Object} Statistics object
     */
    getStats() {
        this._ensureInitialized();
        
        const modules = this.getAllModules();
        const withBackend = modules.filter(m => m.backend?.available).length;
        const withAuth = modules.filter(m => m.frontend?.requires_auth).length;
        const withDeps = modules.filter(m => 
            m.frontend?.dependencies?.length > 0
        ).length;

        return {
            total: this._modules.size,
            categories: this._categories.size,
            withBackend,
            withAuth,
            withDependencies: withDeps,
            categoryCounts: Object.fromEntries(
                Array.from(this._categories.entries()).map(([cat, ids]) => 
                    [cat, ids.length]
                )
            )
        };
    }

    /**
     * Force refresh from API
     * 
     * @returns {Promise<void>}
     */
    async refresh() {
        return this.initialize(true);
    }

    /**
     * Ensure registry is initialized
     * 
     * @private
     * @throws {Error} If not initialized
     */
    _ensureInitialized() {
        if (!this._initialized) {
            throw new Error('ModuleRegistry not initialized. Call initialize() first.');
        }
    }

    /**
     * Get module route path
     * 
     * @param {string} moduleId - Module identifier
     * @returns {string|null} Route path or null if not found
     */
    getModuleRoute(moduleId) {
        const module = this.getModule(moduleId);
        return module?.frontend?.route || null;
    }

    /**
     * Get module entry point
     * 
     * @param {string} moduleId - Module identifier
     * @returns {string|Object|null} Entry point path or object
     */
    getModuleEntryPoint(moduleId) {
        const module = this.getModule(moduleId);
        return module?.frontend?.entry_point || null;
    }

    /**
     * Check if module requires authentication
     * 
     * @param {string} moduleId - Module identifier
     * @returns {boolean}
     */
    requiresAuth(moduleId) {
        const module = this.getModule(moduleId);
        return module?.frontend?.requires_auth || false;
    }

    /**
     * Get module dependencies
     * 
     * @param {string} moduleId - Module identifier
     * @returns {Object} Dependencies object with required and optional arrays
     */
    getModuleDependencies(moduleId) {
        const module = this.getModule(moduleId);
        const deps = module?.dependencies;
        
        // Support both old format (array) and new format (object with required/optional)
        if (Array.isArray(deps)) {
            return { required: deps, optional: [] };
        }
        
        return {
            required: deps?.required || [],
            optional: deps?.optional || []
        };
    }

    /**
     * Validate module dependencies are available in DI container
     * 
     * @param {string} moduleId - Module identifier
     * @param {Object} container - DependencyContainer instance
     * @returns {Object} Validation result { valid, missingRequired, missingOptional }
     */
    validateDependencies(moduleId, container) {
        const deps = this.getModuleDependencies(moduleId);
        const missingRequired = deps.required.filter(dep => !container.has(dep));
        const missingOptional = deps.optional.filter(dep => !container.has(dep));

        return {
            valid: missingRequired.length === 0,
            missingRequired,
            missingOptional,
            allDependencies: [...deps.required, ...deps.optional]
        };
    }

    /**
     * Create module instance via factory function
     * 
     * @param {string} moduleId - Module identifier
     * @param {Object} container - DependencyContainer instance
     * @param {Object} eventBus - EventBus instance
     * @returns {Object|null} Module instance or null if factory not found
     * @throws {Error} If module not found or missing required dependencies
     */
    createModuleInstance(moduleId, container, eventBus) {
        const module = this.getModule(moduleId);
        if (!module) {
            throw new Error(`Module not found: ${moduleId}`);
        }

        // Check required dependencies
        const validation = this.validateDependencies(moduleId, container);
        if (!validation.valid) {
            throw new Error(
                `Module ${moduleId} missing required dependencies: ${validation.missingRequired.join(', ')}`
            );
        }

        // Get factory function name
        const factoryName = module.frontend?.entry_point?.factory;
        if (!factoryName) {
            console.warn(`[ModuleRegistry] Module ${moduleId} has no factory function`);
            return null;
        }

        // Get factory from window
        const factory = window[factoryName];
        if (typeof factory !== 'function') {
            throw new Error(`Factory function not found: ${factoryName}`);
        }

        // Create instance
        console.log(`[ModuleRegistry] Creating instance of ${moduleId} via ${factoryName}`);
        const instance = factory(container, eventBus);

        return instance;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModuleRegistry;
}