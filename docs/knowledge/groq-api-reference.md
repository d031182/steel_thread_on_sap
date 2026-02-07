# Groq API Reference Guide

**Version**: 1.0  
**Last Updated**: February 7, 2026  
**Purpose**: Comprehensive reference for Groq API integration

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Chat Completions API](#chat-completions-api)
4. [Streaming](#streaming)
5. [Tool Calling / Function Calling](#tool-calling--function-calling)
6. [Supported Models](#supported-models)
7. [Rate Limits & Performance](#rate-limits--performance)
8. [Best Practices](#best-practices)
9. [Use Cases](#use-cases)
10. [Related Documentation](#related-documentation)

---

## 📖 Overview

### WHAT is Groq?

**Groq** is an AI infrastructure provider that delivers **ultra-fast inference** using proprietary **Language Processing Units (LPUs)**. It provides OpenAI-compatible APIs for chat completions with speeds **10x faster than traditional GPUs** while using **1/10th the energy**.

### WHY Use Groq?

1. **Speed**: 300-1000+ tokens/second (vs ~100 t/s on GPUs)
2. **Cost**: Low-cost inference for production workloads
3. **Compatibility**: OpenAI-compatible API (easy migration)
4. **Reliability**: Doesn't flake under production load
5. **Global Scale**: Data centers worldwide minimize latency

### WHEN to Use Groq?

✅ **Use Groq when you need:**
- Real-time AI responses (chatbots, assistants)
- High-throughput inference (production APIs)
- Cost-effective scaling
- Low-latency global deployment
- OpenAI-compatible endpoints

❌ **Consider alternatives when:**
- You need fine-tuning (Groq focuses on inference)
- You require proprietary models only available elsewhere
- You need on-premise deployment (cloud-only currently)

---

## 🎯 Core Concepts

### API Endpoint

```
Base URL: https://api.groq.com/openai/v1
Chat Completions: POST /openai/v1/chat/completions
```

### Authentication

```bash
Authorization: Bearer $GROQ_API_KEY
```

Get your API key from: https://console.groq.com/keys

### OpenAI Compatibility

Groq implements the OpenAI API specification, meaning you can:
- Drop-in replace OpenAI SDK with Groq SDK
- Use existing OpenAI-compatible tools (LangChain, LlamaIndex)
- Migrate with minimal code changes

---

## 💬 Chat Completions API

### Basic Request Structure

**Python SDK Example:**

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

chat_completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models"
        }
    ]
)

print(chat_completion.choices[0].message.content)
```

### Key Parameters

#### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `model` | string | Model identifier | `"llama-3.3-70b-versatile"` |
| `messages` | array | Conversation history | `[{"role": "user", "content": "Hello"}]` |

#### Optional Parameters

| Parameter | Type | Default | Description | Use Case |
|-----------|------|---------|-------------|----------|
| `temperature` | float | 1.0 | Randomness (0.0-2.0) | Lower = focused, Higher = creative |
| `max_tokens` | int | model max | Maximum tokens to generate | Control response length |
| `top_p` | float | 1.0 | Nucleus sampling | Alternative to temperature |
| `stop` | array | null | Stop sequences | `["\n", "END"]` to halt generation |
| `stream` | boolean | false | Enable streaming | Real-time token delivery |
| `tools` | array | null | Function definitions | Enable tool/function calling |
| `tool_choice` | string/object | "auto" | Tool selection strategy | `"auto"`, `"none"`, specific tool |

### Message Roles

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI stands for..."},
    {"role": "tool", "content": "Tool result", "tool_call_id": "xyz"}
]
```

**Roles:**
- `system`: Sets assistant behavior/context
- `user`: User input
- `assistant`: AI responses
- `tool`: Tool execution results

---

## 🌊 Streaming

### WHAT is Streaming?

Streaming delivers tokens incrementally as they're generated (Server-Sent Events), enabling real-time UX like ChatGPT's typing effect.

### WHY Use Streaming?

1. **Better UX**: Users see responses appear immediately
2. **Lower latency**: First token arrives faster
3. **Progressive rendering**: Display partial responses
4. **Cancellation**: Stop generation mid-stream if needed

### HOW to Stream

**Python SDK:**

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

**JavaScript SDK:**

```javascript
const stream = await groq.chat.completions.create({
  model: 'llama-3.3-70b-versatile',
  messages: [{role: 'user', content: 'Tell me a story'}],
  stream: true
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content || '';
  process.stdout.write(content);
}
```

### Response Format (Streaming)

```json
{
  "id": "chatcmpl-xyz",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "llama-3.3-70b-versatile",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "Hello"
      },
      "finish_reason": null
    }
  ]
}
```

**Final chunk includes `finish_reason`:**
- `"stop"`: Natural completion
- `"length"`: Hit max_tokens
- `"tool_calls"`: Tool invocation needed

---

## 🔧 Tool Calling / Function Calling

### WHAT is Tool Calling?

Tool calling (aka function calling) allows the model to invoke external functions/APIs when it needs data or actions beyond its training.

### WHY Use Tool Calling?

1. **Real-time data**: Access current information (weather, stocks, databases)
2. **Actions**: Perform operations (send emails, create tickets)
3. **Modularity**: Separate AI logic from tool logic
4. **Reliability**: Structured outputs via JSON schemas

### HOW to Implement Tool Calling

**Step 1: Define Tools**

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. San Francisco"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

**Step 2: Request with Tools**

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "What's the weather in Paris?"}
    ],
    tools=tools,
    tool_choice="auto"  # Let model decide when to use tools
)
```

**Step 3: Handle Tool Calls**

```python
message = response.choices[0].message

if message.tool_calls:
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Execute function
        if function_name == "get_weather":
            result = get_weather(**arguments)
        
        # Add tool result to conversation
        messages.append({
            "role": "tool",
            "content": json.dumps(result),
            "tool_call_id": tool_call.id
        })
    
    # Get final response with tool results
    final_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
```

### Tool Choice Strategies

| Value | Behavior | Use Case |
|-------|----------|----------|
| `"auto"` | Model decides when to use tools | General purpose |
| `"none"` | Never use tools | Force direct response |
| `{"type": "function", "function": {"name": "get_weather"}}` | Force specific tool | When tool is always needed |

### Parallel Tool Calls

Groq supports **parallel tool execution** (multiple tools in one turn):

```python
# Model might call multiple tools simultaneously
message.tool_calls = [
    {"function": {"name": "get_weather", "arguments": "..."}},
    {"function": {"name": "get_traffic", "arguments": "..."}}
]
```

### Built-in Tools (Groq Compound)

Groq offers **Responses API** with built-in tools:
- **Web Search**: Real-time web browsing
- **Code Interpreter**: Execute Python code
- **Calculator**: Mathematical computations

These require no setup - just enable in the request.

---

## 🤖 Supported Models

### Model Comparison

| Model | Context Window | Speed (t/s) | Strengths | Use Cases |
|-------|----------------|-------------|-----------|-----------|
| `llama-3.3-70b-versatile` | ~8K tokens | 300-750 | Tool use, reasoning, general tasks | Production chatbots, agents |
| `llama-3.1-8b-instant` | ~8K tokens | High | Fast inference, efficient | High-throughput APIs, embeddings |
| `mixtral-8x7b-32768` | 32K tokens | High | Long context, multilingual | Document analysis, long conversations |
| `gemma2-9b-it` | Not specified | Ultra-fast | Compact, efficient | Edge deployment, cost-sensitive apps |
| `gpt-oss-120B` | 128K tokens | 500+ | Extremely long context | Complex reasoning, large documents |
| `gpt-oss-20B` | 128K tokens | 1000+ | Balance speed & capability | High-speed production |

### Model Selection Guide

**Choose based on:**

1. **Speed Priority** → `llama-3.1-8b-instant`, `gpt-oss-20B`
2. **Context Length** → `mixtral-8x7b-32768` (32K), `gpt-oss-120B` (128K)
3. **Reasoning Quality** → `llama-3.3-70b-versatile`, `qwen-qwq-32b`
4. **Cost Optimization** → `gemma2-9b-it`, `llama-3.1-8b-instant`

### List Available Models

```python
models = client.models.list()
for model in models.data:
    print(f"{model.id}: {model.context_window} tokens")
```

---

## ⚡ Rate Limits & Performance

### Performance Benchmarks

| Metric | Groq LPU | Traditional GPU | Improvement |
|--------|----------|-----------------|-------------|
| Tokens/second | 300-1000+ | ~100 | **10x faster** |
| First token latency | ~50ms | ~200ms | **4x faster** |
| Energy efficiency | 1x | 10x | **90% less energy** |
| Tokens/minute | 18,000-60,000 | ~6,000 | **10x throughput** |

### Rate Limits

Rate limits vary by:
- **Service Tier**: Free, Flex, Premium
- **Model**: Larger models have stricter limits
- **Account Type**: Individual vs Enterprise

**Check limits via headers:**
```
x-ratelimit-limit-requests: 100
x-ratelimit-remaining-requests: 95
x-ratelimit-reset-requests: 10s
x-ratelimit-limit-tokens: 10000
x-ratelimit-remaining-tokens: 9500
```

### Service Tiers

```python
# Specify service tier for latency/throughput tuning
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    service_tier="flex"  # Higher throughput tier
)
```

**Tiers:**
- `default`: Standard performance
- `flex`: Higher throughput, optimized for scale

---

## 🎯 Best Practices

### 1. API Key Management

```python
# ✅ GOOD: Use environment variables
import os
api_key = os.environ.get("GROQ_API_KEY")

# ❌ BAD: Hardcode keys
api_key = "gsk_abc123..."  # Never do this!
```

### 2. Error Handling

```python
from groq import Groq, APIError, RateLimitError

try:
    response = client.chat.completions.create(...)
except RateLimitError as e:
    # Handle rate limit (wait and retry)
    time.sleep(e.retry_after)
except APIError as e:
    # Handle API errors
    print(f"API Error: {e.status_code} - {e.message}")
```

### 3. Streaming for UX

```python
# ✅ Use streaming for user-facing apps
stream = client.chat.completions.create(..., stream=True)

# ❌ Don't block UI waiting for full response
response = client.chat.completions.create(...)  # Slower UX
```

### 4. Token Management

```python
# Estimate tokens before request (rough: 1 token ≈ 4 chars)
def estimate_tokens(text):
    return len(text) // 4

# Set max_tokens to control costs
response = client.chat.completions.create(
    ...,
    max_tokens=500  # Limit response length
)
```

### 5. System Messages for Context

```python
# ✅ GOOD: Use system messages to guide behavior
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant specializing in Python. "
                   "Provide code examples and explain concepts clearly."
    },
    {"role": "user", "content": "How do I read a CSV file?"}
]
```

### 6. Tool Calling Best Practices

```python
# ✅ Provide clear tool descriptions
tools = [{
    "type": "function",
    "function": {
        "name": "query_database",
        "description": "Query the sales database for invoice data. "
                       "Returns invoice amount, date, and status.",
        "parameters": {...}
    }
}]

