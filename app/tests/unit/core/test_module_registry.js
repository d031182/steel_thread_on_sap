/**
 * Unit Tests for ModuleRegistry
 * 
 * Tests module registration, retrieval, and lifecycle management
 * 
 * Coverage Target: 100% (Gu Wu standard)
 * Pattern: AAA (Arrange, Act, Assert)
 */

describe('ModuleRegistry', () => {
    
    beforeEach(() => {
        // Clear registry before each test
        ModuleRegistry.clear();
    });
    
    afterEach(() => {
        // Clean up after each test
        ModuleRegistry.clear();
    });
    
    describe('register()', () => {
        it('should register a module with metadata', () => {
            // ARRANGE
            const module = {
                id: 'test-module',
                name: 'Test Module',
                version: '1.0.0',
                factory: () => ({ render: () => {} })
            };
            
            // ACT
            ModuleRegistry.register(module);
            
            // ASSERT
            expect(ModuleRegistry.has('test-module')).toBe(true);
        });
        
        it('should throw error if module ID missing', () => {
            // ARRANGE
            const module = {
                name: 'Test Module',
                factory: () => ({})
            };
            
            // ACT & ASSERT
            expect(() => {
                ModuleRegistry.register(module);
            }).toThrow('Module ID is required');
        });
        
        it('should throw error if module factory missing', () => {
            // ARRANGE
            const module = {
                id: 'test-module',
                name: 'Test Module'
            };
            
            // ACT & ASSERT
            expect(() => {
                ModuleRegistry.register(module);
            }).toThrow('Module factory function is required');
        });
        
        it('should throw error if module factory not a function', () => {
            // ARRANGE
            const module = {
                id: 'test-module',
                name: 'Test Module',
                factory: 'not a function'
            };
            
            // ACT & ASSERT
            expect(() => {
                ModuleRegistry.register(module);
            }).toThrow('Module factory must be a function');
        });
        
        it('should allow re-registration (replaces module)', () => {
            // ARRANGE
            const module1 = {
                id: 'test-module',
                name: 'Test Module',
                version: '1.0.0',
                factory: () => ({ version: 1 })
            };
            const module2 = {
                id: 'test-module',
                name: 'Test Module Updated',
                version: '2.0.0',
                factory: () => ({ version: 2 })
            };
            
            // ACT
            ModuleRegistry.register(module1);
            ModuleRegistry.register(module2);
            const metadata = ModuleRegistry.get('test-module');
            
            // ASSERT
            expect(metadata.name).toBe('Test Module Updated');
            expect(metadata.version).toBe('2.0.0');
        });
    });
    
    describe('get()', () => {
        it('should return module metadata', () => {
            // ARRANGE
            const module = {
                id: 'test-module',
                name: 'Test Module',
                version: '1.0.0',
                factory: () => ({})
            };
            ModuleRegistry.register(module);
            
            // ACT
            const metadata = ModuleRegistry.get('test-module');
            
            // ASSERT
            expect(metadata.id).toBe('test-module');
            expect(metadata.name).toBe('Test Module');
            expect(metadata.version).toBe('1.0.0');
        });
        
        it('should throw error if module not found', () => {
            // ACT & ASSERT
            expect(() => {
                ModuleRegistry.get('non-existent');
            }).toThrow("Module 'non-existent' not found in registry");
        });
    });
    
    describe('has()', () => {
        it('should return true if module exists', () => {
            // ARRANGE
            const module = {
                id: 'test-module',
                name: 'Test Module',
                factory: () => ({})
            };
            ModuleRegistry.register(module);
            
            // ACT
            const exists = ModuleRegistry.has('test-module');
            
            // ASSERT
            expect(exists).toBe(true);
        });
        
        it('should return false if module does not exist', () => {
            // ACT
            const exists = ModuleRegistry.has('non-existent');
            
            // ASSERT
            expect(exists).toBe(false);
        });
    });
    
    describe('getAll()', () => {
        it('should return all registered modules', () => {
            // ARRANGE
            ModuleRegistry.register({
                id: 'module1',
                name: 'Module 1',
                factory: () => ({})
            });
            ModuleRegistry.register({
                id: 'module2',
                name: 'Module 2',
                factory: () => ({})
            });
            
            // ACT
            const modules = ModuleRegistry.getAll();
            
            // ASSERT
            expect(modules.length).toBe(2);
            expect(modules.find(m => m.id === 'module1')).toBeDefined();
            expect(modules.find(m => m.id === 'module2')).toBeDefined();
        });
        
        it('should return empty array if no modules', () => {
            // ACT
            const modules = ModuleRegistry.getAll();
            
            // ASSERT
            expect(modules).toEqual([]);
        });
    });
    
    describe('getAllIds()', () => {
        it('should return array of module IDs', () => {
            // ARRANGE
            ModuleRegistry.register({
                id: 'module1',
                name: 'Module 1',
                factory: () => ({})
            });
            ModuleRegistry.register({
                id: 'module2',
                name: 'Module 2',
                factory: () => ({})
            });
            
            // ACT
            const ids = ModuleRegistry.getAllIds();
            
            // ASSERT
            expect(ids).toEqual(['module1', 'module2']);
        });
        
        it('should return empty array if no modules', () => {
            // ACT
            const ids = ModuleRegistry.getAllIds();
            
            // ASSERT
            expect(ids).toEqual([]);
        });
    });
    
    describe('unregister()', () => {
        it('should remove module and return true', () => {
            // ARRANGE
            ModuleRegistry.register({
                id: 'test-module',
                name: 'Test Module',
                factory: () => ({})
            });
            
            // ACT
            const removed = ModuleRegistry.unregister('test-module');
            
            // ASSERT
            expect(removed).toBe(true);
            expect(ModuleRegistry.has('test-module')).toBe(false);
        });
        
        it('should return false if module not found', () => {
            // ACT
            const removed = ModuleRegistry.unregister('non-existent');
            
            // ASSERT
            expect(removed).toBe(false);
        });
    });
    
    describe('clear()', () => {
        it('should remove all modules', () => {
            // ARRANGE
            ModuleRegistry.register({
                id: 'module1',
                name: 'Module 1',
                factory: () => ({})
            });
            ModuleRegistry.register({
                id: 'module2',
                name: 'Module 2',
                factory: () => ({})
            });
            
            // ACT
            ModuleRegistry.clear();
            
            // ASSERT
            expect(ModuleRegistry.getAllIds()).toEqual([]);
        });
    });
    
    describe('createInstance()', () => {
        it('should create module instance using factory', () => {
            // ARRANGE
            const mockInstance = { render: () => 'rendered' };
            ModuleRegistry.register({
                id: 'test-module',
                name: 'Test Module',
                factory: (container) => {
                    expect(container).toBe(DependencyContainer);
                    return mockInstance;
                }
            });
            
            // ACT
            const instance = ModuleRegistry.createInstance('test-module');
            
            // ASSERT
            expect(instance).toBe(mockInstance);
        });
        
        it('should throw error if module not found', () => {
            // ACT & ASSERT
            expect(() => {
                ModuleRegistry.createInstance('non-existent');
            }).toThrow("Module 'non-existent' not found in registry");
        });
        
        it('should handle factory errors gracefully', () => {
            // ARRANGE
            ModuleRegistry.register({
                id: 'broken-module',
                name: 'Broken Module',
                factory: () => {
                    throw new Error('Factory error');
                }
            });
            
            // ACT & ASSERT
            expect(() => {
                ModuleRegistry.createInstance('broken-module');
            }).toThrow('Factory error');
        });
    });
});