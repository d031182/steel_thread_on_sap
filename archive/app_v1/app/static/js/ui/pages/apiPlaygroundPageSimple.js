/**
 * API Playground Page - Simple Vanilla JS Version
 * No UI5 controls, just plain HTML/DOM manipulation
 * 
 * @author P2P Development Team
 * @version 2.0.0
 */

let discoveredAPIs = {};
let selectedEndpoint = null;

/**
 * Create API Playground Page Content
 * Returns HTML control that can be placed in mainContent area
 */
export function createAPIPlaygroundPageSimple() {
    console.log('🚀 createAPIPlaygroundPageSimple called');
    const html = `
        <div style="padding: 20px;">
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h2 style="margin: 0 0 10px 0; color: #333;">🚀 API Playground</h2>
                <p style="margin: 0 0 10px 0;">Test all module APIs • Auto-discovered from module.json</p>
                <div id="statsText" style="color: #666; font-size: 14px;">Loading...</div>
            </div>
            
            <div style="display: grid; grid-template-columns: 300px 1fr; gap: 20px; height: calc(100vh - 350px);">
                <!-- Sidebar -->
                <div style="background: white; border-radius: 8px; padding: 20px; overflow-y: auto; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h3 style="margin: 0 0 15px 0;">API Explorer</h3>
                    <div id="apiListContainer">Loading APIs...</div>
                </div>
                
                <!-- Main -->
                <div style="background: white; border-radius: 8px; padding: 20px; overflow-y: auto; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h3 style="margin: 0 0 10px 0;">Request Builder</h3>
                    <p style="color: #666; margin-bottom: 20px;">Select an endpoint from the left to test it</p>
                    
                    <div style="margin-bottom: 30px;">
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; font-weight: 600; margin-bottom: 5px; color: #333;">HTTP Method</label>
                            <select id="httpMethod" style="width: 200px; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                                <option value="GET">GET</option>
                                <option value="POST">POST</option>
                                <option value="PUT">PUT</option>
                                <option value="DELETE">DELETE</option>
                            </select>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; font-weight: 600; margin-bottom: 5px; color: #333;">Endpoint URL</label>
                            <input type="text" id="endpointUrl" placeholder="/api/module/endpoint" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;" />
                        </div>
                        
                        <div id="paramsDiv" style="margin-bottom: 15px; display: none;">
                            <label style="display: block; font-weight: 600; margin-bottom: 5px; color: #333;">Path Parameters</label>
                            <input type="text" id="pathParams" placeholder="e.g., feature_name for /<feature_name>/ endpoints" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;" />
                        </div>
                        
                        <div id="bodyDiv" style="margin-bottom: 15px; display: none;">
                            <label style="display: block; font-weight: 600; margin-bottom: 5px; color: #333;">Request Body (JSON)</label>
                            <textarea id="requestBody" rows="10" placeholder='{\n  "key": "value"\n}' style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; resize: vertical;"></textarea>
                        </div>
                        
                        <div>
                            <button id="executeBtn" style="padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; background: #007bff; color: white; margin-right: 10px;">▶ Execute</button>
                            <button id="clearBtn" style="padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; background: #6c757d; color: white;">Clear</button>
                        </div>
                    </div>
                    
                    <div id="responseSection" style="display: none;">
                        <h3 style="margin: 20px 0 10px 0;">Response</h3>
                        <div style="background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; padding: 15px;">
                            <div style="display: flex; gap: 20px; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #ddd; font-size: 14px;">
                                <span>Status: <span id="responseStatus" style="font-weight: 600;">-</span></span>
                                <span>Time: <span id="responseTime">-</span></span>
                                <button id="copyBtn" style="padding: 5px 15px; border: none; border-radius: 4px; cursor: pointer; background: #6c757d; color: white;">📋 Copy</button>
                            </div>
                            <pre id="responseBody" style="background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; font-size: 13px; line-height: 1.5; margin: 0;"></pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const htmlControl = new sap.ui.core.HTML({
        content: html,
        afterRendering: function() {
            console.log('✅ HTML afterRendering fired');
            // Delay to ensure DOM is ready
            setTimeout(() => {
                console.log('⏰ setTimeout executing initializeSimplePlayground');
                initializeSimplePlayground();
            }, 100);
        }
    });
    
    console.log('📦 Returning HTML control');
    return htmlControl;
}

/**
 * Initialize the playground after rendering
 */
function initializeSimplePlayground() {
    console.log('🔧 initializeSimplePlayground called');
    
    // Check if elements exist
    const executeBtn = document.getElementById('executeBtn');
    const clearBtn = document.getElementById('clearBtn');
    const copyBtn = document.getElementById('copyBtn');
    const httpMethod = document.getElementById('httpMethod');
    
    console.log('Elements found:', {
        executeBtn: !!executeBtn,
        clearBtn: !!clearBtn,
        copyBtn: !!copyBtn,
        httpMethod: !!httpMethod
    });
    
    // Attach event listeners
    document.getElementById('executeBtn')?.addEventListener('click', executeRequest);
    document.getElementById('clearBtn')?.addEventListener('click', clearForm);
    document.getElementById('copyBtn')?.addEventListener('click', copyResponse);
    document.getElementById('httpMethod')?.addEventListener('change', updateBodyVisibility);
    
    // Discover APIs
    discoverAPIs();
}

/**
 * Discover APIs from backend
 */
async function discoverAPIs() {
    try {
        const response = await fetch('/api/playground/discover');
        const data = await response.json();
        
        if (data.success) {
            discoveredAPIs = data.apis;
            renderAPIList(data.apis);
            updateStats(data.stats);
        } else {
            document.getElementById('apiListContainer').innerHTML = 
                '<p style="color: red;">Failed to discover APIs: ' + data.error + '</p>';
        }
    } catch (error) {
        console.error('API discovery error:', error);
        document.getElementById('apiListContainer').innerHTML = 
            '<p style="color: red;">Error: ' + error.message + '</p>';
    }
}

/**
 * Update stats display
 */
function updateStats(stats) {
    const el = document.getElementById('statsText');
    if (el) {
        el.textContent = `Modules: ${stats.total_modules} • Endpoints: ${stats.total_endpoints}`;
    }
}

/**
 * Render API list
 */
function renderAPIList(apis) {
    const container = document.getElementById('apiListContainer');
    if (!container) return;
    
    let html = '';
    
    Object.entries(apis).forEach(([moduleName, config]) => {
        html += `
            <div style="margin-bottom: 20px;">
                <div style="font-weight: 600; color: #333; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 2px solid #007bff;">
                    ${config.displayName}
                </div>
        `;
        
        config.endpoints.forEach(endpoint => {
            const methodColors = {
                'GET': '#61affe',
                'POST': '#49cc90',
                'PUT': '#fca130',
                'DELETE': '#f93e3e'
            };
            
            html += `
                <div class="api-endpoint" data-module="${moduleName}" data-endpoint='${JSON.stringify(endpoint)}' data-baseurl="${config.baseUrl}"
                     style="padding: 10px; margin-bottom: 5px; border-radius: 4px; cursor: pointer; transition: background 0.2s;"
                     onmouseover="this.style.background='#f8f9fa'"
                     onmouseout="if (!this.classList.contains('selected')) this.style.background=''"
                     onclick="selectEndpoint(this)">
                    <div>
                        <span style="display: inline-block; padding: 2px 8px; border-radius: 3px; font-weight: 600; font-size: 12px; margin-right: 8px; background: ${methodColors[endpoint.method]}; color: white;">
                            ${endpoint.method}
                        </span>
                        <span style="font-family: monospace; font-size: 13px;">${endpoint.path}</span>
                    </div>
                    ${endpoint.description ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${endpoint.description}</div>` : ''}
                </div>
            `;
        });
        
        html += '</div>';
    });
    
    container.innerHTML = html;
}

