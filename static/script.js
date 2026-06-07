// Global variables
let currentPhone = null;
let allGroups = [];
let selectedGroups = new Set();
let currentPendingPhone = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadAccounts();
    loadLogs();
    setupEventListeners();
    
    // Refresh stats every 5 seconds
    setInterval(loadStats, 5000);
    // Refresh logs every 3 seconds
    setInterval(loadLogs, 3000);
});

function setupEventListeners() {
    // API Form
    document.getElementById('apiForm').addEventListener('submit', uploadApiCredentials);
    
    // Account Form
    document.getElementById('addAccountForm').addEventListener('submit', handleAddAccount);
    document.getElementById('verifyOtpBtn').addEventListener('click', handleVerifyOtp);
    
    // Groups
    document.getElementById('accountSelect').addEventListener('change', loadAccountGroups);
    document.getElementById('refreshGroupsBtn').addEventListener('click', refreshGroups);
    document.getElementById('selectAllBtn').addEventListener('click', selectAllGroups);
    document.getElementById('saveGroupsBtn').addEventListener('click', saveSelectedGroups);
    document.getElementById('searchGroups').addEventListener('input', filterGroups);
    
    // Broadcast
    document.getElementById('startBroadcastBtn').addEventListener('click', startBroadcast);
    document.getElementById('stopBroadcastBtn').addEventListener('click', stopBroadcast);
    
    // Logs
    document.getElementById('exportLogsBtn').addEventListener('click', exportLogs);
    document.getElementById('clearLogsBtn').addEventListener('click', clearLogs);
}

// API Credentials Upload
async function uploadApiCredentials(e) {
    e.preventDefault();
    const apiId = document.getElementById('apiId').value;
    const apiHash = document.getElementById('apiHash').value;
    
    try {
        const response = await fetch('/api/upload-api-hash', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({api_id: apiId, api_hash: apiHash})
        });
        
        const data = await response.json();
        const statusEl = document.getElementById('apiStatus');
        
        if (data.success) {
            statusEl.innerHTML = '<span class="badge bg-success">✓ Credentials Saved</span>';
            setTimeout(() => statusEl.innerHTML = '', 3000);
        } else {
            statusEl.innerHTML = '<span class="badge bg-danger">✗ ' + data.error + '</span>';
        }
    } catch (error) {
        document.getElementById('apiStatus').innerHTML = '<span class="badge bg-danger">✗ Error: ' + error.message + '</span>';
    }
}

