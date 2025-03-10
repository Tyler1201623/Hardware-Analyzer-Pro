class HardwareAnalyzer {
      constructor() {
          this.lastRefresh = new Date();
          this.monitoringEnabled = false;
          this.API_BASE_URL = window.location.hostname === 'localhost' 
              ? 'http://localhost:5000' 
              : 'https://your-production-url.com';
          this.initializeUI();
      }

      initializeUI() {
          this.bindEvents();
          this.setupAutoRefresh();
          this.refreshAll(); // Initial data load
      }

      async fetchHardwareData() {
          try {
              const response = await fetch(`${this.API_BASE_URL}/api/hardware_summary`, {
                  method: 'GET',
                  headers: {
                      'Accept': 'application/json',
                      'Content-Type': 'application/json'
                  },
                  mode: 'cors'
              });
            
              if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
              }
              return await response.json();
          } catch (error) {
              console.error('Fetch error:', error);
              throw new Error('Unable to connect to hardware monitoring service');
          }
      }
  }      bindEvents() {
          const refreshBtn = document.getElementById('refresh-btn');
          if (refreshBtn) {
              refreshBtn.addEventListener('click', () => this.refreshAll());
          }

          const exportBtn = document.getElementById('export-btn');
          if (exportBtn) {
              exportBtn.addEventListener('click', () => this.exportData('json'));
          }
      }

      async refreshAll() {
          try {
              const hardwareData = await this.fetchHardwareData();
              this.updateHardwareDisplay(hardwareData);
              this.updateLastRefreshTime();
          } catch (error) {
              this.showError('Refresh Error', error.message);
          }
      }

      async fetchHardwareData() {
          const response = await fetch(`${this.API_BASE_URL}/api/hardware_summary`);
          if (!response.ok) throw new Error('Failed to fetch hardware data');
          return await response.json();
      }

      updateHardwareDisplay(data) {
          this.updateSystemInfo(data.system_info);
          this.updateCPUInfo(data.cpu);
          this.updateMemoryInfo(data.ram);
          this.updateStorageInfo(data.storage);
          this.updateGPUInfo(data.gpu);
      }

      updateSystemInfo(systemInfo) {
          const container = document.querySelector('#system-details');
          if (container) {
              container.innerHTML = this.formatSystemInfo(systemInfo);
          }
      }

      formatSystemInfo(info) {
          return Object.entries(info)
              .map(([key, value]) => `
                  <div class="info-item">
                      <span class="info-label">${key.replace('_', ' ').toUpperCase()}</span>
                      <span class="info-value">${value}</span>
                  </div>
              `).join('');
      }

      updateLastRefreshTime() {
          const lastUpdateElement = document.getElementById('last-update');
          if (lastUpdateElement) {
              this.lastRefresh = new Date();
              lastUpdateElement.textContent = `Last Updated: ${this.lastRefresh.toLocaleString()}`;
          }
      }

      showError(title, message) {
          console.error(`${title}: ${message}`);
          // Add visual error display if needed
      }

      setupAutoRefresh() {
          const interval = 5000; // 5 seconds
          setInterval(() => this.refreshAll(), interval);
      }

      updateCPUInfo(cpuInfo) {
          const container = document.querySelector('#cpu-details');
          container.innerHTML = `
              <div class="info-item">
                  <span class="info-label">Model</span>
                  <span class="info-value">${cpuInfo.name}</span>
              </div>
              <div class="info-item">
                  <span class="info-label">Cores/Threads</span>
                  <span class="info-value">${cpuInfo.cores}/${cpuInfo.threads}</span>
              </div>
              <div class="info-item">
                  <span class="info-label">Usage</span>
                  <span class="info-value">${cpuInfo.current_usage}</span>
              </div>
          `;
      
          // Update CPU usage bar
          const usageBar = document.querySelector('#cpu-usage-bar');
          if (usageBar) {
              const usage = parseFloat(cpuInfo.current_usage);
              usageBar.style.width = `${usage}%`;
              usageBar.style.backgroundColor = this.getUsageColor(usage);
          }
      }

      updateMemoryInfo(ramInfo) {
          const container = document.querySelector('#memory-details');
          container.innerHTML = `
              <div class="info-item">
                  <span class="info-label">Total</span>
                  <span class="info-value">${ramInfo.total}</span>
              </div>
              <div class="info-item">
                  <span class="info-label">Used</span>
                  <span class="info-value">${ramInfo.used}</span>
              </div>
              <div class="info-item">
                  <span class="info-label">Available</span>
                  <span class="info-value">${ramInfo.available}</span>
              </div>
          `;
      
          // Update RAM usage bar
          const usageBar = document.querySelector('#memory-usage-bar');
          if (usageBar) {
              const usage = parseFloat(ramInfo.percent_used);
              usageBar.style.width = `${usage}%`;
              usageBar.style.backgroundColor = this.getUsageColor(usage);
          }
      }

      updateStorageInfo(storageInfo) {
          const container = document.querySelector('#storage-details');
          container.innerHTML = storageInfo.drives.map(drive => `
              <div class="storage-drive">
                  <div class="drive-header">${drive.device} (${drive.type})</div>
                  <div class="drive-bar">
                      <div class="drive-usage" style="width: ${drive.percent_used}; background-color: ${this.getUsageColor(parseFloat(drive.percent_used))}"></div>
                  </div>
                  <div class="drive-details">
                      <span>Total: ${drive.total}</span>
                      <span>Used: ${drive.used}</span>
                      <span>Free: ${drive.free}</span>
                  </div>
              </div>
          `).join('');
      }

      updateGPUInfo(gpuInfo) {
          const container = document.querySelector('#gpu-details');
          container.innerHTML = gpuInfo.gpus.map(gpu => `
              <div class="info-item">
                  <span class="info-label">Model</span>
                  <span class="info-value">${gpu.name}</span>
              </div>
              <div class="info-item">
                  <span class="info-label">Memory</span>
                  <span class="info-value">${gpu.memory_total}</span>
              </div>
          `).join('');
      }

      getUsageColor(percentage) {
          if (percentage < 60) return '#28a745';
          if (percentage < 80) return '#ffc107';
          return '#dc3545';
      }

      exportData(format) {
          const endpoints = {
              json: '/api/export/json',
              csv: '/api/export/csv',
              pdf: '/api/export/pdf'
          };

          fetch(endpoints[format])
              .then(response => response.blob())
              .then(blob => {
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `hardware-report.${format}`;
                  a.click();
              })
              .catch(error => this.showError('Export Error', error.message));
      }
  }

  // Initialize when DOM is ready
  document.addEventListener('DOMContentLoaded', () => {
      window.hardwareAnalyzer = new HardwareAnalyzer();
  });

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching logic
    const tabs = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tab.id.replace('-btn', '')).classList.add('active');
        });
    });

    // Refresh functionality
    const refreshBtn = document.getElementById('refresh-btn');
    refreshBtn.addEventListener('click', async () => {
        await refreshAll();
    });

    // Auto-refresh setup
    let autoRefreshInterval = null;
    const toggleAutoRefresh = (enable) => {
        if (enable && !autoRefreshInterval) {
            autoRefreshInterval = setInterval(refreshAll, 5000);
        } else if (!enable && autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
    };

    // Refresh functions
    async function refreshAll() {
        try {
            await Promise.all([
                refreshHardware(),
                refreshNetwork(),
                refreshMonitoring()
            ]);
            updateLastRefreshTime();
        } catch (error) {
            showError('Refresh failed: ' + error.message);
        }
    }

    async function refreshHardware() {
        try {
            const response = await fetch('/api/hardware');
            const data = await response.json();
            updateHardwareInfo(data);
        } catch (error) {
            showError('Hardware refresh failed');
            throw error;
        }
    }

    async function refreshNetwork() {
        try {
            const response = await fetch('/api/network');
            if (!response.ok) throw new Error('Network response failed');
            
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            
            updateNetworkInfo(data);
        } catch (error) {
            console.error('Network refresh failed:', error);
            showError('Network refresh failed: ' + error.message);
            // Keep the UI responsive by updating the network section with error state
            document.getElementById('network-details').innerHTML = 
                `<div class="error-state">Network information temporarily unavailable</div>`;
        }
    }

    async function refreshMonitoring() {
        try {
            const response = await fetch('/api/monitoring');
            const data = await response.json();
            updateMonitoringGraphs(data);
        } catch (error) {
            showError('Monitoring refresh failed');
            throw error;
        }
    }

    // Update UI functions
    function updateHardwareInfo(data) {
        const systemDetails = document.getElementById('system-details');
        const cpuDetails = document.getElementById('cpu-details');
        const memoryDetails = document.getElementById('memory-details');
        const storageDetails = document.getElementById('storage-details');
        const gpuDetails = document.getElementById('gpu-details');

        // Update system info
        systemDetails.innerHTML = formatSystemInfo(data.system_info);
        
        // Update CPU info
        cpuDetails.innerHTML = formatCPUInfo(data.cpu);
        document.getElementById('cpu-usage-bar').style.width = data.cpu.current_usage;
        
        // Update memory info
        memoryDetails.innerHTML = formatMemoryInfo(data.ram);
        document.getElementById('memory-usage-bar').style.width = data.ram.percent_used;
        
        // Update storage info
        storageDetails.innerHTML = formatStorageInfo(data.storage);
        
        // Update GPU info
        gpuDetails.innerHTML = formatGPUInfo(data.gpu);
    }

    function updateNetworkInfo(data) {
        const networkDetails = document.getElementById('network-details');
        let html = '<div class="network-grid">';
        
        // Add connection status indicator
        const isConnected = data.connectivity?.connected ?? false;
        html += `
            <div class="status-indicator ${isConnected ? 'connected' : 'disconnected'}">
                ${isConnected ? '🟢 Connected' : '🔴 Disconnected'}
            </div>
        `;

        // Add interfaces information with error handling
        if (data.interfaces && data.interfaces.length > 0) {
            data.interfaces.forEach(iface => {
                html += `
                    <div class="network-interface">
                        <div class="interface-name">${escapeHtml(iface.name || 'Unknown')}</div>
                        <div class="interface-status">${escapeHtml(iface.status || 'Unknown')}</div>
                        <div class="interface-speed">${escapeHtml(iface.speed || 'N/A')}</div>
                        ${iface.addresses ? formatAddresses(iface.addresses) : ''}
                    </div>
                `;
            });
        } else {
            html += '<div class="no-data">No network interfaces detected</div>';
        }

        html += '</div>';
        networkDetails.innerHTML = html;
    }

    function updateMonitoringGraphs(data) {
        const ctx = document.getElementById('usage-chart').getContext('2d');
        // Update monitoring graphs with Chart.js
        // ... chart update logic ...
    }

    function updateLastRefreshTime() {
        const lastUpdate = document.getElementById('last-update');
        lastUpdate.textContent = 'Last Updated: ' + new Date().toLocaleTimeString();
    }

    // Formatting helpers
    function formatSystemInfo(info) {
        return `
            <div>System: ${info.system}</div>
            <div>Platform: ${info.platform}</div>
            <div>Machine: ${info.machine}</div>
        `;
    }

    function formatCPUInfo(cpu) {
        return `
            <div>Model: ${cpu.name}</div>
            <div>Cores: ${cpu.cores}</div>
            <div>Usage: ${cpu.current_usage}</div>
        `;
    }

    function formatMemoryInfo(ram) {
        return `
            <div>Total: ${ram.total}</div>
            <div>Used: ${ram.used}</div>
            <div>Available: ${ram.available}</div>
        `;
    }

    function formatStorageInfo(storage) {
        return storage.drives.map(drive => `
            <div class="storage-item">
                <div>Device: ${drive.device}</div>
                <div>Total: ${drive.total}</div>
                <div>Used: ${drive.percent_used}</div>
            </div>
        `).join('');
    }

    function formatNetworkInfo(network) {
        let html = '<div class="network-grid">';
        network.interfaces.forEach(iface => {
            html += `
                <div class="network-interface">
                    <div>Interface: ${iface.name}</div>
                    <div>Status: ${iface.status}</div>
                    <div>Speed: ${iface.speed || 'N/A'}</div>
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    function formatGPUInfo(gpu) {
        return gpu.gpus.map(card => `
            <div>Model: ${card.name}</div>
            <div>Memory: ${card.memory_total}</div>
        `).join('');
    }

    function showError(message) {
        // Add error notification logic
        console.error(message);
    }

    // Helper function to safely escape HTML
    function escapeHtml(unsafe) {
        if (unsafe == null) return '';
        return unsafe
            .toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatAddresses(addresses) {
        if (!addresses || !addresses.length) return '';
        
        return addresses.map(addr => `
            <div class="address-info">
                <span class="address-type">${escapeHtml(addr.family)}</span>
                <span class="address-value">${escapeHtml(addr.address)}</span>
            </div>
        `).join('');
    }

    // Initial refresh
    refreshAll();
});