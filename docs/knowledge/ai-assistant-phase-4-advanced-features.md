# AI Assistant Phase 4: Advanced Features

**Status**: 🟢 PLANNED  
**Version**: To be v4.43  
**Date**: February 13, 2026  
**Effort**: 8-12 hours (estimated)

---

## 🎯 Overview

Phase 4 adds advanced UX features to make the AI Assistant more powerful and user-friendly:
- **Streaming responses**: Real-time typing effect (like ChatGPT)
- **Code syntax highlighting**: Beautiful code display with highlight.js
- **Copy code button**: One-click copy for code blocks
- **SQL execution**: Run SQL directly from chat (with confirmation)
- **Conversation search**: Find messages across all conversations

---

## 📋 Phase 4 Features

### 1. Streaming Responses (4 hours) - PRIORITY 1

**Goal**: Real-time typing effect instead of batch responses

**Current Behavior** (Phase 3):
```
User: "Explain P2P"
[2 second wait]
Assistant: [Full response appears instantly]
```

**Target Behavior** (Phase 4):
```
User: "Explain P2P"
Assistant: [Text appears word-by-word, like typing]
"Procure..." → "Procure-to-Pay..." → "Procure-to-Pay is..."
```

**Technical Approach**:
- **Backend**: Server-Sent Events (SSE) endpoint
  - New endpoint: `POST /api/ai-assistant/conversations/{id}/messages/stream`
  - Groq streaming API: `agent.run_stream()`
  - Yield text chunks as they arrive
  - SSE format: `data: {"text": "chunk"}\n\n`

- **Frontend**: EventSource API
  - Replace `fetch()` with `EventSource`
  - Append text chunks to message container
  - Close stream on completion
  - Fallback to batch if stream fails

**Files to Modify**:
1. `modules/ai_assistant/backend/api.py` - Add SSE endpoint
2. `modules/ai_assistant/backend/services/agent_service.py` - Add streaming method
3. `modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js` - Add streaming method
4. `modules/ai_assistant/frontend/views/AIAssistantOverlay.js` - Use streaming in UI

**Benefits**:
- ✅ Better UX (perceived speed)
- ✅ User feedback during long responses
- ✅ More engaging interaction

---

### 2. Code Syntax Highlighting (2 hours) - PRIORITY 2

**Goal**: Beautiful code display with syntax highlighting

**Current Behavior**:
```
Assistant: "Here's some Python:
def hello():
    print('world')
"
[Plain text, no colors]
```

**Target Behavior**:
```
Assistant: "Here's some Python:
[Syntax-highlighted code block with colors]
def hello():      # 'def' in purple, 'hello' in blue
    print('world')  # 'print' in purple, string in green
```

**Technical Approach**:
- **Library**: highlight.js (CDN)
  - Load: `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js`
  - CSS: `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css`

- **Detection**: Markdown code fences
  ```python
  import re
  code_pattern = r'```(\w+)\n(.*?)```'
  ```

- **Rendering**: Replace text with highlighted HTML
  ```javascript
  const code = extractCodeBlock(text);
  const html = `<pre><code class="language-python">${code}</code></pre>`;
  hljs.highlightElement(codeElement);
  ```

**Files to Modify**:
1. `modules/ai_assistant/frontend/views/AIAssistantOverlay.js` - Add highlight.js loader + code detection

**Languages to Support**:
- Python (primary)
- SQL (for database queries)
- JavaScript (for frontend code)
- JSON (for data examples)

**Benefits**:
- ✅ Better readability
- ✅ Professional appearance
- ✅ Easier to understand code

---

### 3. Copy Code Button (1 hour) - PRIORITY 3

**Goal**: One-click copy for code blocks

**Current Behavior**:
```
[Code block shown]
[User must manually select and copy]
```

**Target Behavior**:
```
┌──────────────────────┐
│ def hello():         │
│     print('world')   │
│ [Copy Code] ✓        │  <- Button appears on hover
└──────────────────────┘
```

