# Groq Documentation Overview

**Version**: 1.0  
**Last Updated**: February 7, 2026  
**Purpose**: High-level overview of Groq platform capabilities and integration patterns

---

## 📋 Table of Contents

1. [What is Groq?](#what-is-groq)
2. [Core Value Proposition](#core-value-proposition)
3. [LPU Technology](#lpu-technology)
4. [Groq Platform Architecture](#groq-platform-architecture)
5. [Groq Compound (Agentic AI)](#groq-compound-agentic-ai)
6. [Integration Patterns](#integration-patterns)
7. [Use Case Recommendations](#use-case-recommendations)
8. [Getting Started](#getting-started)
9. [Ecosystem & SDKs](#ecosystem--sdks)
10. [Related Documentation](#related-documentation)

---

## 🎯 What is Groq?

### WHAT

**Groq** is an AI infrastructure platform that provides **ultra-fast LLM inference** through proprietary hardware called **Language Processing Units (LPUs)**. It hosts open-source models (Llama, Mixtral, Gemma) with speeds **10x faster than traditional GPUs**.

### WHY Groq Exists

**Problems Groq Solves**:
1. **GPU Bottlenecks**: Traditional GPUs have unpredictable latency and variable performance
2. **Cost**: High inference costs limit AI adoption at scale
3. **Speed**: Users expect ChatGPT-level responsiveness (instant responses)
4. **Complexity**: Managing AI infrastructure is difficult
5. **Reliability**: Production AI systems need predictable performance

**Groq's Solution**:
- **Custom Hardware (LPU)**: Purpose-built for AI inference, not general computation
- **Deterministic Performance**: Predictable latency every time (no variability)
- **OpenAI-Compatible**: Drop-in replacement for OpenAI API
- **Managed Service**: No infrastructure management required
- **Open Models**: Access latest Llama, Mixtral, Gemma models

### WHEN to Choose Groq

✅ **Use Groq when you need**:
- Real-time AI responses (<100ms first token)
- High-throughput production APIs (1000s of requests/min)
- Cost-effective scaling (10x cheaper than GPUs)
- OpenAI compatibility (easy migration)
- Predictable, reliable performance

❌ **Consider alternatives when**:
- You need proprietary models (GPT-4, Claude) - Groq focuses on open models
- You require fine-tuning from scratch - Groq supports LoRA but not full fine-tuning
- You need on-premise deployment - Groq is cloud-only (GroqCloud)

---

## ⚡ Core Value Proposition

### Speed: The Groq Advantage

| Metric | Groq LPU | Traditional GPU | Improvement |
|--------|----------|-----------------|-------------|
| Tokens/second | 300-1000+ | ~100 | **10x faster** |
| First token latency | <100ms | 200-500ms | **5x faster** |
| Throughput (tokens/min) | 18,000-60,000 | ~6,000 | **10x higher** |
| Performance variability | None (deterministic) | High | **Predictable** |
| Energy efficiency | 1x | 10x | **90% less energy** |

### Why Speed Matters

**Real-World Impact**:
1. **User Experience**: Instant responses feel like magic (ChatGPT effect)
2. **Cost Savings**: Faster inference = serve more users with same infrastructure
3. **New Use Cases**: Real-time AI agents, live coding assistants, instant search
4. **Competitive Advantage**: Speed = better product = more users
5. **Production Reliability**: Predictable performance = fewer incidents

**Example: Customer Support Bot**:
- **Before (GPU)**: 3-5 second response time → users drop off
- **After (Groq)**: 0.5 second response time → seamless conversation
- **Result**: 2x engagement, 50% cost reduction

---

## 🔧 LPU Technology

### WHAT is an LPU?

**Language Processing Unit (LPU)** is Groq's custom silicon designed specifically for AI inference workloads, particularly Large Language Models.

### HOW LPUs Work

**Key Architectural Differences**:

| Feature | GPU | LPU |
|---------|-----|-----|
| **Design Goal** | General parallel computation | AI inference only |
| **Architecture** | Multi-core, variable latency | Single-core streaming, deterministic |
| **Memory Access** | Random, high latency | Sequential, ultra-low latency |
| **Performance** | Variable (thermal throttling) | Consistent (no throttling) |
| **Best For** | Training, graphics, general AI | Production LLM serving |

**Deterministic Single-Core Streaming**:
- Tokens generated in predictable, sequential order
- No race conditions or memory contention
- Same input → same latency every time
- Ideal for production SLAs

### WHY LPU > GPU for Inference

**Advantages**:
1. **Predictability**: Production systems need reliable response times
2. **Speed**: Optimized data paths for sequential text generation
3. **Cost**: Lower energy = lower operating costs
4. **Simplicity**: One-size-fits-all hardware (no GPU selection complexity)

**Trade-offs**:
- ❌ Not suitable for training (GPUs better)
- ❌ Cloud-only (no on-premise option yet)
- ✅ Perfect for high-volume inference
- ✅ Ideal for real-time applications

---

## 🏗️ Groq Platform Architecture

### Platform Components

```
User Application
      ↓
GroqCloud API (OpenAI-compatible)
      ↓
Orchestration Layer (routing, load balancing)
      ↓
LPU Cluster (inference engines)
      ↓
Model Storage (Llama, Mixtral, Gemma, etc.)
```

### Key Features

#### 1. OpenAI-Compatible API

**WHAT**: Drop-in replacement for OpenAI API endpoints

**WHY**: Zero code changes for migration

**Endpoints**:
- `/openai/v1/chat/completions` - Chat interface
- `/openai/v1/models` - List available models
- `/openai/v1/completions` - Text completion
- `/openai/v1/embeddings` - (Future support)

**Example Migration**:
```python
# Before (OpenAI)
from openai import OpenAI
client = OpenAI(api_key="sk-...")

# After (Groq) - Just change 2 lines!
from groq import Groq
client = Groq(api_key="gsk-...")
# Rest of code unchanged!
```

#### 2. Managed Model Hosting

**WHAT**: Pre-loaded open-source models ready to use

**Models Available** (as of Feb 2026):
- **Llama Family**: 3.1-8b-instant, 3.3-70b-versatile, 4 (upcoming)
- **Mixtral**: 8x7b-32768 (32K context)
- **Gemma**: 2-9b-it (Google's efficient model)
- **GPT-OSS**: 120B, 20B (OpenAI's open models)
- **Groq Compound**: Agentic system (see section 5)

**WHY Managed Hosting Matters**:
- No infrastructure setup
- Auto-scaling (handles traffic spikes)
- Model updates automatic
- Pay-per-use pricing

#### 3. Service Tiers

**WHAT**: Different performance/cost profiles

| Tier | Speed | Cost | Use Case |
|------|-------|------|----------|
| Free | Standard | $0 | Development, testing |
| Flex | High throughput | Pay-as-go | Production, scale-up |
| Premium | Guaranteed capacity | Enterprise | Mission-critical apps |

#### 4. Advanced Features

- **Streaming**: Server-Sent Events for real-time responses
- **Batch Processing**: Submit multiple requests, get results later
- **Fine-tuning (LoRA)**: Adapt models to your domain
- **File Management**: Upload/manage training data
- **Tool Calling**: Function calling for AI agents

---

## 🤖 Groq Compound (Agentic AI)

### WHAT is Groq Compound?

**Groq Compound** is an **agentic AI system** that autonomously uses built-in tools (web search, code execution, browser control) to solve complex multi-step problems **in a single API call**.

### WHY Compound is Revolutionary

**Traditional Approach (Complex)**:
```
User → LLM → Parse response → Decide tool → Call tool → 
  → LLM again → Parse → Another tool → LLM → Final response
```
- 5-10 API calls
- Complex orchestration logic
- High latency (serial calls)
- Error-prone (parsing failures)

**Compound Approach (Simple)**:
```
User → Groq Compound → Autonomous multi-step workflow → Final response
```
- **1 API call**
- **Server-side orchestration** (Groq handles complexity)
- **Low latency** (parallel tool execution)
- **Reliable** (production-grade infrastructure)

### Key Capabilities

#### 1. Built-in Tools

| Tool | Purpose | Example Use |
|------|---------|-------------|
| **Web Search** | Real-time information | "What's the weather in Paris today?" |
| **Code Execution** | Computations, API calls | "Calculate compound interest for 10 years" |
| **Browser Control** | Navigate webpages | "Get latest stock price from Yahoo Finance" |
| **Wolfram Alpha** | Math, science queries | "Solve differential equation" |

#### 2. Autonomous Reasoning

**WHAT**: Compound decides which tools to use and when

**Example Workflow**:
```
User: "Find cheapest flight from NYC to Paris next week"

Compound's Reasoning:
1. Need current date → Use web search
2. Need flight data → Navigate airline websites (browser)
3. Need price comparison → Execute code to compare
4. Return formatted result

All automatic! No user code needed.
```

#### 3. Multi-Step Workflows

**WHAT**: Chain multiple tool calls automatically

**Example: Financial Analysis**:
```
User: "Analyze Tesla stock performance vs S&P 500 YTD"

Compound's Steps:
1. Web search for Tesla current price
2. Web search for S&P 500 current value
3. Code execution to calculate YTD returns
4. Code execution to generate comparison chart
5. Return analysis with visualization

One API call does all of this!
```

### Compound Models

| Model | Capabilities | Tool Calls/Request | Use Case |
|-------|--------------|-------------------|----------|
| `groq/compound` | Full-featured | Up to 10 | Complex research, multi-step analysis |
| `groq/compound-mini` | Lightweight | Up to 5 | Quick lookups, simple tasks |

**Underlying LLMs**:
- GPT-OSS 120B (complex reasoning)
- Llama 4 (efficiency)
- Llama 3.3 70B (balance)

### HOW to Use Compound

**Simple Example**:
```python
from groq import Groq

client = Groq(api_key="gsk-...")

response = client.chat.completions.create(
    model="groq/compound",  # Use Compound!
    messages=[{
        "role": "user",
        "content": "What's the current Bitcoin price and how has it changed in the last 24 hours?"
    }]
)

# Compound automatically:
# 1. Searches web for current BTC price
# 2. Searches for 24h price history
# 3. Calculates change
# 4. Returns formatted answer

print(response.choices[0].message.content)
```

**Advanced Options**:
```python
response = client.chat.completions.create(
    model="groq/compound",
    messages=[...],
    stream=True,  # Watch tools being used in real-time
    max_tool_calls=5,  # Limit complexity
    reasoning_level="detailed"  # Show thinking process
)
```

### WHY Compound for AI Assistants

**Perfect for Joule AI Assistant Because**:
1. **Simplicity**: One API call vs complex orchestration
2. **Reliability**: Groq handles tool failures, retries
3. **Speed**: Parallel execution + LPU speed
4. **Real-time Data**: Web search for current information
5. **Code Execution**: Calculations, data processing
6. **Production-Ready**: Battle-tested infrastructure

**Current Joule → Compound Migration**:
- Current: `llama-3.3-70b-versatile` (no tools)
- Future: `groq/compound` (autonomous tools)
- Benefit: Answer "What's the weather?" without manual integration

---

## 🔌 Integration Patterns

### Pattern 1: Direct SDK Integration

**WHAT**: Use official Groq SDKs

**Python**:
```python
pip install groq

from groq import Groq
client = Groq(api_key=os.environ["GROQ_API_KEY"])
```

**JavaScript/TypeScript**:
```bash
npm install groq-sdk

import Groq from "groq-sdk";
const client = new Groq({ apiKey: process.env.GROQ_API_KEY });
```

**WHY**: Official support, best performance, latest features

### Pattern 2: OpenAI SDK Compatibility

**WHAT**: Use OpenAI SDK with Groq base URL

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="gsk-..."
)
# Now all OpenAI SDK methods work with Groq!
```

**WHY**: Existing codebase, no refactoring, test Groq without changes

### Pattern 3: Framework Integration

**LangChain**:
```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key="gsk-..."
)
```

**LlamaIndex**:
```python
from llama_index.llms.groq import Groq

llm = Groq(model="llama-3.3-70b-versatile")
```

**Vercel AI SDK**:
```typescript
import { createGroq } from "@ai-sdk/groq";

const groq = createGroq({ apiKey: "gsk-..." });
```

**WHY**: Ecosystem compatibility, use existing patterns, community support

### Pattern 4: Tool Use (3 Approaches)

#### A) Groq Built-in Tools (Compound)

**WHAT**: Server-side tools (web search, code, browser)

**HOW**:
```python
# Just use Compound model - tools automatic!
response = client.chat.completions.create(
    model="groq/compound",
    messages=[...]
)
```

**WHY**: Zero setup, production-ready, Groq manages everything

#### B) Remote Tool Calling (MCP Servers)

**WHAT**: External tools via Model Context Protocol

**HOW**:
```python
# Connect to MCP server (e.g., database access)
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Query P2P database",
            "parameters": {...}
        }
    }
]

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    tools=tools,
    messages=[...]
)
```

**WHY**: Custom integrations, private data sources, existing APIs

#### C) Local Tool Execution

**WHAT**: You execute tools based on model's requests

**HOW**:
```python
# 1. Model requests tool
response = client.chat.completions.create(...)

# 2. You execute locally
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = execute_tool(tool_call.function.name, ...)
        
# 3. Send results back
final_response = client.chat.completions.create(
    messages=[..., {"role": "tool", "content": result}]
)
```

**WHY**: Full control, security, custom logic

---

## 💼 Use Case Recommendations

### 1. Real-Time Conversational AI

**WHAT**: Chatbots, virtual assistants, customer support

**WHY Groq**:
- <100ms first token (feels instant)
- Streaming for typing effect
- High concurrency (1000s of simultaneous users)

**Recommended Model**: `llama-3.3-70b-versatile`

**Architecture**:
```
User → Frontend (streaming) → Backend (Groq API) → Database (history)
```

**Example**: Joule AI Assistant (our implementation)

### 2. Agentic Workflows

**WHAT**: AI that takes action (research, data analysis, automation)

**WHY Groq**:
- Compound handles orchestration
- Built-in tools (web, code, browser)
- One API call for multi-step tasks

**Recommended Model**: `groq/compound`

**Example Use Cases**:
- Research assistant (web search + synthesis)
- Financial analyst (data retrieval + calculations)
- Travel planner (search + booking integration)

### 3. Document Processing

**WHAT**: Extract data, summarize, analyze documents

**WHY Groq**:
- Long context models (32K-128K tokens)
- Fast processing (1000s of docs/hour)
- Structured outputs (JSON mode)

**Recommended Model**: `mixtral-8x7b-32768` (long context)

**Architecture**:
```
Upload PDF → Extract text → Groq API (extract structured data) → Database
```

### 4. Code Generation & Analysis

**WHAT**: Generate code, review code, explain code

**WHY Groq**:
- Fast iteration (instant feedback)
- Code-optimized models
- Tool use for execution/validation

**Recommended Model**: `llama-3.3-70b-versatile`

**Example**: IDE assistant, code review bot, debugging helper

### 5. High-Throughput APIs

**WHAT**: Production APIs serving millions of requests

**WHY Groq**:
- 18K-60K tokens/minute throughput
- Predictable latency (SLA-friendly)
- Cost-effective at scale

**Recommended Model**: `llama-3.1-8b-instant` (cost-optimized)

**Architecture**:
```
Load Balancer → API Servers → Groq (batch requests) → Cache → Response
```

---

## 🚀 Getting Started

### Quick Start (5 Minutes)

**Step 1: Sign Up**
- Go to: https://console.groq.com
- Create account (free tier available)
- Generate API key

**Step 2: Install SDK**
```bash
pip install groq
```

**Step 3: Hello World**
```python
import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{
        "role": "user",
        "content": "Explain Groq in one sentence"
    }]
)

print(response.choices[0].message.content)
```

**Step 4: Try Streaming**
```python
stream = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Step 5: Try Compound (Agentic)**
```python
response = client.chat.completions.create(
    model="groq/compound",
    messages=[{
        "role": "user",
        "content": "What's the weather in Tokyo and what time is it there?"
    }]
)

print(response.choices[0].message.content)
# Compound automatically searches web, does timezone conversion!
```

### Development Resources

**Official Docs**:
- Overview: https://console.groq.com/docs/overview
- API Reference: https://console.groq.com/docs/api-reference
- Quickstart: https://console.groq.com/docs/quickstart
- Models: https://console.groq.com/docs/models
- Compound: https://console.groq.com/docs/compound

**SDKs**:
- Python: https://github.com/groq/groq-python
- JavaScript: npm install groq-sdk

**Community**:
- Discord: Join GroqCloud community
- Examples: GitHub groq/examples repo

---

## 🌐 Ecosystem & SDKs

### Official SDKs

| SDK | Language | Repository | Features |
|-----|----------|------------|----------|
| groq-python | Python | github.com/groq/groq-python | Full API, streaming, async |
| groq-sdk | JavaScript/TS | npm package | Full API, streaming, types |

### Framework Support

| Framework | Integration | Status |
|-----------|-------------|--------|
| **LangChain** | ChatGroq | ✅ Production |
| **LlamaIndex** | Groq LLM | ✅ Production |
| **Vercel AI SDK** | @ai-sdk/groq | ✅ Production |
| **Haystack** | GroqGenerator | ✅ Production |
| **AutoGen** | Groq client | ✅ Community |

### Third-Party Tools

- **E2B**: Powers Compound's code execution (secure sandboxes)
- **Factory CLI**: Groq integration for AI workflows
- **Appian**: Enterprise plugin for Groq
- **ElevenLabs**: Voice + Groq for conversational AI

### MCP Server Support

**WHAT**: Model Context Protocol for tool integration

**Groq MCP Server**:
```bash
npm install @groq/mcp-server
```

**Features**:
- Connect local tools to Groq models
- Custom function definitions
- Secure tool execution

---

## 📚 Related Documentation

### Internal Documentation

- [[Groq API Reference]] - Complete API specification with examples
- [[AI Assistant UX Design]] - Joule AI Assistant implementation
- [[Agentic Workflow Patterns]] - AI agent design patterns

### External Resources

1. **Official Groq Docs**: https://console.groq.com/docs
   - Overview: /overview
   - API Reference: /api-reference
   - Compound: /compound
   - Models: /models

2. **Blog Posts**:
   - Introducing Compound: https://groq.com/blog/introducing-the-next-generation-of-compound-on-groqcloud
   - Building AI Research Agents: https://groq.com/blog/how-to-build-your-own-ai-research-agent-with-one-groq-api-call

3. **GitHub**:
   - Python SDK: https://github.com/groq/groq-python
   - MCP Server: https://github.com/groq/groq-mcp-server

---

## 🎓 Key Takeaways

### For AI Assistant Development

1. **Speed Matters**: Sub-100ms responses transform UX
2. **Compound = Simplicity**: Agentic AI in one API call
3. **Open Models**: Llama 3.3 70B rivals proprietary models
4. **Cost-Effective**: 10x cheaper than traditional inference
5. **Production-Ready**: Predictable, reliable, battle-tested

### Migration Path for Joule

**Phase 1 (Current)**: 
- ✅ Basic chat with `llama-3.3-70b-versatile`
- ✅ Streaming enabled
- ✅ Multi-turn conversations

**Phase 2 (Next)**:
- 🔄 Migrate to `groq/compound` for tool use
- 🔄 Enable web search (real-time information)
- 🔄 Add code execution (calculations, data processing)

**Phase 3 (Future)**:
- 🔮 Custom tools via MCP (P2P database queries)
- 🔮 Advanced reasoning modes
- 🔮 Multi-agent workflows

### When to Choose Each Model

| Need | Model | Why |
|------|-------|-----|
| Speed + quality balance | `llama-3.3-70b-versatile` | Best default choice |
| Agentic capabilities | `groq/compound` | Built-in tools, autonomous |
| Long documents | `mixtral-8x7b-32768` | 32K context window |
| High throughput | `llama-3.1-8b-instant` | Fastest, most efficient |
| Extreme context | `gpt-oss-120B` | 128K tokens |

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 7, 2026 | Initial documentation with high-level overview |

---

## 📝 Notes

**For Joule AI Assistant**:
- Current: Using basic `llama-3.3-70b-versatile` (no tools)
- Opportunity: Compound model unlocks autonomous web search, code execution
- Benefit: Answer "What's Bitcoin price?" without manual API integration
- Timeline: After security fixes complete (P2 priority)

**Key Insights**:
- **LPU > GPU** for production inference (speed, cost, predictability)
- **Compound** simplifies agentic AI (one API call vs complex orchestration)
- **Open models** competitive with proprietary (Llama 3.3 ≈ GPT-3.5 quality)
- **OpenAI compatibility** enables easy migration and testing

---

**See Also**: [[Groq API Reference]] (detailed technical specs), [[Agentic Workflow Patterns]] (agent design)