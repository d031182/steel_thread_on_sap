# AI Assistant Shell Overlay Implementation

**Status**: Implementation Plan  
**Date**: February 13, 2026  
**Pattern**: Shell Button + Sidebar Overlay (Industry Standard)  
**References**: Microsoft Copilot, GitHub Copilot, ChatGPT sidebar patterns

---

## 🎯 Why Overlay Pattern?

### Industry Research Findings

**Shell Button-Activated Overlay is the industry standard for AI assistants in product interfaces:**

| Pattern | Best For | Examples | Key Benefits |
|---------|----------|----------|-------------|
| **Shell Button Overlay** | Quick prompts, contextual tasks | GitHub Copilot (VS Code), Microsoft Copilot (Edge/Office) | Low disruption, always accessible, contextual[1] |
| **Tabbed Page** | Multi-turn exploration sessions | ChatGPT standalone web app | Immersive, but breaks workflow |

**Key Insight**: Use overlays for "fire-and-forget" + persistent access (Copilot-style), not tabs for "conversational depth" (ChatGPT standalone-style)[1].

---

## 🏗️ Architecture Design

### Pattern: Split-Screen Sidebar

```
┌─────────────────────────────────────────────────────────┐
│ App Shell Header                          [🤖 AI Button]│ ← Shell Button
├─────────────────────────────────┬───────────────────────┤
│                                 │                       │
│   Main Content Area             │   AI Assistant        │
│   (Data Products/KG/etc.)       │   Sidebar Overlay     │
│                                 │                       │
│                                 │   ┌─────────────────┐ │
│                                 │   │ Message History │ │
│                                 │   │                 │ │
│                                 │   │ User: "..."     │ │
│                                 │   │ AI: "..."       │ │
│                                 │   │                 │ │
│                                 │   └─────────────────┘ │
│                                 │   ┌─────────────────┐ │
│                                 │   │ [Input Area]    │ │
│                                 │   │ [Send Button]   │ │
│                                 │   └─────────────────┘ │
└─────────────────────────────────┴───────────────────────┘
```

**Key Characteristics**:
- **Always accessible**: Button in shell header (not navigation menu)
- **Non-disruptive**: Sidebar slides over content, doesn't replace it
- **Contextual**: Knows what page/data product user is viewing
- **Persistent**: Stays open until user closes it
- **Resizable**: User can adjust sidebar width (future enhancement)

---

## 📐 SAPUI5 Implementation

### 1. Shell Button (App Header)

**Location**: `app_v2/static/index.html` or shell component

```xml
<!-- Add to shell header -->
<sap.m.Button
    id="aiAssistantButton"
    icon="sap-icon://collaborate"
    tooltip="Open AI Assistant"
    type="Transparent"
    press=".onToggleAIAssistant"
    class="sapUiTinyMarginEnd"/>
```

**Alternative**: Use `sap.m.Avatar` with AI icon for premium feel
```xml
<sap.m.Avatar
    src="sap-icon://collaborate"
    displaySize="XS"
    press=".onToggleAIAssistant"
    tooltip="AI Assistant"
    class="aiAssistantAvatar"/>
```

---

### 2. Sidebar Overlay (Responsive Popover)

**Option A: sap.m.ResponsivePopover (Recommended)**
```javascript
onToggleAIAssistant: function(oEvent) {
    if (!this._oAIPopover) {
        this._oAIPopover = sap.ui.xmlfragment(
            "app.v2.fragments.AIAssistant",
            this
        );
        this.getView().addDependent(this._oAIPopover);
    }
    
    if (this._oAIPopover.isOpen()) {
        this._oAIPopover.close();
    } else {
        this._oAIPopover.openBy(oEvent.getSource());
    }
}
```

**Fragment: AIAssistant.fragment.xml**
```xml
<core:FragmentDefinition
    xmlns="sap.m"
    xmlns:core="sap.ui.core">
    
    <ResponsivePopover
        id="aiAssistantPopover"
        placement="Bottom"
        contentWidth="400px"
        contentHeight="600px"
        showHeader="true"
        title="AI Assistant"
        class="aiAssistantPopover">
        
        <customHeader>
            <Toolbar>
                <Title text="AI Assistant" level="H2"/>
                <ToolbarSpacer/>
                <Button
                    icon="sap-icon://decline"
                    type="Transparent"
                    press=".onCloseAIAssistant"/>
            </Toolbar>
        </customHeader>
        
        <content>
            <VBox height="100%" justifyContent="SpaceBetween">
                
                <!-- Message History -->
                <ScrollContainer height="100%" vertical="true">
                    <List
                        id="aiMessageList"
                        mode="None"
                        noDataText="Start a conversation...">
                        <items>
                            <FeedListItem
                                sender="{message>sender}"
                                timestamp="{message>timestamp}"
                                text="{message>text}"
                                icon="{message>icon}"
                                class="{message>cssClass}"/>
                        </items>
                    </List>
                </ScrollContainer>
                
                <!-- Input Area -->
                <Toolbar class="sapUiTinyMarginTop">
                    <TextArea
                        id="aiMessageInput"
                        value="{/currentMessage}"
                        placeholder="Ask about data products..."
                        rows="2"
                        width="100%"
                        growing="true"
                        growingMaxLines="4"
                        submit=".onSendAIMessage"
                        enabled="{= !${/isLoading}}"/>
                    
                    <Button
                        icon="sap-icon://paper-plane"
                        type="Emphasized"
                        press=".onSendAIMessage"
                        enabled="{= ${/currentMessage}.length > 0 &amp;&amp; !${/isLoading}}"/>
                </Toolbar>
                
            </VBox>
        </content>
        
    </ResponsivePopover>
</core:FragmentDefinition>
```

