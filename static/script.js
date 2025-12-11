/**
 * ═══════════════════════════════════════════════════════════════
 * AURA ENERGY - AI Smart Home Optimization
 * Interactive Dashboard Controller
 * ═══════════════════════════════════════════════════════════════
 */

// ─── Configuration ─────────────────────────────────────────────
const API_BASE = '';
const DEVICE_ICONS = {
    'Air Conditioning': '❄️',
    'Heater': '🔥',
    'Dishwasher': '🍽️',
    'Oven': '🍳',
    'Washing Machine': '🧺',
    'Microwave': '📡',
    'Tv': '📺',
    'Computer': '💻',
    'Lights': '💡',
    'Fridge': '🧊',
    'Fan': '🌀',
    'Water Heater': '🚿',
    'default': '🔌'
};

const ROOM_ICONS = {
    'Living Room': '🛋️',
    'Bedroom': '🛏️',
    'Kitchen': '🍳',
    'Bathroom': '🚿',
    'Office': '💼',
    'Garage': '🚗',
    'Dining Room': '🍽️',
    'default': '🏠'
};

const CHART_COLORS = [
    '#FF6B35', '#2EC4B6', '#F7C59F', '#E71D36', 
    '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'
];

// ─── State ─────────────────────────────────────────────────────
let state = {
    homes: {},
    devices: {},
    activeHome: null,
    selectedEpisodes: 30,
    trainingInProgress: false,
    kpiData: [],
    currentModal: null,
    modalContext: {}
};

// ─── DOM Elements ──────────────────────────────────────────────
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// ─── Initialization ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initWelcomeScreen();
    initNavigation();
    initModals();
    initEventListeners();
    fetchInitialData();
});

// ─── Welcome Screen ────────────────────────────────────────────
function initWelcomeScreen() {
    const enterBtn = $('#enter-app');
    const loadingBar = $('#loading-bar');
    
    enterBtn.addEventListener('click', async () => {
        loadingBar.classList.add('active');
        const progress = loadingBar.querySelector('.loading-progress');
        
        // Animate loading
        let width = 0;
        const interval = setInterval(() => {
            width += Math.random() * 15;
            if (width > 100) width = 100;
            progress.style.width = `${width}%`;
        }, 100);
        
        // Initialize system
        try {
            await fetch(`${API_BASE}/api/init`);
            await new Promise(r => setTimeout(r, 800));
        } catch (e) {
            console.log('Init endpoint not available, continuing...');
        }
        
        clearInterval(interval);
        progress.style.width = '100%';
        
        setTimeout(() => {
            $('#welcome-screen').classList.remove('active');
            $('#dashboard').classList.add('active');
            refreshAllData();
        }, 300);
    });
}

// ─── Navigation ────────────────────────────────────────────────
function initNavigation() {
    $$('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const view = tab.dataset.view;
            
            // Update tabs
            $$('.nav-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update views
            $$('.view').forEach(v => v.classList.remove('active'));
            $(`#view-${view}`).classList.add('active');
            
            // Refresh data for specific views
            if (view === 'homes') renderHomes();
            if (view === 'devices') renderDevices();
            if (view === 'training') refreshTrainingView();
            if (view === 'analytics') refreshAnalytics();
        });
    });
}

// ─── Modal System ──────────────────────────────────────────────
function initModals() {
    const overlay = $('#modal-overlay');
    
    // Close modal handlers
    $$('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', closeModal);
    });
    
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });
    
    // Room suggestions
    $$('.suggestion').forEach(sug => {
        sug.addEventListener('click', () => {
            $('#new-room-name').value = sug.dataset.name;
        });
    });
}

function openModal(modalId, context = {}) {
    state.currentModal = modalId;
    state.modalContext = context;
    
    $('#modal-overlay').classList.add('active');
    $$('.modal').forEach(m => m.classList.remove('active'));
    $(`#modal-${modalId}`).classList.add('active');
}

function closeModal() {
    $('#modal-overlay').classList.remove('active');
    $$('.modal').forEach(m => m.classList.remove('active'));
    state.currentModal = null;
    state.modalContext = {};
}

