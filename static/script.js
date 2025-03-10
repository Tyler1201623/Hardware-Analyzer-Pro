// Fetch hardware summary from the Flask backend
async function fetchHardwareSummary() {
    const output = document.getElementById("output");
    output.innerHTML = "<p>Loading hardware summary...</p>";

    try {
        const response = await fetch("/api/hardware_summary");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        displayData("Hardware Summary", data);
    } catch (error) {
        displayError("Error fetching hardware summary", error.message);
    }
}

// Fetch network summary from the Flask backend
async function fetchNetworkSummary() {
    const output = document.getElementById("output");
    output.innerHTML = "<p>Loading network summary...</p>";

    try {
        const response = await fetch("/api/network_summary");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        displayData("Network Summary", data);
    } catch (error) {
        displayError("Error fetching network summary", error.message);
    }
}

// Fetch device details (browser, OS, etc.)
function fetchDeviceDetails() {
    const output = document.getElementById("output");
    output.innerHTML = "<p>Fetching device details...</p>";

    const deviceDetails = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screenResolution: `${window.screen.width}x${window.screen.height}`,
        colorDepth: `${window.screen.colorDepth}-bit`,
        online: navigator.onLine ? "Online" : "Offline",
    };

    displayData("Device Details", deviceDetails);
}

// Display fetched data in a readable format
function displayData(title, data) {
    const output = document.getElementById("output");
    const formattedData = `
        <h2>${title}</h2>
        <div class="data-container">
            <pre>${syntaxHighlight(JSON.stringify(data, null, 4))}</pre>
        </div>
    `;
    output.innerHTML = formattedData;
}

// Display error messages
function displayError(title, message) {
    const output = document.getElementById("output");
    output.innerHTML = `
        <h2 class="error-title">${title}</h2>
        <p class="error-message">${message}</p>
    `;
}

// Utility function for syntax highlighting JSON data
function syntaxHighlight(json) {
    if (typeof json !== "string") {
        json = JSON.stringify(json, undefined, 4);
    }
    json = json.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(:)?|\b(true|false|null)\b|-?\d+(\.\d+)?([eE][+-]?\d+)?)/g, function (match) {
        let cls = "number";
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = "key";
            } else {
                cls = "string";
            }
        } else if (/true|false/.test(match)) {
            cls = "boolean";
        } else if (/null/.test(match)) {
            cls = "null";
        }
        return `<span class="${cls}">${match}</span>`;
    });
}

// Button click event handlers
document.getElementById("hardware-btn").addEventListener("click", fetchHardwareSummary);
document.getElementById("network-btn").addEventListener("click", fetchNetworkSummary);
document.getElementById("device-btn").addEventListener("click", fetchDeviceDetails);

// Show a user-friendly message if JavaScript is disabled
document.addEventListener("DOMContentLoaded", () => {
    const jsWarning = document.getElementById("js-warning");
    if (jsWarning) {
        jsWarning.style.display = "none";
    }
});

// Fetch hardware summary from the Flask backend
async function fetchHardwareSummary() {
    const output = document.getElementById("output");
    output.innerHTML = "<p>Loading hardware summary...</p>";

    try {
        const response = await fetch("/api/hardware_summary");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        displayData("Hardware Summary", data);
    } catch (error) {
        displayError("Error fetching hardware summary", error.message);
    }
}

// Fetch network summary from the Flask backend
async function fetchNetworkSummary() {
    const output = document.getElementById("output");
    output.innerHTML = "<p>Loading network summary...</p>";

    try {
        const response = await fetch("/api/network_summary");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        displayData("Network Summary", data);
    } catch (error) {
        displayError("Error fetching network summary", error.message);
    }
}

// Fetch device details (browser, OS, etc.)
function fetchDeviceDetails() {
    const output = document.getElementById("output");
    output.innerHTML = "<p>Fetching device details...</p>";

    const deviceDetails = {
        userAgent: navigator.userAgent, // User agent string
        platform: navigator.platform, // OS platform
        language: navigator.language, // Browser language
        screenResolution: `${window.screen.width}x${window.screen.height}`, // Screen resolution
        colorDepth: `${window.screen.colorDepth}-bit`, // Screen color depth
        online: navigator.onLine ? "Online" : "Offline", // Network status
        javaEnabled: navigator.javaEnabled(), // Java enabled in browser
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone, // User timezone
        cookiesEnabled: navigator.cookieEnabled, // Cookies enabled status
        touchSupport: getTouchSupport(), // Touchscreen support
        battery: {}, // Placeholder for battery details
    };

    // Fetch additional battery details if supported
    if (navigator.getBattery) {
        navigator.getBattery().then(battery => {
            deviceDetails.battery = {
                charging: battery.charging ? "Yes" : "No",
                level: `${Math.round(battery.level * 100)}%`,
                chargingTime: battery.chargingTime === Infinity ? "N/A" : `${battery.chargingTime} seconds`,
                dischargingTime: battery.dischargingTime === Infinity ? "N/A" : `${battery.dischargingTime} seconds`,
            };
            displayData("Device Details", deviceDetails);
        });
    } else {
        displayData("Device Details", deviceDetails);
    }
}

// Helper function to detect touchscreen support
function getTouchSupport() {
    const hasTouch =
        "ontouchstart" in window ||
        navigator.maxTouchPoints > 0 ||
        navigator.msMaxTouchPoints > 0;
    return hasTouch ? "Supported" : "Not Supported";
}

// Display fetched data in a readable format
function displayData(title, data) {
    const output = document.getElementById("output");
    const formattedData = `
        <h2>${title}</h2>
        <div class="data-container">
            <pre>${syntaxHighlight(JSON.stringify(data, null, 4))}</pre>
        </div>
    `;
    output.innerHTML = formattedData;
}

// Display error messages
function displayError(title, message) {
    const output = document.getElementById("output");
    output.innerHTML = `
        <h2 class="error-title">${title}</h2>
        <p class="error-message">${message}</p>
    `;
}

// Utility function for syntax highlighting JSON data
function syntaxHighlight(json) {
    if (typeof json !== "string") {
        json = JSON.stringify(json, undefined, 4);
    }
    json = json.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(:)?|\b(true|false|null)\b|-?\d+(\.\d+)?([eE][+-]?\d+)?)/g, function (match) {
        let cls = "number";
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = "key";
            } else {
                cls = "string";
            }
        } else if (/true|false/.test(match)) {
            cls = "boolean";
        } else if (/null/.test(match)) {
            cls = "null";
        }
        return `<span class="${cls}">${match}</span>`;
    });
}

// Button click event handlers
document.getElementById("hardware-btn").addEventListener("click", fetchHardwareSummary);
document.getElementById("network-btn").addEventListener("click", fetchNetworkSummary);
document.getElementById("device-btn").addEventListener("click", fetchDeviceDetails);

// Show a user-friendly message if JavaScript is disabled
document.addEventListener("DOMContentLoaded", () => {
    const jsWarning = document.getElementById("js-warning");
    if (jsWarning) {
        jsWarning.style.display = "none";
    }
});