**Technical Approach**:
- **Button Placement**: Top-right corner of code block
- **Copy API**: `navigator.clipboard.writeText(code)`
- **Feedback**: Button text changes "Copy" → "Copied!" → "Copy"
- **Styling**: Minimal, matches SAP Fiori theme

**Implementation**:
```javascript
function addCopyButtons() {
    document.querySelectorAll('pre code').forEach(block => {
        const button = document.createElement('button');
        button.textContent = 'Copy';
        button.className = 'copy-code-btn';
        button.onclick = async () => {
            await navigator.clipboard.writeText(block.textContent);
            button.textContent = 'Copied!';
            setTimeout(() => button.textContent = 'Copy', 2000);
        };
        block.parentElement.style.position = 'relative';
        block.parentElement.appendChild(button);
    });
}
```

**Files to Modify**:
1. `modules/ai_assistant/frontend/views/AIAssistantOverlay.js` - Add copy button logic
2. `app_v2/static/css/ai-assistant.css` - Add button styling

**Benefits**:
- ✅ Faster workflow (no manual selection)
- ✅ Fewer copy errors
- ✅ Better UX

---

### 4. SQL Execution from Chat (3-4 hours) - PRIORITY 4

**Goal**: Execute SQL queries directly from chat interface

**Workflow**:
```
User: "Show me all suppliers with rating > 4.5"
Assistant: "Here's the SQL:
```sql
SELECT * FROM suppliers WHERE rating > 4.5
```
Would you like me to execute this?"
[Execute SQL] [Cancel]  <- User clicks button

[Results shown in table format]
```

**Technical Approach**:

**Detection**:
```python
# Backend: Detect SQL in AI response
sql_pattern = r'```sql\n(.*?)```'
if re.search(sql_pattern, response):
    return {
        "message": response,
        "executable_sql": extracted_sql,
        "requires_confirmation": True
    }
```

**Execution**:
- **Frontend**: Show [Execute SQL] button
- **User clicks**: Confirm dialog
- **Backend**: Execute via data_products API
- **Frontend**: Display results in sap.m.Table

**Safety**:
- ✅ **User confirmation required** (no auto-execution)
- ✅ **Read-only queries only** (SELECT, no UPDATE/DELETE)
- ✅ **Query validation** (reject dangerous queries)
- ✅ **Result limits** (max 1000 rows)

**Files to Modify**:
1. `modules/ai_assistant/backend/services/agent_service.py` - Add SQL detection
2. `modules/ai_assistant/backend/api.py` - Add execute endpoint
3. `modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js` - Add execute method
4. `modules/ai_assistant/frontend/views/AIAssistantOverlay.js` - Add execute button + results table

**Benefits**:
- ✅ Instant query execution
- ✅ No context switching (stay in chat)
- ✅ Visual results

---

### 5. Conversation Search (2 hours) - PRIORITY 5

**Goal**: Full-text search across all conversations

**UI Design**:
```
┌─────────────────────────┐
│ [🔍 Search...        ] │  <- Search input
├─────────────────────────┤
│ Conversations (Filtered)│
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ ...found 3 suppliers │ <- Matching message
│ │ in conversation 1    │ <- Highlighted
│ └─────────────────────┘ │
└─────────────────────────┘
```

**Technical Approach**:
- **Search Method**: Simple string matching (case-insensitive)
  ```javascript
  function searchConversations(query) {
      const results = [];
      for (const [id, conv] of Object.entries(this.conversations)) {
          const matches = conv.messages.filter(msg => 
              msg.text.toLowerCase().includes(query.toLowerCase())
          );
          if (matches.length > 0) {
              results.push({ conversation: conv, matches });
          }
      }
      return results;
  }
  ```

- **UI Updates**:
  - Filter conversation list based on search
  - Highlight matching text in messages
  - Show match count per conversation

**Files to Modify**:
1. `modules/ai_assistant/frontend/views/AIAssistantOverlay.js` - Add search input + filter logic

**Future Enhancement** (Phase 5):
- Regex support
- Date filtering
- Message type filtering (user vs assistant)

**Benefits**:
- ✅ Find past conversations quickly
- ✅ Reference previous answers
- ✅ Better knowledge management

