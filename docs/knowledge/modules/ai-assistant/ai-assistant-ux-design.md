# AI Assistant UX Design - Fiori Compliant

**Status**: Proposed Design  
**Date**: February 6, 2026  
**Author**: P2P Development Team  
**Purpose**: Industry-standard AI chat interface using SAP Fiori + SAPUI5

---

## 🎯 Design Goals

### Primary Objectives
1. **Fiori Compliance**: Follow SAP Fiori design guidelines for consistency
2. **Intuitive**: ChatGPT-like experience (familiar to users)
3. **Context-Aware**: Integrate current data product information
4. **Performant**: Handle 20-25s response times gracefully
5. **Professional**: Enterprise-grade UI suitable for SAP environments

### User Expectations
- Natural conversation flow
- Clear visual distinction between user and AI messages
- Loading states during AI processing
- Error handling with helpful messages
- Ability to retry failed queries
- Conversation history (session-based)

---

## 🏗️ Architecture

### Component Structure
```
modules/ai_assistant/
├── frontend/
│   ├── Component.js          # SAPUI5 component definition
│   ├── manifest.json          # App descriptor
│   ├── controller/
│   │   └── Chat.controller.js # Main chat controller
│   ├── view/
│   │   └── Chat.view.xml      # Chat UI layout
│   ├── model/
│   │   └── formatter.js       # Display formatters
│   └── css/
│       └── style.css          # Custom styling
└── backend/
    └── __init__.py            # (Already implemented)
```

### Integration Points
1. **Data Context**: Pass current schema/table info to AI
2. **API Playground**: Integrate as tab or separate page
3. **Navigation**: Access from main app navigation
4. **State Management**: Use SAPUI5 JSONModel for messages

---

## 🎨 UI Components (SAPUI5)

### 1. Main Container: `sap.m.Page`
```xml
<Page
    title="AI Assistant"
    showNavButton="true"
    navButtonPress=".onNavBack"
    class="sapUiResponsiveContentPadding">
    <content>
        <!-- Chat content here -->
    </content>
    <footer>
        <!-- Input area here -->
    </footer>
</Page>
```

**Why**: Standard Fiori page with header, content, footer pattern

---

### 2. Message Display: `sap.m.FeedListItem`

**Industry Standard Comparison**:
| Pattern | Example | Fiori Equivalent |
|---------|---------|------------------|
| Chat bubbles | WhatsApp, Teams | `sap.m.FeedListItem` |
| Message list | Slack | `sap.m.List` + custom items |
| Timeline | Twitter | `sap.suite.ui.commons.Timeline` |

**Recommendation**: `sap.m.FeedListItem` (closest to chat experience)

```xml
<List
    id="messageList"
    mode="None"
    growing="true"
    growingThreshold="20"
    growingScrollToLoad="true"
    noDataText="Start a conversation with the AI Assistant">
    
    <!-- User Message Template -->
    <FeedListItem
        sender="{message>sender}"
        timestamp="{message>timestamp}"
        text="{message>text}"
        icon="{= ${message>type} === 'user' ? 'sap-icon://person-placeholder' : 'sap-icon://collaborate'}"
        iconDensityAware="false"
        class="{= ${message>type} === 'user' ? 'userMessage' : 'aiMessage'}"/>
</List>
```

**Why**: 
- Native Fiori control
- Shows sender, timestamp, icon
- Supports custom styling per message type
- Built-in scrolling and lazy loading

---

### 3. Input Area: `sap.m.Toolbar` + `sap.m.TextArea`

```xml
<Toolbar class="sapUiMediumMarginTop">
    <TextArea
        id="messageInput"
        value="{/currentMessage}"
        placeholder="Ask about data products, schemas, or request SQL generation..."
        rows="2"
        maxLength="2000"
        width="100%"
        growing="true"
        growingMaxLines="5"
        submit=".onSendMessage"
        enabled="{= !${/isLoading}}"/>
    
    <ToolbarSpacer/>
    
    <Button
        text="Send"
        type="Emphasized"
        icon="sap-icon://paper-plane"
        press=".onSendMessage"
        enabled="{= ${/currentMessage}.length > 0 &amp;&amp; !${/isLoading}}"/>
</Toolbar>
```

