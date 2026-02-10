/**
 * Joule AI Assistant Dialog V2
 * 
 * Complete redesign matching SAP Joule UX exactly
 * - Purple header bar with controls
 * - Chat message bubbles
 * - Large rounded input at bottom
 */

let jouleDialogV2 = null;

/**
 * Open Joule Dialog
 */
export function openJouleDialog() {
    if (!jouleDialogV2) {
        jouleDialogV2 = createJouleDialog();
    }
    jouleDialogV2.open();
}

/**
 * Create Joule Dialog matching SAP Joule exactly
 */
function createJouleDialog() {
    // Model
    const oModel = new sap.ui.model.json.JSONModel({
        messages: [],
        currentMessage: "",
        isLoading: false
    });
    
    window.jouleModel = oModel;
    
    // Custom header bar (purple) with controls
    const oCustomHeader = new sap.m.Bar({
        design: "Header",
        contentLeft: [
            new sap.m.Button({
                icon: "sap-icon://menu2",
                type: "Transparent"
            })
        ],
        contentMiddle: [
            new sap.m.Title({
                text: "Joule is cool",
                level: "H5"
            })
        ],
        contentRight: [
            new sap.m.Button({
                icon: "sap-icon://full-screen",
                type: "Transparent"
            }),
            new sap.m.Button({
                icon: "sap-icon://decline",
                type: "Transparent",
                press: function() {
                    jouleDialogV2.close();
                }
            })
        ]
    }).addStyleClass("jouleCustomHeader");
    
    // Chat messages container
    const oMessageContainer = new sap.m.VBox({
        items: {
            path: "/messages",
            factory: function(sId, oContext) {
                const sType = oContext.getProperty("type");
                const sText = oContext.getProperty("text");
                
                const oBubble = new sap.m.VBox({
                    items: [
                        new sap.m.Text({
                            text: sText,
                            renderWhitespace: true
                        }).addStyleClass("sapUiSmallMargin")
                    ],
                    layoutData: new sap.m.FlexItemData({
                        alignSelf: sType === "user" ? "End" : "Start"
                    })
                });
                
                // Add appropriate class based on message type
                if (sType === "user") {
                    oBubble.addStyleClass("jouleMessageBubble userBubble");
                } else {
                    oBubble.addStyleClass("jouleMessageBubble aiBubble");
                }
                
                return oBubble;
            }
        }
    }).addStyleClass("jouleMessagesContainer");
    
    oMessageContainer.setModel(oModel);
    
    // Scrollable chat area
    const oScrollContainer = new sap.m.ScrollContainer({
        height: "100%",
        width: "100%",
        vertical: true,
        content: [oMessageContainer]
    }).addStyleClass("jouleScrollArea");
    
    // Input area (large rounded box)
    const oInputArea = new sap.m.HBox({
        alignItems: "Center",
        items: [
            new sap.m.Button({
                icon: "sap-icon://add",
                type: "Transparent",
                tooltip: "Add attachment"
            }),
            new sap.m.TextArea({
                value: "{/currentMessage}",
                placeholder: "Message Joule...",
                rows: 1,
                width: "100%",
                growing: true,
                growingMaxLines: 5
            }),
            new sap.m.Button({
                icon: "sap-icon://paper-plane",
                type: "Emphasized",
                press: handleSendMessage,
                enabled: {
                    parts: [{path: "/currentMessage"}, {path: "/isLoading"}],
                    formatter: function(sMsg, bLoading) {
                        return Boolean(sMsg && sMsg.trim() && !bLoading);
                    }
                }
            })
        ]
    }).addStyleClass("jouleInputArea sapUiContentPadding");
    
    oInputArea.setModel(oModel);
    
    // Disclaimer text
    const oDisclaimer = new sap.m.Text({
        text: "using Pydantic AI with Groq",
        textAlign: "Center"
    }).addStyleClass("jouleDisclaimer sapUiTinyMarginTop");
    
    // Content with messages and input at bottom
    const oContent = new sap.m.VBox({
        height: "100%",
        fitContainer: true,
        items: [
            oScrollContainer,
            oInputArea,
            oDisclaimer
        ]
    });
    
    // Give scroll container all the space
    oScrollContainer.setLayoutData(new sap.m.FlexItemData({
        growFactor: 1
    }));
    
    // Dialog
    const oDialog = new sap.m.Dialog({
        customHeader: oCustomHeader,
        contentWidth: "540px",
        contentHeight: "800px",
        resizable: true,
        draggable: true,
        stretch: false,
        content: [oContent],
        afterOpen: function() {
            // Load CSS
            if (!document.querySelector('link[href*="jouleV2.css"]')) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = '/modules/ai_assistant/frontend/jouleV2.css';
                document.head.appendChild(link);
            }
            
            // Add welcome message
            if (oModel.getProperty("/messages").length === 0) {
                oModel.setProperty("/messages", [{
                    type: "ai",
                    text: "Hello! How can I assist you today?",
                    timestamp: new Date().toLocaleTimeString()
                }]);
            }
        }
    }).addStyleClass("jouleDialogV2");
    
    return oDialog;
}

/**
 * Handle send message
 */
function handleSendMessage() {
    const oModel = window.jouleModel;
    if (!oModel) return;
    
    const sMessage = oModel.getProperty("/currentMessage").trim();
    if (!sMessage) return;
    
    // Add user message
    const aMessages = oModel.getProperty("/messages");
    aMessages.push({
        type: "user",
        text: sMessage,
        timestamp: new Date().toLocaleTimeString()
    });
    oModel.setProperty("/messages", aMessages);
    oModel.setProperty("/currentMessage", "");
    oModel.setProperty("/isLoading", true);
    
    // Call API
    fetch("/api/ai-assistant/query", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({prompt: sMessage, context: {}})
    })
    .then(r => {
        if (!r.ok) {
            throw new Error(`HTTP ${r.status}: ${r.statusText}`);
        }
        return r.json();
    })
    .then(data => {
        oModel.setProperty("/isLoading", false);
        
        if (data.success) {
            // Success - display AI response
            aMessages.push({
                type: "ai",
                text: formatResponse(data.response),
                timestamp: new Date().toLocaleTimeString()
            });
            oModel.setProperty("/messages", aMessages);
        } else {
            // Backend returned error
            const errorMsg = data.error || "Unknown error occurred";
            aMessages.push({
                type: "ai",
                text: `❌ Sorry, I ran into an error:\n\n${errorMsg}\n\nPlease check the system logs for more details (click the 'Logging' button in the top menu).`,
                timestamp: new Date().toLocaleTimeString()
            });
            oModel.setProperty("/messages", aMessages);
            
            console.error("AI Assistant error:", errorMsg);
        }
    })
    .catch(err => {
        oModel.setProperty("/isLoading", false);
        
        // Network or parsing error
        const errorMsg = `Network error: ${err.message}`;
        aMessages.push({
            type: "ai",
            text: `❌ Sorry, I couldn't connect to the backend:\n\n${errorMsg}\n\nPlease check:\n- Is the server running?\n- Check the system logs for details (click 'Logging' button).`,
            timestamp: new Date().toLocaleTimeString()
        });
        oModel.setProperty("/messages", aMessages);
        
        console.error("AI Assistant fetch error:", err);
    });
}

/**
 * Format AI response
 */
function formatResponse(sResponse) {
    if (!sResponse) return "No response";
    const match = sResponse.match(/AgentRunResult\(output=["'](.*)["']\)/s);
    if (match && match[1]) {
        return match[1].replace(/\\n/g, '\n').replace(/\\"/g, '"');
    }
    return sResponse;
}