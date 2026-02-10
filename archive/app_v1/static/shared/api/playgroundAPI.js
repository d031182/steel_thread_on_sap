/**
 * API Playground API Client
 * Pure business logic, framework-agnostic
 * Works with both UI5 and Alpine.js UX implementations
 * 
 * @author P2P Development Team
 * @version 2.0.0
 */

/**
 * API Playground API Client
 * Handles all backend communication for API Playground features
 */
export class PlaygroundAPI {
    constructor(baseUrl = '/api/playground') {
        this.baseUrl = baseUrl;
    }

    /**
     * Discover all module APIs
     * @returns {Promise<Object>} { success, apis, stats }
     */
    async discoverAPIs() {
        try {
            const response = await fetch(`${this.baseUrl}/discover`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to discover APIs:', error);
            return {
                success: false,
                error: error.message,
                apis: {},
                stats: { total_modules: 0, total_endpoints: 0 }
            };
        }
    }

    /**
     * Get specific module details
     * @param {string} moduleName - Module name
     * @returns {Promise<Object>} Module configuration
     */
    async getModule(moduleName) {
        try {
            const response = await fetch(`${this.baseUrl}/modules/${moduleName}`);
            return await response.json();
        } catch (error) {
            console.error(`Failed to get module ${moduleName}:`, error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Execute an API request
     * @param {Object} request - { method, url, body }
     * @returns {Promise<Object>} { status, statusText, data, duration }
     */
    async executeRequest({ method, url, body }) {
        const startTime = performance.now();
        
        try {
            const options = {
                method: method,
                headers: { 'Content-Type': 'application/json' }
            };
            
            if (['POST', 'PUT'].includes(method) && body) {
                // Validate JSON
                if (typeof body === 'string') {
                    JSON.parse(body); // Throws if invalid
                    options.body = body;
                } else {
                    options.body = JSON.stringify(body);
                }
            }
            
            const response = await fetch(url, options);
            const endTime = performance.now();
            
            const contentType = response.headers.get('content-type');
            let responseData;
            
            if (contentType && contentType.includes('application/json')) {
                responseData = await response.json();
            } else {
                responseData = await response.text();
            }
            
            return {
                success: true,
                status: response.status,
                statusText: response.ok ? 'OK' : 'Error',
                ok: response.ok,
                data: responseData,
                duration: (endTime - startTime).toFixed(2),
                contentType: contentType
            };
            
        } catch (error) {
            const endTime = performance.now();
            console.error('API execution error:', error);
            
            return {
                success: false,
                status: 0,
                statusText: 'Error',
                ok: false,
                error: error.message,
                duration: (endTime - startTime).toFixed(2)
            };
        }
    }

    /**
     * Get API statistics
     * @returns {Promise<Object>} Statistics
     */
    async getStats() {
        try {
            const response = await fetch(`${this.baseUrl}/stats`);
            return await response.json();
        } catch (error) {
            console.error('Failed to get stats:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get categories
     * @returns {Promise<Object>} Categories list
     */
    async getCategories() {
        try {
            const response = await fetch(`${this.baseUrl}/categories`);
            return await response.json();
        } catch (error) {
            console.error('Failed to get categories:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Helper: Build full URL with path parameters
     * @param {string} urlTemplate - URL with <param> placeholders
     * @param {Object} params - Key-value pairs for parameters
     * @returns {string} URL with parameters filled in
     */
    buildUrl(urlTemplate, params) {
        let url = urlTemplate;
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                url = url.replace(new RegExp(`<${key}>`, 'g'), value);
            });
        }
        return url;
    }
}

// Export singleton instance
export const playgroundAPI = new PlaygroundAPI();