**Why**:
- `TextArea` supports multi-line input (better than `Input`)
- `submit` event on Enter key
- Grows up to 5 lines for longer prompts
- Disabled during AI processing

---

### 4. Loading State: `sap.m.BusyIndicator`

```xml
<!-- In message list -->
<CustomListItem visible="{/isLoading}" class="aiLoadingMessage">
    <HBox alignItems="Center" justifyContent="Start">
        <BusyIndicator size="1rem" class="sapUiTinyMarginEnd"/>
        <Text text="AI is thinking..." class="sapUiTinyMarginBegin"/>
    </HBox>
</CustomListItem>
```

**Alternative**: Use `sap.m.MessageStrip` for inline status

**Why**: Clear visual feedback during 20-25s wait time

---

### 5. Context Panel: `sap.m.Panel` (Collapsible)

```xml
<Panel
    headerText="Current Context"
    expandable="true"
    expanded="false"
    class="sapUiResponsiveMargin">
    <content>
        <VBox>
            <Label text="Data Product:" class="sapUiTinyMarginBottom"/>
            <Text text="{/currentDataProduct}"/>
            
            <Label text="Schema:" class="sapUiTinyMarginTop sapUiTinyMarginBottom"/>
            <Text text="{/currentSchema}"/>
            
            <Label text="Table:" class="sapUiTinyMarginTop sapUiTinyMarginBottom"/>
            <Text text="{/currentTable}"/>
        </VBox>
    </content>
</Panel>
```

**Why**: Users can see what context the AI has access to

---

## 🎯 UX Flow

### Typical User Journey

1. **Open AI Assistant**
   - User clicks "AI Assistant" in navigation
   - Page loads with empty message list
   - Input area is ready

2. **Ask Question**
   - User types: "What tables are in SupplierInvoice?"
   - Presses Send or Enter
   - Message appears in list immediately
   - Loading indicator shows "AI is thinking..."

3. **Receive Response (20-25s wait)**
   - Loading indicator animates
   - After ~23s, AI response appears
   - Response includes formatted text (maybe code blocks)
   - Scroll automatically to new message

4. **Follow-up Questions**
   - User asks: "Generate SQL to count invoices by supplier"
   - Context from previous conversation maintained
   - AI provides SQL query with explanation

5. **Context Awareness**
   - If user has a data product selected in main app:
     - Context panel shows current data product/schema
     - AI automatically knows what they're working on
     - More relevant answers

---

## 💅 Styling (Custom CSS)

### Message Differentiation

```css
/* User messages - right-aligned, blue accent */
.userMessage {
    background-color: #e8f4fd;
    border-left: 3px solid #0070f2;
    margin: 0.5rem 0;
    padding: 0.75rem;
}

/* AI messages - left-aligned, gray accent */
.aiMessage {
    background-color: #f5f5f5;
    border-left: 3px solid #6a6d70;
    margin: 0.5rem 0;
    padding: 0.75rem;
}

/* Code blocks in AI responses */
.aiMessage pre {
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    font-family: 'Consolas', 'Monaco', monospace;
}

/* Loading message */
.aiLoadingMessage {
    opacity: 0.7;
    font-style: italic;
}
```

**Why**: Visual distinction improves readability and conversation flow

---

## 🔧 Controller Logic (Key Methods)

### Chat.controller.js