/**
 * Select an endpoint
 */
window.selectEndpoint = function(element) {
    // Remove previous selection
    document.querySelectorAll('.api-endpoint').forEach(el => {
        el.classList.remove('selected');
        el.style.background = '';
        el.style.borderLeft = '';
    });
    
    // Mark as selected
    element.classList.add('selected');
    element.style.background = '#e7f3ff';
    element.style.borderLeft = '3px solid #007bff';
    
    // Get data
    const moduleName = element.dataset.module;
    const endpoint = JSON.parse(element.dataset.endpoint);
    const baseUrl = element.dataset.baseurl;
    
    selectedEndpoint = { moduleName, endpoint, baseUrl };
    
    // Populate form
    document.getElementById('httpMethod').value = endpoint.method;
    document.getElementById('endpointUrl').value = baseUrl + endpoint.path;
    
    // Show/hide params
    const hasParams = endpoint.path.includes('<') && endpoint.path.includes('>');
    document.getElementById('paramsDiv').style.display = hasParams ? 'block' : 'none';
    
    updateBodyVisibility();
    
    // Clear previous response
    document.getElementById('responseSection').style.display = 'none';
};

/**
 * Update body visibility based on method
 */
function updateBodyVisibility() {
    const method = document.getElementById('httpMethod')?.value;
    const hasBody = ['POST', 'PUT'].includes(method);
    const bodyDiv = document.getElementById('bodyDiv');
    if (bodyDiv) {
        bodyDiv.style.display = hasBody ? 'block' : 'none';
    }
}

