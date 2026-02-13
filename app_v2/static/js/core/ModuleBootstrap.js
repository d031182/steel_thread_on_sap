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
        // Create instances (Industry Standard pattern)
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

            // Step 9: Navigate to first available module
            const modules = this._registry.getAllModules();
            if (modules.length > 0) {
                const firstModule = modules[0];
                console.log(`[Bootstrap] Navigating to first module: ${firstModule.id}`);
                await this._router.navigateTo(firstModule.id);
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

        // Cache fallback (InMemoryCache - fast, volatile)
        // Note: LocalStorageCache available if persistence needed
        this._container.register('ICache', () => new InMemoryCache());

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

        // Check for DataProducts V2 module
        if (this._registry.hasModule('data_products_v2')) {
            // Replace mock with real DataProductsV2Adapter
            this._container.register('IDataSource', () => new DataProductsV2Adapter({
                baseUrl: '/api/data-products',
                source: 'sqlite', // Default to SQLite for App V2
                timeout: 30000
            }));
            console.log('[Bootstrap] DataProductsV2Adapter registered (real implementation)');
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

        // Create AI Assistant button for header
        const aiButton = new sap.m.Button({
            icon: 'sap-icon://collaborate',
            tooltip: 'Open AI Assistant',
            type: sap.m.ButtonType.Transparent,
            press: this._onToggleAIAssistant.bind(this)
        });

        // Create custom header with AI button
        const customHeader = new sap.m.Bar({
            contentLeft: [
                new sap.m.Title({
                    text: 'P2P Data Products',
                    level: sap.ui.core.TitleLevel.H1
                })
            ],
            contentRight: [aiButton]
        });

        // Create page with custom header and navigation
        const page = new sap.m.Page({
            customHeader: [customHeader],
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

        // Store references for AI Assistant
        this._aiButton = aiButton;
        this._mainPage = page;

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

    /**
     * Toggle AI Assistant overlay
     * 
     * @private
     * @param {sap.ui.base.Event} oEvent - Button press event
     */
    _onToggleAIAssistant(oEvent) {
        // PRIORITY 1: Use AI Assistant module if available (Phase 2 integration)
        if (window.aiAssistant && window.aiAssistant.open) {
            window.aiAssistant.open();
            return;
        }

        // FALLBACK: Use built-in dialog (legacy)
        if (!this._aiDialog) {
            this._aiDialog = this._createAIAssistantDialog();
        }

        if (this._aiDialog.isOpen()) {
            this._aiDialog.close();
        } else {
            // Update context before opening
            this._updateAIContext();
            this._aiDialog.open();
        }
    }

    /**
     * Create AI Assistant Dialog
     * 
     * @private
     * @returns {sap.m.Dialog}
     */
    _createAIAssistantDialog() {
        // Initialize AI model
        this._aiModel = new sap.ui.model.json.JSONModel({
            messages: [],
            currentMessage: '',
            isLoading: false,
            context: {
                currentPage: '',
                dataProduct: '',
                schema: '',
                table: ''
            }
        });

        // Message list
        const messageList = new sap.m.List({
            id: 'aiMessageList',
            mode: sap.m.ListMode.None,
            noDataText: 'Start a conversation with the AI Assistant...'
        });
        messageList.bindItems({
            path: '/messages',
            template: new sap.m.FeedListItem({
                sender: '{sender}',
                text: '{text}',
                timestamp: '{timestamp}',
                icon: '{icon}'
            })
        });

        // Input area
        const messageInput = new sap.m.TextArea({
            id: 'aiMessageInput',
            value: '{/currentMessage}',
            placeholder: 'Ask about data products, schemas, or request SQL generation...',
            rows: 2,
            width: '100%',
            growing: true,
            growingMaxLines: 4,
            enabled: '{= !${/isLoading}}'
        });

        const sendButton = new sap.m.Button({
            icon: 'sap-icon://paper-plane',
            type: sap.m.ButtonType.Emphasized,
            press: this._onSendAIMessage.bind(this),
            enabled: '{= ${/currentMessage}.length > 0 && !${/isLoading}}'
        });

        const inputToolbar = new sap.m.Toolbar({
            content: [messageInput, sendButton]
        });

        // Dialog
        const dialog = new sap.m.Dialog({
            title: 'AI Assistant',
            contentWidth: '500px',
            contentHeight: '600px',
            resizable: true,
            draggable: true,
            content: [
                new sap.m.VBox({
                    height: '100%',
                    justifyContent: sap.m.FlexJustifyContent.SpaceBetween,
                    items: [
                        new sap.m.ScrollContainer({
                            height: '100%',
                            vertical: true,
                            content: [messageList]
                        }),
                        inputToolbar
                    ]
                })
            ],
            endButton: new sap.m.Button({
                text: 'Close',
                press: () => dialog.close()
            })
        });

        dialog.setModel(this._aiModel);
        return dialog;
    }

    /**
     * Send AI message
     * 
     * @private
     */
    async _onSendAIMessage() {
        const sMessage = this._aiModel.getProperty('/currentMessage').trim();
        if (!sMessage) return;

        // Add user message
        this._addAIMessage({
            type: 'user',
            sender: 'You',
            text: sMessage,
            timestamp: new Date().toLocaleTimeString(),
            icon: 'sap-icon://person-placeholder'
        });

        // Clear input and set loading
        this._aiModel.setProperty('/currentMessage', '');
        this._aiModel.setProperty('/isLoading', true);

        try {
            // Call AI API
            const context = this._aiModel.getProperty('/context');
            const response = await fetch('/api/ai-assistant/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: sMessage,
                    context: context
                })
            });

            const data = await response.json();
            this._aiModel.setProperty('/isLoading', false);

            if (data.success) {
                this._addAIMessage({
                    type: 'ai',
                    sender: 'AI Assistant',
                    text: this._formatAIResponse(data.response),
                    timestamp: new Date().toLocaleTimeString(),
                    icon: 'sap-icon://collaborate'
                });

                // Scroll to bottom
                setTimeout(() => {
                    const list = sap.ui.getCore().byId('aiMessageList');
                    if (list) {
                        const items = list.getItems();
                        if (items.length > 0) {
                            list.scrollToIndex(items.length - 1);
                        }
                    }
                }, 100);
            } else {
                sap.m.MessageBox.error('AI Error: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            this._aiModel.setProperty('/isLoading', false);
            sap.m.MessageBox.error('Network error: ' + error.message);
        }
    }

    /**
     * Add message to AI conversation
     * 
     * @private
     * @param {Object} oMessage - Message object
     */
    _addAIMessage(oMessage) {
        const messages = this._aiModel.getProperty('/messages');
        messages.push(oMessage);
        this._aiModel.setProperty('/messages', messages);
    }

    /**
     * Update AI context with current page info
     * 
     * @private
     */
    _updateAIContext() {
        if (!this._router) return;

        const currentModule = this._router.getCurrentModule();
        this._aiModel.setProperty('/context/currentPage', currentModule || '');
    }

    /**
     * Format AI response (remove technical wrappers)
     * 
     * @private
     * @param {string} response - Raw AI response
     * @returns {string} Formatted response
     */
    _formatAIResponse(response) {
        // Remove AgentRunResult wrapper if present
        const match = response.match(/AgentRunResult\(output='(.*)'\)/s);
        return match ? match[1] : response;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModuleBootstrap;
}