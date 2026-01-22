/**
 * Data Products Explorer Page Logic
 * 
 * Handles the UI for exploring real data products from HANA Cloud.
 * Integrates with dataProductsAPI for backend communication.
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

import { dataProductsAPI } from '../../api/dataProductsAPI.js';

// State
let allDataProducts = [];
let selectedProduct = null;
let selectedTable = null;

/**
 * Initialize Data Products Explorer
 */
export async function initializeExplorer() {
    console.log('🗄️ Initializing Data Products Explorer...');
    await loadDataProducts();
}

/**
 * Load and display all data products
 */
export async function loadDataProducts() {
    const listContainer = document.getElementById('dataProductsList');
    
    try {
        listContainer.innerHTML = '<div style="text-align: center; padding: 2rem;"><div style="font-size: 2rem;">⏳</div><div>Loading...</div></div>';
        
        const result = await dataProductsAPI.listDataProducts();
        
        if (!result.success) {
            throw new Error(result.error?.message || 'Failed to load data products');
        }
        
        allDataProducts = result.dataProducts;
        renderDataProductsList(allDataProducts);
        
        console.log(`✓ Loaded ${allDataProducts.length} data products`);
        
    } catch (error) {
        console.error('Failed to load data products:', error);
        listContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--sapNegativeColor);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                <div><strong>Error Loading Data Products</strong></div>
                <div style="font-size: 0.75rem; margin-top: 0.5rem;">${error.message}</div>
                <button class="sapButton sapButtonDefault" onclick="window.refreshDataProducts()" style="margin-top: 1rem;">
                    🔄 Retry
                </button>
            </div>
        `;
    }
}

/**
 * Render data products list
 */
function renderDataProductsList(products) {
    const listContainer = document.getElementById('dataProductsList');
    
    if (products.length === 0) {
        listContainer.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--sapNeutralColor);">No data products found</div>';
        return;
    }
    
    listContainer.innerHTML = products.map(dp => `
        <div class="instanceCard ${selectedProduct?.schemaName === dp.schemaName ? 'selected' : ''}" 
             onclick="window.selectDataProduct('${dp.schemaName}')" 
             style="cursor: pointer;">
            <div class="instanceCardHeader">
                <div>
                    <div class="instanceName">📊 ${dp.productName}</div>
                    <span class="sapObjectStatus sapStatusInfo">${dp.version}</span>
                </div>
            </div>
            <div class="instanceDetails">
                <div style="font-size: 0.7rem; color: var(--sapNeutralColor); word-break: break-all;">${dp.schemaName}</div>
                <div style="margin-top: 0.5rem;">🕐 ${new Date(dp.createTime).toLocaleDateString()}</div>
            </div>
        </div>
    `).join('');
}

/**
 * Select and display a data product
 */
export async function selectDataProduct(schemaName) {
    selectedProduct = allDataProducts.find(dp => dp.schemaName === schemaName);
    if (!selectedProduct) return;
    
    renderDataProductsList(allDataProducts);
    
    const contentDiv = document.getElementById('explorerContent');
    contentDiv.innerHTML = '<div style="text-align: center; padding: 2rem;"><div style="font-size: 2rem;">⏳</div><div>Loading tables...</div></div>';
    
    try {
        const result = await dataProductsAPI.getTables(schemaName);
        
        if (!result.success) {
            throw new Error(result.error?.message || 'Failed to load tables');
        }
        
        displayDataProductDetails(selectedProduct, result.tables);
        
    } catch (error) {
        console.error('Failed to load tables:', error);
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--sapNegativeColor);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                <div><strong>Error Loading Tables</strong></div>
                <div style="font-size: 0.75rem; margin-top: 0.5rem;">${error.message}</div>
            </div>
        `;
    }
}

/**
 * Display data product details with tables
 */
