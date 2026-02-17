/**
 * Logger Module Factory
 * ====================
 * Factory function for the Logger module following Module Federation Standard.
 * 
 * @module LoggerModule
 */

import LoggerAdapter from './adapters/LoggerAdapter.js';

/**
 * Logger Module Factory
 * 
 * @param {Object} dependencies - Injected dependencies
 * @param {Object} dependencies.eventBus - Event bus for pub/sub
 * @param {Object} dependencies.logger - Logger instance (optional)
 * @returns {Object} Module instance
 */
export function LoggerModule(dependencies) {
    const { eventBus, logger } = dependencies;
    
    // Module state
    let adapter = null;
    let currentMode = 'default';
    
    return {
        id: 'logger',
        name: 'Logger',
        version: '1.0.0',
        
        /**
         * Initialize the logger module
         */
        async init() {
            try {
                // Create adapter
                adapter = new LoggerAdapter();
                
                // Fetch current logging mode
                const modeData = await adapter.getMode();
                currentMode = modeData.data.mode;
                
                // Initialize Flight Recorder if in that mode
                if (currentMode === 'flight_recorder') {
                    this._initFlightRecorder();
                }
                
                // Emit initialization event
                eventBus.emit('logger:initialized', { mode: currentMode });
                
                if (logger) {
                    logger.info('Logger module initialized', { mode: currentMode });
                }
            } catch (error) {
                console.error('Failed to initialize Logger module:', error);
                if (logger) {
                    logger.error('Logger module initialization failed', { error: error.message });
                }
            }
        },
        
        /**
         * Get the logger adapter
         * @returns {LoggerAdapter} The adapter instance
         */
        getAdapter() {
            if (!adapter) {
                adapter = new LoggerAdapter();
            }
            return adapter;
        },
        
        /**
         * Get current logging mode
         * @returns {string} Current mode ('default' or 'flight_recorder')
         */
        getMode() {
            return currentMode;
        },
        
        /**
         * Set logging mode
         * @param {string} mode - Mode to set ('default' or 'flight_recorder')
         */
        async setMode(mode) {
            try {
                const result = await adapter.setMode(mode);
                currentMode = mode;
                
                // Reinitialize Flight Recorder if needed
                if (mode === 'flight_recorder') {
                    this._initFlightRecorder();
                } else {
                    this._stopFlightRecorder();
                }
                
                eventBus.emit('logger:mode-changed', { mode });
                
                if (logger) {
                    logger.info('Logging mode changed', { mode });
                }
                
                return result;
            } catch (error) {
                console.error('Failed to set logging mode:', error);
                throw error;
            }
        },
        
        /**
         * Submit a log entry to the backend
         * @param {Object} logEntry - Log entry object
         */
        async submitLog(logEntry) {
            if (!adapter) {
                console.warn('Logger adapter not initialized');
                return;
            }
            
            try {
                await adapter.submitLog(logEntry);
            } catch (error) {
                console.error('Failed to submit log:', error);
            }
        },
        
        /**
         * Initialize Flight Recorder mode (captures all frontend events)
         * @private
         */
        _initFlightRecorder() {
            // TODO: Implement Flight Recorder interceptor
            // This would capture:
            // - All console logs (info, warn, error)
            // - All click events
            // - All API calls
            // - All SAPUI5 events
            // - Performance metrics
            
            if (logger) {
                logger.info('Flight Recorder mode activated');
            }
        },
        
        /**
         * Stop Flight Recorder mode
         * @private
         */
        _stopFlightRecorder() {
            // TODO: Clean up Flight Recorder interceptors
            
            if (logger) {
                logger.info('Flight Recorder mode deactivated');
            }
        },
        
        /**
         * Cleanup resources
         */
        destroy() {
            this._stopFlightRecorder();
            adapter = null;
            
            if (logger) {
                logger.info('Logger module destroyed');
            }
        }
    };
}

export default LoggerModule;