---

## 🎯 Implementation Priority

**Recommended Order**:
1. **Code syntax highlighting** (2h) - Easiest, high visual impact
2. **Copy code button** (1h) - Quick win, depends on #1
3. **Conversation search** (2h) - Pure frontend, no backend changes
4. **Streaming responses** (4h) - Most complex, requires backend + frontend
5. **SQL execution** (3-4h) - Complex, requires safety validation

**Rationale**: Start with easy wins (highlighting + copy), build momentum, then tackle complex features

---

## 🧪 Testing Strategy

### Unit Tests (Gu Wu-Conform)
- **Backend**: Agent service with streaming (pytest)
- **Backend**: SQL detection and validation (pytest)
- **Frontend**: E2E tests for new features (pytest via Playwright)

### Manual Testing Checklist
- [ ] Streaming: Text appears word-by-word
- [ ] Highlighting: Python/SQL/JavaScript colored correctly
- [ ] Copy button: Copies to clipboard successfully
- [ ] SQL execution: Only safe queries allowed
- [ ] Search: Finds messages across conversations

---

## 📊 Effort Breakdown

| Feature | Backend | Frontend | Tests | Total |
|---------|---------|----------|-------|-------|
| Streaming responses | 2h | 1.5h | 0.5h | 4h |
| Code highlighting | 0h | 1.5h | 0.5h | 2h |
| Copy button | 0h | 0.5h | 0.5h | 1h |
| SQL execution | 1.5h | 1.5h | 1h | 4h |
| Search | 0h | 1.5h | 0.5h | 2h |
| **TOTAL** | **3.5h** | **6.5h** | **3h** | **13h** |

**Note**: Estimate includes testing time (unlike Phase 3 estimate)

---

## 🔄 Dependencies

**Required Before Phase 4**:
- ✅ Phase 1 complete (Shell overlay)
- ✅ Phase 2 complete (Conversation API)
- ✅ Phase 3 complete (localStorage + history)

**No Blockers**: Phase 4 can start immediately

---

## 📁 Files to Create/Modify

### New Files (0):
- None (all enhancements to existing files)

### Modified Files (5-6):
1. `modules/ai_assistant/backend/api.py` - SSE endpoint, SQL endpoint
2. `modules/ai_assistant/backend/services/agent_service.py` - Streaming, SQL detection
3. `modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js` - Streaming, SQL methods
4. `modules/ai_assistant/frontend/views/AIAssistantOverlay.js` - UI for all features
5. `app_v2/static/css/ai-assistant.css` - Styling for code blocks + buttons
6. `tests/e2e/app_v2/test_ai_assistant_phase4.py` - E2E tests (NEW)

---

## 🚀 Quick Start (For Implementation)

### Step 1: Code Highlighting (2h)
```bash
# 1. Add highlight.js to AIAssistantOverlay.js
# 2. Detect ```language\n code ``` blocks
# 3. Apply hljs.highlightElement()
# 4. Test with Python/SQL/JavaScript examples
```

### Step 2: Copy Button (1h)
```bash
# 1. Add button to each <pre><code> block
# 2. Wire up navigator.clipboard.writeText()
# 3. Add CSS styling
# 4. Test copy functionality
```

### Step 3: Search (2h)
```bash
# 1. Add search input to sidebar
# 2. Filter conversations on keyup
# 3. Highlight matching text
# 4. Test with various queries
```

### Step 4: Streaming (4h)
```bash
# 1. Backend: Add SSE endpoint with Groq streaming
# 2. Frontend: Replace fetch() with EventSource
# 3. Handle connection errors gracefully
# 4. Test with long responses
```

### Step 5: SQL Execution (4h)
```bash
# 1. Backend: SQL detection + validation
# 2. Backend: Execute endpoint with safety checks
# 3. Frontend: [Execute SQL] button + confirmation
# 4. Frontend: Results table rendering
# 5. Test with safe/unsafe queries
```

---

## ⚠️ Important Considerations

