/**
 * GraphPresenter
 * 
 * Manages UI state and coordinates between API/adapter and view.
 * Implements Observer pattern for view updates.
 * 
 * Architecture: Presenter Layer (MVP Pattern)
 * Purpose: State management + orchestration
 * 
 * @author P2P Development Team
 * @version 1.0.0 (Phase 5.2 - Presenter Layer)
 * @date 2026-02-08
 */

class GraphPresenter {
    constructor(apiClient, visJsAdapter) {
        if (!apiClient) {
            throw new Error('API client is required');
        }
        if (!visJsAdapter) {
            throw new Error('VisJs adapter is required');
        }

        this.apiClient = apiClient;
        this.visJsAdapter = visJsAdapter;

        // UI State
        this.state = {
            graph: null,           // Current vis.js graph
            genericGraph: null,    // Original generic graph
            loading: false,        // Loading indicator
            error: null,           // Error message
            cacheStatus: {
                cached: false,
                csnFilesCount: 0,
                csnDirectory: ''
            },
            lastRefresh: null      // Timestamp of last refresh
        };

        // Observer pattern - views subscribe to state changes
        this.observers = [];
    }

    /**
     * Subscribe to state changes (Observer pattern)
     * 
     * @param {Function} callback - Called when state changes
     * @returns {Function} Unsubscribe function
     */
    subscribe(callback) {
        if (typeof callback !== 'function') {
            throw new Error('Callback must be a function');
        }

        this.observers.push(callback);

        // Return unsubscribe function
        return () => {
            const index = this.observers.indexOf(callback);
            if (index > -1) {
                this.observers.splice(index, 1);
            }
        };
    }

    /**
     * Notify all observers of state change
     * 
     * @private
     */
    _notifyObservers() {
        console.log('[GraphPresenter] Notifying observers with state:', {
            hasGraph: this.state.graph !== null,
            hasGenericGraph: this.state.genericGraph !== null,
            loading: this.state.loading,
            error: this.state.error
        });
        
        this.observers.forEach(callback => {
            try {
                callback(this.state);
            } catch (error) {
                console.error('Observer callback error:', error);
            }
        });
    }

    /**
     * Update state and notify observers
     * 
     * @private
     * @param {Object} updates - State updates
     */
    _setState(updates) {
        this.state = {
            ...this.state,
            ...updates
        };
        this._notifyObservers();
    }

    /**
     * Load schema graph (with optional cache bypass)
     * 
     * @param {boolean} useCache - Whether to use cache (default: true)
     * @returns {Promise<void>}
     */
    async loadGraph(useCache = true) {
        try {
            console.log('[GraphPresenter] loadGraph() called with useCache:', useCache);
            
            // Set loading state
            this._setState({
                loading: true,
                error: null
            });

            // Fetch generic graph from API
            console.log('[GraphPresenter] Fetching schema graph from API...');
            const response = await this.apiClient.getSchemaGraph(useCache);
            console.log('[GraphPresenter] API response received:', {
                hasGraph: !!response.graph,
                nodeCount: response.graph?.nodes?.length || 0,
                edgeCount: response.graph?.edges?.length || 0
            });

            // Validate graph structure
            this.visJsAdapter.validateGraph(response.graph);

            // Convert to vis.js format
            console.log('[GraphPresenter] Converting to vis.js format...');
            const visJsGraph = this.visJsAdapter.convertToVisJs(response.graph);
            console.log('[GraphPresenter] Conversion complete:', {
                hasNodes: !!visJsGraph.nodes,
                hasEdges: !!visJsGraph.edges,
                nodesLength: visJsGraph.nodes?.length,
                edgesLength: visJsGraph.edges?.length
            });

            // Update state with success
            this._setState({
                graph: visJsGraph,
                genericGraph: response.graph,
                loading: false,
                error: null,
                cacheStatus: {
                    cached: response.cache_used,
                    csnFilesCount: response.metadata?.csn_files_count || 0,
                    csnDirectory: response.metadata?.csn_directory || ''
                },
                lastRefresh: new Date()
            });
            
            console.log('[GraphPresenter] State updated successfully');

        } catch (error) {
            console.error('[GraphPresenter] loadGraph() error:', error);
            // Update state with error
            this._setState({
                loading: false,
                error: error.message
            });

            throw error; // Re-throw for caller handling
        }
    }

