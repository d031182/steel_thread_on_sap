# GoF Design Patterns - Practical Guide

**Version**: 1.0  
**Last Updated**: 2026-02-03  
**Source**: Logica GoF Catalogue (Java/UML2 Examples)

## Overview

The Gang of Four (GoF) Design Patterns provide 23 fundamental patterns for solving recurring software design problems. This guide focuses on **WHEN** and **WHY** to apply each pattern, not just HOW to implement them.

### Key Principle
> Patterns describe design approaches for specific situations. Apply thoughtfully based on actual need, not just because a pattern exists.

## Pattern Categories

### 1. Creational Patterns (Object Creation)
Control HOW objects are created to improve flexibility and reuse.

### 2. Structural Patterns (Object Composition)
Define HOW objects and classes combine to form larger structures.

### 3. Behavioral Patterns (Object Communication)
Define HOW objects communicate while maintaining loose coupling.

---

## Creational Patterns

### Factory Pattern

**WHEN TO USE:**
- Class can't anticipate which object type to create
- Want to localize knowledge of which class gets created
- Classes share same interface and can be used interchangeably
- Want to insulate client from instantiation type

**WHY IT HELPS:**
- Decouples client from concrete class instantiation
- Encapsulates complex creation logic
- Client only needs abstract class reference

**PROJECT APPLICATIONS:**
- ✅ Data source creation (HANA vs SQLite)
- ✅ API response format selection
- 💡 Module instantiation based on configuration

**DRAWBACK:** Cannot change implementing class without recompile

**REAL WORLD:** `java.sql.Connection` - returns database-specific Statement implementations

---

### Abstract Factory Pattern

**WHEN TO USE:**
- Need to create sets of objects sharing common theme
- Objects could be added/changed during application lifetime
- Want to interchange object sets at runtime

**WHY IT HELPS:**
- Separate implementation from usage
- Interchange concrete classes without code changes (even at runtime)
- Manage themed object families

**PROJECT APPLICATIONS:**
- 💡 Data product creation (different vendors/systems)
- 💡 UI theme switching
- 💡 Test vs production object families

**DRAWBACK:** Unnecessary complexity in initial coding

**KEY DIFFERENCE:** Factory returns one object, Abstract Factory returns families of related objects

---

### Builder Pattern

**WHEN TO USE:**
- Construction algorithm independent of object parts
- Construction allows different representations
- Want to insulate clients from construction details
- Building complex aggregate objects

**WHY IT HELPS:**
- Shield construction details from representation
- Control construction process step-by-step
- Reuse/change process and product independently

**PROJECT APPLICATIONS:**
- 💡 Complex query building
- 💡 Report generation
- 💡 Data product schema construction
- 💡 P2P workflow construction

**RELATED PATTERNS:** Abstract Factory (similar but Builder focuses on step-by-step)

---

### Prototype Pattern

**WHEN TO USE:**
- Instantiation of large/dynamically loaded classes is expensive
- System independent of object creation
- Adding/removing objects at runtime
- State population is expensive/exclusive process

**WHY IT HELPS:**
- Speeds up instantiation
- Reduces subclassing
- Avoids expensive state population

**PROJECT APPLICATIONS:**
- 💡 Cloning data product schemas
- 💡 Graph node templates
- 💡 Expensive P2P document structures with cached data

**DRAWBACK:** Each subclass must implement Clone; difficult with circular references

---

### Singleton Pattern ⚠️

**WHEN TO USE:**
- Only one instance or specific number allowed
- Need controlled access to unique instance
- Often used for Facade objects

**WHY IT HELPS:**
- Controlled access to unique instance
- Reduced namespace
- Allows refinement of operations

**⚠️ ANTIPATTERN WARNING:**
Often overused! Introduces unnecessary limitations when sole instance not actually required. Verify singleton is truly needed before applying.

**PROJECT APPLICATIONS:**
- ✅ Currently used: Connection managers, configuration, logging
- ⚠️ Audit needed: Verify each singleton is necessary

**USER PREFERENCE:** Avoid overuse, ensure singleton is necessary

---

## Structural Patterns

### Adapter Pattern (Wrapper)

**WHEN TO USE:**
- Want to use existing class but interface doesn't match
- Create reusable class cooperating with unrelated classes
- Increase transparency
- Create pluggable kit

