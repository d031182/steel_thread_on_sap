# AI Assistant v2 - Conversational AI with Pydantic AI

**Version**: 1.0.0  
**Status**: Phase 1 - Frontend Implementation  
**Framework**: Pydantic AI + Groq + SAPUI5

---

## 🎯 Overview

Modern conversational AI assistant that queries P2P datasources with type-safe responses and ChatGPT-style UX.

### Key Features
- ✅ Pydantic AI framework (type-safe, structured outputs)
- ✅ Groq `llama-3.3-70b-versatile` backend (10x faster inference)
- ✅ ChatGPT-style overlay UI (SAP Fiori compliant)
- ✅ Query active P2P datasource
- ✅ Industry-standard chatbot UX
- 🔄 RAG capabilities (future phase)

---

## 🏗️ Architecture

### Backend (Python)
```
backend/
├── __init__.py
├── api.py                    # Flask Blueprint
├── agent_service.py          # Pydantic AI Agent
├── models.py                 # Pydantic response models
└── tools/
    ├── __init__.py
    └── datasource_tool.py    # P2P data queries
```

### Frontend (SAPUI5)
```
frontend/
├── module.js                 # App v2 registration
├── adapters/
│   └── AIAssistantAdapter.js # API client
├── views/
│   └── AIAssistantOverlay.js # Chat UI
└── css/
    └── assistant.css         # Custom styling
```

---

## 🚀 Quick Start

### Installation

```bash
# Install Python dependencies
pip install pydantic-ai pydantic-ai[groq]

# No frontend build needed (SAPUI5 runtime)
```

### Usage

**1. Open AI Assistant**:
- Click "AI Assistant" button in app shell
- Or press `Ctrl+Shift+A` (future)

**2. Ask Questions**:
```
User: "What suppliers have rating above 4.5?"
AI: "Found 3 suppliers: ACME (4.8), Globex (4.7), Initech (4.6)"
```

**3. Query Datasource**:
```
User: "Show me pending invoices for ACME"
AI: [Queries P2P data] "ACME has 5 pending invoices totaling $12,450"
```

---

## 🎨 UI Design

### Overlay Window
- **Type**: `sap.m.Dialog` (resizable, draggable)
- **Size**: 600px × 700px
- **Style**: ChatGPT-like (modern, minimal)
- **Behavior**: Non-modal (app interaction continues)

### Message Types
1. **User**: Right-aligned, blue accent (#0070f2)
2. **AI**: Left-aligned, gray accent (#6a6d70)
3. **System**: Centered, italic
4. **Error**: Red accent with retry button

---

## 🔧 API Reference

### POST /api/ai-assistant/chat

**Request**:
```json
{
  "message": "Your question here",
  "conversation_id": "uuid-optional",
  "context": {
    "datasource": "p2p_data"
  }
}
```

**Response**:
```json
{
  "success": true,
  "response": {
    "message": "AI response text",
    "confidence": 0.95,
    "sources": ["Supplier table"],
    "suggested_actions": [],
    "requires_clarification": false
  },
  "conversation_id": "uuid",
  "timestamp": "2026-02-13T20:30:00Z"
}
```

---

## 🧪 Testing

### Run Tests
```bash
# Unit tests (backend)
pytest tests/unit/ -v

# E2E tests (frontend + backend)
pytest tests/e2e/ -v --browser chromium
```

### Test Coverage
- **Unit Tests**: Agent service, API endpoints, tools
- **E2E Tests**: Overlay opens, message sending, response display
- **Target**: 90%+ coverage

---

## 📋 Implementation Status

### Phase 1: Frontend UI (IN PROGRESS) ⭐
- [x] Module structure
- [x] module.json configuration
- [ ] AIAssistantOverlay.js (SAPUI5)
- [ ] AIAssistantAdapter.js (API client)
- [ ] Shell button integration
- [ ] Custom styling (Fiori-compliant)
- [ ] E2E tests

### Phase 2: Pydantic AI Backend (PLANNED)
- [ ] Pydantic AI agent setup
- [ ] Response models
- [ ] Datasource tool
- [ ] Flask API endpoint
- [ ] Unit tests
- [ ] Frontend integration

### Phase 3: RAG Implementation (FUTURE)
- [ ] Document indexing
- [ ] RAG retriever
- [ ] Tool integration
- [ ] Performance optimization

---

## 🎓 Key Technologies

### Pydantic AI
- **Framework**: Type-safe AI agents
- **Model**: Groq `llama-3.3-70b-versatile`
- **Benefits**: Structured outputs, validation, tools

### SAPUI5 Dialog
- **Component**: `sap.m.Dialog`
- **Pattern**: Overlay window
- **Features**: Resizable, draggable, Fiori-compliant

### Groq LLM
- **Model**: llama-3.3-70b-versatile
- **Speed**: 10x faster than standard APIs
- **Cost**: Lower than OpenAI

---

## 📚 Related Documentation

- [[Pydantic AI Framework]] - Framework details
- [[AI Assistant UX Design]] - Original design
- [[SAP Fiori Design Standards]] - UI guidelines

---

## 🤝 Contributing

Follow project standards:
- ✅ **Gu Wu testing** (100% coverage, AAA pattern)
- ✅ **Feng Shui quality** (DI, no violations)
- ✅ **SAP Fiori compliance** (standard controls)

---

**Current Phase**: Phase 1 (Frontend UI Implementation)  
**Next Session**: Complete overlay UI + shell button