/**
 * Dependency Injection Container
 * 
 * Purpose: Service locator pattern for loose coupling between modules
 * Pattern: Instance-based container (Industry Standard)
 * 
 * Features:
 * - Register services with factory functions (lazy instantiation)
 * - Get services (singleton pattern - one instance per service per container)
 * - Check if service available (runtime capability detection)
 * - Clear for testing (isolate test dependencies)
 * 
 * Usage:
 *   // Create container at composition root
 *   const container = new DependencyContainer();
 *   
 *   // Register service
 *   container.register('ILogger', () => new LogManager());
 *   
 *   // Get service (created on first access)
 *   const logger = container.get('ILogger');
 *   
 *   // Check availability
 *   if (container.has('ILogger')) {
 *       // Use logger
 *   }
 * 
 * Architecture: Part of app_v2 core infrastructure (Dependency Inversion Principle)
 * Standard: Follows InversifyJS, TypeDI, NestJS instance-based pattern
 */
class DependencyContainer {
    /**
     * Create new container instance
     */
    constructor() {
        /**
         * Internal storage for service factories
         * @private
         */
        this._factories = new Map();
        
        /**
         * Internal storage for singleton instances
         * @private
         */
        this._instances = new Map();
    }
    
    /**
     * Register a service with a factory function
     * 
     * @param {string} name - Service identifier (e.g., 'ILogger', 'IDataSource')
     * @param {Function} factory - Factory function that creates the service instance
     * @throws {Error} If name or factory is invalid
     * 
     * @example
     * container.register('ILogger', () => new LogManager());
     * container.register('IDataSource', () => new DataProductsService());
     */
    register(name, factory) {
        if (!name || typeof name !== 'string') {
            throw new Error('Service name must be a non-empty string');
        }
        
        if (!factory || typeof factory !== 'function') {
            throw new Error('Factory must be a function');
        }
        
        this._factories.set(name, factory);
        // Clear any existing instance (allow re-registration)
        this._instances.delete(name);
    }
    
    /**
     * Get a service instance (lazy instantiation, singleton)
     * 
     * @param {string} name - Service identifier
     * @returns {*} Service instance
     * @throws {Error} If service not registered
     * 
     * @example
     * const logger = container.get('ILogger');
     * logger.log('Hello, world!');
     */
    get(name) {
        // Return existing instance if available (singleton)
        if (this._instances.has(name)) {
            return this._instances.get(name);
        }
        
        // Get factory
        const factory = this._factories.get(name);
        if (!factory) {
            throw new Error(
                `Service '${name}' not registered. ` +
                `Available services: ${Array.from(this._factories.keys()).join(', ') || 'none'}`
            );
        }
        
        // Create instance and cache it (singleton)
        const instance = factory();
        this._instances.set(name, instance);
        
        return instance;
    }
    
    /**
     * Check if a service is registered
     * 
     * @param {string} name - Service identifier
     * @returns {boolean} True if service is registered
     * 
     * @example
     * if (container.has('ILogger')) {
     *     const logger = container.get('ILogger');
     *     logger.log('Logging available');
     * } else {
     *     console.log('No logger available');
     * }
     */
    has(name) {
        return this._factories.has(name);
    }
    
    /**
     * Get all registered service names
     * 
     * @returns {string[]} Array of service names
     * 
     * @example
     * const services = container.getRegisteredServices();
     * console.log('Available services:', services.join(', '));
     */
    getRegisteredServices() {
        return Array.from(this._factories.keys());
    }
    
    /**
     * Clear all registrations (for testing)
     * 
     * WARNING: This clears ALL services. Use only in tests!
     * 
     * @example
     * // In test setup
     * beforeEach(() => {
     *     container.clear();
     *     container.register('ILogger', () => new MockLogger());
     * });
     */
    clear() {
        this._factories.clear();
        this._instances.clear();
    }
    
    /**
     * Unregister a specific service
     * 
     * @param {string} name - Service identifier
     * @returns {boolean} True if service was registered and removed
     * 
     * @example
     * container.unregister('ILogger');
     */
    unregister(name) {
        const hadFactory = this._factories.delete(name);
        this._instances.delete(name);
        return hadFactory;
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DependencyContainer;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.DependencyContainer = DependencyContainer;
}