**WHY IT HELPS:**
- High class reusability
- Makes incompatible classes work together
- Introduces only one object

**PROJECT APPLICATIONS:**
- ✅ Currently used: `hana_data_source.py` and `sqlite_data_source.py` adapting to DataSource interface
- ✅ Perfect example of object adapter approach (aggregation over inheritance)

**TYPES:**
- Class adapter (uses inheritance)
- Object adapter (uses aggregation) ← **Project uses this**

---

### Bridge Pattern

**WHEN TO USE:**
- Want to switch implementation at runtime
- Independently extend abstraction and implementation
- Separate abstract structure from concrete implementation
- Hide implementation details from clients

**WHY IT HELPS:**
- Implementation selectable/switchable at runtime
- Abstraction and implementation independently extended
- Clear separation of concerns

**PROJECT APPLICATIONS:**
- ✅ Currently used: `graph_query_service.py` bridges abstraction (GraphQueryService) from implementations (HANAGraphQueryEngine, NetworkXGraphQueryEngine)
- ✅ Data source abstraction (HANA vs SQLite)

**DRAWBACK:** Double indirection impacts performance slightly

---

### Composite Pattern

**WHEN TO USE:**
- Represent part-whole hierarchy in tree structure
- Clients treat compositions and individuals uniformly
- Dynamic any-level complexity structure

**WHY IT HELPS:**
- Define primitive and composite hierarchies
- Easy to add new components
- Uniform treatment of individual and composite objects

**PROJECT APPLICATIONS:**
- 💡 Module hierarchy
- 💡 Data product composition
- 💡 Graph node structures

**KEY INTERFACE:** Component defines operations for both leaf and composite nodes

---

### Decorator Pattern

**WHEN TO USE:**
- Add responsibilities dynamically and transparently
- Responsibilities might change in future
- Static subclassing impractical
- Avoid feature-laden classes high in hierarchy

**WHY IT HELPS:**
- More flexible than inheritance
- Simplifies coding (series of targeted classes)
- Enhances extensibility
- Avoids high-hierarchy feature-laden classes

**PROJECT APPLICATIONS:**
- 💡 Logging (add formatting/encryption dynamically)
- 💡 API responses (add caching/validation)
- 💡 Data transformation pipelines

**PATTERN CHAIN:** Can stack multiple decorators (HTMLLogger wrapping EncryptLogger wrapping FileLogger)

**DRAWBACK:** Keep component interface simple; performance overhead with long chains

---

### Facade Pattern

**WHEN TO USE:**
- Make software library easier to use/understand
- Reduce outside code dependencies on inner workings
- Wrap poorly-designed APIs with clean interface
- Allow flexibility in system development

**WHY IT HELPS:**
- Simplifies complex method calls
- Reduces code dependencies
- Weak coupling allows varying components

**PROJECT APPLICATIONS:**
- 💡 P2P workflow orchestration
- 💡 Complex graph operations facade
- 💡 Module initialization facade

**OFTEN SINGLETON:** Facade objects often implemented as Singletons (only one needed)

**DRAWBACK:** Less control beyond surface; variations can create mess

---

### Flyweight Pattern

**WHEN TO USE:**
- Very large number of objects won't fit in memory
- Most state can be stored on disk or calculated at runtime
- Groups of objects share state
- Performance/memory optimization needed

**WHY IT HELPS:**
- Reduce object count
- Decrease memory usage
- Improve performance

**PROJECT APPLICATIONS:**
- 💡 Graph node rendering (thousands of nodes sharing appearance)
- 💡 Repeated UI components
- 💡 Cached data product schemas

**KEY TECHNIQUE:** FlyweightFactory maintains pool; clients supply extrinsic state per use

---

### Proxy Pattern

**WHEN TO USE:**
- Object creation is relatively expensive
- Need login/authority checking before access
- Need local representation for remote object
- Want to control access to object

**WHY IT HELPS:**
- Control access considering cost and security
- Lazy instantiation
- Access control layer

**PROJECT APPLICATIONS:**
- 💡 Database connection pooling
- 💡 Lazy loading of data products
- 💡 Caching layer for graph queries

