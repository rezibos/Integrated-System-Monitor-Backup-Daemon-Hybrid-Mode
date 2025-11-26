// Configuration
const CONFIG = {
    dataFile: 'data.json',
    refreshInterval: 5000, // 5 seconds
};

// Fetch and update data
async function fetchData() {
    try {
        // Add timestamp to prevent caching
        const response = await fetch(`${CONFIG.dataFile}?t=${new Date().getTime()}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching data:', error);
        showError();
    }
}

// Update all dashboard elements
function updateDashboard(data) {
    updateHeader(data);
    updateSystemInfo(data);
    updateResources(data);
    updateUpdates(data);
    updateBackup(data);
    updateLogs(data);
}

// Update header information
function updateHeader(data) {
    const lastCheck = document.getElementById('lastCheck');
    const uptime = document.getElementById('uptime');
    
    if (lastCheck) lastCheck.textContent = data.last_check || 'N/A';
    if (uptime) uptime.textContent = data.uptime || 'N/A';
}

// Update system information bar
function updateSystemInfo(data) {
    const system = data.system || {};
    
    const hostname = document.getElementById('hostname');
    const kernel = document.getElementById('kernel');
    const arch = document.getElementById('arch');
    const bootTime = document.getElementById('bootTime');
    
    if (hostname) hostname.textContent = system.hostname || 'Unknown';
    if (kernel) kernel.textContent = system.kernel || 'Unknown';
    if (arch) arch.textContent = system.arch || 'Unknown';
    if (bootTime) bootTime.textContent = data.boot_time || 'N/A';
}

// Update resource usage (CPU, RAM, Disk)
function updateResources(data) {
    const resources = data.resources || {};
    
    // CPU
    const cpu = resources.cpu || 0;
    updateProgressBar('cpu', cpu, `${cpu}%`);
    
    // RAM
    const ram = resources.ram || {};
    const ramPercent = ram.percent || 0;
    const ramUsed = ram.used_gb || 0;
    const ramTotal = ram.total_gb || 0;
    updateProgressBar('ram', ramPercent, `${ramUsed} GB`);
    
    const ramFooter = document.getElementById('ramFooter');
    if (ramFooter) {
        ramFooter.textContent = `${ramUsed} GB / ${ramTotal} GB (${ramPercent}%)`;
    }
    
    // Disk
    const disk = resources.disk || {};
    const diskPercent = parseFloat(disk.percent) || 0;
    updateProgressBar('disk', diskPercent, `${diskPercent}%`);
    
    const diskFooter = document.getElementById('diskFooter');
    if (diskFooter) {
        diskFooter.textContent = `${disk.used || '0'} / ${disk.total || '0'} (${disk.available || '0'} free)`;
    }
}

// Helper function to update progress bars
function updateProgressBar(type, percent, valueText) {
    const bar = document.getElementById(`${type}Bar`);
    const value = document.getElementById(`${type}Value`);
    
    if (bar) {
        bar.style.width = `${Math.min(percent, 100)}%`;
    }
    
    if (value) {
        value.textContent = valueText;
    }
}

// Update system updates section
function updateUpdates(data) {
    const updates = data.updates || {};
    const count = updates.count || 0;
    const list = updates.list || [];
    const distro = updates.distro || 'Unknown';
    
    // Update badge
    const badge = document.getElementById('updateBadge');
    if (badge) {
        badge.textContent = count;
        badge.className = count > 0 ? 'badge badge-warning' : 'badge badge-success';
    }
    
    // Update info box
    const infoBox = document.getElementById('updateInfo');
    if (infoBox) {
        if (count === 0) {
            infoBox.innerHTML = `
                <p style="color: var(--success); font-weight: 600;">
                    ✅ System is fully updated!
                </p>
                <p style="font-size: 0.9rem; margin-top: 5px;">
                    Distribution: ${distro}
                </p>
            `;
        } else {
            infoBox.innerHTML = `
                <p style="color: var(--warning); font-weight: 600;">
                    ⚠️ ${count} package(s) available for update
                </p>
                <p style="font-size: 0.9rem; margin-top: 5px;">
                    Distribution: ${distro} | Log: ${updates.log_file || 'N/A'}
                </p>
            `;
        }
    }
    
    // Update table
    const tableBody = document.querySelector('#updateTable tbody');
    if (tableBody) {
        if (count === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center" style="color: var(--success); padding: 20px;">
                        ✅ No updates available
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = list.map(pkg => `
                <tr>
                    <td style="font-weight: 600; color: var(--primary);">${escapeHtml(pkg.name)}</td>
                    <td style="font-family: monospace;">${escapeHtml(pkg.current || '-')}</td>
                    <td style="font-family: monospace; color: var(--success);">${escapeHtml(pkg.new || '-')}</td>
                </tr>
            `).join('');
        }
    }
}

// Update backup section
function updateBackup(data) {
    const backup = data.backup || {};
    const current = backup.current || {};
    const history = backup.history || [];
    
    // Update badge
    const badge = document.getElementById('backupBadge');
    if (badge) {
        if (current.status === 'success') {
            badge.textContent = '✓';
            badge.className = 'badge badge-success';
        } else {
            badge.textContent = '✗';
            badge.className = 'badge badge-danger';
        }
    }
    
    // Update status box
    const statusBox = document.getElementById('currentBackup');
    if (statusBox) {
        if (current.status === 'success') {
            statusBox.className = 'status-box';
            statusBox.innerHTML = `
                <div class="status-icon">✅</div>
                <div class="status-content">
                    <div class="status-title">Backup Successful</div>
                    <div class="status-details">
                        <strong>${escapeHtml(current.filename || 'N/A')}</strong><br>
                        Size: ${escapeHtml(current.size || 'N/A')} | 
                        Files: ${current.files || 0} | 
                        Time: ${escapeHtml(current.timestamp || 'N/A')}
                    </div>
                </div>
            `;
        } else {
            statusBox.className = 'status-box error';
            statusBox.innerHTML = `
                <div class="status-icon">❌</div>
                <div class="status-content">
                    <div class="status-title">Backup Failed</div>
                    <div class="status-details">${escapeHtml(current.msg || 'Unknown error')}</div>
                </div>
            `;
        }
    }
    
    // Update history list
    const historyList = document.getElementById('backupList');
    if (historyList) {
        if (history.length === 0) {
            historyList.innerHTML = '<li class="text-center">No backup history available</li>';
        } else {
            historyList.innerHTML = history.map(item => `
                <li>
                    <span class="item-name">📦 ${escapeHtml(item.name)}</span>
                    <div class="item-meta">
                        <span class="item-size">${escapeHtml(item.size)}</span>
                        <span class="item-date">${escapeHtml(item.date)}</span>
                    </div>
                </li>
            `).join('');
        }
    }
}

// Update logs section
function updateLogs(data) {
    const logs = data.logs || {};
    const updateLogs = logs.update_logs || [];
    
    const logsList = document.getElementById('logsList');
    if (logsList) {
        if (updateLogs.length === 0) {
            logsList.innerHTML = '<li class="text-center">No log files found</li>';
        } else {
            logsList.innerHTML = updateLogs.map(log => `
                <li>
                    <span class="item-name">📋 ${escapeHtml(log.name)}</span>
                    <div class="item-meta">
                        <span class="item-size">${escapeHtml(log.size)}</span>
                        <span class="item-date">${escapeHtml(log.date)}</span>
                    </div>
                </li>
            `).join('');
        }
    }
}

// Show error state
function showError() {
    const lastCheck = document.getElementById('lastCheck');
    if (lastCheck) {
        lastCheck.textContent = 'Error loading data';
        lastCheck.style.color = 'var(--danger)';
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Initialize dashboard
function init() {
    console.log('🚀 Dashboard initialized');
    fetchData();
    
    // Set up auto-refresh
    setInterval(fetchData, CONFIG.refreshInterval);
}

// Run on page load
document.addEventListener('DOMContentLoaded', init);