/**
 * Execute API request
 */
async function executeRequest() {
    const method = document.getElementById('httpMethod').value;
    let url = document.getElementById('endpointUrl').value;
    const params = document.getElementById('pathParams').value;
    const body = document.getElementById('requestBody').value;
    
    // Handle path parameters
    if (url.includes('<') && url.includes('>') && params) {
        url = url.replace(/<[^>]+>/, params);
    }
    
    // Show loading
    const responseSection = document.getElementById('responseSection');
    responseSection.style.display = 'block';
    document.getElementById('responseStatus').textContent = 'Loading...';
    document.getElementById('responseStatus').style.color = '';
    document.getElementById('responseTime').textContent = '-';
    document.getElementById('responseBody').textContent = 'Executing request...';
    
    try {
        const startTime = performance.now();
        
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        if (['POST', 'PUT'].includes(method) && body.trim()) {
            options.body = body;
        }
        
        const response = await fetch(url, options);
        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(2);
        
        const contentType = response.headers.get('content-type');
        let responseData;
        
        if (contentType && contentType.includes('application/json')) {
            responseData = await response.json();
        } else {
            responseData = await response.text();
        }
        
        // Display response
        document.getElementById('responseStatus').textContent = `${response.status} ${response.ok ? 'OK' : 'Error'}`;
        document.getElementById('responseStatus').style.color = response.ok ? '#28a745' : '#dc3545';
        document.getElementById('responseTime').textContent = `${duration}ms`;
        document.getElementById('responseBody').textContent = 
            typeof responseData === 'object' ? JSON.stringify(responseData, null, 2) : responseData;
        
    } catch (error) {
        document.getElementById('responseStatus').textContent = 'Error';
        document.getElementById('responseStatus').style.color = '#dc3545';
        document.getElementById('responseTime').textContent = '-';
        document.getElementById('responseBody').textContent = error.message;
    }
}

/**
 * Clear form
 */
function clearForm() {
    document.getElementById('httpMethod').value = 'GET';
    document.getElementById('endpointUrl').value = '';
    document.getElementById('pathParams').value = '';
    document.getElementById('requestBody').value = '';
    document.getElementById('responseSection').style.display = 'none';
    document.getElementById('paramsDiv').style.display = 'none';
    document.getElementById('bodyDiv').style.display = 'none';
    
    // Remove selection
    document.querySelectorAll('.api-endpoint').forEach(el => {
        el.classList.remove('selected');
        el.style.background = '';
        el.style.borderLeft = '';
    });
    
    selectedEndpoint = null;
}

/**
 * Copy response to clipboard
 */
function copyResponse() {
    const text = document.getElementById('responseBody').textContent;
    navigator.clipboard.writeText(text).then(() => {
        sap.m.MessageToast.show('Response copied to clipboard');
    }).catch(err => {
        console.error('Copy failed:', err);
        sap.m.MessageToast.show('Copy failed');
    });
}

export async function initializeAPIPlaygroundSimple() {
    console.log('📋 API Playground (Simple) initialized');
}