**TYPES:**
- Virtual proxy (lazy instantiation)
- Protection proxy (access control)
- Remote proxy (local representation)

---

## Behavioral Patterns

### Chain of Responsibility Pattern

**WHEN TO USE:**
- More than one object may handle request
- Handler is unknown a priori
- Set of handlers specified dynamically
- Want to avoid coupling sender to receiver

**WHY IT HELPS:**
- Reduces coupling
- Increases handling flexibility
- Dynamic handler configuration

**PROJECT APPLICATIONS:**
- 💡 Validation pipeline
- 💡 Error handling hierarchy
- 💡 Request processing middleware

**DRAWBACK:** Reception not guaranteed unless chain configured properly

---

### Command Pattern

**WHEN TO USE:**
- Action represented many ways (menu, button, popup)
- Need undo/redo functionality
- Want to separate action from representation
- Need to queue/log operations

**WHY IT HELPS:**
- Storage for procedure parameters
- Delayed execution
- Undo-able operations
- Action history tracking

**PROJECT APPLICATIONS:**
- 💡 API operation history
- 💡 Workflow step commands
- 💡 User action tracking with undo/redo

**KEY TECHNIQUE:** Command interface with execute() method; commands stored for undo/redo

---

### Iterator Pattern

**WHEN TO USE:**
- Access aggregate elements sequentially
- Need different traversal types
- Want to encapsulate internal structure
- Avoid bloating aggregate class with traversals

**WHY IT HELPS:**
- Same iterator for different aggregates
- Encapsulates iteration logic
- No bloat in aggregate class

**PROJECT APPLICATIONS:**
- ✅ Currently used: Throughout Python code (for loops use iterators)
- 💡 Custom iterators for graph traversal algorithms

**DRAWBACK:** Not thread safe unless robust iterator (can use Memento pattern to capture state)

---

### Mediator Pattern

**WHEN TO USE:**
- Complex unstructured interdependencies
- Difficult to reuse objects (many references)
- Customize spread-out behavior without subclassing
- Well-specified but complex communication patterns

**WHY IT HELPS:**
- Limited subclassing
- Decoupled colleagues
- Simplified protocols (many-to-many → one-to-many)
- Centralized control

**PROJECT APPLICATIONS:**
- 💡 Module coordination
- 💡 UI component state management
- 💡 Workflow step coordination

**DRAWBACK:** Mediator can become complex monolith; performance bottleneck

**USE CASES:** List servers, chat rooms, GUI widget groups

---

### Memento Pattern

**WHEN TO USE:**
- Need to save/restore object state
- Create state snapshots
- Implement undo/redo features
- Capture state without violating encapsulation

**WHY IT HELPS:**
- Restore object to previous state
- State snapshots for rollback

**PROJECT APPLICATIONS:**
- 💡 Undo/redo in graph editing
- 💡 Transaction rollback
- 💡 Configuration snapshots

**DRAWBACK:** Expensive if storing large amounts of data; operates on single object

**KEY ROLES:**
- Originator (creates/restores from memento)
- Caretaker (manages mementos)
- Memento (stores state snapshot)

---

### Observer Pattern (Publish/Subscribe)

**WHEN TO USE:**
- Object wants to publish information
- Many objects need to receive information
- Want loose coupling between publisher and subscribers

