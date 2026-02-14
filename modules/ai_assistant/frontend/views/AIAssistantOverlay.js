/**
 * AI Assistant Overlay - Phase 4.7: SQL Execution UI
 * 
 * Features:
 * - Tabbed interface (Chat vs SQL)
 * - Chat: Streaming conversation with AI
 * - SQL: Direct SQL query execution with results
 */
(function() {
    'use strict';

    class AIAssistantOverlay {
        constructor(adapter) {
            this.adapter = adapter;
            this.dialog = null;
            this.messages = [];
            this.messageContainer = null;
            this.currentTab = 'chat'; // 'chat' or 'sql'
            this.sqlQuery = '';
            this.sqlDatabase = 'p2p_data';
            this.sqlResult = null;
            console.log('[AIAssistantOverlay] Phase 4.7: Tabbed interface with SQL execution initialized');
        }

        open() {
            console.log('[AIAssistantOverlay] Opening dialog');
            
            if (!this.dialog) {
                this._createDialog();
            }
            
            this.dialog.open();
        }

        close() {
            if (this.dialog) {
                this.dialog.close();
            }
        }

        _createDialog() {
            console.log('[AIAssistantOverlay] Creating tabbed dialog');
            
            // Create tab bar
            const chatTab = new sap.m.Button({
                text: "Chat",
                type: this.currentTab === 'chat' ? "Emphasized" : "Default",
                press: () => this._switchTab('chat')
            });
            
            const sqlTab = new sap.m.Button({
                text: "SQL Query",
                type: this.currentTab === 'sql' ? "Emphasized" : "Default",
                press: () => this._switchTab('sql')
            });
            
            const tabBar = new sap.m.Bar({
                contentLeft: [chatTab, sqlTab]
            });
            
            // Store tab buttons for updates
            this.chatTabButton = chatTab;
            this.sqlTabButton = sqlTab;
            
            // Create content container (will switch between chat and SQL)
            this.contentContainer = new sap.ui.core.HTML({
                content: this._renderCurrentTab()
            });
            
            // Create dialog
            this.dialog = new sap.m.Dialog({
                title: "Joule AI Assistant",
                contentWidth: "900px",
                contentHeight: "700px",
                customHeader: tabBar,
                content: [this.contentContainer],
                endButton: new sap.m.Button({
                    text: "Close",
                    press: () => this.close()
                })
            });
            
            console.log('[AIAssistantOverlay] Tabbed dialog created');
        }

        _switchTab(tab) {
            console.log('[AIAssistantOverlay] Switching to tab:', tab);
            this.currentTab = tab;
            
            // Update tab button styling
            this.chatTabButton.setType(tab === 'chat' ? "Emphasized" : "Default");
            this.sqlTabButton.setType(tab === 'sql' ? "Emphasized" : "Default");
            
            // Re-render content
            this.contentContainer.setContent(this._renderCurrentTab());
            
            // Attach event handlers for SQL tab
            if (tab === 'sql') {
                this._attachSQLHandlers();
            }
        }

        _renderCurrentTab() {
            if (this.currentTab === 'chat') {
                return this._renderChatTab();
            } else {
                return this._renderSQLTab();
            }
        }

        _renderChatTab() {
            return `
                <div id="chat-content" style="display: flex; flex-direction: column; height: 600px;">
                    <!-- Messages area -->
                    <div style="flex: 1; padding: 1rem; overflow-y: auto; border-bottom: 1px solid #e0e0e0;">
                        ${this.messages.length === 0 ? `
                            <div style="color: #666; text-align: center; padding: 2rem;">
                                <p><strong>Welcome to Joule AI Assistant!</strong></p>
                                <p>Ask me anything about your P2P data:</p>
                                <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
                                    <li>"Show me data products"</li>
                                    <li>"What is in the knowledge graph?"</li>
                                    <li>"Calculate total PO value"</li>
                                    <li>"Find suppliers in Germany"</li>
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${this.messages.map(msg => this._renderChatMessage(msg)).join('')}
                    </div>
                    
                    <!-- Input area -->
                    <div style="padding: 1rem; background: #fafafa;">
                        <div style="display: flex; gap: 0.5rem;">
                            <input 
                                id="chat-input" 
                                type="text" 
                                placeholder="Ask me anything about your P2P data..."
                                style="
                                    flex: 1;
                                    padding: 0.75rem;
                                    border: 1px solid #ccc;
                                    border-radius: 4px;
                                    font-size: 14px;
                                "
                            />
                            <button 
                                id="chat-send-btn"
                                style="
                                    padding: 0.75rem 1.5rem;
                                    background: #0070f2;
                                    color: white;
                                    border: none;
                                    border-radius: 4px;
                                    cursor: pointer;
                                    font-weight: bold;
                                "
                            >Send</button>
                        </div>
                    </div>
                </div>
            `;
        }

        _renderChatMessage(msg) {
            const isUser = msg.type === 'user';
            const isStreaming = msg.type === 'streaming';
            const isError = msg.type === 'error';
            
            const bgColor = isUser ? '#e3f2fd' : (isError ? '#ffebee' : '#f5f5f5');
            const textColor = isUser ? '#1976d2' : (isError ? '#c62828' : '#333333');
            const borderColor = isUser ? '#1976d2' : (isStreaming ? '#ff9800' : (isError ? '#c62828' : '#4caf50'));
            
            return `
                <div style="
                    margin-bottom: 1rem;
                    padding: 0.75rem;
                    background: ${bgColor};
                    border-radius: 4px;
                    border-left: 4px solid ${borderColor};
                ">
                    <div style="
                        font-weight: bold;
                        color: ${textColor};
                        margin-bottom: 0.25rem;
                    ">
                        ${isUser ? 'You' : (isError ? 'Error' : 'Assistant')} (${msg.timestamp})
                        ${isStreaming ? ' <span style="color: #ff9800;">[STREAMING...]</span>' : ''}
                    </div>
                    <div style="color: ${textColor}; white-space: pre-wrap;">
                        ${msg.text || '<span style="color: #999;">Waiting for response...</span>'}
                    </div>
                </div>
            `;
        }

        _renderSQLTab() {
            const hasResult = this.sqlResult !== null;
            const isSuccess = hasResult && this.sqlResult.success;
            const hasRows = isSuccess && this.sqlResult.rows && this.sqlResult.rows.length > 0;
            
            return `
                <div id="sql-content" style="display: flex; flex-direction: column; height: 600px;">
                    <!-- SQL Editor Area -->
                    <div style="flex: 0 0 40%; display: flex; flex-direction: column; padding: 1rem; border-bottom: 2px solid #e0e0e0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <label style="font-weight: bold; color: #333;">SQL Query</label>
                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                <label style="font-size: 0.9em; color: #666;">Database:</label>
                                <select 
                                    id="sql-database-selector"
                                    style="padding: 0.25rem 0.5rem; border: 1px solid #ccc; border-radius: 4px; font-size: 0.9em;"
                                >
                                    <option value="p2p_data" ${this.sqlDatabase === 'p2p_data' ? 'selected' : ''}>P2P Data</option>
                                    <option value="p2p_graph" ${this.sqlDatabase === 'p2p_graph' ? 'selected' : ''}>P2P Graph</option>
                                </select>
                            </div>
                        </div>
                        
                        <textarea 
                            id="sql-query-editor"
                            placeholder="Enter SQL query (SELECT only)...&#10;&#10;Example:&#10;SELECT * FROM PurchaseOrder LIMIT 10;"
                            style="
                                flex: 1;
                                padding: 0.75rem;
                                border: 1px solid #ccc;
                                border-radius: 4px;
                                font-family: 'Courier New', monospace;
                                font-size: 13px;
                                resize: none;
                            "
                        >${this.sqlQuery}</textarea>
                        
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                            <span style="font-size: 0.85em; color: #666;">
                                💡 Tip: Only SELECT queries allowed. LIMIT enforced at 1000 rows.
                            </span>
                            <button 
                                id="sql-execute-btn"
                                style="
                                    padding: 0.5rem 1.5rem;
                                    background: #0070f2;
                                    color: white;
                                    border: none;
                                    border-radius: 4px;
                                    cursor: pointer;
                                    font-weight: bold;
                                "
                            >▶ Execute</button>
                        </div>
                    </div>
                    
                    <!-- Results Area -->
                    <div style="flex: 1; padding: 1rem; overflow: auto; background: #fafafa;">
                        ${!hasResult ? `
                            <div style="color: #666; text-align: center; padding: 2rem;">
                                <p><strong>SQL Query Execution</strong></p>
                                <p style="margin-top: 1rem;">Enter a SELECT query above and click Execute.</p>
                                <p style="font-size: 0.9em; color: #999; margin-top: 1rem;">
                                    Security: Only SELECT statements allowed<br/>
                                    Limit: Maximum 1000 rows returned
                                </p>
                            </div>
                        ` : ''}
                        
                        ${hasResult && !isSuccess ? `
                            <div style="
                                padding: 1rem;
                                background: #ffebee;
                                border-left: 4px solid #c62828;
                                border-radius: 4px;
                            ">
                                <div style="font-weight: bold; color: #c62828; margin-bottom: 0.5rem;">
                                    ❌ Error
                                </div>
                                <div style="color: #c62828; font-family: monospace; font-size: 0.9em;">
                                    ${this.sqlResult.error || 'Unknown error occurred'}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${isSuccess && !hasRows ? `
                            <div style="
                                padding: 1rem;
                                background: #fff3cd;
                                border-left: 4px solid #ffc107;
                                border-radius: 4px;
                            ">
                                <div style="font-weight: bold; color: #856404; margin-bottom: 0.5rem;">
                                    ℹ️ No Results
                                </div>
                                <div style="color: #856404;">
                                    Query executed successfully but returned no rows.
                                </div>
                                ${this._renderSQLMetadata()}
                            </div>
                        ` : ''}
                        
                        ${isSuccess && hasRows ? `
                            <div>
                                <!-- Metadata Bar -->
                                ${this._renderSQLMetadata()}
                                
                                <!-- Results Table -->
                                <div style="margin-top: 1rem; overflow-x: auto;">
                                    ${this._renderSQLTable()}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }

        _renderSQLMetadata() {
            if (!this.sqlResult || !this.sqlResult.success) return '';
            
            const rowCount = this.sqlResult.rows ? this.sqlResult.rows.length : 0;
            const execTime = this.sqlResult.execution_time_ms || 0;
            const wasLimited = this.sqlResult.warnings && this.sqlResult.warnings.includes('LIMIT');
            
            return `
                <div style="
                    padding: 0.75rem;
                    background: #e8f5e9;
                    border-left: 4px solid #4caf50;
                    border-radius: 4px;
                    font-size: 0.9em;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #2e7d32;">✅ Query Executed Successfully</strong>
                        </div>
                        <div style="color: #666;">
                            <span style="margin-right: 1rem;">⏱️ ${execTime}ms</span>
                            <span>📊 ${rowCount} row${rowCount !== 1 ? 's' : ''}</span>
                        </div>
                    </div>
                    ${wasLimited ? `
                        <div style="margin-top: 0.5rem; color: #f57c00;">
                            ⚠️ ${this.sqlResult.warnings}
                        </div>
                    ` : ''}
                </div>
            `;
        }

        _renderSQLTable() {
            if (!this.sqlResult || !this.sqlResult.rows || this.sqlResult.rows.length === 0) {
                return '';
            }
            
            const columns = this.sqlResult.columns || [];
            const rows = this.sqlResult.rows || [];
            
            return `
                <table style="
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                ">
                    <thead>
                        <tr style="background: #f5f5f5; border-bottom: 2px solid #e0e0e0;">
                            ${columns.map(col => `
                                <th style="
                                    padding: 0.75rem;
                                    text-align: left;
                                    font-weight: bold;
                                    color: #333;
                                    border-bottom: 2px solid #0070f2;
                                ">${col}</th>
                            `).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${rows.map((row, idx) => `
                            <tr style="
                                border-bottom: 1px solid #e0e0e0;
                                ${idx % 2 === 0 ? 'background: #fafafa;' : 'background: white;'}
                            ">
                                ${columns.map(col => {
                                    const value = row[col];
                                    const displayValue = value === null ? '<em style="color: #999;">null</em>' : 
                                                       value === '' ? '<em style="color: #999;">(empty)</em>' : 
                                                       String(value);
                                    return `
                                        <td style="
                                            padding: 0.5rem 0.75rem;
                                            color: #333;
                                            font-family: 'Segoe UI', sans-serif;
                                            font-size: 0.9em;
                                        ">${displayValue}</td>
                                    `;
                                }).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }

        _attachSQLHandlers() {
            // Use setTimeout to ensure DOM is rendered
            setTimeout(() => {
                const executeBtn = document.getElementById('sql-execute-btn');
                const queryEditor = document.getElementById('sql-query-editor');
                const dbSelector = document.getElementById('sql-database-selector');
                
                if (executeBtn) {
                    executeBtn.onclick = () => this._executeSQLQuery();
                }
                
                if (queryEditor) {
                    queryEditor.onkeydown = (e) => {
                        // Ctrl+Enter or Cmd+Enter to execute
                        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                            e.preventDefault();
                            this._executeSQLQuery();
                        }
                    };
                    
                    queryEditor.oninput = (e) => {
                        this.sqlQuery = e.target.value;
                    };
                }
                
                if (dbSelector) {
                    dbSelector.onchange = (e) => {
                        this.sqlDatabase = e.target.value;
                        console.log('[AIAssistantOverlay] Database changed to:', this.sqlDatabase);
                    };
                }
            }, 100);
        }

        async _executeSQLQuery() {
            console.log('[AIAssistantOverlay] Executing SQL query');
            
            const query = this.sqlQuery.trim();
            if (!query) {
                this.sqlResult = {
                    success: false,
                    error: 'Please enter a SQL query'
                };
                this.contentContainer.setContent(this._renderCurrentTab());
                return;
            }
            
            // Show loading state
            this.sqlResult = {
                loading: true
            };
            this.contentContainer.setContent(this._renderSQLTab());
            
            try {
                // Call adapter
                const result = await this.adapter.executeSQL(query, this.sqlDatabase);
                
                console.log('[AIAssistantOverlay] SQL execution result:', result);
                this.sqlResult = result;
                
                // Re-render with results
                this.contentContainer.setContent(this._renderCurrentTab());
                this._attachSQLHandlers(); // Re-attach after render
                
            } catch (error) {
                console.error('[AIAssistantOverlay] SQL execution failed:', error);
                this.sqlResult = {
                    success: false,
                    error: error.message
                };
                this.contentContainer.setContent(this._renderCurrentTab());
                this._attachSQLHandlers(); // Re-attach after render
            }
        }

        _handleRealStreaming(userMessage) {
            console.log('[AIAssistantOverlay] Starting real API streaming');
            
            // Add user message
            this.messages.push({
                type: 'user',
                text: userMessage,
                timestamp: new Date().toLocaleTimeString()
            });
            
            // Add empty assistant message for streaming
            const streamIndex = this.messages.length;
            this.messages.push({
                type: 'streaming',
                text: '',
                timestamp: new Date().toLocaleTimeString()
            });
            
            this.contentContainer.setContent(this._renderCurrentTab());
            this._attachChatHandlers(); // Re-attach handlers
            
            let accumulatedText = '';
            
            // Connect to real streaming API
            const cleanup = this.adapter.sendMessageStream(userMessage, {
                onDelta: (content) => {
                    accumulatedText += content;
                    
                    if (this.messages[streamIndex]) {
                        this.messages[streamIndex].text = accumulatedText;
                        this.contentContainer.setContent(this._renderCurrentTab());
                        this._attachChatHandlers(); // Re-attach after render
                    }
                },
                
                onToolCall: (toolName) => {
                    console.log('[AIAssistantOverlay] Tool called:', toolName);
                },
                
                onDone: (response, conversationId) => {
                    console.log('[AIAssistantOverlay] Streaming done');
                    
                    if (this.messages[streamIndex]) {
                        this.messages[streamIndex].type = 'assistant';
                        this.contentContainer.setContent(this._renderCurrentTab());
                        this._attachChatHandlers(); // Re-attach after render
                    }
                },
                
                onError: (error) => {
                    console.error('[AIAssistantOverlay] Streaming error:', error);
                    
                    if (this.messages[streamIndex]) {
                        this.messages[streamIndex].type = 'error';
                        this.messages[streamIndex].text = `Error: ${error}`;
                        this.contentContainer.setContent(this._renderCurrentTab());
                        this._attachChatHandlers(); // Re-attach after render
                    }
                }
            });
        }

        _attachChatHandlers() {
            setTimeout(() => {
                const sendBtn = document.getElementById('chat-send-btn');
                const inputField = document.getElementById('chat-input');
                
                if (sendBtn) {
                    sendBtn.onclick = () => {
                        const message = inputField ? inputField.value : '';
                        if (message.trim()) {
                            this._handleRealStreaming(message);
                            if (inputField) {
                                inputField.value = '';
                            }
                        }
                    };
                }
                
                if (inputField) {
                    inputField.onkeydown = (e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            sendBtn.click();
                        }
                    };
                }
            }, 100);
        }
    }

    window.AIAssistantOverlay = AIAssistantOverlay;
    console.log('[AIAssistantOverlay] Phase 4.7: Tabbed interface with SQL execution loaded');

})();