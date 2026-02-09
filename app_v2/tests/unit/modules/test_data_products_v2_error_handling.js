/**
 * Unit Tests: Data Products V2 - SAP Fiori Error Handling
 * 
 * Test Framework: Gu Wu (顾武) Frontend Testing
 * Pattern: AAA (Arrange-Act-Assert)
 * 
 * PURPOSE: Verify SAP Fiori-compliant error handling
 * - MessageBox.error for errors (NOT MessageToast)
 * - MessageToast for success ONLY
 * - Context-aware error messages
 * - Auto-fallback functionality
 * 
 * @author P2P Development Team
 * @version 1.0.0
 * @date 2026-02-09
 */

describe('Data Products V2 Module - SAP Fiori Error Handling', () => {
    let mockContainer;
    let mockEventBus;
    let mockDataSource;
    let messageBoxErrorSpy;
    let messageToastShowSpy;
    let DataProductsV2Factory;
    let module;

    beforeEach(() => {
        // Mock SAPUI5 MessageBox and MessageToast
        global.sap = {
            m: {
                MessageBox: {
                    error: jest.fn(),
                    Action: {
                        OK: 'OK'
                    }
                },
                MessageToast: {
                    show: jest.fn()
                }
            }
        };

        messageBoxErrorSpy = global.sap.m.MessageBox.error;
        messageToastShowSpy = global.sap.m.MessageToast.show;

        // Mock window globals needed by module
        global.window = global.window || {};
        global.window.createDataProductsV2Page = jest.fn();
        global.window.showDataProductDetailsV2 = jest.fn();
        global.window.DataProductsV2Adapter = class MockAdapter {
            constructor(config) {
                this.config = config;
            }
        };
        global.DataProductsV2Adapter = global.window.DataProductsV2Adapter;

        // Mock DependencyContainer
        mockContainer = {
            has: jest.fn(),
            get: jest.fn(),
            register: jest.fn()
        };

        // Mock EventBus
        mockEventBus = {
            subscribe: jest.fn(),
            publish: jest.fn()
        };

        // Mock DataSource
        mockDataSource = {
            query: jest.fn()
        };

        // Setup default container behavior
        mockContainer.has.mockImplementation((service) => {
            return service === 'IDataSource' || service === 'ILogger' || service === 'ICache';
        });

        mockContainer.get.mockImplementation((service) => {
            if (service === 'IDataSource') return mockDataSource;
            if (service === 'ILogger') return {
                log: jest.fn(),
                warn: jest.fn(),
                error: jest.fn()
            };
            if (service === 'ICache') return null;
        });

        // Load module factory using eval (since it's in IIFE)
        const moduleCode = require('fs').readFileSync(
            'modules/data_products_v2/frontend/module.js',
            'utf-8'
        );
        eval(moduleCode);
        
        DataProductsV2Factory = global.window.DataProductsV2Factory;
        module = DataProductsV2Factory(mockContainer, mockEventBus);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    // ========================================
    // SAP FIORI BEST PRACTICE: MessageBox for Errors
    // ========================================

    describe('SAP Fiori Best Practice: MessageBox.error for Errors', () => {
        test('CRITICAL: Uses MessageBox.error (NOT MessageToast) for HANA connection failures', async () => {
            // ARRANGE: HANA connection fails
            const errorMessage = 'Connection failed: HANA Cloud not reachable';
            mockDataSource.query.mockRejectedValue(new Error(errorMessage));

            // ACT: Try to initialize (will fail)
            try {
                await module.initialize();
            } catch (error) {
                // Expected to fail
            }

            // ASSERT: MessageBox.error was called (Fiori best practice ✅)
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorText = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorText).toContain('Failed to load data products');
            expect(errorText).toContain(errorMessage);

            // ASSERT: MessageToast was NOT used for errors (violates Fiori ❌)
            expect(messageToastShowSpy).not.toHaveBeenCalled();
        });

        test('Shows context-aware error message for HANA failures', async () => {
            // ARRANGE: Simulate HANA source
            mockDataSource.query.mockRejectedValue(new Error('HANA timeout'));

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT: Error message mentions HANA Cloud specifically
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toContain('HANA Cloud');
            expect(errorMessage).toContain('SQLite');  // Mentions fallback
        });

        test('Offers "Switch to SQLite" action button for HANA failures', async () => {
            // ARRANGE
            mockDataSource.query.mockRejectedValue(new Error('HANA connection failed'));

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT: MessageBox config includes "Switch to SQLite" action
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const messageBoxConfig = messageBoxErrorSpy.mock.calls[0][1];
            
            expect(messageBoxConfig.title).toBe('Data Loading Error');
            expect(messageBoxConfig.actions).toContain('Switch to SQLite');
            expect(messageBoxConfig.emphasizedAction).toBe('OK');
            expect(messageBoxConfig.onClose).toBeInstanceOf(Function);
        });

        test('Shows different error for SQLite failures (no fallback offered)', async () => {
            // ARRANGE: SQLite fails (no fallback available)
            mockDataSource.query.mockRejectedValue(new Error('SQLite file not found'));

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT: Error mentions SQLite
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toContain('SQLite');
            
            // ASSERT: No "Switch to SQLite" for SQLite errors
            const messageBoxConfig = messageBoxErrorSpy.mock.calls[0][1];
            expect(messageBoxConfig.actions).toEqual(['OK']);
            expect(messageBoxConfig.actions).not.toContain('Switch to SQLite');
        });

        test('Shows MessageBox.error for render failures', async () => {
            // ARRANGE: Initialize succeeds, but render fails (missing view factory)
            mockDataSource.query.mockResolvedValue([]);
            await module.initialize();
            
            delete global.window.createDataProductsV2Page;  // Remove view factory

            // ACT
            try {
                await module.render();
            } catch (error) {
                // Expected
            }

            // ASSERT: MessageBox.error shows render failure
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toContain('Failed to render Data Products module');
            expect(errorMessage).toContain('createDataProductsV2Page');
            expect(errorMessage).toContain('ensure all module scripts are loaded');
        });
    });

    // ========================================
    // SAP FIORI BEST PRACTICE: MessageToast for Success ONLY
    // ========================================

    describe('SAP Fiori Best Practice: MessageToast for Success ONLY', () => {
        test('Uses MessageToast.show for successful refresh (correct usage ✅)', async () => {
            // ARRANGE: Module initialized successfully
            mockDataSource.query.mockResolvedValue([
                { product_name: 'Product1' },
                { product_name: 'Product2' }
            ]);
            
            global.window.createDataProductsV2Page.mockReturnValue({
                refresh: jest.fn()
            });

            await module.initialize();
            const view = await module.render();

            // Get the onRefresh callback
            const createPageCall = global.window.createDataProductsV2Page.mock.calls[0];
            const callbacks = createPageCall[2];  // Third argument
            const onRefresh = callbacks.onRefresh;

            // ACT: Trigger refresh (simulating user clicking refresh button)
            await onRefresh();

            // ASSERT: MessageToast shows success message
            expect(messageToastShowSpy).toHaveBeenCalledWith('Data products refreshed successfully');
            
            // ASSERT: No MessageBox.error for successful operation
            expect(messageBoxErrorSpy).not.toHaveBeenCalled();
        });

        test('NEVER uses MessageToast for errors (Fiori guideline)', async () => {
            // ARRANGE: Module initialized
            mockDataSource.query
                .mockResolvedValueOnce([])  // Initial load succeeds
                .mockRejectedValueOnce(new Error('Refresh failed'));  // Refresh fails
            
            global.window.createDataProductsV2Page.mockReturnValue({
                refresh: jest.fn()
            });

            await module.initialize();
            await module.render();

            const createPageCall = global.window.createDataProductsV2Page.mock.calls[0];
            const callbacks = createPageCall[2];
            const onRefresh = callbacks.onRefresh;

            messageBoxErrorSpy.mockClear();  // Clear initial load call

            // ACT: Refresh fails
            await onRefresh();

            // ASSERT: Error shown in MessageBox (not MessageToast)
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toContain('Failed to load data products');
            
            // ASSERT: MessageToast NOT used for error (Fiori violation would be here)
            expect(messageToastShowSpy).not.toHaveBeenCalled();
        });
    });

    // ========================================
    // ERROR PROPAGATION & TRANSPARENCY
    // ========================================

    describe('Error Transparency (No Silent Failures)', () => {
        test('Errors propagate up the call stack (not suppressed)', async () => {
            // ARRANGE: DataSource fails
            const specificError = new Error('Specific HANA error');
            mockDataSource.query.mockRejectedValue(specificError);

            // ACT & ASSERT: Error propagates to caller
            await expect(module.initialize()).rejects.toThrow('Specific HANA error');
            
            // ASSERT: Error was also shown to user
            expect(messageBoxErrorSpy).toHaveBeenCalled();
        });

        test('Technical error details are included in user-facing message', async () => {
            // ARRANGE
            const technicalError = 'IP address 192.168.1.1 not in HANA allowlist';
            mockDataSource.query.mockRejectedValue(new Error(technicalError));

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT: Technical details visible in MessageBox
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toContain(technicalError);
        });
    });

    // ========================================
    // AUTO-FALLBACK FUNCTIONALITY
    // ========================================

    describe('Auto-Fallback to SQLite', () => {
        test('Provides "Switch to SQLite" button for HANA failures', async () => {
            // ARRANGE
            mockDataSource.query.mockRejectedValue(new Error('HANA unreachable'));

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT: Button is available
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const config = messageBoxErrorSpy.mock.calls[0][1];
            expect(config.actions).toContain('Switch to SQLite');
            expect(config.onClose).toBeInstanceOf(Function);
        });

        test('onClose handler triggers switchSource when button clicked', async () => {
            // ARRANGE
            mockDataSource.query
                .mockRejectedValueOnce(new Error('HANA failed'))
                .mockResolvedValueOnce([]);  // SQLite succeeds

            // ACT: Trigger error
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // Get the onClose callback
            const config = messageBoxErrorSpy.mock.calls[0][1];
            const onClose = config.onClose;

            messageBoxErrorSpy.mockClear();

            // ACT: Simulate user clicking "Switch to SQLite"
            await onClose('Switch to SQLite');

            // ASSERT: Container.register was called to switch source
            expect(mockContainer.register).toHaveBeenCalledWith(
                'IDataSource',
                expect.any(Function)
            );

            // ASSERT: Data reloaded after switch
            expect(mockDataSource.query).toHaveBeenCalledTimes(2); // Initial fail + reload success
        });
    });

    // ========================================
    // COMPREHENSIVE ERROR SCENARIOS
    // ========================================

    describe('Comprehensive Error Scenarios', () => {
        test('Handles network timeout errors gracefully', async () => {
            // ARRANGE
            const timeoutError = new Error('Request timeout after 30000ms');
            mockDataSource.query.mockRejectedValue(timeoutError);

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toContain('Failed to load data products');
            expect(errorMessage).toContain('timeout');
        });

        test('Handles authentication errors with clear message', async () => {
            // ARRANGE
            const authError = new Error('Authentication failed: Invalid credentials');
            mockDataSource.query.mockRejectedValue(authError);

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toContain('Authentication failed');
        });

        test('Handles SQL execution errors with details', async () => {
            // ARRANGE
            const sqlError = new Error('SQL Error: Table "NONEXISTENT" not found');
            mockDataSource.query.mockRejectedValue(sqlError);

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toContain('SQL Error');
            expect(errorMessage).toContain('NONEXISTENT');
        });
    });

    // ========================================
    // INTEGRATION WITH EXISTING ERROR FLOW
    // ========================================

    describe('Error Flow Integration', () => {
        test('Backend error → MessageBox → User sees dialog', async () => {
            // ARRANGE: Backend returns HTTP 503
            const backendError = new Error('Service Unavailable: HANA connection pool exhausted');
            mockDataSource.query.mockRejectedValue(backendError);

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT: Full error flow
            expect(messageBoxErrorSpy).toHaveBeenCalledTimes(1);
            
            const errorDialog = messageBoxErrorSpy.mock.calls[0];
            const errorMessage = errorDialog[0];
            const errorConfig = errorDialog[1];

            // Verify error message content
            expect(errorMessage).toContain('Failed to load data products');
            expect(errorMessage).toContain('HANA connection pool exhausted');

            // Verify dialog configuration
            expect(errorConfig.title).toBe('Data Loading Error');
            expect(errorConfig.actions).toContain('OK');
        });

        test('onRefresh callback error → MessageBox (not silent failure)', async () => {
            // ARRANGE: Initial load succeeds
            mockDataSource.query.mockResolvedValueOnce([]);
            
            global.window.createDataProductsV2Page.mockReturnValue({
                refresh: jest.fn()
            });

            await module.initialize();
            await module.render();

            // Get onRefresh callback
            const callbacks = global.window.createDataProductsV2Page.mock.calls[0][2];
            const onRefresh = callbacks.onRefresh;

            // Now make refresh fail
            mockDataSource.query.mockRejectedValueOnce(new Error('Refresh failed'));
            messageBoxErrorSpy.mockClear();

            // ACT: Trigger refresh
            await onRefresh();

            // ASSERT: Error shown in MessageBox
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            expect(messageBoxErrorSpy.mock.calls[0][0]).toContain('Refresh failed');
        });

        test('onSourceChange error → MessageBox (not silent)', async () => {
            // ARRANGE
            mockDataSource.query.mockResolvedValueOnce([]);
            global.window.createDataProductsV2Page.mockReturnValue({
                refresh: jest.fn()
            });

            await module.initialize();
            await module.render();

            const callbacks = global.window.createDataProductsV2Page.mock.calls[0][2];
            const onSourceChange = callbacks.onSourceChange;

            // Make source switch fail
            mockDataSource.query.mockRejectedValueOnce(new Error('Switch failed'));
            messageBoxErrorSpy.mockClear();

            // ACT: Trigger source change
            await onSourceChange('hana');

            // ASSERT: Error shown in MessageBox
            expect(messageBoxErrorSpy).toHaveBeenCalled();
        });
    });

    // ========================================
    // USER EXPERIENCE VALIDATION
    // ========================================

    describe('User Experience Validation', () => {
        test('Error dialog requires user acknowledgment (modal blocking)', async () => {
            // ARRANGE
            mockDataSource.query.mockRejectedValue(new Error('Critical error'));

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT: MessageBox config ensures modal behavior
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const config = messageBoxErrorSpy.mock.calls[0][1];
            
            // Modal dialogs have title and actions (user must respond)
            expect(config.title).toBeDefined();
            expect(config.actions).toBeDefined();
            expect(config.actions.length).toBeGreaterThan(0);
        });

        test('Error messages are user-friendly (not technical jargon)', async () => {
            // ARRANGE
            mockDataSource.query.mockRejectedValue(
                new Error('Error: ERR_CONNECTION_REFUSED at TcpSocket.connect')
            );

            // ACT
            try {
                await module.initialize();
            } catch (error) {
                // Expected
            }

            // ASSERT: Error message starts with user-friendly text
            expect(messageBoxErrorSpy).toHaveBeenCalled();
            const errorMessage = messageBoxErrorSpy.mock.calls[0][0];
            expect(errorMessage).toMatch(/^Failed to load data products/);
            expect(errorMessage).toContain('Please check your connection');
        });

        test('Success operations show non-intrusive toast (auto-dismiss)', async () => {
            // ARRANGE
            mockDataSource.query.mockResolvedValue([]);
            global.window.createDataProductsV2Page.mockReturnValue({
                refresh: jest.fn()
            });

            await module.initialize();
            await module.render();

            const callbacks = global.window.createDataProductsV2Page.mock.calls[0][2];
            const onRefresh = callbacks.onRefresh;

            // ACT: Successful refresh
            await onRefresh();

            // ASSERT: MessageToast (non-blocking, auto-dismiss)
            expect(messageToastShowSpy).toHaveBeenCalledWith('Data products refreshed successfully');
            
            // ASSERT: No MessageBox for success (would be intrusive)
            expect(messageBoxErrorSpy).not.toHaveBeenCalled();
        });
    });
});