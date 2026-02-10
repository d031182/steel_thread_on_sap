/**
 * Unit Tests for App v2 Core Infrastructure
 * 
 * Tests:
 * - DependencyContainer (DI system)
 * - EventBus (Pub/Sub system)
 * - ILogger interface + NoOpLogger
 * - IDataSource interface + MockDataSource
 * - ICache interface
 * 
 * Coverage Target: 100% (Gu Wu standard)
 * Pattern: AAA (Arrange, Act, Assert)
 */

describe('App v2 Core Infrastructure', () => {
    
    // ==================== DependencyContainer Tests ====================
    
    describe('DependencyContainer', () => {
        
        beforeEach(() => {
            // Clear container before each test
            DependencyContainer.clear();
        });
        
        afterEach(() => {
            // Clean up after each test
            DependencyContainer.clear();
        });
        
        describe('register()', () => {
            it('should register a service with factory function', () => {
                // ARRANGE
                const factory = () => ({ name: 'TestService' });
                
                // ACT
                DependencyContainer.register('TestService', factory);
                
                // ASSERT
                expect(DependencyContainer.has('TestService')).toBe(true);
            });
            
            it('should throw error if name is not a string', () => {
                // ARRANGE
                const factory = () => ({});
                
                // ACT & ASSERT
                expect(() => {
                    DependencyContainer.register(null, factory);
                }).toThrow('Service name must be a non-empty string');
            });
            
            it('should throw error if factory is not a function', () => {
                // ACT & ASSERT
                expect(() => {
                    DependencyContainer.register('TestService', 'not a function');
                }).toThrow('Factory must be a function');
            });
            
            it('should allow re-registration (replaces factory)', () => {
                // ARRANGE
                DependencyContainer.register('TestService', () => ({ version: 1 }));
                
                // ACT
                DependencyContainer.register('TestService', () => ({ version: 2 }));
                const instance = DependencyContainer.get('TestService');
                
                // ASSERT
                expect(instance.version).toBe(2);
            });
        });
        
        describe('get()', () => {
            it('should return service instance (lazy instantiation)', () => {
                // ARRANGE
                let factoryCalled = false;
                DependencyContainer.register('TestService', () => {
                    factoryCalled = true;
                    return { name: 'Test' };
                });
                
                // ACT
                const instance = DependencyContainer.get('TestService');
                
                // ASSERT
                expect(factoryCalled).toBe(true);
                expect(instance.name).toBe('Test');
            });
            
            it('should return same instance on multiple calls (singleton)', () => {
                // ARRANGE
                let callCount = 0;
                DependencyContainer.register('TestService', () => {
                    callCount++;
                    return { id: callCount };
                });
                
                // ACT
                const instance1 = DependencyContainer.get('TestService');
                const instance2 = DependencyContainer.get('TestService');
                
                // ASSERT
                expect(instance1).toBe(instance2);  // Same reference
                expect(callCount).toBe(1);  // Factory called only once
            });
            
            it('should throw error if service not registered', () => {
                // ACT & ASSERT
                expect(() => {
                    DependencyContainer.get('NonExistentService');
                }).toThrow("Service 'NonExistentService' not registered");
            });
        });
        
        describe('has()', () => {
            it('should return true if service registered', () => {
                // ARRANGE
                DependencyContainer.register('TestService', () => ({}));
                
                // ACT
                const exists = DependencyContainer.has('TestService');
                
                // ASSERT
                expect(exists).toBe(true);
            });
            
            it('should return false if service not registered', () => {
                // ACT
                const exists = DependencyContainer.has('NonExistentService');
                
                // ASSERT
                expect(exists).toBe(false);
            });
        });
        
        describe('getRegisteredServices()', () => {
            it('should return array of registered service names', () => {
                // ARRANGE
                DependencyContainer.register('Service1', () => ({}));
                DependencyContainer.register('Service2', () => ({}));
                
                // ACT
                const services = DependencyContainer.getRegisteredServices();
                
                // ASSERT
                expect(services).toEqual(['Service1', 'Service2']);
            });
            
            it('should return empty array if no services', () => {
                // ACT
                const services = DependencyContainer.getRegisteredServices();
                
                // ASSERT
                expect(services).toEqual([]);
            });
        });
        
        describe('unregister()', () => {
            it('should remove service and return true', () => {
                // ARRANGE
                DependencyContainer.register('TestService', () => ({}));
                
                // ACT
                const removed = DependencyContainer.unregister('TestService');
                
                // ASSERT
                expect(removed).toBe(true);
                expect(DependencyContainer.has('TestService')).toBe(false);
            });
            
            it('should return false if service was not registered', () => {
                // ACT
                const removed = DependencyContainer.unregister('NonExistent');
                
                // ASSERT
                expect(removed).toBe(false);
            });
        });
        
        describe('clear()', () => {
            it('should remove all registrations', () => {
                // ARRANGE
                DependencyContainer.register('Service1', () => ({}));
                DependencyContainer.register('Service2', () => ({}));
                
                // ACT
                DependencyContainer.clear();
                
                // ASSERT
                expect(DependencyContainer.getRegisteredServices()).toEqual([]);
            });
        });
    });
    
    // ==================== EventBus Tests ====================
    
    describe('EventBus', () => {
        
        beforeEach(() => {
            // Clear event bus before each test
            EventBus.clear();
        });
        
        afterEach(() => {
            // Clean up after each test
            EventBus.clear();
        });
        
        describe('subscribe()', () => {
            it('should subscribe to an event', () => {
                // ARRANGE
                let called = false;
                const callback = () => { called = true; };
                
                // ACT
                EventBus.subscribe('test:event', callback);
                EventBus.publish('test:event');
                
                // ASSERT
                expect(called).toBe(true);
            });
            
            it('should return unsubscribe function', () => {
                // ARRANGE
                let callCount = 0;
                const callback = () => { callCount++; };
                
                // ACT
                const unsubscribe = EventBus.subscribe('test:event', callback);
                EventBus.publish('test:event');  // Should call
                unsubscribe();
                EventBus.publish('test:event');  // Should NOT call
                
                // ASSERT
                expect(callCount).toBe(1);
            });
            
            it('should allow multiple subscribers to same event', () => {
                // ARRANGE
                let count1 = 0, count2 = 0;
                
                // ACT
                EventBus.subscribe('test:event', () => { count1++; });
                EventBus.subscribe('test:event', () => { count2++; });
                EventBus.publish('test:event');
                
                // ASSERT
                expect(count1).toBe(1);
                expect(count2).toBe(1);
            });
            
            it('should throw error if event name invalid', () => {
                // ACT & ASSERT
                expect(() => {
                    EventBus.subscribe(null, () => {});
                }).toThrow('Event name must be a non-empty string');
            });
            
            it('should throw error if callback invalid', () => {
                // ACT & ASSERT
                expect(() => {
                    EventBus.subscribe('test:event', 'not a function');
                }).toThrow('Callback must be a function');
            });
        });
        
        describe('publish()', () => {
            it('should publish event with data payload', () => {
                // ARRANGE
                let receivedData = null;
                EventBus.subscribe('test:event', (data) => {
                    receivedData = data;
                });
                
                // ACT
                EventBus.publish('test:event', { message: 'Hello' });
                
                // ASSERT
                expect(receivedData).toEqual({ message: 'Hello' });
            });
            
            it('should return number of subscribers notified', () => {
                // ARRANGE
                EventBus.subscribe('test:event', () => {});
                EventBus.subscribe('test:event', () => {});
                
                // ACT
                const count = EventBus.publish('test:event');
                
                // ASSERT
                expect(count).toBe(2);
            });
            
            it('should return 0 if no subscribers', () => {
                // ACT
                const count = EventBus.publish('test:event');
                
                // ASSERT
                expect(count).toBe(0);
            });
            
            it('should handle subscriber errors gracefully', () => {
                // ARRANGE
                const consoleError = jest.spyOn(console, 'error').mockImplementation();
                EventBus.subscribe('test:event', () => {
                    throw new Error('Subscriber error');
                });
                
                // ACT
                const count = EventBus.publish('test:event');
                
                // ASSERT
                expect(count).toBe(1);  // Still counts as notified
                expect(consoleError).toHaveBeenCalled();
                
                // Cleanup
                consoleError.mockRestore();
            });
        });
        
        describe('getSubscriberCount()', () => {
            it('should return count of subscribers', () => {
                // ARRANGE
                EventBus.subscribe('test:event', () => {});
                EventBus.subscribe('test:event', () => {});
                
                // ACT
                const count = EventBus.getSubscriberCount('test:event');
                
                // ASSERT
                expect(count).toBe(2);
            });
            
            it('should return 0 if no subscribers', () => {
                // ACT
                const count = EventBus.getSubscriberCount('test:event');
                
                // ASSERT
                expect(count).toBe(0);
            });
        });
        
        describe('hasSubscribers()', () => {
            it('should return true if event has subscribers', () => {
                // ARRANGE
                EventBus.subscribe('test:event', () => {});
                
                // ACT
                const has = EventBus.hasSubscribers('test:event');
                
                // ASSERT
                expect(has).toBe(true);
            });
            
            it('should return false if no subscribers', () => {
                // ACT
                const has = EventBus.hasSubscribers('test:event');
                
                // ASSERT
                expect(has).toBe(false);
            });
        });
        
        describe('getHistory()', () => {
            it('should return recent event history', () => {
                // ARRANGE
                EventBus.publish('test:event1', { data: 1 });
                EventBus.publish('test:event2', { data: 2 });
                
                // ACT
                const history = EventBus.getHistory(10);
                
                // ASSERT
                expect(history.length).toBe(2);
                expect(history[0].eventName).toBe('test:event1');
                expect(history[1].eventName).toBe('test:event2');
            });
        });
    });
    
    // ==================== NoOpLogger Tests ====================
    
    describe('NoOpLogger', () => {
        
        it('should implement ILogger interface', () => {
            // ARRANGE
            const logger = new NoOpLogger();
            
            // ACT & ASSERT
            expect(logger).toBeInstanceOf(ILogger);
            expect(typeof logger.log).toBe('function');
            expect(typeof logger.showUI).toBe('function');
            expect(typeof logger.getRecentLogs).toBe('function');
        });
        
        it('should log silently by default', () => {
            // ARRANGE
            const consoleDebug = jest.spyOn(console, 'debug').mockImplementation();
            const logger = new NoOpLogger(false);  // logToConsole = false
            
            // ACT
            logger.log('Test message', 'INFO');
            
            // ASSERT
            expect(consoleDebug).not.toHaveBeenCalled();
            
            // Cleanup
            consoleDebug.mockRestore();
        });
        
        it('should log to console if logToConsole=true', () => {
            // ARRANGE
            const consoleDebug = jest.spyOn(console, 'debug').mockImplementation();
            const logger = new NoOpLogger(true);  // logToConsole = true
            
            // ACT
            logger.log('Test message', 'INFO');
            
            // ASSERT
            expect(consoleDebug).toHaveBeenCalled();
            
            // Cleanup
            consoleDebug.mockRestore();
        });
        
        it('should handle showUI() safely (no-op)', () => {
            // ARRANGE
            const logger = new NoOpLogger();
            
            // ACT & ASSERT (should not throw)
            expect(() => logger.showUI()).not.toThrow();
        });
        
        it('should return empty array from getRecentLogs()', async () => {
            // ARRANGE
            const logger = new NoOpLogger();
            
            // ACT
            const logs = await logger.getRecentLogs();
            
            // ASSERT
            expect(logs).toEqual([]);
        });
    });
    
    // ==================== MockDataSource Tests ====================
    
    describe('MockDataSource', () => {
        
        it('should implement IDataSource interface', () => {
            // ARRANGE
            const dataSource = new MockDataSource();
            
            // ACT & ASSERT
            expect(dataSource).toBeInstanceOf(IDataSource);
            expect(typeof dataSource.query).toBe('function');
            expect(typeof dataSource.getTables).toBe('function');
            expect(typeof dataSource.getTableSchema).toBe('function');
            expect(typeof dataSource.getType).toBe('function');
            expect(typeof dataSource.testConnection).toBe('function');
        });
        
        it('should return mock table list', async () => {
            // ARRANGE
            const dataSource = new MockDataSource();
            
            // ACT
            const tables = await dataSource.getTables();
            
            // ASSERT
            expect(tables).toContain('Supplier');
            expect(tables).toContain('PurchaseOrder');
            expect(tables).toContain('Invoice');
        });
        
        it('should return mock schema for known table', async () => {
            // ARRANGE
            const dataSource = new MockDataSource();
            
            // ACT
            const schema = await dataSource.getTableSchema('Supplier');
            
            // ASSERT
            expect(schema.columns).toContain('ID');
            expect(schema.columns).toContain('Name');
            expect(schema.types).toContain('TEXT');
        });
        
        it('should return generic schema for unknown table', async () => {
            // ARRANGE
            const dataSource = new MockDataSource();
            
            // ACT
            const schema = await dataSource.getTableSchema('UnknownTable');
            
            // ASSERT
            expect(schema.columns).toEqual(['ID', 'Name']);
            expect(schema.types).toEqual(['TEXT', 'TEXT']);
        });
        
        it('should return empty results from query()', async () => {
            // ARRANGE
            const dataSource = new MockDataSource();
            
            // ACT
            const results = await dataSource.query('SELECT * FROM Supplier');
            
            // ASSERT
            expect(results).toEqual([]);
        });
        
        it('should return "mock" as type', () => {
            // ARRANGE
            const dataSource = new MockDataSource();
            
            // ACT
            const type = dataSource.getType();
            
            // ASSERT
            expect(type).toBe('mock');
        });
        
        it('should always pass testConnection()', async () => {
            // ARRANGE
            const dataSource = new MockDataSource();
            
            // ACT
            const isHealthy = await dataSource.testConnection();
            
            // ASSERT
            expect(isHealthy).toBe(true);
        });
    });
});