### Security (SQL Execution)
- ⚠️ **CRITICAL**: Only SELECT queries (no INSERT/UPDATE/DELETE)
- ⚠️ **CRITICAL**: User confirmation required
- ⚠️ **CRITICAL**: Query validation (reject DROP, TRUNCATE, etc.)
- ⚠️ **CRITICAL**: Result limits (max 1000 rows)

### Performance (Streaming)
- ⚠️ **Token efficiency**: Stream reduces perceived latency
- ⚠️ **Error handling**: Graceful fallback if stream fails
- ⚠️ **Connection management**: Close streams properly

### UX (Code Highlighting)
- ⚠️ **Language detection**: Auto-detect from ```language tags
- ⚠️ **Theme**: Use "github" theme (matches SAP Fiori light)
- ⚠️ **Loading**: Load highlight.js async (don't block page)

---

## 📚 Architecture Decisions

### Why Server-Sent Events (SSE) for Streaming?

**Chosen**: SSE (one-way server→client)

**Alternatives Considered**:
- ❌ WebSockets (two-way, overkill for streaming)
- ❌ Long polling (inefficient, not real-time)

**Benefits of SSE**:
- ✅ Simple HTTP (no special protocol)
- ✅ Auto-reconnection built-in
- ✅ Perfect for one-way streaming
- ✅ Works with Groq streaming API

---

### Why highlight.js Instead of Prism?

**Chosen**: highlight.js

**Alternatives Considered**:
- ❌ Prism.js (requires manual language loading)
- ❌ Monaco Editor (too heavy for display-only)

**Benefits of highlight.js**:
- ✅ Auto language detection
- ✅ 190+ languages supported
- ✅ Small bundle size (~100KB)
- ✅ CDN available (no npm install)
- ✅ SAP Fiori-compatible themes

---

## 🧪 Testing Checklist

### E2E Tests (Gu Wu-Conform)

**File**: `tests/e2e/app_v2/test_ai_assistant_phase4.py`

```python
@pytest.mark.e2e
@pytest.mark.app_v2
def test_streaming_response(app_v2_base_url):
    """Test: Streaming response delivers text incrementally"""
    # ARRANGE
    conversation_id = create_test_conversation()
    
    # ACT
    response = requests.post(
        f"{app_v2_base_url}/api/ai-assistant/conversations/{conversation_id}/messages/stream",
        json={"message": "Explain P2P"},
        stream=True
    )
    
    # ASSERT
    chunks = []
    for line in response.iter_lines():
        if line:
            chunks.append(line.decode('utf-8'))
    
    assert len(chunks) > 1, "Should receive multiple chunks"
    assert response.status_code == 200

@pytest.mark.e2e
@pytest.mark.app_v2
def test_code_highlighting_applied(browser_page):
    """Test: Code blocks are syntax highlighted"""
    # ARRANGE
    browser_page.goto("http://localhost:5000/")
    send_message_with_code(browser_page)
    
    # ACT
    code_block = browser_page.locator('pre code.hljs')
    
    # ASSERT
    assert code_block.is_visible()
    assert 'hljs' in code_block.get_attribute('class')

@pytest.mark.e2e
@pytest.mark.app_v2
def test_copy_code_button_works(browser_page):
    """Test: Copy button copies code to clipboard"""
    # ARRANGE
    send_message_with_code(browser_page)
    
    # ACT
    copy_button = browser_page.locator('.copy-code-btn')
    copy_button.click()
    
    # ASSERT
    assert copy_button.text_content() == 'Copied!'

@pytest.mark.e2e
@pytest.mark.app_v2
def test_sql_execution_requires_confirmation(app_v2_base_url):
    """Test: SQL execution requires user confirmation"""
    # ARRANGE
    conversation_id = create_test_conversation()
    send_message_with_sql(conversation_id)
    
    # ACT
    response = requests.post(
        f"{app_v2_base_url}/api/ai-assistant/conversations/{conversation_id}/execute-sql",
        json={"sql": "SELECT * FROM suppliers"}
    )
    
    # ASSERT
    assert response.status_code == 200
    assert 'results' in response.json()