// ─── Event Listeners ───────────────────────────────────────────
function initEventListeners() {
    // Add Home
    $('#add-home-btn').addEventListener('click', () => openModal('add-home'));
    $('#confirm-add-home').addEventListener('click', handleAddHome);
    
    // Add Device
    $('#add-device-btn').addEventListener('click', () => openModal('add-device'));
    $('#confirm-add-device').addEventListener('click', handleAddDevice);
    
    // Add Room
    $('#confirm-add-room').addEventListener('click', handleAddRoom);
    
    // Assign Device
    $('#confirm-assign-device').addEventListener('click', handleAssignDevice);
    
    // Device Filters
    $$('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            $$('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderDevices(btn.dataset.filter);
        });
    });
    
    // Episode Selector
    $$('.episode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            $$('.episode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.selectedEpisodes = parseInt(btn.dataset.value);
        });
    });
    
    // Training
    $('#start-training').addEventListener('click', handleStartTraining);
    
    // Optimizer
    $('#activate-optimizer').addEventListener('click', handleActivateOptimizer);
    
    // Simulate Day
    $('#simulate-day').addEventListener('click', handleSimulateDay);
    
    // Active Home Select
    $('#active-home-select').addEventListener('change', (e) => {
        state.activeHome = e.target.value;
        updateHomeQuickStats();
        updateComfortDisplay();
    });
    
    // Time Filter
    $$('.time-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            $$('.time-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            refreshAnalytics(btn.dataset.period);
        });
    });
}

// ─── API Calls ─────────────────────────────────────────────────
async function fetchInitialData() {
    try {
        const [homesRes, devicesRes] = await Promise.all([
            fetch(`${API_BASE}/api/homes`),
            fetch(`${API_BASE}/api/devices`)
        ]);
        
        state.homes = await homesRes.json();
        state.devices = await devicesRes.json();
        
        // Set initial counts on welcome screen
        $('#init-homes').textContent = Object.keys(state.homes).length;
        $('#init-devices').textContent = Object.keys(state.devices).length;
        
        // Fetch weather
        fetchWeather();
    } catch (error) {
        console.error('Error fetching initial data:', error);
        showToast('Failed to connect to server', 'error');
    }
}

async function fetchWeather() {
    try {
        const res = await fetch(`${API_BASE}/api/weather`);
        const data = await res.json();
        
        const badge = $('#weather-badge');
        badge.querySelector('.weather-temp').textContent = `${Math.round(data.temperature)}°C`;
        badge.querySelector('.weather-city').textContent = data.city;
        
        // Update current temp display
        $('#current-temp').textContent = Math.round(data.temperature);
    } catch (error) {
        console.log('Weather fetch failed:', error);
    }
}

