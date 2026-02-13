/**
 * KnowledgeGraphApiClient
 * 
 * HTTP client for Knowledge Graph v2 API endpoints.
 * Abstracts API communication and error handling.
 * 
 * Architecture: Adapter Layer
 * Purpose: API communication abstraction
 * 
 * @author P2P Development Team
 * @version 1.0.0 (Phase 5.1 - Adapter Layer)
 * @date 2026-02-08
 */

class KnowledgeGraphApiClient {
    constructor(baseUrl = '/api/knowledge-graph') {
        this.baseUrl = baseUrl;
        this.timeout = 30000; // 30 second timeout
    }

    /**
     * Get schema graph (with optional cache bypass)
     * 
     * @param {boolean} useCache - Whether to use cache (default: true)
     * @returns {Promise<Object>} API response with graph data
     * @throws {Error} If request fails
     * 
     * Response format:
     * {
     *   success: true,
     *   graph: { nodes: [...], edges: [...] },
     *   cache_used: true,
     *   metadata: { node_count: 10, edge_count: 15, ... }
     * }
     */
    async getSchemaGraph(useCache = true) {
        const url = `${this.baseUrl}/schema?use_cache=${useCache}`;
        
        try {
            const response = await this._fetchWithTimeout(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to get schema graph');
            }

            return data;

        } catch (error) {
            throw new Error(`Get schema graph failed: ${error.message}`);
        }
    }

    /**
     * Force rebuild of schema graph (ignores cache)
     * 
     * @returns {Promise<Object>} API response with rebuilt graph
     * @throws {Error} If request fails
     * 
     * Response format:
     * {
     *   success: true,
     *   graph: { nodes: [...], edges: [...] },
     *   cache_used: false,
     *   metadata: { ... }
     * }
     */
    async rebuildSchemaGraph() {
        const url = `${this.baseUrl}/schema/rebuild`;
        
        try {
            const response = await this._fetchWithTimeout(url, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to rebuild schema graph');
            }

            return data;

        } catch (error) {
            throw new Error(`Rebuild schema graph failed: ${error.message}`);
        }
    }

    /**
     * Get cache status and CSN information
     * 
     * @returns {Promise<Object>} Status information
     * @throws {Error} If request fails
     * 
     * Response format:
     * {
     *   success: true,
     *   cached: true,
     *   csn_files_count: 8,
     *   csn_directory: "docs/csn"
     * }
     */
    async getStatus() {
        const url = `${this.baseUrl}/status`;
        
        try {
            const response = await this._fetchWithTimeout(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to get status');
            }

            return data;

        } catch (error) {
            throw new Error(`Get status failed: ${error.message}`);
        }
    }

    /**
     * Clear schema graph cache (admin operation)
     * 
     * @returns {Promise<Object>} Deletion result
     * @throws {Error} If request fails
     * 
     * Response format:
     * {
     *   success: true,
     *   cleared: true
     * }
     */
    async clearCache() {
        const url = `${this.baseUrl}/cache`;
        
        try {
            const response = await this._fetchWithTimeout(url, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json'
                }
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to clear cache');
            }

            return data;

        } catch (error) {
            throw new Error(`Clear cache failed: ${error.message}`);
        }
    }

    /**
     * Health check endpoint
     * 
     * @returns {Promise<Object>} Health status
     * @throws {Error} If request fails
     * 
     * Response format:
     * {
     *   status: "healthy",
     *   version: "2.0",
     *   api: "knowledge-graph-v2"
     * }
     */
    async healthCheck() {
        const url = `${this.baseUrl}/health`;
        
        try {
            const response = await this._fetchWithTimeout(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            return await response.json();

        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }

    /**
     * Fetch with timeout support
     * 
     * @private
     * @param {string} url - Request URL
     * @param {Object} options - Fetch options
     * @returns {Promise<Response>} Fetch response
     * @throws {Error} If timeout or network error
     */
    async _fetchWithTimeout(url, options) {
        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            // Check HTTP status
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.error || 
                    `HTTP ${response.status}: ${response.statusText}`
                );
            }

            return response;

        } catch (error) {
            clearTimeout(timeoutId);

            // Handle timeout
            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${this.timeout}ms`);
            }

            // Handle network errors
            if (error.message.includes('Failed to fetch')) {
                throw new Error('Network error: Unable to reach server');
            }

            // Re-throw other errors
            throw error;
        }
    }

    /**
     * Set custom timeout
     * 
     * @param {number} timeoutMs - Timeout in milliseconds
     */
    setTimeout(timeoutMs) {
        if (timeoutMs <= 0) {
            throw new Error('Timeout must be positive');
        }
        this.timeout = timeoutMs;
    }

    /**
     * Get current timeout
     * 
     * @returns {number} Current timeout in milliseconds
     */
    getTimeout() {
        return this.timeout;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KnowledgeGraphApiClient;
}