```javascript
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast",
    "sap/m/MessageBox"
], function (Controller, JSONModel, MessageToast, MessageBox) {
    "use strict";

    return Controller.extend("ai.assistant.controller.Chat", {
        
        onInit: function () {
            // Initialize models
            const oViewModel = new JSONModel({
                messages: [],
                currentMessage: "",
                isLoading: false,
                currentDataProduct: "",
                currentSchema: "",
                currentTable: ""
            });
            this.getView().setModel(oViewModel);
            
            // Load context from main app (if available)
            this._loadContext();
        },
        
        onSendMessage: function () {
            const oModel = this.getView().getModel();
            const sMessage = oModel.getProperty("/currentMessage").trim();
            
            if (!sMessage) {
                return;
            }
            
            // Add user message
            this._addMessage({
                type: "user",
                sender: "You",
                text: sMessage,
                timestamp: new Date().toLocaleTimeString()
            });
            
            // Clear input
            oModel.setProperty("/currentMessage", "");
            oModel.setProperty("/isLoading", true);
            
            // Call AI API
            this._callAIAPI(sMessage);
        },
        
        _callAIAPI: function (sPrompt) {
            const oModel = this.getView().getModel();
            const oContext = this._getContext();
            
            fetch("/api/ai-assistant/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: sPrompt,
                    context: oContext
                })
            })
            .then(response => response.json())
            .then(data => {
                oModel.setProperty("/isLoading", false);
                
                if (data.success) {
                    this._addMessage({
                        type: "ai",
                        sender: "AI Assistant",
                        text: this._formatResponse(data.response),
                        timestamp: new Date().toLocaleTimeString(),
                        tokensUsed: data.tokens_used
                    });
                    
                    // Scroll to bottom
                    this._scrollToBottom();
                } else {
                    MessageBox.error("AI Error: " + data.error);
                }
            })
            .catch(error => {
                oModel.setProperty("/isLoading", false);
                MessageBox.error("Network error: " + error.message);
            });
        },
        
        _addMessage: function (oMessage) {
            const oModel = this.getView().getModel();
            const aMessages = oModel.getProperty("/messages");
            aMessages.push(oMessage);
            oModel.setProperty("/messages", aMessages);
        },
        
        _scrollToBottom: function () {
            setTimeout(() => {
                const oList = this.byId("messageList");
                const aItems = oList.getItems();
                if (aItems.length > 0) {
                    oList.scrollToIndex(aItems.length - 1);
                }
            }, 100);
        },
        
        _getContext: function () {
            const oModel = this.getView().getModel();
            return {
                data_product: oModel.getProperty("/currentDataProduct"),
                schema: oModel.getProperty("/currentSchema"),
                table: oModel.getProperty("/currentTable")
            };
        },
        
        _formatResponse: function (sResponse) {
            // Remove "AgentRunResult(output='...')" wrapper if present
            const match = sResponse.match(/AgentRunResult\(output='(.*)'\)/s);
            return match ? match[1] : sResponse;
        },
        
        _loadContext: function () {
            // Get context from main app if integrated
            // For now, leave empty
        }
    });
});
```

---

## 📊 Data Model Structure

### Message Model

```json
{
    "messages": [
        {
            "type": "user",
            "sender": "You",
            "text": "What is SAP S/4HANA?",
            "timestamp": "11:00:15 PM"
        },
        {
            "type": "ai",
            "sender": "AI Assistant",
            "text": "SAP S/4HANA is a next-generation ERP...",
            "timestamp": "11:00:38 PM",
            "tokensUsed": 126
        }
    ],
    "currentMessage": "",
    "isLoading": false,
    "currentDataProduct": "SupplierInvoice",
    "currentSchema": "sap_s4com_supplierinvoice_v1",
    "currentTable": "A_SupplierInvoice"
}
```

---

## 🚀 Advanced Features (Future)

### 1. Streaming Responses
```javascript
// Use Server-Sent Events (SSE) for real-time streaming
const eventSource = new EventSource("/api/ai-assistant/stream?prompt=" + encodeURIComponent(sPrompt));

eventSource.onmessage = function(event) {
    const chunk = event.data;
    // Append chunk to current AI message
    _appendToLastMessage(chunk);
};

eventSource.onerror = function() {
    eventSource.close();
    oModel.setProperty("/isLoading", false);
};
```