async function refreshAllData() {
    try {
        const [homesRes, devicesRes] = await Promise.all([
            fetch(`${API_BASE}/api/homes`),
            fetch(`${API_BASE}/api/devices`)
        ]);
        
        state.homes = await homesRes.json();
        state.devices = await devicesRes.json();
        
        updateOverviewStats();
        populateHomeSelects();
        renderHomes();
        renderDevices();
        drawNeuralNetwork();
        checkTrainedModels();
        
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

// ─── Overview Functions ────────────────────────────────────────
function updateOverviewStats() {
    const homeCount = Object.keys(state.homes).length;
    const deviceCount = Object.keys(state.devices).length;
    
    let roomCount = 0;
    Object.values(state.homes).forEach(home => {
        roomCount += Object.keys(home.rooms || {}).length;
    });
    
    $('#stat-homes').textContent = homeCount;
    $('#stat-devices').textContent = deviceCount;
    $('#stat-trained').textContent = homeCount; // Assume each home can have a model
    
    // Animate energy value
    animateValue('#today-energy', 0, Math.random() * 50 + 30, 1500, 2);
}

function populateHomeSelects() {
    const homeNames = Object.keys(state.homes);
    
    // Active home select
    const activeSelect = $('#active-home-select');
    activeSelect.innerHTML = homeNames.map(name => 
        `<option value="${name}">${name}</option>`
    ).join('');
    
    // Training home select
    const trainingSelect = $('#training-home');
    trainingSelect.innerHTML = homeNames.map(name => 
        `<option value="${name}">${name}</option>`
    ).join('');
    
    if (homeNames.length > 0 && !state.activeHome) {
        state.activeHome = homeNames[0];
    }
    
    updateHomeQuickStats();
    updateComfortDisplay();
}

function updateHomeQuickStats() {
    if (!state.activeHome || !state.homes[state.activeHome]) return;
    
    const home = state.homes[state.activeHome];
    const rooms = Object.keys(home.rooms || {});
    let deviceCount = 0;
    
    rooms.forEach(room => {
        deviceCount += (home.rooms[room].devices || []).length;
    });
    
    $('#qs-rooms').textContent = rooms.length;
    $('#qs-devices').textContent = deviceCount;
}

function updateComfortDisplay() {
    if (!state.activeHome || !state.homes[state.activeHome]) return;
    
    const home = state.homes[state.activeHome];
    const [min, max] = home.comfort_range || [21, 25];
    
    $('#comfort-range').textContent = `${min}°C - ${max}°C`;
}

// ─── Home Management ───────────────────────────────────────────
function renderHomes() {
    const grid = $('#homes-grid');
    const homes = state.homes;
    
    if (Object.keys(homes).length === 0) {
        grid.innerHTML = `
            <div class="card" style="grid-column: span 2; text-align: center; padding: 60px;">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" 
                     style="width: 64px; height: 64px; margin: 0 auto 20px; opacity: 0.3;">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                </svg>
                <h3 style="margin-bottom: 10px; opacity: 0.7;">No Homes Yet</h3>
                <p style="color: var(--text-tertiary); margin-bottom: 20px;">
                    Create your first smart home to get started
                </p>
                <button class="add-btn" onclick="openModal('add-home')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"/>
                        <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Add Your First Home
                </button>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = Object.entries(homes).map(([name, data]) => {
        const rooms = Object.entries(data.rooms || {});
        const [min, max] = data.comfort_range || [21, 25];
        
        return `
            <div class="card home-card" data-home="${name}">
                <div class="home-card-header">
                    <div>
                        <h3 class="home-name">${name}</h3>
                        <span class="home-comfort">Comfort: ${min}°C - ${max}°C</span>
                    </div>
                    <div class="home-actions">
                        <button class="icon-btn" onclick="openAddRoomModal('${name}')" title="Add Room">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"/>
                                <line x1="5" y1="12" x2="19" y2="12"/>
                            </svg>
                        </button>
                        <button class="icon-btn danger" onclick="handleDeleteHome('${name}')" title="Delete Home">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="rooms-section">
                    <div class="rooms-header">
                        <span class="rooms-title">Rooms (${rooms.length})</span>
                    </div>
                    ${rooms.length > 0 ? `
                        <div class="rooms-list">
                            ${rooms.map(([roomName, roomData]) => {
                                const devices = roomData.devices || [];
                                const icon = ROOM_ICONS[roomName] || ROOM_ICONS.default;
                                return `
                                    <div class="room-item" data-room="${roomName}">
                                        <div class="room-info">
                                            <div class="room-icon">${icon}</div>
                                            <div>
                                                <div class="room-name">${roomName}</div>
                                                <div class="room-devices-count">${devices.length} device${devices.length !== 1 ? 's' : ''}</div>
                                            </div>
                                        </div>
                                        <div class="room-actions">
                                            <button class="icon-btn" onclick="openAssignDeviceModal('${name}', '${roomName}')" title="Add Device">
                                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                    <line x1="12" y1="5" x2="12" y2="19"/>
                                                    <line x1="5" y1="12" x2="19" y2="12"/>
                                                </svg>
                                            </button>
                                            <button class="icon-btn danger" onclick="handleDeleteRoom('${name}', '${roomName}')" title="Delete Room">
                                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                    <line x1="18" y1="6" x2="6" y2="18"/>
                                                    <line x1="6" y1="6" x2="18" y2="18"/>
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    ` : `
                        <div class="empty-rooms">
                            <p>No rooms yet. Add your first room!</p>
                        </div>
                    `}
                </div>
            </div>
        `;
    }).join('');
}

async function handleAddHome() {
    const name = $('#new-home-name').value.trim();
    const min = parseInt($('#comfort-min').value) || 21;
    const max = parseInt($('#comfort-max').value) || 25;
    
    if (!name) {
        showToast('Please enter a home name', 'warning');
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/api/homes/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                home_name: name,
                comfort_range: [min, max]
            })
        });
        
        const data = await res.json();
        
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(`Home "${name}" created!`, 'success');
            closeModal();
            $('#new-home-name').value = '';
            await refreshAllData();
            addActivity(`Created new home: ${name}`);
        }
    } catch (error) {
        showToast('Failed to create home', 'error');
    }
}