// Load Statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('total-accounts').textContent = data.total_accounts;
        document.getElementById('total-groups').textContent = data.total_groups;
        document.getElementById('messages-sent').textContent = data.messages_sent;
        document.getElementById('failed-count').textContent = data.failed_count;
        
        const statusBadge = document.getElementById('status-badge');
        if (data.broadcasting) {
            statusBadge.textContent = '🔴 Broadcasting...';
            statusBadge.style.color = '#dc3545';
        } else {
            statusBadge.textContent = '🟢 Status: Ready';
            statusBadge.style.color = '#28a745';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Add Account
async function handleAddAccount(e) {
    e.preventDefault();
    const phone = document.getElementById('phoneNumber').value;
    
    try {
        const response = await fetch('/api/add-account', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone: phone})
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPendingPhone = phone;
            document.getElementById('otpModal').style.display = 'block';
            document.getElementById('phoneNumber').value = '';
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Verify OTP
async function handleVerifyOtp() {
    const otp = document.getElementById('otpCode').value;
    
    if (!otp || !currentPendingPhone) {
        alert('Please enter OTP code');
        return;
    }
    
    try {
        const response = await fetch('/api/verify-otp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone: currentPendingPhone, otp: otp})
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('otpModal').style.display = 'none';
            document.getElementById('otpCode').value = '';
            currentPendingPhone = null;
            loadAccounts();
            alert('Account added successfully!');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Load Accounts
async function loadAccounts() {
    try {
        const response = await fetch('/api/accounts');
        const accounts = await response.json();
        
        const accountsList = document.getElementById('accountsList');
        const accountSelect = document.getElementById('accountSelect');
        
        accountsList.innerHTML = '';
        accountSelect.innerHTML = '<option value="">Select Account</option>';
        
        accounts.forEach(account => {
            // Add to accounts list
            const card = document.createElement('div');
            card.className = 'col-md-6 mb-3';
            card.innerHTML = `
                <div class="account-card">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6>${account.phone}</h6>
                            <small>Groups: ${account.groups_loaded}</small>
                            <br>
                            <span class="badge ${account.status === 'online' ? 'badge-online' : 'badge-offline'}">${account.status.toUpperCase()}</span>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-warning" onclick="reconnectAccount('${account.phone}')">Reconnect</button>
                            <button class="btn btn-sm btn-danger" onclick="removeAccount('${account.phone}')">Remove</button>
                        </div>
                    </div>
                </div>
            `;
            accountsList.appendChild(card);
            
            // Add to select dropdown
            const option = document.createElement('option');
            option.value = account.phone;
            option.textContent = account.phone;
            accountSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading accounts:', error);
    }
}

// Remove Account
async function removeAccount(phone) {
    if (!confirm('Are you sure you want to remove this account?')) return;
    
    try {
        const response = await fetch('/api/remove-account', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone: phone})
        });
        
        const data = await response.json();
        if (data.success) {
            loadAccounts();
            alert('Account removed successfully');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Reconnect Account
async function reconnectAccount(phone) {
    try {
        const response = await fetch('/api/reconnect-account', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone: phone})
        });
        
        const data = await response.json();
        if (data.success) {
            loadAccounts();
            alert('Account reconnected successfully');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Load Account Groups
async function loadAccountGroups() {
    const phone = document.getElementById('accountSelect').value;
    if (!phone) {
        document.getElementById('groupsList').innerHTML = '';
        return;
    }
    
    currentPhone = phone;
    
    try {
        const response = await fetch(`/api/groups/${phone}`);
        allGroups = await response.json();
        displayGroups(allGroups);
    } catch (error) {
        console.error('Error loading groups:', error);
    }
}

// Refresh Groups
async function refreshGroups() {
    if (!currentPhone) {
        alert('Please select an account first');
        return;
    }
    
    try {
        const response = await fetch('/api/load-groups', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone: currentPhone})
        });
        
        const data = await response.json();
        if (data.success) {
            allGroups = data.groups;
            displayGroups(allGroups);
            alert(`Loaded ${data.count} groups`);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Display Groups
function displayGroups(groups) {
    const groupsList = document.getElementById('groupsList');
    groupsList.innerHTML = '';
    
    if (groups.length === 0) {
        groupsList.innerHTML = '<p class="text-muted">No groups found</p>';
        return;
    }
    
    groups.forEach((group, index) => {
        const isSelected = selectedGroups.has(group.id);
        const item = document.createElement('div');
        item.className = 'group-item';
        item.innerHTML = `
            <input type="checkbox" id="group_${index}" ${isSelected ? 'checked' : ''} 
                onchange="toggleGroup('${group.id}', this.checked)">
            <label for="group_${index}" style="cursor: pointer; margin-bottom: 0;">
                <strong>${group.name}</strong>
                <small class="text-muted">(${group.type})</small>
            </label>
        `;
        groupsList.appendChild(item);
    });
}

// Toggle Group Selection
function toggleGroup(groupId, checked) {
    if (checked) {
        selectedGroups.add(groupId);
    } else {
        selectedGroups.delete(groupId);
    }
}

// Select All Groups
function selectAllGroups() {
    allGroups.forEach(group => selectedGroups.add(group.id));
    displayGroups(allGroups);
}

// Filter Groups
function filterGroups() {
    const searchTerm = document.getElementById('searchGroups').value.toLowerCase();
    const filtered = allGroups.filter(g => g.name.toLowerCase().includes(searchTerm));
    displayGroups(filtered);
}

// Save Selected Groups
async function saveSelectedGroups() {
    if (selectedGroups.size === 0) {
        alert('Please select at least one group');
        return;
    }
    
    const groups = allGroups
        .filter(g => selectedGroups.has(g.id))
        .map(g => ({...g, phone: currentPhone}));
    
    try {
        const response = await fetch('/api/save-selected-groups', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({groups: groups})
        });
        
        const data = await response.json();
        if (data.success) {
            alert(`Saved ${groups.length} groups`);
            loadStats();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Start Broadcast
async function startBroadcast() {
    const message = document.getElementById('message').value;
    
    if (!message) {
        alert('Please enter a message');
        return;
    }
    
    const delay = parseInt(document.getElementById('delay').value) || 0;
    const randomDelay = document.getElementById('randomDelay').checked;
    const autoRepeat = document.getElementById('autoRepeat').checked;
    const repeatInterval = parseInt(document.getElementById('repeatInterval').value) || 300;
    
    try {
        const response = await fetch('/api/start-broadcast', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                delay: delay,
                random_delay: randomDelay,
                auto_repeat: autoRepeat,
                repeat_interval: repeatInterval
            })
        });
        
        const data = await response.json();
        if (data.success) {
            document.getElementById('startBroadcastBtn').style.display = 'none';
            document.getElementById('stopBroadcastBtn').style.display = 'inline-block';
            alert('Broadcasting started');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Stop Broadcast
async function stopBroadcast() {
    try {
        const response = await fetch('/api/stop-broadcast', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        if (data.success) {
            document.getElementById('startBroadcastBtn').style.display = 'inline-block';
            document.getElementById('stopBroadcastBtn').style.display = 'none';
            alert('Broadcasting stopped');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Load Logs
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        
        const logsList = document.getElementById('logsList');
        logsList.innerHTML = '';
        
        if (logs.length === 0) {
            logsList.innerHTML = '<p class="text-muted">No logs yet</p>';
            return;
        }
        
        logs.forEach(log => {
            const entry = document.createElement('div');
            entry.className = `log-entry ${log[2].toLowerCase()}`;
            entry.innerHTML = `
                <strong>[${log[2].toUpperCase()}]</strong> ${log[1]}<br>
                <small>${log[3]}</small>
            `;
            logsList.appendChild(entry);
        });
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Export Logs
function exportLogs() {
    window.location.href = '/api/export-logs';
}

// Clear Logs
async function clearLogs() {
    if (!confirm('Are you sure you want to clear all logs?')) return;
    
    try {
        const response = await fetch('/api/clear-logs', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        if (data.success) {
            loadLogs();
            alert('Logs cleared');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}