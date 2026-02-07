# Pydantic AI Framework

**Version**: 1.0  
**Last Updated**: February 7, 2026  
**Purpose**: Comprehensive guide to Pydantic AI for building production-grade AI agents

---

## 📋 Table of Contents

1. [What is Pydantic AI?](#what-is-pydantic-ai)
2. [Core Value Proposition](#core-value-proposition)
3. [Key Capabilities](#key-capabilities)
4. [Agent Framework](#agent-framework)
5. [Tool System](#tool-system)
6. [Dependency Injection](#dependency-injection)
7. [Structured Outputs & Validation](#structured-outputs--validation)
8. [Integration with Groq](#integration-with-groq)
9. [Use Case Recommendations](#use-case-recommendations)
10. [Getting Started](#getting-started)
11. [Related Documentation](#related-documentation)

---

## 🎯 What is Pydantic AI?

### WHAT

**Pydantic AI** is a Python agent framework from the Pydantic team for building production-grade AI applications with **type safety**, **structured outputs**, and **robust validation**. It's a lightweight alternative to LangChain/LlamaIndex, focusing on simplicity and reliability.

### WHY Pydantic AI Exists

**Problems It Solves**:
1. **Type Safety**: LLM outputs are unpredictable - need compile-time validation
2. **Reliability**: Production AI needs structured, validated responses
3. **Complexity**: LangChain/LlamaIndex have steep learning curves
4. **Debugging**: Runtime errors difficult to trace in complex frameworks
5. **Production Gaps**: Frameworks great for prototyp, hard to productionize

**Pydantic AI's Solution**:
- **Type-First Design**: Full type hints, auto-completion, static checking
- **Validation Built-in**: Pydantic models validate LLM outputs automatically
- **Simple Architecture**: Like FastAPI for AI (minimal boilerplate)
- **Model-Agnostic**: Works with any LLM (OpenAI, Anthropic, **Groq**, Google)
- **Production-Ready**: Observability, streaming, error handling out-of-box

### WHEN to Choose Pydantic AI

✅ **Use Pydantic AI when you need**:
- Type-safe AI agent development (catch errors at dev-time)
- Structured outputs validated against schemas
- Simple, FastAPI-like API for agents
- Model-agnostic flexibility (switch providers easily)
- Production observability (Logfire, OpenTelemetry)
- Dependency injection for tools and context

❌ **Consider alternatives when**:
- You need pre-built chains (LangChain has more templates)
- You're already deep in LangChain ecosystem
- You need non-Python language support

---

## ⚡ Core Value Proposition

### The Pydantic AI Philosophy

**Problem**: Traditional LLM frameworks treat outputs as strings → runtime chaos

**Pydantic AI Approach**: Treat LLM outputs as **data structures** → compile-time safety

```python
# Traditional approach (runtime errors)
response = llm.chat("Get user info")
user_id = response.split(':')[1]  # ❌ What if format changes?

# Pydantic AI approach (type-safe)
class UserInfo(BaseModel):
    user_id: int
    name: str
    email: EmailStr

result = agent.run("Get user info", result_type=UserInfo)
print(result.data.user_id)  # ✅ Type-checked, validated
```

### Key Benefits

| Benefit | Description | Value |
|---------|-------------|-------|
| **Type Safety** | Full type hints, IDE auto-complete | Catch 80% of bugs at dev-time |
| **Validation** | Pydantic models validate LLM outputs | Zero invalid data in production |
| **Simplicity** | FastAPI-like API | 10x faster development |
| **Model-Agnostic** | Works with any LLM provider | Switch providers in 1 line |
| **Production-Ready** | Streaming, observability, retries | Deploy with confidence |

### Comparison: Pydantic AI vs Alternatives

| Feature | Pydantic AI | LangChain | LlamaIndex | Raw LLM API |
|---------|-------------|-----------|------------|-------------|
| **Type Safety** | ✅ Full | ⚠️ Partial | ⚠️ Partial | ❌ None |
| **Learning Curve** | 🟢 Low (FastAPI-like) | 🔴 High | 🟡 Medium | 🟢 Low |
| **Validation** | ✅ Automatic | ⚠️ Manual | ⚠️ Manual | ❌ None |
| **Model Agnostic** | ✅ Easy swap | ✅ Yes | ✅ Yes | ❌ Per-provider |
| **Production Tools** | ✅ Built-in | ⚠️ Add-ons | ⚠️ Add-ons | ❌ DIY |
| **Boilerplate** | 🟢 Minimal | 🔴 Heavy | 🟡 Moderate | 🟢 Minimal |

**When to use each**:
- **Pydantic AI**: Production apps, type safety critical, simple architecture
- **LangChain**: Prototyping, need pre-built chains, large ecosystem
- **LlamaIndex**: RAG-focused apps, document heavy
- **Raw API**: Extreme simplicity, no framework overhead

---

## 🔧 Key Capabilities

### 1. Type-Safe Agent Definition

**WHAT**: Define agents with full type hints

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# Agent with typed output
agent = Agent(
    'groq:llama-3.3-70b-versatile',  # Works with Groq!
    result_type=User,  # Type-safe output
    system_prompt="Extract user information"
)

# Run with validation
result = agent.run_sync("John Doe, john@example.com, ID: 123")
user: User = result.data  # Type-checked at compile time!
```

**WHY**: Catch errors during development, not production

### 2. Structured Outputs & Validation

**WHAT**: LLM outputs validated against Pydantic schemas

```python
from pydantic import BaseModel, Field, field_validator

class Invoice(BaseModel):
    invoice_id: str
    amount: float = Field(gt=0)  # Must be positive
    currency: str = Field(pattern=r'^[A-Z]{3}$')  # 3-letter code
    
    @field_validator('currency')
    def validate_currency(cls, v):
        if v not in ['USD', 'EUR', 'GBP']:
            raise ValueError(f'Unsupported currency: {v}')
        return v

# Agent automatically validates
agent = Agent('groq:llama-3.3-70b-versatile', result_type=Invoice)
result = agent.run_sync("Invoice INV-001 for $150.00")

# If LLM returns invalid data, Pydantic raises ValidationError
# Framework can auto-retry with error message to LLM!
```

**WHY**: Zero invalid data reaches your database

### 3. Model-Agnostic Support

**WHAT**: Switch LLM providers easily

```python
# Groq (fast, cheap)
agent = Agent('groq:llama-3.3-70b-versatile')

# OpenAI (reliable)
agent = Agent('openai:gpt-4')

# Anthropic (complex reasoning)
agent = Agent('anthropic:claude-3-opus')

# Fallback on error
agent = Agent(
    'groq:llama-3.3-70b-versatile',
    fallback_models=['openai:gpt-3.5-turbo']  # If Groq fails
)
```

**WHY**: Not locked into one provider, handle outages gracefully

### 4. Tools & Function Calling

**WHAT**: Give agents tools to execute actions

```python
from pydantic_ai import Agent, RunContext

agent = Agent('groq:llama-3.3-70b-versatile')

@agent.tool
def query_database(ctx: RunContext[str], supplier_id: int) -> dict:
    """Query P2P database for supplier information.
    
    Args:
        supplier_id: The unique supplier ID
    """
    # Access dependency-injected repository
    repo = ctx.deps
    return repo.get_supplier(supplier_id)

@agent.tool
def calculate_discount(amount: float, percent: float) -> float:
    """Calculate discount amount.
    
    Args:
        amount: Original amount
        percent: Discount percentage (0-100)
    """
    return amount * (percent / 100)

# LLM can now call these tools automatically!
result = agent.run_sync(
    "What's the discount on $100 with 15% off for supplier 42?",
    deps=supplier_repository  # Dependency injection!
)
```

**WHY**: Agents can access real data and perform actions

### 5. Streaming Support

**WHAT**: Real-time token streaming for better UX

```python
async with agent.run_stream("Tell me about supplier analytics") as result:
    async for message in result.stream_text():
        print(message, end='', flush=True)  # Real-time output
    
    final_data = await result.get_data()  # Validated result
```

**WHY**: Users see progress immediately (ChatGPT-like UX)

### 6. Dependency Injection

**WHAT**: Inject context into tools without exposing to LLM

```python
from dataclasses import dataclass

@dataclass
class AppContext:
    user_id: int
    repository: Repository
    logger: Logger

agent = Agent('groq:llama-3.3-70b-versatile')

@agent.tool
def get_user_orders(ctx: RunContext[AppContext]) -> list:
    """Get orders for current user."""
    # ctx.deps NOT passed to LLM schema
    user_id = ctx.deps.user_id
    return ctx.deps.repository.get_orders(user_id)

# Run with dependencies
result = agent.run_sync(
    "Show my recent orders",
    deps=AppContext(user_id=123, repository=repo, logger=log)
)
```

**WHY**: Clean separation - LLM sees tool signature, not implementation

### 7. Observability (Logfire)

**WHAT**: Built-in tracing, monitoring, cost tracking

```python
import logfire

# Configure Logfire (Pydantic's observability platform)
logfire.configure()

# Automatically logs:
# - Agent runs (timing, tokens, cost)
# - Tool calls (arguments, results)
# - Validation errors
# - Model retries

agent = Agent('groq:llama-3.3-70b-versatile')
result = agent.run_sync("Query data")

# View in Logfire dashboard:
# - Request/response traces
# - Token usage and costs
# - Error rates
# - Performance metrics
```

**WHY**: Debug production issues, optimize costs, track performance

---

## 🤖 Agent Framework

### Agent Architecture

```
User Query
    ↓
Agent (system prompt, result_type)
    ↓
[Dynamic Instructions] ← Dependencies
    ↓
LLM (via model provider)
    ↓
[Tool Calls] → Execute Tools → Results back to LLM
    ↓
[Validation] → Pydantic schema check
    ↓
[Retry if invalid] → Send error to LLM
    ↓
Validated Result
```

### Agent Lifecycle

**1. Define Agent**:
```python
agent = Agent(
    'groq:llama-3.3-70b-versatile',
    result_type=MyModel,
    system_prompt="You are a helpful assistant",
    retries=2  # Auto-retry on validation failure
)
```

**2. Register Tools**:
```python
@agent.tool
def my_tool(arg: str) -> str:
    """Tool description for LLM."""
    return process(arg)
```

**3. Run Agent**:
```python
# Sync
result = agent.run_sync("user query", deps=context)

# Async
result = await agent.run("user query", deps=context)

# Streaming
async with agent.run_stream("query") as result:
    async for chunk in result.stream_text():
        print(chunk)
```

### Dynamic Instructions

**WHAT**: Change system prompt based on runtime context

```python
@agent.system_prompt
def get_instructions(ctx: RunContext[AppContext]) -> str:
    user = ctx.deps.current_user
    if user.is_admin:
        return "You have admin privileges. Full data access."
    else:
        return f"Limited access for user {user.id}. Only show their data."

# Instructions adapt per user!
```

**WHY**: Personalize behavior without creating multiple agents

---

## 🛠️ Tool System

### Tool Types

#### 1. Function Tools (Most Common)

**WHAT**: Python functions the LLM can call

```python
@agent.tool
def search_suppliers(
    name: str,
    min_rating: float = 4.0
) -> list[dict]:
    """Search for suppliers by name and rating.
    
    Args:
        name: Supplier name (partial match)
        min_rating: Minimum rating (0-5)
    """
    return repository.search(name=name, min_rating=min_rating)

# LLM can call: search_suppliers(name="ACME", min_rating=4.5)
```

**Features**:
- Docstring → tool description
- Type hints → parameter schema
- Default values → optional parameters
- Pydantic validation → argument checking

#### 2. Toolsets

**WHAT**: Group related tools

```python
from pydantic_ai import FunctionToolset

supplier_tools = FunctionToolset(
    search_suppliers,
    get_supplier_rating,
    update_supplier_status
)

invoice_tools = FunctionToolset(
    create_invoice,
    get_invoice_status,
    mark_invoice_paid
)

# Use different toolsets per context
agent.run_sync("query", toolsets=[supplier_tools])
```

#### 3. Filtered Toolsets

**WHAT**: Dynamically enable/disable tools

```python
from pydantic_ai import FilteredToolset

def filter_tools(ctx: RunContext[AppContext]) -> list[str]:
    """Only allow tools user has permission for."""
    if ctx.deps.user.is_admin:
        return ['search_suppliers', 'update_supplier_status']
    else:
        return ['search_suppliers']  # Read-only

filtered = FilteredToolset(supplier_tools, filter_func=filter_tools)

agent.run_sync("query", toolsets=[filtered], deps=context)
```

**WHY**: Security - control tool access per user

#### 4. MCP Server Tools

**WHAT**: Connect to Model Context Protocol servers

```python
from pydantic_ai import MCPServer

# Connect to MCP server (e.g., database access)
mcp_server = MCPServer(
    name="p2p-database",
    url="http://localhost:8080/mcp"
)

# Tools from MCP server automatically available
agent = Agent('groq:llama-3.3-70b-versatile', toolsets=[mcp_server])
```

**WHY**: Reuse tools across agents, external tool providers

### Tool Execution Flow

```
User: "Find suppliers rated above 4.5"
    ↓
LLM: "I need to call search_suppliers"
    ↓
Pydantic AI: Validates arguments (name=None, min_rating=4.5)
    ↓
Tool: Executes search_suppliers(min_rating=4.5)
    ↓
Tool: Returns [{"name": "ACME", "rating": 4.8}, ...]
    ↓
LLM: Receives results, generates response
    ↓
User: "Found 3 suppliers: ACME (4.8), ..."
```

---

## 💉 Dependency Injection

### Why Dependency Injection?

**Problem**: Tools need context (DB, user, config) but LLM doesn't need to know

**Solution**: Inject dependencies via `RunContext`, invisible to LLM schema

### Injection Pattern

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class Dependencies:
    repository: Repository
    user_id: int
    config: Config

agent = Agent('groq:llama-3.3-70b-versatile')

@agent.tool
def query_user_data(
    ctx: RunContext[Dependencies],  # ← Injected, NOT in LLM schema
    data_type: str  # ← In LLM schema
) -> dict:
    """Query user-specific data.
    
    Args:
        data_type: Type of data (orders, invoices, suppliers)
    """
    # Access injected dependencies
    repo = ctx.deps.repository
    user_id = ctx.deps.user_id
    
    return repo.get_user_data(user_id, data_type)

# Run with dependencies
deps = Dependencies(
    repository=my_repo,
    user_id=123,
    config=app_config
)

result = agent.run_sync("Show my orders", deps=deps)
```

### Benefits

✅ **Clean Separation**: LLM sees simple signature, implementation complex  
✅ **Security**: User ID never exposed to prompt  
✅ **Testability**: Mock dependencies easily  
✅ **Reusability**: Same tool, different contexts

---

## ✅ Structured Outputs & Validation

### The Validation Flow

```
LLM generates response
    ↓
Pydantic validates against schema
    ↓
[Valid] → Return result.data
    ↓
[Invalid] → Send error to LLM → Retry (up to retries=N)
    ↓
[Still invalid] → Raise ValidationError
```

### Validation Levels

#### 1. Basic Type Validation

```python
class Supplier(BaseModel):
    id: int  # Must be integer
    name: str  # Must be string
    rating: float  # Must be float

# LLM outputs: {"id": "123", "name": "ACME", "rating": 4.5}
# Pydantic coerces: {"id": 123, "name": "ACME", "rating": 4.5}
```

#### 2. Field Constraints

```python
from pydantic import Field

class Invoice(BaseModel):
    amount: float = Field(gt=0, le=1000000)  # 0 < amount <= 1M
    currency: str = Field(pattern=r'^[A-Z]{3}$')  # USD, EUR, etc.
    line_items: list = Field(min_length=1)  # At least 1 item
```

#### 3. Custom Validators

```python
from pydantic import field_validator

class Order(BaseModel):
    order_date: str
    delivery_date: str
    
    @field_validator('delivery_date')
    def delivery_after_order(cls, v, info):
        if v <= info.data['order_date']:
            raise ValueError('Delivery must be after order date')
        return v
```

#### 4. Streaming Validation

**WHAT**: Validate while tokens stream (don't wait for complete response)

```python
async with agent.run_stream("query") as result:
    async for chunk in result.stream_text(delta=True):
        print(chunk, end='')
    
    # Validation happens incrementally during streaming!
    validated_data = await result.get_data()
```

**WHY**: Catch errors early, better UX

---

## 🤝 Integration with Groq

### Why Pydantic AI + Groq is Perfect

| Pydantic AI Strength | Groq Strength | Combined Benefit |
|---------------------|---------------|------------------|
| Type-safe agents | Ultra-fast inference (10x GPU) | Type-safe + lightning fast |
| Structured outputs | Streaming optimized | Validated real-time responses |
| Model-agnostic | OpenAI-compatible | Easy switch, no vendor lock |
| Tool calling | Function calling support | Reliable tool execution |
| Production focus | Production reliability | Enterprise-ready stack |

### Integration Patterns

#### Pattern 1: Simple Agent with Groq

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class SupplierInfo(BaseModel):
    supplier_id: int
    name: str
    rating: float
    status: str

# Groq as backend (fast + cheap)
agent = Agent(
    'groq:llama-3.3-70b-versatile',
    result_type=SupplierInfo,
    system_prompt="Extract supplier information"
)

result = agent.run_sync("ACME Corp, ID 42, rated 4.5 stars, active")
supplier: SupplierInfo = result.data  # Type-safe, validated
```

#### Pattern 2: Agent with Groq + Tools

```python
agent = Agent('groq:llama-3.3-70b-versatile')

@agent.tool
def search_p2p_database(query: str) -> list[dict]:
    """Search P2P database for suppliers, invoices, orders."""
    return repository.search(query)

@agent.tool
def calculate_kpi(metric: str, period: str) -> float:
    """Calculate P2P KPI (cycle time, spend, etc.)."""
    return kpi_service.calculate(metric, period)

# Groq's fast inference + Pydantic's type safety
result = agent.run_sync(
    "What's our P2P cycle time this quarter?",
    deps=app_context
)
```

#### Pattern 3: Groq Primary + OpenAI Fallback

```python
agent = Agent(
    'groq:llama-3.3-70b-versatile',  # Primary (fast, cheap)
    fallback_models=['openai:gpt-3.5-turbo']  # Fallback (reliable)
)

# Pydantic AI automatically:
# 1. Tries Groq first (10x faster)
# 2. Falls back to OpenAI if Groq unavailable
# 3. Validates output from either model
```

#### Pattern 4: Streaming with Groq + Validation

```python
agent = Agent(
    'groq:llama-3.3-70b-versatile',
    result_type=AnalysisResult
)

# Groq's LPU streams tokens FAST (<100ms first token)
# Pydantic validates incrementally during stream
async with agent.run_stream("Analyze supplier data") as result:
    async for chunk in result.stream_text():
        print(chunk, end='', flush=True)  # Real-time display
    
    validated_result = await result.get_data()  # Guaranteed valid
```

### Groq-Specific Optimizations

**1. Use Groq for Speed-Critical Paths**:
```python
# Real-time user interaction → Groq (sub-100ms)
chat_agent = Agent('groq:llama-3.3-70b-versatile')

# Background analysis → OpenAI (better reasoning)
analysis_agent = Agent('openai:gpt-4')
```

**2. Leverage Groq's High Throughput**:
```python
# Process 100s of requests concurrently
tasks = [agent.run(query, deps=ctx) for query in queries]
results = await asyncio.gather(*tasks)  # Groq handles load
```

**3. Combine Groq Compound + Pydantic Tools**:
```python
# Option A: Groq Compound (built-in tools)
compound_agent = Agent('groq/compound')  # Web search, code execution

# Option B: Pydantic AI tools (custom logic)
custom_agent = Agent('groq:llama-3.3-70b-versatile')
@custom_agent.tool
def custom_tool(): ...

# Option C: Both!
hybrid_agent = Agent(
    'groq/compound',  # Built-in tools
    toolsets=[custom_toolset]  # + Custom tools
)
```

---

## 💼 Use Case Recommendations

### 1. Joule AI Assistant Enhancement

**Current State**: Basic chat with Groq `llama-3.3-70b-versatile`

**With Pydantic AI**:
```python
from pydantic_ai import Agent
from pydantic import BaseModel

class AssistantResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[str]
    requires_action: bool

joule = Agent(
    'groq:llama-3.3-70b-versatile',
    result_type=AssistantResponse,
    system_prompt="You are Joule, SAP P2P assistant"
)

@joule.tool
def query_p2p_data(ctx: RunContext[AppContext], query: str) -> dict:
    """Query P2P database (suppliers, invoices, orders)."""
    return ctx.deps.repository.execute_query(query)

# Now Joule returns STRUCTURED, VALIDATED responses
result = joule.run_sync(
    "What are my pending invoices?",
    deps=app_context
)

# Frontend receives typed data:
response: AssistantResponse = result.data
if response.requires_action:
    show_action_buttons(response.sources)
```

**Benefits**:
- ✅ Type-safe responses (no parsing errors)
- ✅ Validated data (confidence scores, sources)
- ✅ Tool calling (P2P database access)
- ✅ Production-ready (error handling, retries)

### 2. P2P Dashboard Agent

**WHAT**: AI agent for dashboard insights

```python
class DashboardInsight(BaseModel):
    metric: str
    value: float
    trend: str  # "up", "down", "stable"
    recommendation: str

dashboard_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    result_type=DashboardInsight
)

@dashboard_agent.tool
def get_kpi(metric: str, period: str) -> float:
    """Get P2P KPI value."""
    return kpi_service.calculate(metric, period)

# User: "How's our P2P cycle time?"
result = dashboard_agent.run_sync("Analyze P2P cycle time this quarter")

insight: DashboardInsight = result.data
# Display structured insight in dashboard
```

### 3. Document Processing

**WHAT**: Extract structured data from unstructured text

```python
class InvoiceData(BaseModel):
    invoice_id: str
    supplier: str
    amount: float
    currency: str
    line_items: list[dict]
    due_date: str

extraction_agent = Agent(
    'groq:mixtral-8x7b-32768',  # Long context for documents
    result_type=InvoiceData
)

# Upload PDF → extract text → agent extracts structured data
result = extraction_agent.run_sync(f"Extract invoice data:\n\n{pdf_text}")

invoice: InvoiceData = result.data  # Validated, ready for database
repository.save_invoice(invoice)
```

### 4. Multi-Agent Workflow

**WHAT**: Chain multiple specialized agents

```python
# Agent 1: Classify query
classifier = Agent('groq:llama-3.1-8b-instant', result_type=QueryType)

# Agent 2: Answer supplier questions
supplier_agent = Agent('groq:llama-3.3-70b-versatile', result_type=SupplierAnswer)

# Agent 3: Answer invoice questions
invoice_agent = Agent('groq:llama-3.3-70b-versatile', result_type=InvoiceAnswer)

# Orchestration
query_type = classifier.run_sync(user_query)
if query_type.data.category == "supplier":
    result = supplier_agent.run_sync(user_query)
else:
    result = invoice_agent.run_sync(user_query)
```

### 5. Agentic Testing (Gu Wu Enhancement)

**WHAT**: Use Pydantic AI to generate tests

```python
class TestCase(BaseModel):
    test_name: str
    test_code: str
    assertions: list[str]
    coverage_area: str

test_generator = Agent(
    'groq:llama-3.3-70b-versatile',
    result_type=TestCase
)

@test_generator.tool
def analyze_code(file_path: str) -> dict:
    """Analyze code to find test gaps."""
    return static_analyzer.analyze(file_path)

# Generate test for untested function
result = test_generator.run_sync(
    f"Generate unit test for function {func_name} in {file_path}"
)

test: TestCase = result.data
write_test_file(test.test_code)  # Auto-generate tests!
```

**Integration with Gu Wu**:
- Gu Wu finds test gaps → Pydantic AI generates tests
- Type-safe test generation
- Validated test structure

---

## 🚀 Getting Started

### Installation

```bash
pip install pydantic-ai

# For Groq support
pip install pydantic-ai[groq]

# For observability
pip install pydantic-ai[logfire]
```

### Quick Start (5 Minutes)

**Step 1: Define Agent**:
```python
from pydantic_ai import Agent
from pydantic import BaseModel

class SupplierInfo(BaseModel):
    name: str
    rating: float
    status: str

agent = Agent(
    'groq:llama-3.3-70b-versatile',
    result_type=SupplierInfo,
    system_prompt="Extract supplier information"
)
```

**Step 2: Add Tools** (optional):
```python
@agent.tool
def search_database(query: str) -> list[dict]:
    """Search P2P database."""
    return db.search(query)
```

**Step 3: Run Agent**:
```python
result = agent.run_sync("ACME Corp rated 4.5 stars, active")
supplier: SupplierInfo = result.data

print(f"Name: {supplier.name}")
print(f"Rating: {supplier.rating}")
print(f"Status: {supplier.status}")
```

**Step 4: Add Streaming**:
```python
async with agent.run_stream("Tell me about suppliers") as result:
    async for chunk in result.stream_text():
        print(chunk, end='', flush=True)
    
    final_data = await result.get_data()
```

### Development Resources

**Official Docs**:
- Homepage: https://ai.pydantic.dev
- Agents: https://ai.pydantic.dev/agents/
- Tools: https://ai.pydantic.dev/tools/
- Models: https://ai.pydantic.dev/models/overview/

**GitHub**:
- Repository: https://github.com/pydantic/pydantic-ai
- Examples: https://github.com/pydantic/pydantic-ai/tree/main/examples

**Observability**:
- Logfire: https://logfire.pydantic.dev
- Braintrust: https://www.braintrust.dev/docs/integrations/agent-frameworks/pydantic-ai

---

## 📚 Related Documentation

### Internal Documentation

- [[Groq API Reference]] - Groq API technical specification
- [[Groq Documentation Overview]] - Groq platform and Compound
- [[AI Assistant UX Design]] - Joule implementation
- [[Agentic Workflow Patterns]] - Agent design patterns

### External Resources

1. **Pydantic AI Docs**: https://ai.pydantic.dev
2. **Pydantic Docs**: https://docs.pydantic.dev (for validation)
3. **Groq Docs**: https://console.groq.com/docs (for LLM backend)
4. **FastAPI Docs**: https://fastapi.tiangolo.com (similar design philosophy)

---

## 🎓 Key Takeaways

### For Joule AI Assistant

**Current Architecture**:
```
User → Frontend → Backend (raw Groq API) → Response string
```

**With Pydantic AI**:
```
User → Frontend → Pydantic AI Agent → Groq → Validated typed response
                        ↓
                    [Tools: P2P DB, KPI calc, etc.]
```

**Benefits**:
1. ✅ **Type Safety**: No more parsing JSON strings, runtime errors
2. ✅ **Validation**: Guaranteed valid responses (schema-checked)
3. ✅ **Tools**: Easy database access, KPI calculations
4. ✅ **Observability**: Built-in logging, monitoring
5. ✅ **Testability**: Mock dependencies, validate schemas

### Migration Path

**Phase 1: Add Pydantic AI** (2-3 hours):
```python
# Before: Raw Groq API
response = groq_client.chat.completions.create(...)
answer = response.choices[0].message.content  # String

# After: Pydantic AI
agent = Agent('groq:llama-3.3-70b-versatile', result_type=Response)
result = agent.run_sync(query)
answer: Response = result.data  # Typed, validated
```

**Phase 2: Add Tools** (3-4 hours):
```python
@agent.tool
def query_p2p_data(query: str) -> dict:
    return repository.search(query)
```

**Phase 3: Add Observability** (1-2 hours):
```python
import logfire
logfire.configure()
# Now all agent runs logged automatically
```

### Pydantic AI + Groq: The Perfect Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Framework** | Pydantic AI | Type safety, validation, tools |
| **LLM Backend** | Groq | 10x speed, low cost, reliability |
| **Observability** | Logfire | Production monitoring |
| **Validation** | Pydantic | Industry-standard schemas |

**Philosophy**: "Type-safe agents with lightning-fast inference"

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 7, 2026 | Initial documentation with Groq integration guide |

---

## 📝 Notes

**For Joule Enhancement**:
- Current: Raw Groq API (strings, manual parsing)
- Opportunity: Pydantic AI (type-safe, validated, tools)
- Migration: 2-3 hours for Phase 1 (type-safe responses)
- Full value: 6-9 hours total (types + tools + observability)

**Key Decision Factors**:
1. **Type Safety Critical?** → Use Pydantic AI
2. **Need Structured Outputs?** → Use Pydantic AI
3. **Want Simple API?** → Use Pydantic AI
4. **Already have LangChain?** → Maybe stick with it (ecosystem)
5. **Prototyping only?** → Raw Groq API fine

**Perfect Fit For**:
- ✅ Joule AI Assistant (type-safe responses)
- ✅ P2P Dashboard agent (structured insights)
- ✅ Document extraction (validated data)
- ✅ Gu Wu test generation (type-safe test code)
- ✅ Any production AI app (reliability matters)

---

**See Also**: [[Groq API Reference]] (LLM backend), [[Groq Documentation Overview]] (Compound agents), [[Agentic Workflow Patterns]] (design patterns)