async function handleDeleteHome(name) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;
    
    try {
        const res = await fetch(`${API_BASE}/api/homes/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ home_name: name })
        });
        
        const data = await res.json();
        
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(`Home "${name}" deleted`, 'success');
            await refreshAllData();
            addActivity(`Deleted home: ${name}`);
        }
    } catch (error) {
        showToast('Failed to delete home', 'error');
    }
}

function openAddRoomModal(homeName) {
    $('#room-modal-home').textContent = homeName;
    openModal('add-room', { homeName });
}

async function handleAddRoom() {
    const roomName = $('#new-room-name').value.trim();
    const homeName = state.modalContext.homeName;
    
    if (!roomName) {
        showToast('Please enter a room name', 'warning');
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/api/rooms/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                home_name: homeName,
                room_name: roomName
            })
        });
        
        const data = await res.json();
        
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(`Room "${roomName}" added to ${homeName}`, 'success');
            closeModal();
            $('#new-room-name').value = '';
            await refreshAllData();
            addActivity(`Added room "${roomName}" to ${homeName}`);
        }
    } catch (error) {
        showToast('Failed to add room', 'error');
    }
}

async function handleDeleteRoom(homeName, roomName) {
    if (!confirm(`Delete room "${roomName}" from ${homeName}?`)) return;
    
    try {
        const res = await fetch(`${API_BASE}/api/rooms/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                home_name: homeName,
                room_name: roomName
            })
        });
        
        const data = await res.json();
        
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(`Room "${roomName}" deleted`, 'success');
            await refreshAllData();
            addActivity(`Deleted room "${roomName}" from ${homeName}`);
        }
    } catch (error) {
        showToast('Failed to delete room', 'error');
    }
}

