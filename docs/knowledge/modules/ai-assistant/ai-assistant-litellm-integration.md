# AI Assistant LiteLLM Integration

**Date**: February 20, 2026
**Status**: ✅ Complete
**Version**: 1.0

## Overview

Enhanced the AI Assistant module with LiteLLM support alongside existing providers (Groq, GitHub Models, SAP AI Core). LiteLLM provides a unified interface to 100+ AI models through a local proxy server.

## Implementation Details

### Configuration

Added LiteLLM provider support in `agent_service.py` with environment variables:

```bash
# .env configuration
AI_PROVIDER=litellm
LITELLM_BASE_URL=http://localhost:6655/litellm/v1
LITELLM_API_KEY=4930f138-112d-4d69-bf98-77a7e5dbebc5
LITELLM_MODEL_NAME=gpt-4.1-mini
```

### Multi-Provider Architecture

The AI Assistant now supports 4 providers:

1. **LiteLLM** (new): Local proxy for multiple models
   - Base URL: http://localhost:6655/litellm/v1
   - Model: gpt-4.1-mini
   - API Key: Custom key for authentication

2. **Groq**: Ultra-fast LPU inference
3. **GitHub Models**: OpenAI via Azure
4. **SAP AI Core**: Enterprise OpenAI deployment

### Enhanced System Prompts

Updated both structured and streaming agent prompts with:

- **Comprehensive Data Capabilities**: Multi-source querying (SQLite + HANA)
- **Smart P2P Queries**: Automatic question-to-SQL mapping
- **Business Intelligence**: KPI calculation and insights
- **Tool Documentation**: Clear usage patterns for AI

### Key Features

#### Data Product Discovery
- List all available data products across sources
- Show metadata (table count, version, description)
- Explore table structures and relationships

#### Smart Query Generation
Users can ask natural language questions:
- "Show me all data products" → Uses `list_data_products` tool
- "How many invoices?" → Generates `SELECT COUNT(*) FROM SupplierInvoice`
- "Highest value invoice" → Generates `ORDER BY InvoiceAmount DESC LIMIT 1`

#### Multi-Source Support
- **SQLite**: Local development (PascalCase tables)
- **HANA Cloud**: Production SAP data (P2P_DATAPRODUCT_sap_bdc_*_V1)
- Automatic syntax adaptation

## Integration Points

### Repository Factory
Leverages existing `RepositoryFactory` for data access:

```python
from modules.data_products_v2.repositories.repository_factory import RepositoryFactory

# Auto-detects datasource and returns appropriate repository
repository = RepositoryFactory.create('sqlite')  # or 'hana'
```

### Tool Registration
Three core tools available to AI:

1. **list_data_products()** - Show available data products
2. **query_p2p(entity_type, filters, limit)** - Query specific entities  
3. **execute_sql(sql_query)** - Run custom SQL (SELECT only)

## Security Features

- **SQL Injection Prevention**: All queries validated
- **Read-Only Access**: Only SELECT statements allowed
- **Query Limits**: Automatic LIMIT 1000 enforcement
- **Input Sanitization**: Parameterized queries

## Usage Examples

### Environment Setup
```bash
# Start LiteLLM server (separate terminal)
litellm --config config.yaml --port 6655

# Set environment variables
AI_PROVIDER=litellm
LITELLM_BASE_URL=http://localhost:6655/litellm/v1
LITELLM_API_KEY=4930f138-112d-4d69-bf98-77a7e5dbebc5
LITELLM_MODEL_NAME=gpt-4.1-mini
```

### Chat Interactions
Users can now ask sophisticated questions:

- **Data Discovery**: "What data products are available?"
- **Business Queries**: "Show me overdue invoices"
- **Analytics**: "Which supplier has the most purchase orders?"
- **KPI Calculation**: "What's our average invoice processing time?"

## Technical Architecture

### Enhanced Context Building
- Dynamic HANA table name injection when needed
- Conversation history preservation
- Datasource-specific SQL syntax adaptation

### Streaming Support
- Real-time text streaming for better UX
- Tool execution during streaming
- Proper error handling and recovery

## Benefits

1. **Flexibility**: Support for 100+ models via LiteLLM
2. **Performance**: Local proxy reduces latency
3. **Cost Control**: Better model selection and usage tracking
4. **Development**: Easier testing with multiple models
5. **Intelligence**: Advanced data query capabilities

## Future Enhancements

- **Model Routing**: Automatic best model selection
- **Caching**: Query result caching for performance
- **Analytics**: Usage metrics and optimization
- **Security**: Enhanced access controls

## Dependencies

- **LiteLLM**: Proxy server for model access
- **Pydantic AI**: Structured AI interactions
- **Repository Pattern**: Clean data access abstraction
- **Environment Configuration**: Flexible provider switching

---

**Result**: AI Assistant now provides comprehensive data querying capabilities with LiteLLM integration, enabling users to interact with P2P data using natural language while maintaining security and performance.