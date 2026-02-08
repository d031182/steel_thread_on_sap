/**
 * Navigation Builder - Auto-Generate UI Navigation
 * =================================================
 * 
 * Dynamically builds SAP Fiori IconTabBar navigation from module metadata.
 * 
 * Features:
 * - Auto-generates tabs from ModuleRegistry
 * - Groups by category (if multiple categories)
 * - Respects module order
 * - Handles icons and labels
 * - Publishes navigation events
 * 
 * Architecture:
 * - Consumes ModuleRegistry for module metadata
 * - Builds SAPUI5 IconTabBar dynamically
 * - Integrates with RouterService for navigation
 * - Uses EventBus for navigation events
 * 
 * Usage:
 *   const builder = new NavigationBuilder(registry, eventBus);
 *   const tabBar = builder.buildNavigation();
 *   // tabBar is sap.m.IconTabBar instance
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

class NavigationBuilder {
    /**
     * Create navigation builder
     * 
     * @param {ModuleRegistry} registry - Module registry instance
     * @param {EventBus} eventBus - Event bus for navigation events
     */
    constructor(registry, eventBus) {
        if (!registry || !registry.isInitialized()) {
            throw new Error('NavigationBuilder requires initialized ModuleRegistry');
        }
        if (!eventBus) {
            throw new Error('NavigationBuilder requires EventBus instance');
        }

        this._registry = registry;
        this._eventBus = eventBus;
        this._tabBar = null;
    }

    /**
     * Build navigation tab bar
     * 
     * @returns {sap.m.IconTabBar} Icon tab bar with module tabs
     */
    buildNavigation() {
        const modules = this._registry.getAllModules();
        const categories = this._registry.getCategories();

        // Decide layout based on categories
        if (categories.length > 1) {
            return this._buildCategorizedNavigation(categories);
        } else {
            return this._buildFlatNavigation(modules);
        }
    }

    /**
     * Build flat navigation (single category or no categories)
     * 
     * @private
     * @param {Array<Object>} modules - Module metadata array
     * @returns {sap.m.IconTabBar}
     */
    _buildFlatNavigation(modules) {
        const filters = modules.map(module => this._createTabFilter(module));

        this._tabBar = new sap.m.IconTabBar({
            expandable: false,
            stretchContentHeight: true,
            items: filters,
            select: (event) => this._handleTabSelect(event)
        });

        return this._tabBar;
    }

    /**
     * Build categorized navigation (multiple categories)
     * 
     * @private
     * @param {Array<string>} categories - Category names
     * @returns {sap.m.IconTabBar}
     */
    _buildCategorizedNavigation(categories) {
        const categoryFilters = categories.map(category => {
            const modules = this._registry.getModulesByCategory(category);
            const subFilters = modules.map(module => this._createTabFilter(module));

            return new sap.m.IconTabFilter({
                text: this._formatCategoryName(category),
                icon: this._getCategoryIcon(category),
                items: subFilters
            });
        });

        this._tabBar = new sap.m.IconTabBar({
            expandable: false,
            stretchContentHeight: true,
            items: categoryFilters,
            select: (event) => this._handleTabSelect(event)
        });

        return this._tabBar;
    }

    /**
     * Create tab filter for a module
     * 
     * @private
     * @param {Object} module - Module metadata
     * @returns {sap.m.IconTabFilter}
     */
    _createTabFilter(module) {
        return new sap.m.IconTabFilter({
            key: module.id,
            text: module.name,
            icon: module.icon || 'sap-icon://product',
            tooltip: module.description,
            customData: [
                new sap.ui.core.CustomData({
                    key: 'moduleId',
                    value: module.id
                }),
                new sap.ui.core.CustomData({
                    key: 'route',
                    value: module.frontend?.route || `/${module.id}`
                })
            ]
        });
    }

    /**
     * Handle tab selection
     * 
     * @private
     * @param {sap.ui.base.Event} event - Tab select event
     */
    _handleTabSelect(event) {
        const selectedItem = event.getParameter('item') || event.getParameter('key');
        
        if (!selectedItem) {
            console.warn('[NavigationBuilder] No item selected');
            return;
        }

        // Get module ID from custom data
        let moduleId;
        if (selectedItem.data) {
            moduleId = selectedItem.data('moduleId');
        } else if (selectedItem.getKey) {
            moduleId = selectedItem.getKey();
        }

        if (!moduleId) {
            console.warn('[NavigationBuilder] No module ID found for selected item');
            return;
        }

        // Get module metadata
        const module = this._registry.getModule(moduleId);
        if (!module) {
            console.error(`[NavigationBuilder] Module not found: ${moduleId}`);
            return;
        }

        // Get route from custom data or module metadata
        let route;
        if (selectedItem.data) {
            route = selectedItem.data('route');
        }
        if (!route) {
            route = module.frontend?.route || `/${moduleId}`;
        }

        // Publish navigation event
        this._eventBus.publish('navigation:moduleSelected', {
            moduleId,
            module,
            route,
            timestamp: new Date().toISOString()
        });

        console.log(`[NavigationBuilder] Navigate to: ${moduleId} (${route})`);
    }

    /**
     * Format category name for display
     * 
     * @private
     * @param {string} category - Category name
     * @returns {string} Formatted name
     */
    _formatCategoryName(category) {
        return category
            .split(/[_\s]+/)
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }

    /**
     * Get icon for category
     * 
     * @private
     * @param {string} category - Category name
     * @returns {string} SAP icon name
     */
    _getCategoryIcon(category) {
        const iconMap = {
            'analytics': 'sap-icon://bar-chart',
            'business_logic': 'sap-icon://business-objects',
            'data_management': 'sap-icon://database',
            'developer_tools': 'sap-icon://wrench',
            'infrastructure': 'sap-icon://settings',
            'ai_analytics': 'sap-icon://learning-assistant',
            'general': 'sap-icon://product'
        };

        const key = category.toLowerCase().replace(/\s+/g, '_');
        return iconMap[key] || 'sap-icon://product';
    }

    /**
     * Get current tab bar instance
     * 
     * @returns {sap.m.IconTabBar|null}
     */
    getTabBar() {
        return this._tabBar;
    }

    /**
     * Select tab by module ID
     * 
     * @param {string} moduleId - Module identifier
     * @returns {boolean} True if tab found and selected
     */
    selectTab(moduleId) {
        if (!this._tabBar) {
            console.warn('[NavigationBuilder] Tab bar not built yet');
            return false;
        }

        // Find tab with matching key
        const items = this._tabBar.getItems();
        
        for (const item of items) {
            // Check direct match
            if (item.getKey && item.getKey() === moduleId) {
                this._tabBar.setSelectedItem(item);
                return true;
            }

            // Check nested items (for categorized navigation)
            if (item.getItems) {
                const subItems = item.getItems();
                for (const subItem of subItems) {
                    if (subItem.getKey && subItem.getKey() === moduleId) {
                        this._tabBar.setSelectedItem(subItem);
                        return true;
                    }
                }
            }
        }

        console.warn(`[NavigationBuilder] Tab not found: ${moduleId}`);
        return false;
    }

    /**
     * Rebuild navigation (after module changes)
     * 
     * @returns {sap.m.IconTabBar} New tab bar instance
     */
    rebuild() {
        if (this._tabBar) {
            this._tabBar.destroy();
            this._tabBar = null;
        }

        return this.buildNavigation();
    }

    /**
     * Get all tab keys
     * 
     * @returns {Array<string>} Array of module IDs
     */
    getTabKeys() {
        if (!this._tabBar) {
            return [];
        }

        const keys = [];
        const items = this._tabBar.getItems();

        for (const item of items) {
            if (item.getKey) {
                keys.push(item.getKey());
            }

            // Get nested items (for categorized navigation)
            if (item.getItems) {
                const subItems = item.getItems();
                for (const subItem of subItems) {
                    if (subItem.getKey) {
                        keys.push(subItem.getKey());
                    }
                }
            }
        }

        return keys;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavigationBuilder;
}