# AI Assistant v2 - Pydantic AI Implementation

**Version**: 1.0  
**Last Updated**: February 13, 2026  
**Status**: Phase 1 In Progress  
**Purpose**: Modern conversational AI assistant with Pydantic AI + Groq

---

## 🎯 Project Overview

### What We're Building
A ChatGPT-style conversational AI assistant that:
- ✅ Queries active P2P datasource
- ✅ Uses Pydantic AI for type-safe responses
- ✅ Groq `llama-3.3-70b-versatile` backend
- ✅ Modern overlay UI (SAP Fiori compliant)
- ✅ RAG capabilities (future phases)

### User Requirements (Confirmed)
1. **Priority**: UI first (Phase 3 before Phase 2)
2. **Datasource**: Active datasource only (not historical)
3. **RAG Content**: TBD (Phase 2)
4. **UI Style**: Fiori shell button + overlay (separate icon alternate)
5. **LLM**: Continue with `llama-3.3-70b-versatile`

---

## 🏗️ Architecture

### Module Structure
```
modules/ai_assistant_v2/
├── backend/
│   ├── __init__.py
│   ├── api.py                    # Flask Blueprint
│   ├── agent_service.py          # Pydantic AI Agent
│   ├── models.py                 # Pydantic response models
│   └── tools/
│       ├── __init__.py
│       └── datasource_tool.py    # Query P2P data
├── frontend/
│   ├── module.js                 # App v2 registration
│   ├── adapters/
│   │   └── AIAssistantAdapter.js # API client
│   ├── views/
│   │   └── AIAssistantOverlay.js # Chat UI (SAPUI5)
│   └── css/
│       └── assistant.css         # Custom styling
├── tests/
│   ├── unit/
│   │   ├── test_agent_service.py
│   │   └── test_api.py
│   └── e2e/
│       └── test_ai_assistant_v2.py
├── module.json
└── README.md
```

### Technology Stack
| Layer | Technology | Why |
|-------|------------|-----|
| **AI Framework** | Pydantic AI | Type-safe, structured outputs |
| **LLM Backend** | Groq (llama-3.3-70b-versatile) | 10x speed, reliable |
| **Frontend** | SAPUI5 (sap.m.Dialog) | Fiori-compliant overlay |
| **API** | Flask Blueprint | Existing pattern |
| **Validation** | Pydantic v2 | Industry standard |

---

## 📋 Implementation Phases

### Phase 1: Frontend Overlay UI (PRIORITY - 12-18h) ⭐
**Goal**: ChatGPT-style overlay with industry-standard UX

**Tasks**:
- [x] Create module structure
- [ ] Implement AIAssistantOverlay.js (SAPUI5 Dialog)
- [ ] Create AIAssistantAdapter.js (API client)
- [ ] Add shell button (app header)
- [ ] Style with SAP Fiori guidelines
- [ ] Mock API responses for testing
- [ ] Write E2E tests

**Deliverable**: Working overlay UI with mock responses

### Phase 2: Pydantic AI Backend (8-12h)
**Goal**: Type-safe agent with datasource queries

**Tasks**:
- [ ] Install pydantic-ai dependencies
- [ ] Implement agent_service.py (Pydantic AI Agent)
- [ ] Create response models (models.py)
- [ ] Implement datasource tool
- [ ] Create Flask API endpoint
- [ ] Write unit tests
- [ ] Integration with frontend

**Deliverable**: Working agent querying P2P data

### Phase 3: RAG Implementation (10-15h) - FUTURE
**Goal**: Enhanced context retrieval

**Tasks**: TBD after Phase 1-2 complete

---

## 🎨 UI Design Specification

### Overlay Window (sap.m.Dialog)
```javascript
{
  title: "Joule AI Assistant",
  contentWidth: "600px",
  contentHeight: "700px",
  resizable: true,
  draggable: true,
  modal: false  // Allow interaction with app
}
```

### Message Types
1. **User Messages**: Right-aligned, blue accent
2. **AI Messages**: Left-aligned, gray accent
3. **System Messages**: Centered, italic
4. **Error Messages**: Red accent with retry button