# ✅ Validate tool inputs before execution
def safe_tool_execution(function_name, arguments):
    # Validate arguments
    if not validate_args(arguments):
        return {"error": "Invalid arguments"}
    
    # Execute with error handling
    try:
        return execute_tool(function_name, arguments)
    except Exception as e:
        return {"error": str(e)}
```

---

## 💡 Use Cases

### 1. Real-Time Chatbots

**WHY Groq?**
- Ultra-low latency (<100ms first token)
- Streaming for responsive UX
- High throughput for concurrent users

**Example:**
```python
# Customer support chatbot
def handle_chat(user_message, conversation_history):
    messages = conversation_history + [
        {"role": "user", "content": user_message}
    ]
    
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        stream=True
    )
    
    for chunk in stream:
        yield chunk.choices[0].delta.content
```

### 2. AI Agents with Tool Use

**WHY Groq?**
- Native tool calling support
- Fast inference for multi-step reasoning
- Parallel tool execution

**Example:**
```python
# Data analysis agent
tools = [
    {"type": "function", "function": {
        "name": "query_database",
        "description": "Query sales database",
        "parameters": {...}
    }},
    {"type": "function", "function": {
        "name": "generate_chart",
        "description": "Create visualization",
        "parameters": {...}
    }}
]

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{
        "role": "user",
        "content": "Show me top 5 products by revenue this quarter"
    }],
    tools=tools,
    tool_choice="auto"
)
```

### 3. Document Processing

**WHY Groq?**
- Long context models (32K-128K tokens)
- Fast processing of large documents
- Extract structured data

**Example:**
```python
# Extract invoice data
with open("invoice.pdf", "rb") as f:
    invoice_text = extract_text(f)