@pytest.mark.e2e
@pytest.mark.app_v2
def test_unsafe_sql_rejected(app_v2_base_url):
    """Test: Unsafe SQL queries are rejected"""
    # ARRANGE
    conversation_id = create_test_conversation()
    
    # ACT
    response = requests.post(
        f"{app_v2_base_url}/api/ai-assistant/conversations/{conversation_id}/execute-sql",
        json={"sql": "DROP TABLE suppliers"}
    )
    
    # ASSERT
    assert response.status_code == 400
    assert 'unsafe' in response.json()['error'].lower()

@pytest.mark.e2e
@pytest.mark.app_v2
def test_conversation_search_filters(browser_page):
    """Test: Search filters conversation list"""
    # ARRANGE
    create_multiple_conversations()
    browser_page.goto("http://localhost:5000/")
    
    # ACT
    search_input = browser_page.locator('#ai-conversation-search')
    search_input.fill('supplier')
    
    # ASSERT
    visible_conversations = browser_page.locator('.conversation-item:visible')
    assert visible_conversations.count() < total_conversations
```

---

## 📋 Implementation Checklist

### Phase 4.1: Code Highlighting (2h)
- [ ] Load highlight.js library (CDN)
- [ ] Detect code blocks in messages (```language pattern)
- [ ] Apply syntax highlighting on message render
- [ ] Test with Python/SQL/JavaScript examples
- [ ] Add CSS for code block styling
- [ ] Write E2E test

### Phase 4.2: Copy Button (1h)
- [ ] Add copy button to code blocks
- [ ] Implement clipboard copy logic
- [ ] Add "Copied!" feedback animation
- [ ] Add CSS styling for button
- [ ] Test copy functionality
- [ ] Write E2E test

### Phase 4.3: Search (2h)
- [ ] Add search input to conversation sidebar
- [ ] Implement filter logic (case-insensitive)
- [ ] Highlight matching text in results
- [ ] Update UI on search input
- [ ] Test with various search terms
- [ ] Write E2E test

### Phase 4.4: Streaming (4h)
- [ ] Backend: Add SSE endpoint
- [ ] Backend: Implement Groq streaming
- [ ] Frontend: Replace fetch() with EventSource
- [ ] Frontend: Append chunks to message
- [ ] Frontend: Handle stream errors
- [ ] Test with long responses
- [ ] Write E2E test

### Phase 4.5: SQL Execution (4h)
- [ ] Backend: SQL detection in responses
- [ ] Backend: SQL validation (safety checks)
- [ ] Backend: Execute endpoint with data_products integration
- [ ] Frontend: [Execute SQL] button
- [ ] Frontend: Confirmation dialog
- [ ] Frontend: Results table rendering
- [ ] Test safe and unsafe queries
- [ ] Write E2E tests (2 tests)

---

## 🎯 Success Criteria

### Phase 4 Complete When:
- ✅ Code blocks syntax highlighted (Python/SQL/JavaScript)
- ✅ Copy button works on all code blocks
- ✅ Search filters conversations by text
- ✅ Streaming responses show real-time typing
- ✅ SQL execution works with safety validation
- ✅ 7 E2E tests passing (Gu Wu-conform)
- ✅ Zero UX dependencies (testable via pytest)

---

## 📚 Related Documentation

- [[AI Assistant Phase 2 Implementation]] - Conversation API foundation
- [[AI Assistant Phase 3 Conversation Enhancement]] - localStorage + history
- [[AI Assistant UX Design]] - Original Fiori design
- [[Groq API Reference]] - Streaming API details
- [[Pydantic AI Framework]] - Agent architecture

---

## 🔮 Phase 5+ Future Ideas

1. **Conversation branching** - Fork conversations at any message
2. **Multi-user support** - Share conversations with team
3. **Voice input** - Speech-to-text for hands-free
4. **Conversation analytics** - Most asked questions, usage patterns
5. **AI memory** - Remember user preferences across sessions
6. **Suggested questions** - AI proposes follow-up questions
7. **Conversation templates** - Quick start templates for common tasks

---

**Status**: 🟢 READY TO START - Phase 3 complete, no blockers