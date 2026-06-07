let currentPhone = null;
let allGroups = [];
let selectedGroupsMap = new Map();

async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('totalAccounts').textContent = data.total_accounts;
        document.getElementById('totalGroups').textContent = data.total_groups;
        document.getElementById('selectedGroups').textContent = data.selected_groups;
        document.getElementById('messagesSent').textContent = data.messages_sent;
        document.getElementById('failedCount').textContent = data.failed_count;
        
        const statusBadge = document.getElementById('statusBadge');
        if (data.broadcasting) {
            statusBadge.textContent = 'Broadcasting';
            statusBadge.style.backgroundColor = '#28a745';
        } else {
            statusBadge.textContent = 'Idle';
            statusBadge.style.backgroundColor = '#dc3545';
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

async function updateAccountsList() {
    try {
        const response = await fetch('/api/accounts');
        const accounts = await response.json();
        
        const accountsList = document.getElementById('accountsList');
        const accountSelect = document.getElementById('accountSelect');
        
        accountsList.innerHTML = '';
        accountSelect.innerHTML = '<option value="">Choose an account...</option>';
        
        if (accounts.length === 0) {
            accountsList.innerHTML = '<p class="text-muted">No accounts connected</p>';
            return;
        }
        
        accounts.forEach(account => {
            const statusColor = account.status === 'online' ? 'success' : 'danger';
            const statusText = account.status.toUpperCase();
            
            const accountItem = document.createElement('div');
            accountItem.className = 'account-item';
            accountItem.innerHTML = `
                <div class="account-info">
                    <h6>${account.phone}</h6>
                    <small>Status: <span class="badge bg-${statusColor}">${statusText}</span> | Groups: ${account.groups_loaded}</small>
                </div>
                <div class="account-actions">
                    <button class="btn btn-sm btn-info" onclick="loadGroupsForAccount('${account.phone}')">Load Groups</button>
                    <button class="btn btn-sm btn-warning" onclick="reconnectAccount('${account.phone}')">Reconnect</button>
                    <button class="btn btn-sm btn-danger" onclick="removeAccount('${account.phone}')">Remove</button>
                </div>
            `;
            accountsList.appendChild(accountItem);
            
            const option = document.createElement('option');
            option.value = account.phone;
            option.textContent = account.phone + (account.status === 'online' ? ' (Online)' : ' (Offline)');
            accountSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error updating accounts list:', error);
    }
}

async function updateLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        
        const logsList = document.getElementById('logsList');
        
        if (logs.length === 0) {
            logsList.innerHTML = '<p class="text-muted">No logs yet</p>';
            return;
        }
        
        logsList.innerHTML = '';
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log[2].toLowerCase()}`;
            logEntry.innerHTML = `<strong>[${log[1]}]</strong> [${log[2].toUpperCase()}] ${log[3]}`;
            logsList.appendChild(logEntry);
        });
        
        logsList.scrollTop = logsList.scrollHeight;
    } catch (error) {
        console.error('Error updating logs:', error);
    }
}

async function addAccount() {
    const phone = document.getElementById('phoneInput').value.trim();
    
    if (!phone) {
        alert('Please enter a phone number');
        return;
    }
    
    try {
        const response = await fetch('/api/add-account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPhone = phone;
            showOtpModal(phone);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error adding account:', error);
        alert('Error adding account');
    }
}

function showOtpModal(phone) {
    document.getElementById('otpPhone').textContent = `Enter OTP sent to ${phone}`;
    document.getElementById('otpInput').value = '';
    document.getElementById('otpModal').style.display = 'block';
}

function closeOtpModal() {
    document.getElementById('otpModal').style.display = 'none';
    currentPhone = null;
}

async function submitOtp() {
    const otp = document.getElementById('otpInput').value.trim();
    
    if (!otp || !currentPhone) {
        alert('Please enter OTP');
        return;
    }
    
    try {
        const response = await fetch('/api/verify-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: currentPhone, otp: otp })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Account added successfully!');
            document.getElementById('phoneInput').value = '';
            closeOtpModal();
            updateAccountsList();
            updateStats();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error verifying OTP:', error);
        alert('Error verifying OTP');
    }
}

async function removeAccount(phone) {
    if (!confirm(`Are you sure you want to remove account ${phone}?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/remove-account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateAccountsList();
            updateStats();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error removing account:', error);
    }
}

