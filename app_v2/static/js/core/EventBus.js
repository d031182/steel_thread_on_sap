/**
 * Event Bus (Pub/Sub Pattern)
 * 
 * Purpose: Decoupled inter-module communication via publish/subscribe
 * Pattern: Instance-based observer with event namespacing (Industry Standard)
 * 
 * Features:
 * - Subscribe to events (multiple subscribers per event)
 * - Publish events with data payload
 * - Unsubscribe from events
 * - List all available events (discoverability)
 * - Wildcard subscriptions (*) for debugging
 * 
 * Usage:
 *   // Create event bus at composition root
 *   const eventBus = new EventBus();
 *   
 *   // Subscribe
 *   const unsubscribe = eventBus.subscribe('graph:refreshed', (data) => {
 *       console.log('Graph refreshed with', data.nodeCount, 'nodes');
 *   });
 *   
 *   // Publish
 *   eventBus.publish('graph:refreshed', { nodeCount: 42, timestamp: Date.now() });
 *   
 *   // Unsubscribe
 *   unsubscribe();
 * 
 * Event Naming Convention:
 *   - Format: '<module>:<action>' (e.g., 'graph:refreshed', 'log:created')
 *   - Use past tense for completed actions ('refreshed', not 'refresh')
 *   - Use present tense for notifications ('node_selected', not 'node_select')
 * 
 * Architecture: Part of app_v2 core infrastructure (Observer Pattern)
 * Standard: Follows industry best practices for event-driven architecture
 */
class EventBus {
    /**
     * Create new event bus instance
     */
    constructor() {
        /**
         * Internal storage for event subscribers
         * Map<eventName, Set<callback>>
         * @private
         */
        this._subscribers = new Map();
        
        /**
         * Event history for debugging (last 100 events)
         * @private
         */
        this._history = [];
        this._maxHistorySize = 100;
    }
    
    /**
     * Subscribe to an event
     * 
     * @param {string} eventName - Event identifier (e.g., 'graph:refreshed')
     * @param {Function} callback - Function to call when event published
     * @returns {Function} Unsubscribe function
     * @throws {Error} If eventName or callback is invalid
     * 
     * @example
     * const unsubscribe = eventBus.subscribe('graph:refreshed', (data) => {
     *     console.log('Graph has', data.nodeCount, 'nodes');
     * });
     * 
     * // Later: unsubscribe when no longer needed
     * unsubscribe();
     */
    subscribe(eventName, callback) {
        if (!eventName || typeof eventName !== 'string') {
            throw new Error('Event name must be a non-empty string');
        }
        
        if (!callback || typeof callback !== 'function') {
            throw new Error('Callback must be a function');
        }
        
        // Get or create subscriber set for this event
        if (!this._subscribers.has(eventName)) {
            this._subscribers.set(eventName, new Set());
        }
        
        const subscribers = this._subscribers.get(eventName);
        subscribers.add(callback);
        
        // Return unsubscribe function (closure)
        return () => {
            subscribers.delete(callback);
            // Clean up empty sets
            if (subscribers.size === 0) {
                this._subscribers.delete(eventName);
            }
        };
    }
    
    /**
     * Publish an event with optional data
     * 
     * @param {string} eventName - Event identifier
     * @param {*} data - Event payload (optional)
     * @returns {number} Number of subscribers notified
     * 
     * @example
     * eventBus.publish('graph:refreshed', { 
     *     nodeCount: 42, 
     *     timestamp: Date.now() 
     * });
     * 
     * eventBus.publish('user:logged_in');  // No data
     */
    publish(eventName, data = null) {
        if (!eventName || typeof eventName !== 'string') {
            throw new Error('Event name must be a non-empty string');
        }
        
        // Add to history for debugging
        this._addToHistory(eventName, data);
        
        let notifiedCount = 0;
        
        // Notify specific subscribers
        const subscribers = this._subscribers.get(eventName);
        if (subscribers) {
            subscribers.forEach(callback => {
                try {
                    callback(data);
                    notifiedCount++;
                } catch (error) {
                    console.error(
                        `Error in event subscriber for '${eventName}':`,
                        error
                    );
                }
            });
        }
        
        // Notify wildcard subscribers (for debugging/logging)
        const wildcardSubscribers = this._subscribers.get('*');
        if (wildcardSubscribers) {
            wildcardSubscribers.forEach(callback => {
                try {
                    callback({ eventName, data });
                } catch (error) {
                    console.error('Error in wildcard subscriber:', error);
                }
            });
        }
        
        return notifiedCount;
    }
    
    /**
     * Unsubscribe all callbacks for an event
     * 
     * @param {string} eventName - Event identifier
     * @returns {boolean} True if event had subscribers
     * 
     * @example
     * eventBus.unsubscribeAll('graph:refreshed');
     */
    unsubscribeAll(eventName) {
        return this._subscribers.delete(eventName);
    }
    
    /**
     * Get all registered event names
     * 
     * @returns {string[]} Array of event names (sorted)
     * 
     * @example
     * const events = eventBus.getRegisteredEvents();
     * console.log('Available events:', events.join(', '));
     */
    getRegisteredEvents() {
        return Array.from(this._subscribers.keys())
            .filter(name => name !== '*')  // Exclude wildcard
            .sort();
    }
    
    /**
     * Get subscriber count for an event
     * 
     * @param {string} eventName - Event identifier
     * @returns {number} Number of subscribers
     * 
     * @example
     * const count = eventBus.getSubscriberCount('graph:refreshed');
     * console.log(`${count} modules listening to graph:refreshed`);
     */
    getSubscriberCount(eventName) {
        const subscribers = this._subscribers.get(eventName);
        return subscribers ? subscribers.size : 0;
    }
    
    /**
     * Check if an event has subscribers
     * 
     * @param {string} eventName - Event identifier
     * @returns {boolean} True if event has subscribers
     * 
     * @example
     * if (eventBus.hasSubscribers('graph:refreshed')) {
     *     // Publish event
     *     eventBus.publish('graph:refreshed', data);
     * }
     */
    hasSubscribers(eventName) {
        return this.getSubscriberCount(eventName) > 0;
    }
    
    /**
     * Clear all subscriptions (for testing)
     * 
     * WARNING: This clears ALL subscriptions. Use only in tests!
     * 
     * @example
     * // In test setup
     * beforeEach(() => {
     *     eventBus.clear();
     * });
     */
    clear() {
        this._subscribers.clear();
        this._history = [];
    }
    
    /**
     * Get event history (for debugging)
     * 
     * @param {number} count - Number of recent events to return (default: 10)
     * @returns {Array} Array of event records
     * 
     * @example
     * const recent = eventBus.getHistory(5);
     * console.table(recent);
     */
    getHistory(count = 10) {
        return this._history.slice(-count);
    }
    
    /**
     * Add event to history (internal)
     * @private
     */
    _addToHistory(eventName, data) {
        this._history.push({
            eventName,
            data,
            timestamp: new Date().toISOString(),
            subscriberCount: this.getSubscriberCount(eventName)
        });
        
        // Keep history size limited
        if (this._history.length > this._maxHistorySize) {
            this._history.shift();  // Remove oldest
        }
    }
    
    /**
     * Subscribe to all events (wildcard) - for debugging/logging
     * 
     * @param {Function} callback - Function to call for every event
     * @returns {Function} Unsubscribe function
     * 
     * @example
     * // Log all events
     * const unsubscribe = eventBus.subscribeAll((event) => {
     *     console.log('Event:', event.eventName, event.data);
     * });
     */
    subscribeAll(callback) {
        return this.subscribe('*', callback);
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventBus;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.EventBus = EventBus;
}