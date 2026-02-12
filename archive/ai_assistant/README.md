# AI Assistant Module

Modern AI agent for natural language interaction with P2P Data Products using **Pydantic AI + Groq**.

## Architecture

**Technology Stack**:
- **Pydantic AI**: Agent framework with structured outputs
- **Groq**: Ultra-fast LLM inference (llama-3.1-70b-versatile)
- **Flask**: REST API endpoints
- **python-dotenv**: Secure API key management

**Design Philosophy**:
- Cloud-based inference (no local model needed)
- Fast responses (~1-2 seconds via Groq)
- Structured data handling via Pydantic
- Secure API key management via .env

## Features

### 1. Natural Language Queries
Ask questions about data products in plain English:
```python
POST /api/ai-assistant/query
{
  "prompt": "What data products do we have?",
  "context": {
    "data_products": ["SupplierInvoice", "PurchaseOrder"]
  }
}
```

### 2. Data Product Analysis
Get AI-powered insights on specific data products:
```python
POST /api/ai-assistant/analyze-product
{
  "data_product_name": "SupplierInvoice",
  "schema_info": { ... },
  "question": "What are the key relationships?"
}
```

### 3. SQL Generation
Generate SQL queries from natural language:
```python
POST /api/ai-assistant/generate-sql
{
  "query": "Show me all invoices from last month",
  "table_schema": { ... }
}
```

## Configuration

### Setup (Required)

1. **Get Groq API Key**:
   - Visit https://console.groq.com
   - Create account and generate API key
   - Free tier available!

2. **Add to .env file**:
   ```bash
   GROQ_API_KEY=gsk_your_key_here
   ```

3. **Verify Configuration**:
   ```python
   GET /api/ai-assistant/status
   # Should return: {"ready": true}
   ```

### Advanced Configuration

Update agent parameters at runtime:
```python
POST /api/ai-assistant/config
{
  "model": "groq:llama-3.1-70b-versatile",
  "temperature": 0.1,
  "max_tokens": 1000,
  "system_prompt": "Custom instructions..."
}
```

**Available Models**:
- `groq:llama-3.1-70b-versatile` (Default - balanced)
- `groq:llama-3.1-8b-instant` (Faster, smaller)
- `groq:mixtral-8x7b-32768` (Larger context)

## API Reference

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/status` | GET | Service health & config |
| `/query` | POST | Natural language query |
| `/analyze-product` | POST | Data product analysis |
| `/generate-sql` | POST | SQL generation |
| `/config` | GET/POST | Agent configuration |
| `/health` | GET | Health check |

### Response Format

All endpoints return JSON with standard structure:
```json
{
  "success": true,
  "response": "Agent's answer here",
  "tokens_used": 150,
  "error": null,
  "context_used": {...}
}
```

## Testing

### Run Tests
```bash
# All tests (37 tests, ~11s)
pytest tests/unit/modules/ai_assistant/ -v

# Coverage: 87-93% (excellent!)
# - agent_service.py: 93% coverage
# - __init__.py (API): 87% coverage
```

### Test Structure
- **22 tests**: `test_agent_service.py` - Core agent logic
- **15 tests**: `test_api.py` - Flask endpoints

## Usage Examples

### Python SDK Example
```python
from modules.ai_assistant.backend.agent_service import AgentService

# Initialize (requires GROQ_API_KEY in .env)
agent = AgentService()

# Simple query
result = agent.query("What is a supplier invoice?")
print(result["response"])

# Query with context
result = agent.query(
    prompt="Explain the PurchaseOrder structure",
    context={
        "data_products": ["PurchaseOrder"],
        "current_schema": "sap_s4_hana"
    }
)

# Data product analysis
result = agent.analyze_data_product(
    data_product_name="SupplierInvoice",
    question="What are the main fields?"
)

# SQL generation
result = agent.generate_sql(
    "Find all invoices over $10,000",
    table_schema={"invoices": {"columns": ["id", "amount"]}}
)
```

### API Playground Integration

The AI Assistant is accessible via the API Playground UI:
1. Navigate to "AI Assistant" tab
2. Enter your question
3. Optionally provide context
4. View structured response

## Security

### API Key Protection ✅
- **NEVER commit .env to git** (already in .gitignore)
- API key loaded via `os.getenv('GROQ_API_KEY')`
- Service fails gracefully if key missing
- No keys in code or logs

### Best Practices
- Rotate keys periodically
- Use separate keys for dev/prod
- Monitor usage at https://console.groq.com

## Performance

**Groq Performance**:
- **Speed**: ~1-2 second response times
- **Model**: llama-3.1-70b (70 billion parameters)
- **Context**: Up to 8K tokens
- **Free Tier**: 30 requests/minute

**vs. Local Models (ctransformers)**:
- Groq: 1-2s, no hardware needed
- Local: 30-60s, requires GPU/CPU load

## Dependencies

Installed automatically:
- `pydantic-ai` - Agent framework
- `groq` - Groq SDK
- `python-dotenv` - Environment management

## Migration from Old LLM Service

**Old** (ctransformers - local models):
- Required downloading large GGUF files (3-7GB)
- Slow inference (30-60 seconds)
- Windows compatibility issues
- Memory intensive

**New** (Pydantic AI + Groq - cloud):
- No model downloads needed
- Fast inference (1-2 seconds)
- Works on any OS
- Minimal memory usage
- Production-ready

## Future Enhancements

**Phase 2** (Planned):
- [ ] Streaming responses (real-time output)
- [ ] Multi-turn conversations (memory)
- [ ] Tool use (function calling)
- [ ] Integration with knowledge_graph module
- [ ] Custom prompt templates per data product

**Phase 3** (Advanced):
- [ ] RAG (Retrieval Augmented Generation)
- [ ] Fine-tuning on P2P domain knowledge
- [ ] Multi-model support (fallbacks)
- [ ] Usage analytics & cost tracking

## Troubleshooting

### "GROQ_API_KEY not found"
**Solution**: Add your key to `.env` file in project root

### "Agent error: Rate limit exceeded"
**Solution**: Wait 60 seconds or upgrade Groq plan

### "Agent error: Invalid model"
**Solution**: Check available models at https://console.groq.com

## Module Information

- **Version**: 1.0.0
- **Status**: ✅ Production Ready
- **Tests**: 37/37 passing (100%) in 11s
- **Coverage**: 87-93%
- **Dependencies**: pydantic-ai, groq, python-dotenv
- **API Prefix**: `/api/ai-assistant`

## Related Documentation

- [[Pydantic AI Documentation]]
- [[Groq API Reference]]
- [[Knowledge Graph Integration]]
- [[API Playground Usage]]