// ─── Device Management ─────────────────────────────────────────
function renderDevices(filter = 'all') {
    const grid = $('#devices-grid');
    const devices = state.devices;
    
    let filteredDevices = Object.entries(devices);
    
    if (filter === 'high') {
        filteredDevices = filteredDevices.filter(([_, d]) => d.base_kWh > 2);
    } else if (filter === 'medium') {
        filteredDevices = filteredDevices.filter(([_, d]) => d.base_kWh >= 1 && d.base_kWh <= 2);
    } else if (filter === 'low') {
        filteredDevices = filteredDevices.filter(([_, d]) => d.base_kWh < 1);
    }
    
    if (filteredDevices.length === 0) {
        grid.innerHTML = `
            <div class="card" style="grid-column: span 2; text-align: center; padding: 40px;">
                <p style="color: var(--text-tertiary);">No devices found for this filter</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = filteredDevices.map(([name, data]) => {
        const icon = DEVICE_ICONS[name] || DEVICE_ICONS.default;
        const kwh = data.base_kWh;
        const kwhClass = kwh > 2 ? 'high' : kwh >= 1 ? 'medium' : 'low';
        const permissions = data.permissions || [];
        
        return `
            <div class="card device-card" data-device="${name}">
                <div class="device-header">
                    <div class="device-icon">${icon}</div>
                </div>
                <div class="device-name">${name}</div>
                <div class="device-kwh ${kwhClass}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;">
                        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                    </svg>
                    ${kwh.toFixed(2)} kWh
                </div>
                <div class="device-permissions">
                    ${permissions.slice(0, 4).map(p => 
                        `<span class="permission-tag">${p.replace('_', ' ')}</span>`
                    ).join('')}
                    ${permissions.length > 4 ? `<span class="permission-tag">+${permissions.length - 4}</span>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

async function handleAddDevice() {
    const name = $('#new-device-name').value.trim();
    const kwh = parseFloat($('#new-device-kwh').value) || 1.0;
    const permissions = Array.from($$('#permissions-grid input:checked')).map(cb => cb.value);
    
    if (!name) {
        showToast('Please enter a device name', 'warning');
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/api/devices/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                base_kWh: kwh,
                permissions: permissions
            })
        });
        
        const data = await res.json();
        
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(`Device "${name}" added!`, 'success');
            closeModal();
            $('#new-device-name').value = '';
            $('#new-device-kwh').value = '';
            await refreshAllData();
            addActivity(`Added new device: ${name}`);
        }
    } catch (error) {
        showToast('Failed to add device', 'error');
    }
}

function openAssignDeviceModal(homeName, roomName) {
    $('#assign-modal-room').textContent = roomName;
    
    const grid = $('#device-select-grid');
    grid.innerHTML = Object.entries(state.devices).map(([name, data]) => {
        const icon = DEVICE_ICONS[name] || DEVICE_ICONS.default;
        return `
            <div class="device-select-item" data-device="${name}">
                <div class="device-select-icon">${icon}</div>
                <div>
                    <div class="device-select-name">${name}</div>
                    <div class="device-select-kwh">${data.base_kWh.toFixed(2)} kWh</div>
                </div>
            </div>
        `;
    }).join('');
    
    // Add click handlers
    $$('.device-select-item').forEach(item => {
        item.addEventListener('click', () => {
            item.classList.toggle('selected');
        });
    });
    
    openModal('assign-device', { homeName, roomName });
}

async function handleAssignDevice() {
    const selected = $$('.device-select-item.selected');
    const { homeName, roomName } = state.modalContext;
    
    if (selected.length === 0) {
        showToast('Please select at least one device', 'warning');
        return;
    }
    
    let successCount = 0;
    
    for (const item of selected) {
        const deviceName = item.dataset.device;
        
        try {
            const res = await fetch(`${API_BASE}/api/rooms/assign_device`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    home_name: homeName,
                    room_name: roomName,
                    device_name: deviceName
                })
            });
            
            const data = await res.json();
            if (!data.error) successCount++;
        } catch (error) {
            console.error(`Failed to assign ${deviceName}:`, error);
        }
    }
    
    if (successCount > 0) {
        showToast(`${successCount} device(s) assigned to ${roomName}`, 'success');
        closeModal();
        await refreshAllData();
        addActivity(`Assigned ${successCount} device(s) to ${roomName}`);
    } else {
        showToast('Failed to assign devices', 'error');
    }
}

// ─── Training Functions ────────────────────────────────────────
function refreshTrainingView() {
    populateHomeSelects();
    drawNeuralNetwork();
    checkTrainedModels();
    fetchKPIData();
}

function drawNeuralNetwork() {
    const connections = $('#nn-connections');
    if (!connections) return;
    
    // Clear existing
    connections.innerHTML = '';
    
    // Define layer positions
    const layers = [
        { x: 50, ys: [30, 70, 110, 150, 190] },
        { x: 150, ys: [40, 80, 120, 160] },
        { x: 250, ys: [40, 80, 120, 160] },
        { x: 350, ys: [70, 110, 150] }
    ];
    
    // Draw connections
    for (let i = 0; i < layers.length - 1; i++) {
        const from = layers[i];
        const to = layers[i + 1];
        
        from.ys.forEach(y1 => {
            to.ys.forEach(y2 => {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', from.x);
                line.setAttribute('y1', y1);
                line.setAttribute('x2', to.x);
                line.setAttribute('y2', y2);
                line.setAttribute('stroke', 'rgba(255,255,255,0.1)');
                line.setAttribute('stroke-width', '1');
                connections.appendChild(line);
            });
        });
    }
}

async function handleStartTraining() {
    const home = $('#training-home').value;
    const episodes = state.selectedEpisodes;
    
    if (!home) {
        showToast('Please select a home', 'warning');
        return;
    }
    
    state.trainingInProgress = true;
    $('#start-training').disabled = true;
    $('#start-training').innerHTML = `
        <svg class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
        </svg>
        Training...
    `;
    
    // Add spinning animation
    const style = document.createElement('style');
    style.innerHTML = `
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    `;
    document.head.appendChild(style);
    
    // Animate neural network
    animateNeuralNetwork();
    
    try {
        showToast(`Training started for ${home} (${episodes} episodes)`, 'info');
        addActivity(`Started training for ${home} with ${episodes} episodes`);
        
        const res = await fetch(`${API_BASE}/api/train`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                home: home,
                episodes: episodes
            })
        });
        
        const data = await res.json();
        
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(`Training complete for ${home}!`, 'success');
            addActivity(`Completed training for ${home}`);
            checkTrainedModels();
            fetchKPIData();
        }
    } catch (error) {
        showToast('Training failed', 'error');
    } finally {
        state.trainingInProgress = false;
        $('#start-training').disabled = false;
        $('#start-training').innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            Start Training
        `;
    }
}

function animateNeuralNetwork() {
    const neurons = $$('.neural-svg .neuron');
    let index = 0;
    
    const interval = setInterval(() => {
        if (!state.trainingInProgress) {
            clearInterval(interval);
            neurons.forEach(n => n.classList.remove('active'));
            return;
        }
        
        neurons.forEach(n => n.classList.remove('active'));
        
        // Light up random neurons
        const count = Math.floor(Math.random() * 5) + 3;
        for (let i = 0; i < count; i++) {
            const randomNeuron = neurons[Math.floor(Math.random() * neurons.length)];
            randomNeuron.classList.add('active');
        }
        
        index++;
    }, 200);
}

async function checkTrainedModels() {
    const modelsList = $('#models-list');
    const homes = Object.keys(state.homes);
    
    // Simulate model checking (in real app, would check file system via API)
    const models = homes.map(home => ({
        name: home,
        file: `${home.toLowerCase().replace(' ', '_')}_final.pth`,
        episodes: 30,
        trained: true
    }));
    
    if (models.length === 0) {
        modelsList.innerHTML = `
            <div class="model-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <p>No models trained yet</p>
            </div>
        `;
        return;
    }
    
    modelsList.innerHTML = models.map(model => `
        <div class="model-item">
            <div class="model-info">
                <div class="model-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2a10 10 0 1 0 10 10"/>
                        <polyline points="12 6 12 12 16 14"/>
                    </svg>
                </div>
                <div>
                    <div class="model-name">${model.name}</div>
                    <div class="model-meta">${model.file}</div>
                </div>
            </div>
            <button class="icon-btn" onclick="runSimulation('${model.name}')" title="Run Simulation">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
            </button>
        </div>
    `).join('');
}

async function fetchKPIData() {
    try {
        const res = await fetch(`${API_BASE}/api/kpis/full`);
        const data = await res.json();
        
        if (!data.error && Array.isArray(data)) {
            state.kpiData = data;
            updateKPIMetrics(data);
            drawKPIChart(data);
        }
    } catch (error) {
        console.log('KPI fetch failed:', error);
    }
}

function updateKPIMetrics(data) {
    if (data.length === 0) return;
    
    const lastEntry = data[data.length - 1];
    const rewards = data.map(d => d.reward);
    const avgReward = rewards.reduce((a, b) => a + b, 0) / rewards.length;
    
    // Update metric rings
    const progress = (data.length / 30) * 100;
    $('#episode-ring').style.strokeDashoffset = 251 - (251 * progress / 100);
    $('#episode-count').textContent = data.length;
    
    const rewardNorm = Math.min(100, Math.max(0, (avgReward + 500) / 10));
    $('#reward-ring').style.strokeDashoffset = 251 - (251 * rewardNorm / 100);
    $('#avg-reward').textContent = avgReward.toFixed(0);
    
    const epsilonPct = lastEntry.epsilon * 100;
    $('#epsilon-ring').style.strokeDashoffset = 251 - (251 * epsilonPct / 100);
    $('#epsilon-value').textContent = lastEntry.epsilon.toFixed(2);
}

function drawKPIChart(data) {
    const canvas = $('#reward-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (data.length < 2) return;
    
    const rewards = data.map(d => d.reward);
    const maxReward = Math.max(...rewards);
    const minReward = Math.min(...rewards);
    const range = maxReward - minReward || 1;
    
    const padding = 10;
    const width = canvas.width - padding * 2;
    const height = canvas.height - padding * 2;
    
    // Draw line
    ctx.beginPath();
    ctx.strokeStyle = '#FF6B35';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    rewards.forEach((reward, i) => {
        const x = padding + (i / (rewards.length - 1)) * width;
        const y = padding + height - ((reward - minReward) / range) * height;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // Draw gradient fill
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, 'rgba(255, 107, 53, 0.3)');
    gradient.addColorStop(1, 'rgba(255, 107, 53, 0)');
    
    ctx.lineTo(padding + width, padding + height);
    ctx.lineTo(padding, padding + height);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();
}

// ─── Optimizer & Simulation ────────────────────────────────────
async function handleActivateOptimizer() {
    const home = state.activeHome || 'Default';
    
    try {
        showToast(`Activating optimizer for ${home}...`, 'info');
        
        const res = await fetch(`${API_BASE}/api/activate_optimizer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                home: home,
                interval_sec: 3600
            })
        });
        
        const data = await res.json();
        
        if (data.status === 'already_running') {
            showToast(`Optimizer already running for ${home}`, 'warning');
        } else {
            showToast(`Optimizer activated for ${home}!`, 'success');
            addActivity(`Activated live optimizer for ${home}`);
        }
    } catch (error) {
        showToast('Failed to activate optimizer', 'error');
    }
}

async function handleSimulateDay() {
    const home = state.activeHome || 'Default';
    runSimulation(home);
}

async function runSimulation(home) {
    showToast(`Running 24-hour simulation for ${home}...`, 'info');
    
    try {
        const res = await fetch(`${API_BASE}/api/simulate/day`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ home: home })
        });
        
        const data = await res.json();
        
        if (!res.ok || data.error) {
            showToast(data.error || data.detail || 'Simulation failed', 'error');
            return;
        }
        
        // Show results in modal
        const results = $('#sim-results');
        results.innerHTML = `
            <div class="sim-stat">
                <div class="sim-stat-icon">🏆</div>
                <div class="sim-stat-value">${data.total_reward.toFixed(1)}</div>
                <div class="sim-stat-label">Total Reward</div>
            </div>
            <div class="sim-stat">
                <div class="sim-stat-icon">⚡</div>
                <div class="sim-stat-value">${data.total_energy_kWh.toFixed(2)}</div>
                <div class="sim-stat-label">Energy Used (kWh)</div>
            </div>
            <div class="sim-stat">
                <div class="sim-stat-icon">🌡️</div>
                <div class="sim-stat-value">${data.avg_temp.toFixed(1)}°C</div>
                <div class="sim-stat-label">Average Temperature</div>
            </div>
            <div class="sim-stat">
                <div class="sim-stat-icon">✅</div>
                <div class="sim-stat-value">${data.comfort_range[0]}-${data.comfort_range[1]}°C</div>
                <div class="sim-stat-label">Comfort Range</div>
            </div>
        `;
        
        openModal('simulation');
        addActivity(`Simulated 24h for ${home}: ${data.total_energy_kWh.toFixed(2)} kWh`);
        
    } catch (error) {
        console.error('Simulation error:', error);
        showToast('Simulation failed: ' + error.message, 'error');
    }
}

// ─── Analytics Functions ───────────────────────────────────────
function refreshAnalytics(period = 'day') {
    drawDonutChart();
    drawComparisonBars();
    drawRoomBars();
    updateSavings();
}

function drawDonutChart() {
    const chart = $('#donut-chart');
    const legend = $('#breakdown-legend');
    
    // Get device data for active home
    const home = state.homes[state.activeHome];
    if (!home) return;
    
    const deviceData = [];
    let totalKwh = 0;
    
    Object.values(home.rooms || {}).forEach(room => {
        (room.devices || []).forEach(deviceName => {
            const device = state.devices[deviceName];
            if (device) {
                const usage = device.base_kWh * (Math.random() * 2 + 1);
                deviceData.push({ name: deviceName, kwh: usage });
                totalKwh += usage;
            }
        });
    });
    
    if (deviceData.length === 0) {
        // Add sample data
        deviceData.push({ name: 'Air Conditioning', kwh: 8.5 });
        deviceData.push({ name: 'Heater', kwh: 5.2 });
        deviceData.push({ name: 'Lights', kwh: 2.1 });
        deviceData.push({ name: 'TV', kwh: 1.8 });
        totalKwh = 17.6;
    }
    
    $('#total-kwh').textContent = totalKwh.toFixed(1);
    
    // Draw donut segments
    let currentAngle = 0;
    const radius = 70;
    const cx = 100;
    const cy = 100;
    
    chart.innerHTML = deviceData.map((item, i) => {
        const percent = item.kwh / totalKwh;
        const angle = percent * 360;
        const color = CHART_COLORS[i % CHART_COLORS.length];
        
        // Calculate arc
        const startAngle = currentAngle * Math.PI / 180;
        const endAngle = (currentAngle + angle) * Math.PI / 180;
        
        const x1 = cx + radius * Math.cos(startAngle);
        const y1 = cy + radius * Math.sin(startAngle);
        const x2 = cx + radius * Math.cos(endAngle);
        const y2 = cy + radius * Math.sin(endAngle);
        
        const largeArc = angle > 180 ? 1 : 0;
        
        const circumference = 2 * Math.PI * radius;
        const dashLength = (angle / 360) * circumference;
        const dashOffset = (currentAngle / 360) * circumference;
        
        currentAngle += angle;
        
        return `
            <circle cx="${cx}" cy="${cy}" r="${radius}" 
                    fill="none" 
                    stroke="${color}" 
                    stroke-width="30"
                    stroke-dasharray="${dashLength} ${circumference}"
                    stroke-dashoffset="${-dashOffset}"
                    class="donut-segment"/>
        `;
    }).join('');
    
    // Draw legend
    legend.innerHTML = deviceData.map((item, i) => `
        <div class="legend-item">
            <div class="legend-color" style="background: ${CHART_COLORS[i % CHART_COLORS.length]}"></div>
            <span>${item.name} (${item.kwh.toFixed(1)} kWh)</span>
        </div>
    `).join('');
}

function drawComparisonBars() {
    const container = $('#comparison-bars');
    
    const data = [
        { label: 'Morning (6-12)', estimated: 4.5, real: 3.8 },
        { label: 'Afternoon (12-18)', estimated: 6.2, real: 5.9 },
        { label: 'Evening (18-24)', estimated: 8.1, real: 7.2 },
        { label: 'Night (0-6)', estimated: 2.4, real: 2.1 }
    ];
    
    const maxVal = Math.max(...data.flatMap(d => [d.estimated, d.real]));
    
    container.innerHTML = data.map(item => `
        <div class="comparison-row">
            <div class="comparison-label">${item.label}</div>
            <div class="comparison-bar-group">
                <div class="bar-container">
                    <div class="bar-fill estimated" style="width: ${(item.estimated / maxVal) * 100}%"></div>
                </div>
                <div class="bar-value">${item.estimated} kWh</div>
            </div>
            <div class="comparison-bar-group">
                <div class="bar-container">
                    <div class="bar-fill real" style="width: ${(item.real / maxVal) * 100}%"></div>
                </div>
                <div class="bar-value">${item.real} kWh</div>
            </div>
        </div>
    `).join('');
}

function drawRoomBars() {
    const container = $('#room-bars');
    const home = state.homes[state.activeHome];
    
    if (!home) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-tertiary);">No data available</p>';
        return;
    }
    
    const roomData = Object.entries(home.rooms || {}).map(([name, data]) => {
        let totalKwh = 0;
        (data.devices || []).forEach(deviceName => {
            const device = state.devices[deviceName];
            if (device) {
                totalKwh += device.base_kWh * (Math.random() + 0.5);
            }
        });
        return { name, kwh: totalKwh || Math.random() * 5 + 1 };
    });
    
    if (roomData.length === 0) {
        roomData.push({ name: 'Living Room', kwh: 5.2 });
        roomData.push({ name: 'Bedroom', kwh: 3.1 });
        roomData.push({ name: 'Kitchen', kwh: 6.8 });
    }
    
    const maxKwh = Math.max(...roomData.map(r => r.kwh));
    
    container.innerHTML = roomData.map(room => `
        <div class="room-bar-item">
            <div class="room-bar-label">${room.name}</div>
            <div class="room-bar-container">
                <div class="room-bar-fill" style="width: ${(room.kwh / maxKwh) * 100}%">
                    ${room.kwh.toFixed(1)} kWh
                </div>
            </div>
        </div>
    `).join('');
}

function updateSavings() {
    // Simulate savings data
    const energySaved = (Math.random() * 20 + 10).toFixed(1);
    const moneySaved = (energySaved * 0.12).toFixed(2);
    const co2Saved = (energySaved * 0.5).toFixed(1);
    const efficiency = Math.floor(Math.random() * 20 + 70);
    
    $('#energy-saved').textContent = `${energySaved} kWh`;
    $('#money-saved').textContent = `$${moneySaved}`;
    $('#co2-saved').textContent = `${co2Saved} kg`;
    $('#efficiency-fill').style.width = `${efficiency}%`;
    $('#efficiency-value').textContent = `${efficiency}%`;
}

// ─── Utility Functions ─────────────────────────────────────────
function showToast(message, type = 'info') {
    const container = $('#toast-container');
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function addActivity(text) {
    const list = $('#activity-list');
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const item = document.createElement('div');
    item.className = 'activity-item';
    item.innerHTML = `
        <div class="activity-dot"></div>
        <div class="activity-content">
            <span class="activity-text">${text}</span>
            <span class="activity-time">${time}</span>
        </div>
    `;
    
    list.insertBefore(item, list.firstChild);
    
    // Keep only last 10 items
    while (list.children.length > 10) {
        list.removeChild(list.lastChild);
    }
}

function animateValue(selector, start, end, duration, decimals = 0) {
    const element = $(selector);
    if (!element) return;
    
    const range = end - start;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + range * eased;
        
        element.textContent = current.toFixed(decimals);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// ─── Global Functions (for onclick handlers) ───────────────────
window.openModal = openModal;
window.openAddRoomModal = openAddRoomModal;
window.openAssignDeviceModal = openAssignDeviceModal;
window.handleDeleteHome = handleDeleteHome;
window.handleDeleteRoom = handleDeleteRoom;
window.runSimulation = runSimulation;