    /**
     * Force rebuild schema graph (ignores cache)
     * 
     * @returns {Promise<Object>} Success result with metadata
     */
    async rebuild() {
        try {
            console.log('[GraphPresenter] rebuild() called');
            
            // Set loading state
            this._setState({
                loading: true,
                error: null
            });

            // Trigger rebuild via API
            console.log('[GraphPresenter] Calling rebuildSchemaGraph API...');
            const response = await this.apiClient.rebuildSchemaGraph();
            console.log('[GraphPresenter] Rebuild API response:', {
                hasGraph: !!response.graph,
                nodeCount: response.graph?.nodes?.length || 0,
                edgeCount: response.graph?.edges?.length || 0
            });

            // Validate graph structure
            this.visJsAdapter.validateGraph(response.graph);

            // Convert to vis.js format
            console.log('[GraphPresenter] Converting rebuild response to vis.js format...');
            const visJsGraph = this.visJsAdapter.convertToVisJs(response.graph);
            console.log('[GraphPresenter] Rebuild conversion complete:', {
                hasNodes: !!visJsGraph.nodes,
                hasEdges: !!visJsGraph.edges,
                nodesLength: visJsGraph.nodes?.length,
                edgesLength: visJsGraph.edges?.length
            });

            // Update state with success
            this._setState({
                graph: visJsGraph,
                genericGraph: response.graph,
                loading: false,
                error: null,
                cacheStatus: {
                    cached: false, // Rebuild always bypasses cache
                    csnFilesCount: response.metadata?.csn_files_count || 0,
                    csnDirectory: response.metadata?.csn_directory || ''
                },
                lastRefresh: new Date()
            });
            
            console.log('[GraphPresenter] Rebuild state updated successfully');

            // Return success result
            return {
                success: true,
                nodes: response.graph.nodes.length,
                edges: response.graph.edges.length,
                metadata: response.metadata
            };

        } catch (error) {
            console.error('[GraphPresenter] rebuild() error:', error);
            // Update state with error
            this._setState({
                loading: false,
                error: error.message
            });

            throw error;
        }
    }

    /**
     * Refresh current view (reload with cache)
     * 
     * @returns {Promise<void>}
     */
    async refresh() {
        console.log('[GraphPresenter] refresh() called');
        return this.loadGraph(true);
    }

    /**
     * Clear cache and reload
     * 
     * @returns {Promise<void>}
     */
    async clearCacheAndReload() {
        try {
            console.log('[GraphPresenter] clearCacheAndReload() called');
            
            // Set loading state
            this._setState({
                loading: true,
                error: null
            });

            // Clear cache via API
            await this.apiClient.clearCache();

            // Reload graph (will rebuild since cache is now empty)
            await this.loadGraph(false);

        } catch (error) {
            console.error('[GraphPresenter] clearCacheAndReload() error:', error);
            // Update state with error
            this._setState({
                loading: false,
                error: error.message
            });

            throw error;
        }
    }

    /**
     * Update cache status only (lightweight refresh)
     * 
     * @returns {Promise<void>}
     */
    async updateStatus() {
        try {
            const status = await this.apiClient.getStatus();

            this._setState({
                cacheStatus: {
                    cached: status.cached,
                    csnFilesCount: status.csn_files_count,
                    csnDirectory: status.csn_directory
                }
            });

        } catch (error) {
            console.error('Failed to update status:', error);
            // Don't throw - status update is non-critical
        }
    }

    /**
     * Get current state (read-only)
     * 
     * @returns {Object} Current state (copy)
     */
    getState() {
        return { ...this.state };
    }

    /**
     * Check if graph is loaded
     * 
     * @returns {boolean}
     */
    isGraphLoaded() {
        return this.state.graph !== null;
    }

    /**
     * Check if loading
     * 
     * @returns {boolean}
     */
    isLoading() {
        return this.state.loading;
    }

    /**
     * Check if error state
     * 
     * @returns {boolean}
     */
    hasError() {
        return this.state.error !== null;
    }

    /**
     * Clear error state
     */
    clearError() {
        this._setState({ error: null });
    }

    /**
     * Reset presenter to initial state
     */
    reset() {
        this._setState({
            graph: null,
            genericGraph: null,
            loading: false,
            error: null,
            cacheStatus: {
                cached: false,
                csnFilesCount: 0,
                csnDirectory: ''
            },
            lastRefresh: null
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GraphPresenter;
}
// Make presenter available globally for debugging
if (typeof window !== 'undefined') {
    window.GraphPresenterClass = GraphPresenter;
}