response = client.chat.completions.create(
    model="mixtral-8x7b-32768",  # Long context
    messages=[{
        "role": "user",
        "content": f"Extract invoice number, amount, and date:\n{invoice_text}"
    }],
    response_format={"type": "json_object"}  # Structured output
)
```

### 4. Code Generation & Analysis

**WHY Groq?**
- Fast iteration cycles
- Code-optimized models
- Tool use for execution

**Example:**
```python
# Code generation with validation
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{
        "role": "system",
        "content": "You are a Python expert. Generate clean, documented code."
    }, {
        "role": "user",
        "content": "Write a function to calculate Fibonacci numbers"
    }]
)
```

### 5. Multi-Turn Conversations

**WHY Groq?**
- Stateless API (you manage history)
- Fast multi-turn inference
- Context preservation

**Example:**
```python
# Conversation management
class ConversationManager:
    def __init__(self):
        self.messages = []
    
    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})
    
    def get_response(self):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=self.messages
        )
        
        assistant_message = response.choices[0].message.content
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
```

---

## 📚 Related Documentation

### Internal Documentation

- [[AI Assistant UX Design]] - Joule AI Assistant implementation
- [[Groq Documentation Overview]] - High-level Groq concepts (see P2 task)
- [[Modular Architecture]] - How AI Assistant module integrates

### External Resources

1. **Official Groq Docs**: https://console.groq.com/docs
   - API Reference: https://console.groq.com/docs/api-reference
   - Quickstart: https://console.groq.com/docs/quickstart
   - Models: https://console.groq.com/docs/models
   - Responses API: https://console.groq.com/docs/responses-api

2. **Python SDK**: https://github.com/groq/groq-python
   - Full API: See `api.md` in repo
   - Examples: See `examples/` directory

3. **Integration Guides**:
   - LangChain: https://docs.langchain.com/oss/python/integrations/chat/groq
   - LlamaIndex: Check Groq integration docs
   - Vercel AI SDK: See `ai-sdk.dev/providers/ai-sdk-providers/groq`

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 7, 2026 | Initial documentation with WHAT/WHY/USE CASES |

---

## 📝 Notes

**For AI Assistant Implementation:**
- Current implementation uses `llama-3.3-70b-versatile` (see `modules/ai_assistant/backend/agent_service.py`)
- Streaming enabled for better UX
- Tool calling not yet implemented (P2 enhancement)

**Performance Considerations:**
- Groq's speed advantage is most significant for:
  * Real-time applications (chatbots, assistants)
  * High-throughput APIs (concurrent users)
  * Long context processing (32K-128K tokens)

**Cost Optimization:**
- Use `llama-3.1-8b-instant` for cost-sensitive workloads
- Set `max_tokens` to control response length
- Cache system messages when possible
- Use smaller models for simple tasks

---

**See Also**: [[Groq Documentation Overview]] (P2 task for high-level concepts)