**WHY IT HELPS:**
- Loose coupling (publisher doesn't know who/how many subscribers)
- Dynamic subscription management
- Event-driven architecture

**PROJECT APPLICATIONS:**
- 💡 Data change notifications
- 💡 Event system
- 💡 Reactive UI updates
- 💡 May already be used in frontend state management

**DRAWBACK:** Complex scenarios - hard to determine update relevance; communication overhead

**KEY INTERFACE:**
- Observer: update() method
- Subject: attach()/detach()/notify()

---

### State Pattern

**WHEN TO USE:**
- Define context class presenting single interface
- Represent different states as derived classes
- State machine implementation
- Object behavior changes based on state

**WHY IT HELPS:**
- Cleaner code (class per state vs constants)
- Eliminates long conditional statements
- Partial type change at runtime

**PROJECT APPLICATIONS:**
- 💡 Workflow state management (draft → submitted → approved)
- 💡 Connection state (connected/disconnected/reconnecting)
- 💡 UI mode switching (view/edit modes)

**DRAWBACK:** Generates many small class objects (but simplifies program)

**RELATED TO:** Strategy pattern (State focuses on state-dependent behavior)

---

### Strategy Pattern

**WHEN TO USE:**
- Need to use algorithms dynamically
- Configure class with one of many behaviors
- Hide algorithmic data from client
- Avoid multiple conditional statements

**WHY IT HELPS:**
- Reduces conditional statements
- Hides complex data
- Alternative to subclassing
- Algorithm varies independently

**PROJECT APPLICATIONS:**
- 💡 Query optimization strategies
- 💡 Data export formats (CSV, JSON, XML)
- 💡 Validation strategies
- ✅ Potentially used: Graph query engine selection (HANA vs NetworkX)

**DRAWBACK:** Clients must be aware of different strategies

**RELATED TO:** State pattern (Strategy focuses on algorithm selection)

---

## Pattern Relationships

### Pattern Combinations That Work Well

1. **Singleton + Facade**: Facade objects often implemented as Singletons
2. **Builder + Composite**: Builder often builds Composite structures
3. **Command + Memento**: Enables undo/redo functionality
4. **Iterator + Memento**: Captures iteration state for robust iterators
5. **Decorator + Composite**: Both use recursive composition
6. **Bridge + Strategy**: Similar separation of abstraction from implementation

### Pattern Alternatives

1. **Builder vs Abstract Factory**: Both create complex objects, Builder focuses on step-by-step construction
2. **Decorator vs Strategy**: Decorator changes object skin, Strategy changes object guts
3. **State vs Strategy**: State is Strategy with state-dependent behavior

---

## Project-Specific Pattern Usage

### Currently Applied ✅

1. **Adapter**: Data source abstraction (HANA/SQLite)
2. **Bridge**: Graph query service abstraction
3. **Singleton**: Connection managers, configuration (audit needed)
4. **Iterator**: Throughout Python codebase
5. **Strategy**: Potentially in graph query engine selection

### Recommended Applications 💡

1. **Factory**: Module instantiation, data source creation
2. **Builder**: Complex query building, P2P workflow construction
3. **Decorator**: Logging enhancements, API response transformations
4. **Facade**: P2P workflow orchestration, module initialization
5. **Observer**: Event system, reactive UI updates
6. **State**: Workflow state management, connection state handling
7. **Command**: API operation history with undo/redo

### Anti-Pattern Warnings ⚠️

1. **Singleton Overuse**: Verify each singleton is truly necessary
2. **Mediator Complexity**: Can become bottleneck if too centralized
3. **Decorator Chains**: Performance impact with long chains
4. **Flyweight Overhead**: Only use when massive object quantities justify complexity

---

## Decision Framework

### When Considering a Pattern, Ask:

1. **WHAT problem am I solving?** (Not "which pattern can I use?")
2. **WHY is this problem occurring?** (Root cause, not symptom)
3. **WHEN would this pattern help?** (Check "When to Use" section)
4. **WHO benefits?** (Does it simplify client code or just move complexity?)
5. **HOW does it align with project standards?** (Modular architecture, DI, etc.)

### Red Flags (Don't Use Pattern If):

- ❌ Only reason is "it's a best practice"
- ❌ Problem doesn't match pattern's intended use case
- ❌ Simpler solution already exists
- ❌ Adds unnecessary complexity for current needs
- ❌ Conflicts with project's established patterns

---

## References

- **Primary Source**: Logica GoF Catalogue (Java/UML2 Examples)
- **Original**: Design Patterns: Elements of Reusable Object-Oriented Software by Gamma, Helm, Johnson, Vlissides (1995)
- **Project Context**: Steel Thread P2P Application
- **Knowledge Graph**: All patterns stored in memory with relationships and project-specific observations

## Related Documents

- [[Modular Architecture]] - Project's module pattern
- [[Data Abstraction Layers]] - Adapter and Bridge patterns in use
- [[Knowledge Graph DI Refactoring]] - Dependency Injection patterns
- [[Graph Query API Abstraction]] - Bridge and Strategy patterns

---

**Remember**: Patterns are tools, not goals. Apply based on actual need, not theoretical elegance.