### 2. Export Conversation
```javascript
onExportConversation: function() {
    const oModel = this.getView().getModel();
    const aMessages = oModel.getProperty("/messages");
    
    const sMarkdown = aMessages.map(msg => {
        return `**${msg.sender}** (${msg.timestamp}):\n${msg.text}\n`;
    }).join("\n---\n\n");
    
    // Download as .md file
    this._downloadFile("conversation.md", sMarkdown);
}
```

### 3. Suggested Questions
```xml
<!-- Show common questions as chips -->
<HBox class="sapUiTinyMarginTop" wrap="Wrap">
    <Button 
        text="Show all data products"
        press=".onSuggestedQuestion"
        type="Ghost"
        class="sapUiTinyMarginEnd"/>
    <Button 
        text="Generate SQL for..."
        press=".onSuggestedQuestion"
        type="Ghost"
        class="sapUiTinyMarginEnd"/>
</HBox>
```

### 4. Code Syntax Highlighting
```javascript
// Use highlight.js for SQL code blocks
_formatResponse: function(sResponse) {
    // Detect SQL code blocks
    return sResponse.replace(/```sql\n([\s\S]*?)```/g, function(match, code) {
        return '<pre class="sql-code">' + hljs.highlight(code, {language: 'sql'}).value + '</pre>';
    });
}
```

---

## 📱 Responsive Design

### Mobile Considerations

1. **Compact Mode**: Use `cozy` mode for desktop, `compact` for mobile
2. **Input Area**: Full-width text area on mobile
3. **Context Panel**: Collapsed by default on mobile
4. **Messages**: Stack vertically with appropriate padding

```xml
<!-- Responsive margin/padding -->
<Page class="sapUiResponsiveContentPadding">
    <content>
        <List class="sapUiResponsiveMargin">
            <!-- Messages -->
        </List>
    </content>
</Page>
```

---

## ✅ Implementation Checklist

### Phase 1: Basic Chat (This Sprint)
- [ ] Create frontend folder structure
- [ ] Implement Chat.view.xml with FeedListItem
- [ ] Implement Chat.controller.js with API integration
- [ ] Add custom CSS for message styling
- [ ] Test with real Groq API (23s response handling)
- [ ] Add loading indicator
- [ ] Error handling (network, API errors)

### Phase 2: Context Integration
- [ ] Pass current data product to AI
- [ ] Show context panel
- [ ] Update context when user changes data product
- [ ] Test context-aware queries

### Phase 3: Advanced Features
- [ ] Conversation history persistence
- [ ] Export conversation
- [ ] Suggested questions
- [ ] Code syntax highlighting
- [ ] Streaming responses (if Groq supports)

---

## 🎓 Best Practices

### DO's ✅
- Use native SAPUI5 controls (FeedListItem, TextArea)
- Follow Fiori design guidelines (spacing, colors, typography)
- Show loading states during API calls
- Handle errors gracefully with MessageBox
- Auto-scroll to latest message
- Disable input during processing
- Format AI responses (remove technical wrappers)

### DON'Ts ❌
- Don't use custom chat bubble components (use FeedListItem)
- Don't block UI during AI processing
- Don't show raw AgentRunResult wrapper to user
- Don't ignore 20-25s response time (show progress)
- Don't lose context between messages

---

## 📚 References

- [SAP Fiori Design Guidelines - Conversational UX](https://experience.sap.com/fiori-design-web/)
- [SAPUI5 SDK - sap.m.FeedListItem](https://sapui5.hana.ondemand.com/#/api/sap.m.FeedListItem)
- [SAPUI5 SDK - sap.m.TextArea](https://sapui5.hana.ondemand.com/#/api/sap.m.TextArea)
- ChatGPT, Microsoft Copilot, GitHub Copilot (UX inspiration)
- [[SAP Fiori Design Standards]] (project knowledge)

---

**Next Steps**: Implement Phase 1 (Basic Chat) following this design