async function reconnectAccount(phone) {
    try {
        const response = await fetch('/api/reconnect-account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Account reconnected successfully');
            updateAccountsList();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error reconnecting account:', error);
    }
}

async function loadGroupsForAccount(phone) {
    try {
        const response = await fetch('/api/load-groups', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Loaded ${data.count} groups for ${phone}`);
            updateAccountsList();
            updateStats();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error loading groups:', error);
    }
}

async function loadGroups() {
    const phone = document.getElementById('accountSelect').value;
    
    if (!phone) {
        document.getElementById('groupsList').innerHTML = '<p class="text-muted">Select an account to load groups</p>';
        return;
    }
    
    try {
        const response = await fetch(`/api/groups/${phone}`);
        const groups = await response.json();
        
        allGroups = groups;
        displayGroups(groups);
    } catch (error) {
        console.error('Error loading groups:', error);
    }
}

function displayGroups(groups) {
    const groupsList = document.getElementById('groupsList');
    
    if (groups.length === 0) {
        groupsList.innerHTML = '<p class="text-muted">No groups found for this account</p>';
        return;
    }
    
    groupsList.innerHTML = '';
    groups.forEach(group => {
        const isSelected = selectedGroupsMap.has(`${group.id}`);
        const groupItem = document.createElement('div');
        groupItem.className = 'list-group-item';
        groupItem.style.cursor = 'pointer';
        groupItem.innerHTML = `
            <div style="display: flex; align-items: center;">
                <input type="checkbox" class="form-check-input group-checkbox" ${isSelected ? 'checked' : ''} onchange="toggleGroupSelection('${group.id}', '${group.name}')">
                <span>${group.name}</span>
            </div>
        `;
        groupsList.appendChild(groupItem);
    });
}

function toggleGroupSelection(groupId, groupName) {
    const phone = document.getElementById('accountSelect').value;
    const key = `${groupId}`;
    
    if (selectedGroupsMap.has(key)) {
        selectedGroupsMap.delete(key);
    } else {
        selectedGroupsMap.set(key, { phone: phone, id: groupId, name: groupName });
    }
}

function filterGroups() {
    const searchTerm = document.getElementById('groupSearch').value.toLowerCase();
    const filtered = allGroups.filter(group => group.name.toLowerCase().includes(searchTerm));
    displayGroups(filtered);
}

function selectAllGroups() {
    const phone = document.getElementById('accountSelect').value;
    if (!phone) {
        alert('Please select an account');
        return;
    }
    
    allGroups.forEach(group => {
        selectedGroupsMap.set(`${group.id}`, { phone: phone, id: group.id, name: group.name });
    });
    displayGroups(allGroups);
}

async function saveSelectedGroups() {
    if (selectedGroupsMap.size === 0) {
        alert('Please select at least one group');
        return;
    }
    
    const groups = Array.from(selectedGroupsMap.values());
    
    try {
        const response = await fetch('/api/save-selected-groups', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ groups: groups })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            updateStats();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error saving selected groups:', error);
    }
}

async function startBroadcast() {
    const message = document.getElementById('messageBox').value.trim();
    const delay = parseInt(document.getElementById('delayInput').value) || 0;
    const randomDelay = document.getElementById('randomDelayCheck').checked;
    const autoRepeat = document.getElementById('autoRepeatCheck').checked;
    const repeatInterval = parseInt(document.getElementById('repeatInterval').value) || 300;
    
    if (!message) {
        alert('Please enter a message');
        return;
    }
    
    try {
        const response = await fetch('/api/start-broadcast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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
            alert('Broadcasting started');
            updateStats();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error starting broadcast:', error);
    }
}

async function stopBroadcast() {
    try {
        const response = await fetch('/api/stop-broadcast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Broadcasting stopped');
            updateStats();
        }
    } catch (error) {
        console.error('Error stopping broadcast:', error);
    }
}

async function exportLogs() {
    try {
        const response = await fetch('/api/export-logs');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logs_${new Date().getTime()}.txt`;
        a.click();
    } catch (error) {
        console.error('Error exporting logs:', error);
    }
}

async function clearLogs() {
    if (!confirm('Are you sure you want to clear all logs?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/clear-logs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateLogs();
        }
    } catch (error) {
        console.error('Error clearing logs:', error);
    }
}

setInterval(updateStats, 2000);
setInterval(updateAccountsList, 3000);
setInterval(updateLogs, 1000);

window.addEventListener('load', () => {
    updateStats();
    updateAccountsList();
    updateLogs();
});