function displayDataProductDetails(product, tables) {
    const contentDiv = document.getElementById('explorerContent');
    
    let html = `
        <div style="padding: 1.5rem;">
            <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊 ${product.productName}</h2>
            <p style="color: var(--sapNeutralColor); margin-bottom: 1rem;">
                ${product.namespace} • ${product.version}
            </p>
            
            <div style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
                <span class="sapObjectStatus sapStatusSuccess">${tables.length} Tables</span>
                <span class="sapObjectStatus sapStatusInfo">Installed: ${new Date(product.createTime).toLocaleDateString()}</span>
                <button class="sapButton sapButtonEmphasized" onclick="window.viewCSNDefinition('${product.schemaName}', '${product.productName}')" style="font-size: 0.75rem; padding: 0.375rem 0.75rem; margin-left: auto;">
                    📄 View CSN Definition
                </button>
            </div>
            
            <h3 style="font-size: 1.125rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e5e5;">
                Tables
            </h3>
            
            <div style="display: grid; gap: 1rem;">
    `;
    
    tables.forEach(table => {
        const recordCount = table.RECORD_COUNT || 0;
        html += `
            <div class="tableCard" style="cursor: pointer;" onclick="window.viewTableData('${product.schemaName}', '${table.TABLE_NAME}')">
                <h4 style="font-size: 1rem; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
                    <span>📋 ${table.TABLE_NAME}</span>
                    <span class="sapObjectStatus sapStatusSuccess">${recordCount.toLocaleString()} rows</span>
                </h4>
                <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
                    <button class="sapButton sapButtonDefault" onclick="event.stopPropagation(); window.viewTableStructure('${product.schemaName}', '${table.TABLE_NAME}')" style="font-size: 0.75rem; padding: 0.375rem 0.75rem;">
                        🔍 Structure
                    </button>
                    <button class="sapButton sapButtonEmphasized" onclick="event.stopPropagation(); window.viewTableData('${product.schemaName}', '${table.TABLE_NAME}')" style="font-size: 0.75rem; padding: 0.375rem 0.75rem;">
                        📊 View Data
                    </button>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

/**
 * View table structure
 */
export async function viewTableStructure(schemaName, tableName) {
    const contentDiv = document.getElementById('explorerContent');
    contentDiv.innerHTML = '<div style="text-align: center; padding: 2rem;"><div style="font-size: 2rem;">⏳</div><div>Loading structure...</div></div>';
    
    try {
        const result = await dataProductsAPI.getTableStructure(schemaName, tableName);
        
        if (!result.success) {
            throw new Error(result.error?.message || 'Failed to load structure');
        }
        
        displayTableStructure(schemaName, tableName, result.columns);
        
    } catch (error) {
        console.error('Failed to load structure:', error);
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--sapNegativeColor);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                <div><strong>Error Loading Structure</strong></div>
                <div style="font-size: 0.75rem; margin-top: 0.5rem;">${error.message}</div>
            </div>
        `;
    }
}

/**
 * Display table structure
 */
function displayTableStructure(schemaName, tableName, columns) {
    const contentDiv = document.getElementById('explorerContent');
    
    let html = `
        <div style="padding: 1.5rem;">
            <button class="sapButton sapButtonTransparent" onclick="window.selectDataProduct('${schemaName}')" style="margin-bottom: 1rem;">
                ← Back to ${selectedProduct?.productName || 'Tables'}
            </button>
            
            <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">📋 ${tableName}</h2>
            <p style="color: var(--sapNeutralColor); margin-bottom: 1.5rem;">Table Structure</p>
            
            <div style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem;">
                <span class="sapObjectStatus sapStatusSuccess">${columns.length} Columns</span>
                <button class="sapButton sapButtonEmphasized" onclick="window.viewTableData('${schemaName}', '${tableName}')">
                    📊 View Data
                </button>
            </div>
            
            <table class="sapTable">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Column Name</th>
                        <th>Data Type</th>
                        <th>Length</th>
                        <th>Nullable</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    columns.forEach(col => {
        const nullable = col.IS_NULLABLE === 'TRUE' ? '✓' : '';
        const length = col.LENGTH || '-';
        html += `
            <tr>
                <td>${col.POSITION}</td>
                <td><code>${col.COLUMN_NAME}</code></td>
                <td><span class="sapObjectStatus sapStatusInfo">${col.DATA_TYPE_NAME}</span></td>
                <td>${length}</td>
                <td>${nullable}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

/**
 * View table data
 */
export async function viewTableData(schemaName, tableName, page = 1) {
    const contentDiv = document.getElementById('explorerContent');
    contentDiv.innerHTML = '<div style="text-align: center; padding: 2rem;"><div style="font-size: 2rem;">⏳</div><div>Loading data...</div></div>';
    
    const limit = 100;
    const offset = (page - 1) * limit;
    
    try {
        const result = await dataProductsAPI.queryTable(schemaName, tableName, {
            limit,
            offset
        });
        
        if (!result.success) {
            throw new Error(result.error?.message || 'Failed to load data');
        }
        
        displayTableData(schemaName, tableName, result, page);
        
    } catch (error) {
        console.error('Failed to load data:', error);
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--sapNegativeColor);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                <div><strong>Error Loading Data</strong></div>
                <div style="font-size: 0.75rem; margin-top: 0.5rem;">${error.message}</div>
            </div>
        `;
    }
}

/**
 * Display table data
 */
function displayTableData(schemaName, tableName, result, page) {
    const contentDiv = document.getElementById('explorerContent');
    
    const totalPages = Math.ceil(result.totalCount / result.limit);
    
    let html = `
        <div style="padding: 1.5rem;">
            <button class="sapButton sapButtonTransparent" onclick="window.selectDataProduct('${schemaName}')" style="margin-bottom: 1rem;">
                ← Back to ${selectedProduct?.productName || 'Tables'}
            </button>
            
            <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊 ${tableName}</h2>
            <p style="color: var(--sapNeutralColor); margin-bottom: 1.5rem;">
                Showing ${result.rowCount} of ${result.totalCount.toLocaleString()} rows • ${result.executionTime}ms
            </p>
            
            <div style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem; align-items: center;">
                <button class="sapButton sapButtonDefault" onclick="window.viewTableStructure('${schemaName}', '${tableName}')">
                    🔍 View Structure
                </button>
                <button class="sapButton sapButtonDefault" onclick="window.exportTableData('${schemaName}', '${tableName}')">
                    📥 Export CSV
                </button>
                <div style="margin-left: auto; display: flex; gap: 0.5rem; align-items: center;">
                    <button class="sapButton sapButtonDefault" ${page === 1 ? 'disabled' : ''} onclick="window.viewTableData('${schemaName}', '${tableName}', ${page - 1})">
                        ◀ Previous
                    </button>
                    <span>Page ${page} of ${totalPages}</span>
                    <button class="sapButton sapButtonDefault" ${page >= totalPages ? 'disabled' : ''} onclick="window.viewTableData('${schemaName}', '${tableName}', ${page + 1})">
                        Next ▶
                    </button>
                </div>
            </div>
            
            <div style="overflow-x: auto;">
                <table class="sapTable">
                    <thead>
                        <tr>
    `;
    
    // Headers
    result.columns.forEach(col => {
        html += `<th>${col.name}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    // Rows
    result.rows.forEach(row => {
        html += '<tr>';
        result.columns.forEach(col => {
            const value = row[col.name];
            html += `<td>${value !== null && value !== undefined ? escapeHtml(String(value)) : '<span style="color: var(--sapNeutralColor);">NULL</span>'}</td>`;
        });
        html += '</tr>';
    });
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

/**
 * Filter data products list
 */
export function filterDataProducts() {
    const searchInput = document.getElementById('dpSearchInput');
    const searchTerm = searchInput.value.toLowerCase();
    
    const filtered = allDataProducts.filter(dp => 
        dp.productName.toLowerCase().includes(searchTerm) ||
        dp.schemaName.toLowerCase().includes(searchTerm)
    );
    
    renderDataProductsList(filtered);
}

/**
 * View CSN Definition for a data product
 */
export async function viewCSNDefinition(schemaName, productName) {
    console.log(`📄 Viewing CSN definition for ${productName}...`);
    
    // Create modal overlay
    const modal = document.createElement('div');
    modal.id = 'csnModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 1rem;
    `;
    
    // Create modal content
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        max-width: 90vw;
        max-height: 90vh;
        width: 1200px;
        display: flex;
        flex-direction: column;
    `;
    
    // Modal header
    modalContent.innerHTML = `
        <div style="padding: 1.5rem; border-bottom: 1px solid #e5e5e5; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="font-size: 1.5rem; margin: 0;">📄 CSN Definition - ${productName}</h2>
                <p style="color: var(--sapNeutralColor); margin: 0.5rem 0 0 0; font-size: 0.875rem;">Core Schema Notation</p>
            </div>
            <button onclick="window.closeCSNModal()" class="sapButton sapButtonTransparent" style="font-size: 1.5rem; padding: 0.25rem 0.5rem;">
                ✕
            </button>
        </div>
        <div id="csnContent" style="padding: 1.5rem; overflow-y: auto; flex: 1;">
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem;">⏳</div>
                <div>Loading CSN definition...</div>
            </div>
        </div>
        <div style="padding: 1rem 1.5rem; border-top: 1px solid #e5e5e5; display: flex; gap: 0.5rem; justify-content: flex-end;">
            <button onclick="window.downloadCSN()" class="sapButton sapButtonDefault" id="downloadCSNBtn" disabled>
                📥 Download JSON
            </button>
            <button onclick="window.copyCSN()" class="sapButton sapButtonDefault" id="copyCSNBtn" disabled>
                📋 Copy to Clipboard
            </button>
            <button onclick="window.closeCSNModal()" class="sapButton sapButtonEmphasized">
                Close
            </button>
        </div>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Close modal on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeCSNModal();
        }
    });
    
    // Fetch CSN definition
    try {
        const result = await dataProductsAPI.getCSNDefinition(schemaName);
        
        const contentDiv = document.getElementById('csnContent');
        
        if (!result.success) {
            contentDiv.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--sapNegativeColor);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                    <div><strong>Error Loading CSN</strong></div>
                    <div style="font-size: 0.875rem; margin-top: 0.5rem;">${result.error?.message || 'Failed to retrieve CSN definition'}</div>
                    ${result.error?.hint ? `<div style="font-size: 0.75rem; margin-top: 0.5rem; color: var(--sapInformationColor);">💡 ${result.error.hint}</div>` : ''}
                </div>
            `;
            return;
        }
        
        // Store CSN data globally for copy/download
        window.currentCSN = result.csn;
        window.currentCSNProductName = productName;
        
        // Enable buttons
        document.getElementById('downloadCSNBtn').disabled = false;
        document.getElementById('copyCSNBtn').disabled = false;
        
        // Display CSN with metadata
        const entities = result.csn.definitions ? Object.keys(result.csn.definitions) : [];
        const entityCount = entities.length;
        
        contentDiv.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
                    <span class="sapObjectStatus sapStatusSuccess">${entityCount} Entities</span>
                    <span class="sapObjectStatus sapStatusInfo">Source: ${result.source === 'local_file' ? 'Local File' : 'BDC MCP'}</span>
                    ${result.ordId ? `<span class="sapObjectStatus sapStatusNeutral">ORD ID: ${result.ordId}</span>` : ''}
                </div>
                ${result.message ? `<div style="padding: 0.75rem; background: var(--sapInformationBackground); border-left: 3px solid var(--sapInformationColor); margin-bottom: 1rem; font-size: 0.875rem;">ℹ️ ${result.message}</div>` : ''}
            </div>
            
            ${entityCount > 0 ? `
                <h3 style="font-size: 1.125rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e5e5;">
                    Entities (${entityCount})
                </h3>
                <div style="display: grid; gap: 0.5rem; margin-bottom: 1.5rem;">
                    ${entities.map(entity => {
                        const def = result.csn.definitions[entity];
                        const elements = def.elements ? Object.keys(def.elements).length : 0;
                        return `
                            <div style="padding: 0.75rem; background: var(--sapBackgroundColor); border: 1px solid #e5e5e5; border-radius: 0.25rem;">
                                <div style="font-weight: 600; margin-bottom: 0.25rem;">${entity}</div>
                                <div style="font-size: 0.75rem; color: var(--sapNeutralColor);">${elements} fields • ${def.kind || 'entity'}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            ` : ''}
            
            <h3 style="font-size: 1.125rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e5e5;">
                Full CSN Definition
            </h3>
            <pre style="background: #f5f5f5; padding: 1rem; border-radius: 0.25rem; overflow-x: auto; margin: 0; font-family: 'Courier New', monospace; font-size: 0.875rem; line-height: 1.5;"><code>${escapeHtml(JSON.stringify(result.csn, null, 2))}</code></pre>
        `;
        
    } catch (error) {
        console.error('Failed to load CSN:', error);
        const contentDiv = document.getElementById('csnContent');
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--sapNegativeColor);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                <div><strong>Unexpected Error</strong></div>
                <div style="font-size: 0.875rem; margin-top: 0.5rem;">${error.message || 'Failed to load CSN definition'}</div>
            </div>
        `;
    }
}

/**
 * Close CSN modal
 */
export function closeCSNModal() {
    const modal = document.getElementById('csnModal');
    if (modal) {
        modal.remove();
    }
    window.currentCSN = null;
    window.currentCSNProductName = null;
}

/**
 * Download CSN as JSON file
 */
export function downloadCSN() {
    if (!window.currentCSN) return;
    
    const jsonString = JSON.stringify(window.currentCSN, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${window.currentCSNProductName || 'csn'}_definition.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('✓ CSN downloaded');
}

/**
 * Copy CSN to clipboard
 */
export async function copyCSN() {
    if (!window.currentCSN) return;
    
    try {
        const jsonString = JSON.stringify(window.currentCSN, null, 2);
        await navigator.clipboard.writeText(jsonString);
        
        // Show temporary success message
        const btn = document.getElementById('copyCSNBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✓ Copied!';
        btn.disabled = true;
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 2000);
        
        console.log('✓ CSN copied to clipboard');
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        alert('Failed to copy to clipboard');
    }
}

/**
 * Export table data as CSV (placeholder)
 */
export function exportTableData(schemaName, tableName) {
    alert(`CSV export for ${tableName} will be implemented in Phase 5`);
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions for global access
export function refresh() {
    selectedProduct = null;
    selectedTable = null;
    loadDataProducts();
}