### Industry-Standard UX Features
- ✅ Auto-scroll to latest message
- ✅ Typing indicator during AI processing
- ✅ Message timestamps
- ✅ Input grows with text (up to 5 lines)
- ✅ Send on Enter, Shift+Enter for newline
- ✅ Disabled input during processing
- ✅ Conversation history (session-based)

---

## 🔧 API Design

### Endpoint: POST /api/ai-assistant/chat

**Request**:
```json
{
  "message": "What suppliers have rating above 4.5?",
  "conversation_id": "uuid",
  "context": {
    "datasource": "p2p_data",
    "user_id": "D031182"
  }
}
```

**Response** (Pydantic-validated):
```json
{
  "success": true,
  "response": {
    "message": "Found 3 suppliers with rating above 4.5...",
    "confidence": 0.95,
    "sources": ["Supplier table query"],
    "suggested_actions": [
      {"text": "Show details", "action": "view_details"}
    ],
    "requires_clarification": false
  },
  "conversation_id": "uuid",
  "timestamp": "2026-02-13T20:30:00Z"
}
```

---

## 📊 Pydantic Models

### Response Models
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class SuggestedAction(BaseModel):
    text: str
    action: str
    params: Optional[dict] = None

class AssistantResponse(BaseModel):
    message: str = Field(description="AI response text")
    confidence: float = Field(ge=0.0, le=1.0, description="Response confidence")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    suggested_actions: Optional[List[SuggestedAction]] = None
    requires_clarification: bool = False

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    success: bool
    response: Optional[AssistantResponse] = None
    error: Optional[str] = None
    conversation_id: str
    timestamp: str
```

---

## 🧪 Testing Strategy

### Unit Tests (Gu Wu Standards)
```python
@pytest.mark.unit
@pytest.mark.fast
def test_agent_responds_with_valid_structure():
    """Test: Agent returns Pydantic-validated response"""
    # ARRANGE
    agent = create_test_agent()
    
    # ACT
    result = agent.run_sync("test query")
    
    # ASSERT
    assert isinstance(result.data, AssistantResponse)
    assert 0.0 <= result.data.confidence <= 1.0
    assert len(result.data.message) > 0
```

### E2E Tests (Playwright)
```python
@pytest.mark.e2e
@pytest.mark.app_v2
def test_overlay_opens_and_sends_message(page):
    """Test: User can open overlay and send message"""
    # ARRANGE
    page.goto("http://localhost:5000/v2")
    
    # ACT
    page.click("button[data-action='open-ai-assistant']")
    page.fill("textarea[placeholder*='Ask']", "Test message")
    page.click("button[aria-label='Send']")
    
    # ASSERT
    assert page.locator(".assistantMessage").count() > 0
```

---

## 📝 Next Steps

### Immediate (This Session)
1. ✅ Create documentation (this file)
2. [ ] Create module structure
3. [ ] Implement AIAssistantOverlay.js
4. [ ] Add shell button
5. [ ] Mock API for testing

### Follow-up (Next Session)
1. [ ] Implement Pydantic AI backend
2. [ ] Connect frontend to real API
3. [ ] Write comprehensive tests
4. [ ] Deploy and validate

---

## 📚 Related Documentation

- [[Pydantic AI Framework]] - Framework details
- [[AI Assistant UX Design]] - Original design (archived module)
- [[SAP Fiori Design Standards]] - UI guidelines
- [[App V2 Modular Architecture]] - Integration pattern

---

## 🎓 Key Decisions

### Why Pydantic AI?
- ✅ Type-safe responses (no parsing errors)
- ✅ Structured outputs (validated schemas)
- ✅ Model-agnostic (easy Groq integration)
- ✅ Production-ready (observability built-in)

### Why UI First?
- User priority: See working interface ASAP
- Can mock backend responses initially
- Validates UX before backend investment
- Allows parallel frontend/backend development

### Why Overlay Window?
- Industry standard (ChatGPT, Copilot)
- Non-blocking (user can still see app)
- Resizable/draggable (flexible)
- SAP Fiori compliant (sap.m.Dialog)

---

**Status**: Ready to implement Phase 1 (Frontend Overlay)