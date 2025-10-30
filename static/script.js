// System data
let systemData = {
    initialized: false,
    homes_count: 0,
    devices_count: 0,
    settings: {
        theme: 'light'
    }
};

// Helper function to count all devices across all homes
function countAllDevices(homes) {
    let count = 0;
    for (const homeName in homes) {
        const home = homes[homeName];
        for (const roomName in home.rooms) {
            count += home.rooms[roomName].devices.length;
        }
    }
    return count;
}

// Helper function to simulate API call
// Real API call function
function apiCall(endpoint) {
    console.log("Making API call to:", endpoint);
    return fetch(endpoint)
        .then(response => {
            console.log("API response received:", response);
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("API data:", data);
            return data;
        });
}

// Save system data to localStorage
function saveSystemData() {
    localStorage.setItem('energySystemData', JSON.stringify(systemData));
}

// Load system data from localStorage
function loadSystemData() {
    const savedData = localStorage.getItem('energySystemData');
    if (savedData) {
        systemData = JSON.parse(savedData);
        return true;
    }
    return false;
}

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if system data exists in localStorage
    const dataLoaded = loadSystemData();

    // Get references to elements - General
    const welcomeScreen = document.getElementById('welcome-screen');
    const welcomeButton = document.getElementById('welcome-button');
    const mainDashboard = document.getElementById('main-dashboard');
    const currentDateElement = document.getElementById('current-date');
    const systemStatusElement = document.getElementById('system-status');
    const initLoader = document.getElementById('init-loader');
    const initStatus = document.getElementById('init-status');

    // Get references to dashboard elements
    const kwhSavedElement = document.getElementById('kwh-saved');
    const moneySavedElement = document.getElementById('money-saved');
    const devicesCountElement = document.getElementById('devices-count');
    const homesCountElement = document.getElementById('homes-count');

    // Update system status based on loaded data
    if (dataLoaded && systemData.initialized) {
        systemStatusElement.textContent = "Ready";
        systemStatusElement.classList.add('active');
    }

    // Get references to elements - Manage Homes
    const manageHomesPage = document.getElementById('manage-homes-page');
    const manageHomesButton = document.getElementById('manage-homes');
    const backToDashboardButton = document.getElementById('back-to-dashboard');

    // Get references to elements - Manage Devices
    const manageDevicesPage = document.getElementById('manage-devices-page');
    const manageDevicesButton = document.getElementById('manage-devices');
    const backToDashboardFromDevicesButton = document.getElementById('back-to-dashboard-from-devices');

    // Get references to elements - Train
    const trainPage = document.getElementById('train-page');
    const trainButton = document.getElementById('train');
    const backToDashboardFromTrainButton = document.getElementById('back-to-dashboard-from-train');
    const trainHomeSelector = document.getElementById('train-home-selector');
    const startTrainButton = document.querySelector('.train-button');
    const simulateButton = document.querySelector('.simulate-button');

    // Add theme toggle button to body
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.innerHTML = '🌓';
    themeToggle.setAttribute('aria-label', 'Toggle dark mode');
    document.body.appendChild(themeToggle);

    // Check for saved theme preference
    if (systemData.settings && systemData.settings.theme === 'dark') {
        document.body.classList.add('dark-mode');
    }

    // Add click event for theme toggle
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        systemData.settings.theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
        saveSystemData();
    });

    // Set current date
    const today = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    if (currentDateElement) {
        currentDateElement.textContent = today.toLocaleDateString('en-US', options);
    }

    // Function to update dashboard with system data
    function updateDashboard() {
        console.log("Updating dashboard with data:", systemData);

        // Update homes and devices count if elements exist
        if (devicesCountElement) {
            console.log("Updating devices count to:", systemData.devices_count);
            devicesCountElement.textContent = systemData.devices_count;
        }

        if (homesCountElement) {
            console.log("Updating homes count to:", systemData.homes_count || Object.keys(systemData.homes).length);
            homesCountElement.textContent = systemData.homes_count || Object.keys(systemData.homes).length;
        }
    }

    // Add click event listener to the welcome button
    welcomeButton.addEventListener('click', async function() {
        // Show loader
        systemData.initialized = false;
        initLoader.style.display = 'block';
        welcomeButton.style.display = 'none';

        // Initialize system if not already initialized
        if (!systemData.initialized) {
            // First update
            initStatus.textContent = "Initializing system...";

            try {
                // Real API call
                const result = await apiCall('/api/init');

                // Update system status
                systemStatusElement.textContent = "Active";
                systemStatusElement.classList.add('active');

                // Update init status
                initStatus.textContent = "System initialized successfully!";

                // Update system data
                systemData.initialized = true;
                systemData.devices_count = result.devices_count;

                // If your API returns homes_count
                if (result.homes_count) {
                    systemData.homes_count = result.homes_count;
                } else {
                    // If it doesn't return homes_count, calculate from homes object
                    systemData.homes_count = Object.keys(result.homes).length;
                }

                // Save to localStorage
                saveSystemData();

                // Short delay before transitioning
                await new Promise(resolve => setTimeout(resolve, 1000));

            } catch (error) {
                console.error('Initialization error:', error);
                initStatus.textContent = "Error initializing system. Please try again.";
                welcomeButton.style.display = 'block';
                initLoader.style.display = 'none';
                return;
            }
        } else {
            // If already initialized, just show loading for a moment
            initStatus.textContent = "Loading system...";
            await new Promise(resolve => setTimeout(resolve, 1000));
            initStatus.textContent = "System loaded successfully!";
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        // Update dashboard with system data
        updateDashboard();

        // Hide welcome screen
        welcomeScreen.style.display = 'none';

        // Show main dashboard
        mainDashboard.style.display = 'block';

        // Animate the dashboard in
        animatePageIn(mainDashboard);
    });

    // ===== DASHBOARD OPTIMIZATION BUTTON =====

    // Get reference to the optimization button
    const startOptimizationButton = document.getElementById('start-optimization');
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');

    if (startOptimizationButton) {
        // Add click event listener to the Start Optimization button
        startOptimizationButton.addEventListener('click', function() {
            // Check if optimization is already running
            const isActive = this.classList.contains('active');

            if (isActive) {
                // Stop optimization
                this.textContent = 'Start Home Optimization';
                this.classList.remove('active');
                statusIndicator.classList.remove('active');
                statusText.textContent = 'Optimization Inactive';
            } else {
                // Start optimization
                this.textContent = 'Stop Home Optimization';
                this.classList.add('active');
                statusIndicator.classList.add('active');
                statusText.textContent = 'Optimization Active';

                // Simulate optimization starting by incrementing saved values
                let kwhSaved = parseInt(kwhSavedElement.textContent);
                let moneySaved = parseInt(moneySavedElement.textContent.replace('$', ''));

                // Set interval to update the values every 10 seconds to simulate ongoing optimization
                const optimizationInterval = setInterval(function() {
                    // Only update if optimization is still active
                    if (startOptimizationButton.classList.contains('active')) {
                        // Increase values
                        kwhSaved += Math.floor(Math.random() * 5) + 1;
                        moneySaved += Math.floor(Math.random() * 2) + 1;

                        // Update display
                        kwhSavedElement.textContent = kwhSaved;
                        moneySavedElement.textContent = '$' + moneySaved;
                    } else {
                        // Clear interval if optimization is stopped
                        clearInterval(optimizationInterval);
                    }
                }, 10000); // Update every 10 seconds
            }
        });
    }

    // ===== MANAGE HOMES PAGE NAVIGATION =====

    if (manageHomesButton) {
        // Add click event listener to the Manage Homes button
        manageHomesButton.addEventListener('click', function() {
            // Hide main dashboard
            mainDashboard.style.display = 'none';

            // Show manage homes page
            manageHomesPage.style.display = 'block';

            // Animate page in
            animatePageIn(manageHomesPage);
        });
    }

    if (backToDashboardButton) {
        // Add click event listener to the Back to Dashboard button
        backToDashboardButton.addEventListener('click', function() {
            // Hide manage homes page
            manageHomesPage.style.display = 'none';

            // Show main dashboard
            mainDashboard.style.display = 'block';

            // Animate page in
            animatePageIn(mainDashboard);
        });
    }

    // Add event listeners to all home option items
    const homeOptionItems = document.querySelectorAll('.home-management-options .option-item');
    homeOptionItems.forEach(function(item) {
        item.addEventListener('click', function() {
            // Here you would add specific functionality for each option
            // For now we'll just display an alert with the option name
            const optionName = this.querySelector('h3').textContent;
            alert('Selected home option: ' + optionName);
        });
    });

    // Add change event listener to home selector dropdown
    const homeSelector = document.getElementById('home-selector');
    if (homeSelector) {
        // Populate home selector with homes from system data
        for (const homeName in systemData.homes) {
            const option = document.createElement('option');
            option.value = homeName;
            option.textContent = homeName;
            homeSelector.appendChild(option);
        }

        homeSelector.addEventListener('change', function() {
            // Here you would load the selected home's data
            // For now we'll just display an alert with the selected home
            const selectedHome = this.options[this.selectedIndex].text;
            alert('Selected home: ' + selectedHome);
        });
    }

    // ===== MANAGE DEVICES PAGE NAVIGATION =====

    if (manageDevicesButton) {
        // Add click event listener to the Manage Devices button
        manageDevicesButton.addEventListener('click', function() {
            // Hide main dashboard
            mainDashboard.style.display = 'none';

            // Show manage devices page
            manageDevicesPage.style.display = 'block';

            // Animate page in
            animatePageIn(manageDevicesPage);
        });
    }

    if (backToDashboardFromDevicesButton) {
        // Add click event listener to the Back to Dashboard button (from Devices page)
        backToDashboardFromDevicesButton.addEventListener('click', function() {
            // Hide manage devices page
            manageDevicesPage.style.display = 'none';

            // Show main dashboard
            mainDashboard.style.display = 'block';

            // Animate page in
            animatePageIn(mainDashboard);
        });
    }

    // Add event listeners to all device option items
    const deviceOptionItems = document.querySelectorAll('.device-management-options .option-item');
    deviceOptionItems.forEach(function(item) {
        item.addEventListener('click', function() {
            // Here you would add specific functionality for each option
            // For now we'll just display an alert with the option name
            const optionName = this.querySelector('h3').textContent;
            alert('Selected device option: ' + optionName);
        });
    });

    // Add change event listener to device selector dropdown
    const deviceSelector = document.getElementById('device-selector');
    if (deviceSelector) {
        // Populate device selector
        // Get all devices from all homes
        const allDevices = [];
        for (const homeName in systemData.homes) {
            const home = systemData.homes[homeName];
            for (const roomName in home.rooms) {
                home.rooms[roomName].devices.forEach(device => {
                    if (!allDevices.includes(device)) {
                        allDevices.push(device);
                    }
                });
            }
        }

        // Add devices to selector
        allDevices.forEach(device => {
            const option = document.createElement('option');
            option.value = device;
            option.textContent = device;
            deviceSelector.appendChild(option);
        });

        deviceSelector.addEventListener('change', function() {
            // Here you would load the selected device's data
            // For now we'll just display an alert with the selected device
            const selectedDevice = this.options[this.selectedIndex].text;
            alert('Selected device: ' + selectedDevice);
        });
    }

    // ===== TRAIN PAGE NAVIGATION & FUNCTIONALITY =====

    if (trainButton) {
        // Add click event listener to the Train button
        trainButton.addEventListener('click', function() {
            // Hide main dashboard
            mainDashboard.style.display = 'none';

            // Show train page
            trainPage.style.display = 'block';

            // Animate page in
            animatePageIn(trainPage);
        });
    }

    if (backToDashboardFromTrainButton) {
        // Add click event listener to the Back to Dashboard button (from Train page)
        backToDashboardFromTrainButton.addEventListener('click', function() {
            // Hide train page
            trainPage.style.display = 'none';

            // Show main dashboard
            mainDashboard.style.display = 'block';

            // Animate page in
            animatePageIn(mainDashboard);
        });
    }

    // Add change event listener to the train home selector dropdown
    if (trainHomeSelector) {
        // Populate home selector with homes from system data
        for (const homeName in systemData.homes) {
            const option = document.createElement('option');
            option.value = homeName;
            option.textContent = homeName;
            trainHomeSelector.appendChild(option);
        }

        trainHomeSelector.addEventListener('change', function() {
            const selectedHome = this.options[this.selectedIndex].text;
            alert('Selected home for training: ' + selectedHome);

            // Here you would update the training statistics based on the selected home
            // For demo purposes, we'll update the progress bar randomly
            const randomProgress = Math.floor(Math.random() * 100);
            document.querySelector('.progress').style.width = randomProgress + '%';
            document.querySelector('.progress-text').textContent = randomProgress + '% Trained';

            // Update simulation results
            const randomSavings = Math.floor(Math.random() * 15) + 10;
            document.querySelector('.sim-value').textContent = randomSavings + '-' + (randomSavings + 7) + '%';
        });
    }

    if (startTrainButton) {
        // Add click event listener to the Start Training button
        startTrainButton.addEventListener('click', function() {
            const selectedHome = trainHomeSelector.options[trainHomeSelector.selectedIndex].text;

            // Simulate training process
            this.textContent = 'Training...';
            this.disabled = true;

            // Using setTimeout to simulate the training process
            setTimeout(function() {
                // Update progress bar
                document.querySelector('.progress').style.width = '100%';
                document.querySelector('.progress-text').textContent = '100% Trained';

                // Re-enable button
                startTrainButton.textContent = 'Start Training';
                startTrainButton.disabled = false;

                alert('Training completed for ' + selectedHome + '!');
            }, 3000);
        });
    }

    if (simulateButton) {
        // Add click event listener to the Run Simulation button
        simulateButton.addEventListener('click', function() {
            const selectedHome = trainHomeSelector.options[trainHomeSelector.selectedIndex].text;

            // Simulate simulation process
            this.textContent = 'Simulating...';
            this.disabled = true;

            // Using setTimeout to simulate the simulation process
            setTimeout(function() {
                // Update simulation results with random values
                const randomSavings = Math.floor(Math.random() * 15) + 10;
                document.querySelector('.sim-value').textContent = randomSavings + '-' + (randomSavings + 7) + '%';

                // Re-enable button
                simulateButton.textContent = 'Run Simulation';
                simulateButton.disabled = false;

                alert('Simulation completed for ' + selectedHome + '!');
            }, 2000);
        });
    }

    // Page Transitions
    function animatePageIn(page) {
        page.style.opacity = '0';
        page.style.transform = 'translateY(20px)';
        setTimeout(function() {
            page.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            page.style.opacity = '1';
            page.style.transform = 'translateY(0)';
        }, 50);
    }
});