**Option B: sap.m.Dialog (Alternative - Full Modal)**
- Use if ResponsivePopover feels too small
- Dialog supports resizing, ResponsivePopover is fixed-size
- Dialog is more modal, ResponsivePopover is lighter

---

### 3. Controller Integration

**Shell Controller (or Main App Controller)**

```javascript
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel"
], function(Controller, JSONModel) {
    "use strict";

    return Controller.extend("app.v2.controller.Shell", {
        
        onInit: function() {
            // Initialize AI Assistant model
            const oAIModel = new JSONModel({
                messages: [],
                currentMessage: "",
                isLoading: false,
                context: {
                    currentPage: "",
                    dataProduct: "",
                    schema: "",
                    table: ""
                }
            });
            this.getView().setModel(oAIModel, "ai");
        },
        
        onToggleAIAssistant: function(oEvent) {
            if (!this._oAIPopover) {
                this._oAIPopover = sap.ui.xmlfragment(
                    "ai.assistant.popover",
                    "app.v2.fragments.AIAssistant",
                    this
                );
                this.getView().addDependent(this._oAIPopover);
            }
            
            // Update context before opening
            this._updateAIContext();
            
            if (this._oAIPopover.isOpen()) {
                this._oAIPopover.close();
            } else {
                this._oAIPopover.openBy(oEvent.getSource());
            }
        },
        
        onCloseAIAssistant: function() {
            if (this._oAIPopover) {
                this._oAIPopover.close();
            }
        },
        
        onSendAIMessage: function() {
            const oAIModel = this.getView().getModel("ai");
            const sMessage = oAIModel.getProperty("/currentMessage").trim();
            
            if (!sMessage) return;
            
            // Add user message
            this._addAIMessage({
                type: "user",
                sender: "You",
                text: sMessage,
                timestamp: new Date().toLocaleTimeString(),
                icon: "sap-icon://person-placeholder",
                cssClass: "userMessage"
            });
            
            // Clear input
            oAIModel.setProperty("/currentMessage", "");
            oAIModel.setProperty("/isLoading", true);
            
            // Call API
            this._callAIAPI(sMessage);
        },
        
        _callAIAPI: function(sPrompt) {
            const oAIModel = this.getView().getModel("ai");
            const oContext = oAIModel.getProperty("/context");
            
            fetch("/api/ai-assistant/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: sPrompt,
                    context: oContext
                })
            })
            .then(res => res.json())
            .then(data => {
                oAIModel.setProperty("/isLoading", false);
                
                if (data.success) {
                    this._addAIMessage({
                        type: "ai",
                        sender: "AI Assistant",
                        text: this._formatAIResponse(data.response),
                        timestamp: new Date().toLocaleTimeString(),
                        icon: "sap-icon://collaborate",
                        cssClass: "aiMessage"
                    });
                    
                    this._scrollToBottom();
                } else {
                    sap.m.MessageBox.error("AI Error: " + data.error);
                }
            })
            .catch(err => {
                oAIModel.setProperty("/isLoading", false);
                sap.m.MessageBox.error("Network error: " + err.message);
            });
        },
        
        _addAIMessage: function(oMessage) {
            const oAIModel = this.getView().getModel("ai");
            const aMessages = oAIModel.getProperty("/messages");
            aMessages.push(oMessage);
            oAIModel.setProperty("/messages", aMessages);
        },
        
        _updateAIContext: function() {
            const oAIModel = this.getView().getModel("ai");
            const oRouter = sap.ui.core.UIComponent.getRouterFor(this);
            const sCurrentRoute = oRouter.getHashChanger().getHash();
            
            // Parse current route to extract context
            // Example: "data-products-v2" or "knowledge-graph-v2"
            oAIModel.setProperty("/context/currentPage", sCurrentRoute);
            
            // TODO: Get current data product/schema/table if available
            // This requires integration with Data Products module
        },
        
        _scrollToBottom: function() {
            setTimeout(() => {
                const oList = sap.ui.core.Fragment.byId(
                    "ai.assistant.popover",
                    "aiMessageList"
                );
                if (oList) {
                    const aItems = oList.getItems();
                    if (aItems.length > 0) {
                        oList.scrollToIndex(aItems.length - 1);
                    }
                }
            }, 100);
        },
        
        _formatAIResponse: function(sResponse) {
            // Remove AgentRunResult wrapper if present
            const match = sResponse.match(/AgentRunResult\(output='(.*)'\)/s);
            return match ? match[1] : sResponse;
        }
    });
});
```

