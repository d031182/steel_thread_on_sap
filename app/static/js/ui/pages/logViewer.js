/**
 * Log Viewer Page Logic
 * 
 * Handles the UI for viewing application logs from Flask backend.
 * Displays logs in a table with filtering and auto-refresh capabilities.
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

import { LogViewerAPI } from '../../api/logViewerAPI.js';

// Create API instance
const logViewerAPI = new LogViewerAPI();

// State
let currentFilter = null;
let autoRefreshInterval = null;
let isAutoRefreshEnabled = false;

/**
 * Initialize Log Viewer
 */
export async function initializeLogViewer() {
    console.log('📋 Initializing Log Viewer...');
    await loadLogs();
    startAutoRefresh();
}

/**
 * Load and display logs
 */
export async function loadLogs(level = null) {
    const logsContainer = document.getElementById('logsContainer');
    const statsContainer = document.getElementById('logStats');
    
    try {
        // Show loading state
        logsContainer.innerHTML = '<div style="text-align: center; padding: 2rem;"><div style="font-size: 2rem;">⏳</div><div>Loading logs...</div></div>';
        
        // Fetch logs
        const result = await logViewerAPI.getLogs({ level, limit: 100 });
        
        currentFilter = level;
        
        // Display logs
        renderLogs(result.logs);
        
        // Update statistics
        const statsResult = await logViewerAPI.getLogStats();
        if (statsResult.success) {
            renderStatistics(statsResult.stats);
        }
        
        console.log(`✓ Loaded ${result.count} log entries`);
        
    } catch (error) {
        console.error('Failed to load logs:', error);
        logsContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--sapNegativeColor);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                <div><strong>Error Loading Logs</strong></div>
                <div style="font-size: 0.75rem; margin-top: 0.5rem;">${error.message}</div>
                <button class="sapButton sapButtonDefault" onclick="window.refreshLogs()" style="margin-top: 1rem;">
                    🔄 Retry
                </button>
            </div>
        `;
    }
}

/**
 * Format log level with color and icon
 */
function formatLogLevel(level) {
    const formats = {
        'INFO': { color: '#0070f2', icon: 'ℹ️', label: 'INFO' },
        'WARNING': { color: '#e9730c', icon: '⚠️', label: 'WARNING' },
        'ERROR': { color: '#b00', icon: '❌', label: 'ERROR' }
    };
    return formats[level] || { color: '#666', icon: '●', label: level };
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

/**
 * Render logs in table
 */
function renderLogs(logs) {
    const logsContainer = document.getElementById('logsContainer');
    
    if (logs.length === 0) {
        logsContainer.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--sapNeutralColor);">No logs found</div>';
        return;
    }
    
    let html = `
        <table class="sapTable" style="width: 100%; font-size: 0.75rem;">
            <thead>
                <tr>
                    <th style="width: 140px;">Time</th>
                    <th style="width: 80px;">Level</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    logs.forEach(log => {
        const levelFormat = formatLogLevel(log.level);
        const timestamp = formatTimestamp(log.timestamp);
        
        html += `
            <tr>
                <td style="font-family: monospace; font-size: 0.7rem;">${timestamp}</td>
                <td>
                    <span class="sapObjectStatus" style="background-color: ${levelFormat.color}; color: white; padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-size: 0.625rem;">
                        ${levelFormat.icon} ${levelFormat.label}
                    </span>
                </td>
                <td style="font-family: monospace; font-size: 0.7rem; word-break: break-all;">${escapeHtml(log.message)}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    logsContainer.innerHTML = html;
}

/**
 * Render statistics
 */
function renderStatistics(stats) {
    const statsContainer = document.getElementById('logStats');
    
    const html = `
        <div style="display: flex; gap: 1rem; padding: 0.75rem; background-color: var(--sapBackgroundColor); border: 1px solid #e5e5e5; border-radius: 0.25rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-weight: 600;">Total:</span>
                <span class="sapObjectStatus sapStatusInfo">${stats.total || 0}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-weight: 600;">ℹ️ Info:</span>
                <span class="sapObjectStatus sapStatusInfo" style="background-color: #0070f2;">${stats.info || 0}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-weight: 600;">⚠️ Warnings:</span>
                <span class="sapObjectStatus sapStatusWarning" style="background-color: #e9730c;">${stats.warning || 0}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-weight: 600;">❌ Errors:</span>
                <span class="sapObjectStatus sapStatusError" style="background-color: #b00;">${stats.error || 0}</span>
            </div>
        </div>
    `;
    
    statsContainer.innerHTML = html;
}

/**
 * Filter logs by level
 */
export function filterLogs(level) {
    loadLogs(level === 'ALL' ? null : level);
}

/**
 * Clear all logs
 */
export async function clearAllLogs() {
    if (!confirm('Are you sure you want to clear all logs?')) {
        return;
    }
    
    try {
        const result = await logViewerAPI.clearLogs();
        showToast('✓ Logs cleared successfully');
        await loadLogs(currentFilter);
    } catch (error) {
        console.error('Failed to clear logs:', error);
        showToast('❌ Failed to clear logs: ' + error.message);
    }
}

/**
 * Toggle auto-refresh
 */
export function toggleAutoRefresh() {
    isAutoRefreshEnabled = !isAutoRefreshEnabled;
    
    if (isAutoRefreshEnabled) {
        startAutoRefresh();
        showToast('✓ Auto-refresh enabled (5s)');
    } else {
        stopAutoRefresh();
        showToast('○ Auto-refresh disabled');
    }
    
    // Update button state
    updateAutoRefreshButton();
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    isAutoRefreshEnabled = true;
    autoRefreshInterval = setInterval(() => {
        loadLogs(currentFilter);
    }, 5000);  // Refresh every 5 seconds
    
    updateAutoRefreshButton();
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
    isAutoRefreshEnabled = false;
    updateAutoRefreshButton();
}

/**
 * Update auto-refresh button state
 */
function updateAutoRefreshButton() {
    const button = document.getElementById('autoRefreshBtn');
    if (button) {
        button.textContent = isAutoRefreshEnabled ? '⏸️ Pause Auto-Refresh' : '▶️ Start Auto-Refresh';
        button.className = isAutoRefreshEnabled ? 'sapButton sapButtonEmphasized' : 'sapButton sapButtonDefault';
    }
}

/**
 * Refresh logs manually
 */
export function refreshLogs() {
    loadLogs(currentFilter);
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show toast notification
 */
function showToast(message) {
    // Use existing toast function if available
    if (window.showToast) {
        window.showToast(message);
    } else {
        console.log(message);
    }
}

// Cleanup on page navigation
export function cleanup() {
    stopAutoRefresh();
}