---

## 🎨 Custom Styling

**CSS: app_v2/static/css/ai-assistant.css**

```css
/* AI Assistant Shell Button */
.aiAssistantAvatar {
    cursor: pointer;
    transition: transform 0.2s ease;
}

.aiAssistantAvatar:hover {
    transform: scale(1.1);
}

/* AI Assistant Popover */
.aiAssistantPopover {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

/* Message Styling */
.userMessage {
    background-color: #e8f4fd;
    border-left: 3px solid #0070f2;
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-radius: 4px;
}

.aiMessage {
    background-color: #f5f5f5;
    border-left: 3px solid #6a6d70;
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-radius: 4px;
}

/* Code blocks in AI responses */
.aiMessage pre {
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.875rem;
}

/* Loading state */
.aiMessage .sapMBusyIndicator {
    display: inline-block;
    margin-right: 0.5rem;
}
```

---

## 🔄 Integration Points

### 1. Context Awareness

**EventBus Integration**: When user navigates or selects data product

```javascript
// In Data Products module
onDataProductSelected: function(oDataProduct) {
    // Publish to EventBus
    sap.ui.getCore().getEventBus().publish(
        "app",
        "dataProductSelected",
        { dataProduct: oDataProduct }
    );
}

// In Shell controller
onInit: function() {
    // Subscribe to context changes
    sap.ui.getCore().getEventBus().subscribe(
        "app",
        "dataProductSelected",
        this._onDataProductSelected,
        this
    );
},

_onDataProductSelected: function(sChannel, sEvent, oData) {
    const oAIModel = this.getView().getModel("ai");
    oAIModel.setProperty("/context/dataProduct", oData.dataProduct.name);
}
```

---

### 2. Backend API (Already Implemented)

**Endpoint**: `/api/ai-assistant/query`

**Request**:
```json
{
  "prompt": "What tables are in SupplierInvoice?",
  "context": {
    "currentPage": "data-products-v2",
    "dataProduct": "SupplierInvoice",
    "schema": "sap_s4com_supplierinvoice_v1",
    "table": ""
  }
}
```

**Response**:
```json
{
  "success": true,
  "response": "The SupplierInvoice data product contains...",
  "tokens_used": 126
}
```

---

## 📋 Implementation Checklist

### Phase 1: Shell Integration (This Sprint)
- [ ] Add AI button to app shell header
- [ ] Create AIAssistant.fragment.xml (ResponsivePopover)
- [ ] Implement shell controller methods (toggle, send, close)
- [ ] Add custom CSS for message styling
- [ ] Test basic open/close behavior
- [ ] Test message sending (user → AI → response)

### Phase 2: Context Integration
- [ ] Implement EventBus subscription for context updates
- [ ] Pass current page/data product to AI API
- [ ] Display context in popover header or panel
- [ ] Test context-aware queries

### Phase 3: UX Enhancements
- [ ] Add loading indicator during AI processing
- [ ] Implement auto-scroll to latest message
- [ ] Add suggested questions (chips)
- [ ] Error handling with retry option
- [ ] Code syntax highlighting (highlight.js)

### Phase 4: Advanced Features
- [ ] Conversation history persistence (localStorage)
- [ ] Export conversation (markdown)
- [ ] Streaming responses (SSE)
- [ ] Resizable sidebar
- [ ] Keyboard shortcuts (e.g., Ctrl+K to open)

---

## 🎯 Success Criteria

1. **Accessibility**: AI assistant accessible from any page via shell button
2. **Non-Disruptive**: Sidebar overlay doesn't replace main content
3. **Contextual**: AI knows what page/data product user is viewing
4. **Responsive**: Works on desktop and tablet (mobile optional Phase 2)
5. **Performance**: Handles 20-25s AI response time gracefully
6. **Fiori Compliance**: Uses standard SAPUI5 controls (ResponsivePopover, FeedListItem)

---

## 📚 References

1. [Perplexity Research](https://www.smashingmagazine.com/2026/02/designing-agentic-ai-practical-ux-patterns/) - UX patterns for AI assistants
2. [Microsoft Copilot UX](https://departmentofproduct.substack.com/p/deep-the-ux-of-ai-assistants) - Split-screen sidebar pattern
3. [GitHub Copilot](https://uxplanet.org/7-key-design-patterns-for-ai-interfaces-893ab96988f6) - Sidebar activation
4. [[SAP Fiori Design Standards]] - SAPUI5 component guidelines
5. [[AI Assistant UX Design]] - Original Fiori-compliant design doc

---

**Next Action**: Implement Phase 1 (Shell Integration) following this architecture