import sys
import os
import json
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QLabel,
    QProgressBar,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer, QSize, QObject
from PyQt6.QtGui import QTextCursor, QIcon, QFont
from core.hardware_manager import HardwareManager
from core.network import Network
from core.utils import setup_logging
from themes import ThemeManager

# Add at the top of the file, before other imports
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta

    matplotlib_available = True
except ImportError:
    matplotlib_available = False

import numpy as np
from collections import deque
from threading import Lock
import csv


class HardwareAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize time first
        self.last_refresh = datetime.now()

        # Setup logging first
        setup_logging()
        self.logger = logging.getLogger("Hardware_Analyzer")

        # Initialize window properties and DPI settings
        if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        if hasattr(Qt.ApplicationAttribute, "AA_Use96Dpi"):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi)

        self.setWindowTitle("Hardware Analyzer Pro")
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowIcon(QIcon("favicon.ico"))

        # Add theme manager instance
        self.theme_manager = ThemeManager()
        self.current_theme = "Light"

        try:
            # Initialize managers with optimized settings
            self.hardware_manager = HardwareManager()
            self.network_manager = Network()

            # Setup UI with performance improvements
            self.init_ui()
            self.setup_optimized_refresh()

            # Apply light theme by default
            self.setStyleSheet(self.theme_manager.get_light_theme())

            # Load settings last
            self.load_settings()

        except Exception as e:
            self.logger.critical(f"Failed to initialize: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize: {e}")
            raise

        # Add monitoring locks and buffers
        self.data_lock = Lock()
        self.max_points = 60  # 60 seconds of data
        self.initialize_data_buffers()

    def print_log_locations(self):
        """Print locations of all log files."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        log_files = {
            "Main Log": os.path.join(base_dir, "logs", "hardware_analyzer.log"),
            "CPU Log": os.path.join(base_dir, "logs", "cpu_manager.log"),
            "GPU Log": os.path.join(base_dir, "logs", "gpu_manager.log"),
            "RAM Log": os.path.join(base_dir, "logs", "ram_manager.log"),
            "Network Log": os.path.join(base_dir, "logs", "network_manager.log"),
            "Storage Log": os.path.join(base_dir, "logs", "storage_manager.log"),
        }

        print("\nLog File Locations:")
        print("=" * 50)
        for name, path in log_files.items():
            print(f"{name}: {path}")
        print("=" * 50 + "\n")

    def load_theme(self):
        """Load application theme with fallback."""
        try:
            # Try multiple theme file locations
            theme_paths = [
                "src/static/style.qss",
                "static/style.qss",
                "style.qss",
                os.path.join(os.path.dirname(__file__), "static", "style.qss"),
            ]

            for path in theme_paths:
                try:
                    if os.path.exists(path):
                        with open(path, "r") as f:
                            self.setStyleSheet(f.read())
                            self.logger.info(f"Theme loaded from: {path}")
                            return
                except Exception:
                    continue

            # If no theme file found, use default theme
            self.setStyleSheet(ThemeManager.get_dark_theme())
            self.logger.info("Using default dark theme")

        except Exception as e:
            self.logger.error(f"Theme loading failed, using basic theme: {e}")
            # Set minimal fallback theme
            self.setStyleSheet(
                """
                QMainWindow, QWidget {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
            """
            )

    def init_ui(self):
        """Initialize the main user interface."""
        # Create central widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create status bar first
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Add toolbar
        self.create_toolbar(main_layout)

        # Create and initialize tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Initialize tabs
        self.init_hardware_tab()
        self.init_network_tab()
        self.init_monitoring_tab()
        self.init_settings_tab()

    def init_hardware_tab(self):
        """Initialize hardware information tab with enhanced visuals."""
        hardware_tab = QWidget()
        layout = QVBoxLayout(hardware_tab)

        # Hardware info display with improved styling
        self.hardware_text = QTextEdit()
        self.hardware_text.setReadOnly(True)
        self.hardware_text.setFont(QFont("Consolas", 11))
        self.hardware_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
                padding: 10px;
            }
        """
        )
        layout.addWidget(self.hardware_text)

        # Control buttons with modern styling
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """
        )
        refresh_btn.clicked.connect(self.refresh_hardware)
        button_layout.addWidget(refresh_btn)

        export_btn = QPushButton("💾 Export")
        export_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            """
        )
        export_btn.clicked.connect(self.export_hardware)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)
        self.tab_widget.addTab(hardware_tab, "Hardware")

    def init_network_tab(self):
        """Initialize enhanced network information tab."""
        network_tab = QWidget()
        layout = QVBoxLayout(network_tab)

        # Add refresh button at the top
        refresh_btn = QPushButton("🔄 Refresh Network")
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """
        )
        refresh_btn.clicked.connect(self.refresh_network)
        layout.addWidget(refresh_btn)

        # Network Status Card
        status_group = QGroupBox("Network Status")
        status_group.setStyleSheet(
            """
            QGroupBox {
                border: 2px solid #2196F3;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )
        status_layout = QVBoxLayout()

        self.connection_status = QLabel()
        self.connection_status.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
        """
        )
        status_layout.addWidget(self.connection_status)

        self.external_ip = QLabel()
        self.external_ip.setStyleSheet("font-size: 12px; padding: 5px;")
        status_layout.addWidget(self.external_ip)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Network Interfaces Card
        interfaces_group = QGroupBox("Network Interfaces")
        interfaces_group.setStyleSheet(
            """
            QGroupBox {
                border: 2px solid #4CAF50;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )
        interfaces_layout = QVBoxLayout()

        self.interfaces_area = QScrollArea()
        self.interfaces_area.setWidgetResizable(True)
        self.interfaces_widget = QWidget()
        self.interfaces_layout = QVBoxLayout(self.interfaces_widget)
        self.interfaces_area.setWidget(self.interfaces_widget)

        interfaces_layout.addWidget(self.interfaces_area)
        interfaces_group.setLayout(interfaces_layout)
        layout.addWidget(interfaces_group)

        # Network Statistics Card
        stats_group = QGroupBox("Network Statistics")
        stats_group.setStyleSheet(
            """
            QGroupBox {
                border: 2px solid #9C27B0;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )
        stats_layout = QVBoxLayout()

        self.network_stats = QLabel()
        self.network_stats.setStyleSheet(
            """
            QLabel {
                font-family: 'Consolas';
                font-size: 12px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """
        )
        stats_layout.addWidget(self.network_stats)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Initialize network_text for JSON display
        self.network_text = QTextEdit()
        self.network_text.setReadOnly(True)
        self.network_text.setFont(QFont("Consolas", 10))
        self.network_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #252526;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 10px;
            }
        """
        )

        # Add to layout
        layout.addWidget(self.network_text)

        self.tab_widget.addTab(network_tab, "Network")

        # Do initial network refresh
        self.refresh_network()

    def update_network(self):
        """Update network information with enhanced visuals."""
        try:
            network_info = self.network_manager.get_network_summary()

            # Update connection status
            if network_info.get("connectivity", {}).get("connected"):
                self.connection_status.setText("🟢 Connected")
                self.connection_status.setStyleSheet(
                    """
                    QLabel {
                        background-color: #E8F5E9;
                        color: #2E7D32;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 5px;
                    }
                """
                )
            else:
                self.connection_status.setText("🔴 No Internet Connection")
                self.connection_status.setStyleSheet(
                    """
                    QLabel {
                        background-color: #FFEBEE;
                        color: #C62828;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 5px;
                    }
                """
                )

            # Update external IP
            external_ip = network_info.get("connectivity", {}).get(
                "external_ip", "Unknown"
            )
            self.external_ip.setText(f"External IP: {external_ip}")

            # Update interfaces
            self._clear_layout(self.interfaces_layout)
            for iface in network_info.get("interfaces", []):
                interface_card = self._create_interface_card(iface)
                self.interfaces_layout.addWidget(interface_card)

            # Update network statistics
            io_stats = network_info.get("io_stats", {})
            stats_text = (
                f"📥 Bytes Received: {self._format_bytes(io_stats.get('bytes_recv', 0))}\n"
                f"📤 Bytes Sent: {self._format_bytes(io_stats.get('bytes_sent', 0))}\n"
                f"📦 Packets Received: {io_stats.get('packets_recv', 0):,}\n"
                f"📦 Packets Sent: {io_stats.get('packets_sent', 0):,}\n"
                f"❌ Errors In: {io_stats.get('errin', 0):,}\n"
                f"❌ Errors Out: {io_stats.get('errout', 0):,}"
            )
            self.network_stats.setText(stats_text)

        except Exception as e:
            self.logger.error(f"Error updating network display: {e}")

    def _create_interface_card(self, iface):
        """Create a styled network interface card."""
        card = QGroupBox(f"🔌 {iface['name']}")
        layout = QVBoxLayout()

        # Status with icon
        status = "🟢 Up" if iface["status"] == "Up" else "🔴 Down"
        status_label = QLabel(f"Status: {status}")
        status_label.setStyleSheet(
            """
            QLabel {
                padding: 5px;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
        """
        )
        layout.addWidget(status_label)

        # Speed and MTU
        layout.addWidget(QLabel(f"Speed: {iface['speed']}"))
        layout.addWidget(QLabel(f"MTU: {iface['mtu']}"))

        # IP Addresses
        if iface["addresses"]:
            addr_group = QGroupBox("Addresses")
            addr_layout = QVBoxLayout()
            for addr in iface["addresses"]:
                addr_text = QLabel(f"{addr['family']}: {addr['address']}")
                addr_text.setStyleSheet("font-family: 'Consolas'; padding: 2px;")
                addr_layout.addWidget(addr_text)
            addr_group.setLayout(addr_layout)
            layout.addWidget(addr_group)

        card.setLayout(layout)
        return card

    def _format_bytes(self, bytes):
        """Format bytes as human-readable text."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"

    def _clear_layout(self, layout):
        """Clear all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def init_monitoring_tab(self):
        """Initialize real-time monitoring tab."""
        monitoring_tab = QWidget()
        layout = QVBoxLayout(monitoring_tab)

        # CPU Usage
        layout.addWidget(QLabel("CPU Usage:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0066cc;
                border-radius: 5px;
            }
        """
        )
        layout.addWidget(self.cpu_progress)

        # RAM Usage
        layout.addWidget(QLabel("RAM Usage:"))
        self.ram_progress = QProgressBar()
        self.ram_progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 5px;
            }
        """
        )
        layout.addWidget(self.ram_progress)

        # GPU Usage
        layout.addWidget(QLabel("GPU Usage:"))
        self.gpu_progress = QProgressBar()
        self.gpu_progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #dc3545;
                border-radius: 5px;
            }
        """
        )
        layout.addWidget(self.gpu_progress)

        # Add graphs if matplotlib is available
        if matplotlib_available:
            self.add_monitoring_graphs(layout)

        self.tab_widget.addTab(monitoring_tab, "Monitoring")

    def add_monitoring_graphs(self, layout):
        """Add performance graphs using matplotlib."""
        try:
            # Create figure with dark theme
            plt.style.use("dark_background")
            self.fig, (ax1, ax2, ax3) = plt.subplots(
                3, 1, figsize=(8, 8), constrained_layout=True, facecolor="#1E1E1E"
            )

            # Store axes for updates
            self.performance_axes = [ax1, ax2, ax3]

            # Initialize data structures
            self.time_data = deque(maxlen=60)  # Store 60 seconds of data
            self.cpu_data = deque(maxlen=60)
            self.ram_data = deque(maxlen=60)
            self.gpu_data = deque(maxlen=60)

            # Configure axes
            for ax in self.performance_axes:
                ax.set_facecolor("#2D2D2D")
                ax.grid(True, linestyle="--", alpha=0.3)
                ax.tick_params(colors="white")
                ax.set_ylim(0, 100)
                ax.yaxis.set_major_formatter(
                    plt.FuncFormatter(lambda x, p: f"{int(x)}%")
                )

            # Create lines
            (self.cpu_line,) = ax1.plot([], [], "c-", linewidth=2, label="CPU")
            (self.ram_line,) = ax2.plot([], [], "g-", linewidth=2, label="RAM")
            (self.gpu_line,) = ax3.plot([], [], "r-", linewidth=2, label="GPU")

            # Set titles
            ax1.set_title("CPU Usage", color="cyan", pad=10)
            ax2.set_title("RAM Usage", color="lightgreen", pad=10)
            ax3.set_title("GPU Usage", color="red", pad=10)

            # Add value labels
            style = dict(
                size=10,
                color="white",
                bbox=dict(facecolor="#1E1E1E", edgecolor="none", alpha=0.7),
            )
            self.cpu_text = ax1.text(0.02, 0.95, "", transform=ax1.transAxes, **style)
            self.ram_text = ax2.text(0.02, 0.95, "", transform=ax2.transAxes, **style)
            self.gpu_text = ax3.text(0.02, 0.95, "", transform=ax3.transAxes, **style)

            # Add legends
            for ax in self.performance_axes:
                ax.legend(loc="upper right")

            self.canvas = FigureCanvas(self.fig)
            layout.addWidget(self.canvas)

            # Start update timer
            self.graph_timer = QTimer()
            self.graph_timer.timeout.connect(self.update_graphs)
            self.graph_timer.start(1000)  # Update every second

        except Exception as e:
            self.logger.error(f"Error setting up monitoring graphs: {e}")

    def update_graphs(self):
        """Update performance graphs with latest data."""
        try:
            current_time = datetime.now()

            # Get latest values
            cpu_usage = float(self.hardware_manager.get_cpu_usage())
            ram_usage = float(self.hardware_manager.get_ram_usage())
            gpu_usage = float(self.hardware_manager.get_gpu_usage())

            # Update data
            self.time_data.append(current_time)
            self.cpu_data.append(cpu_usage)
            self.ram_data.append(ram_usage)
            self.gpu_data.append(gpu_usage)

            # Update line data
            times = list(self.time_data)
            self.cpu_line.set_data(times, self.cpu_data)
            self.ram_line.set_data(times, self.ram_data)
            self.gpu_line.set_data(times, self.gpu_data)

            # Update text displays
            self.cpu_text.set_text(f"{cpu_usage:.1f}%")
            self.ram_text.set_text(f"{ram_usage:.1f}%")
            self.gpu_text.set_text(f"{gpu_usage:.1f}%")

            # Update axes limits
            for ax in self.performance_axes:
                ax.set_xlim(current_time - timedelta(seconds=60), current_time)
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

            # Draw update
            self.canvas.draw()

        except Exception as e:
            self.logger.error(f"Error updating graphs: {e}")

    def initialize_data_buffers(self):
        """Initialize efficient data storage for monitoring."""
        self.time_data = deque(maxlen=self.max_points)
        self.cpu_data = deque(maxlen=self.max_points)
        self.ram_data = deque(maxlen=self.max_points)
        self.gpu_data = deque(maxlen=self.max_points)

    def init_settings_tab(self):
        """Initialize settings tab."""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)

        # Theme selection
        layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setStyleSheet(
            """
            QComboBox {
                background-color: #252526;
                color: #FFFFFF;
                padding: 5px 10px;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                color: #FFFFFF;
                /* Use unicode triangle as fallback */
                image: none;
                /* Add the arrow using pseudo-element */
            }
            QComboBox::down-arrow:after {
                content: "▼";
            }
            QComboBox:hover {
                background-color: #3d3d3d;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                color: #FFFFFF;
                border: 1px solid #3a3a3a;
                selection-background-color: #0078d4;
            }
        """
        )
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        layout.addWidget(self.theme_combo)

        # Refresh interval
        layout.addWidget(QLabel("Auto-refresh Interval:"))
        self.refresh_combo = QComboBox()
        self.refresh_combo.addItems(["5s", "10s", "30s", "1m"])
        self.refresh_combo.setStyleSheet(
            """
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """
        )
        layout.addWidget(self.refresh_combo)

        # Auto-start option
        self.autostart_check = QCheckBox("Start with System")
        self.autostart_check.setStyleSheet(
            """
            QCheckBox {
                spacing: 5px;
            }
        """
        )
        layout.addWidget(self.autostart_check)

        layout.addStretch()
        self.tab_widget.addTab(settings_tab, "Settings")

    def create_toolbar(self, layout):
        """Create the main toolbar with modern styling."""
        toolbar = QHBoxLayout()

        # Refresh All button with modern styling
        refresh_btn = QPushButton("🔄 Refresh All")
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """
        )
        refresh_btn.clicked.connect(self.refresh_all)
        toolbar.addWidget(refresh_btn)

        # Export options with styled dropdown
        export_combo = QComboBox()
        export_combo.addItems(["Export JSON", "Export CSV", "Export PDF"])
        export_combo.setStyleSheet(
            """
            QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 150px;
            }
        """
        )
        export_combo.currentTextChanged.connect(self.handle_export)
        toolbar.addWidget(export_combo)

        # Auto refresh toggle with modern switch style
        self.auto_refresh_cb = QCheckBox("Auto Refresh")
        self.auto_refresh_cb.setStyleSheet(
            """
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """
        )
        self.auto_refresh_cb.stateChanged.connect(self.toggle_auto_refresh)
        toolbar.addWidget(self.auto_refresh_cb)

        layout.addLayout(toolbar)

    def setup_optimized_refresh(self):
        """Setup optimized refresh timers with reduced overhead."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_all)
        self.refresh_timer.setInterval(5000)  # Default 5 second interval

        self.network_timer = QTimer(self)
        self.network_timer.timeout.connect(self.update_network)
        self.network_timer.setInterval(10000)  # Network updates every 10 seconds

        # Start timers only when needed
        if self.auto_refresh_cb.isChecked():
            self.refresh_timer.start()
            self.network_timer.start()

    def toggle_auto_refresh(self, state):
        """Toggle automatic refresh functionality."""
        try:
            if state:
                # Get interval from combo box
                interval_text = self.refresh_combo.currentText()
                interval = int(interval_text.rstrip("sm"))

                # Convert to milliseconds
                if "m" in interval_text:
                    interval *= 60000  # minutes to milliseconds
                else:
                    interval *= 1000  # seconds to milliseconds

                self.refresh_timer.start(interval)
                self.status_bar.showMessage(
                    f"Auto-refresh enabled: Every {interval_text}"
                )
                self.logger.info(f"Auto-refresh enabled with interval: {interval_text}")
            else:
                self.refresh_timer.stop()
                self.status_bar.showMessage("Auto-refresh disabled")
                self.logger.info("Auto-refresh disabled")

        except Exception as e:
            self.logger.error(f"Auto-refresh error: {e}")
            self.show_error("Auto-refresh Error", str(e))

    def refresh_all(self):
        """Optimized refresh method with reduced UI updates."""
        try:
            QApplication.processEvents()  # Process pending events

            # Batch updates with proper error handling
            self.setUpdatesEnabled(False)  # Disable updates during refresh
            try:
                # Refresh hardware info first
                formatted_output = self.hardware_manager.get_formatted_summary()
                self.hardware_text.setFont(QFont("Cascadia Code", 10))
                self.hardware_text.setText(formatted_output)

                # Get current metrics
                cpu_usage = float(self.hardware_manager.get_cpu_usage())
                ram_usage = float(self.hardware_manager.get_ram_usage())
                gpu_usage = float(self.hardware_manager.get_gpu_usage())

                # Update progress bars
                self.cpu_progress.setValue(int(cpu_usage))
                self.ram_progress.setValue(int(ram_usage))
                self.gpu_progress.setValue(int(gpu_usage))

                # Update network info
                network_info = self.network_manager.get_network_summary()
                self.update_network_status(network_info)
                formatted_json = json.dumps(network_info, indent=2)
                self.network_text.setText(formatted_json)

                # Update status bar
                self.status_bar.showMessage(
                    f"✓ All Updated | CPU: {cpu_usage:.1f}% | RAM: {ram_usage:.1f}% | GPU: {gpu_usage:.1f}% | {datetime.now().strftime('%H:%M:%S')}"
                )

                # Update graphs if available
                if hasattr(self, 'graph_timer'):
                    self.update_graphs()

            finally:
                self.setUpdatesEnabled(True)  # Re-enable updates

            # Update timestamp
            self.last_refresh = datetime.now()
            self.logger.info("Successfully refreshed all components")

        except Exception as e:
            self.logger.error(f"Refresh failed: {e}")
            self.show_error("Refresh Error", str(e))

    def refresh_hardware(self):
        """Refresh hardware information with optimized display."""
        try:
            # Use the new pre-formatted summary method
            formatted_output = self.hardware_manager.get_formatted_summary()
            self.hardware_text.setFont(
                QFont("Cascadia Code", 10)
            )  # Better monospace font
            self.hardware_text.setText(formatted_output)

            # Update status bar with CPU and RAM usage
            cpu_usage = self.hardware_manager.get_cpu_usage()
            ram_usage = self.hardware_manager.get_ram_usage()
            self.status_bar.showMessage(
                f"✓ Updated | CPU: {cpu_usage:.1f}% | RAM: {ram_usage:.1f}% | {datetime.now().strftime('%H:%M:%S')}"
            )

        except Exception as e:
            self.logger.error(f"Error refreshing hardware: {e}")
            self.show_error("Hardware Refresh Error", str(e))

    def _format_hardware_summary(self, summary):
        """Format hardware summary for display."""
        try:
            sections = []

            # CPU Section with enhanced visuals
            cpu_info = summary.get("cpu", {})
            sections.append("╔════════════════ CPU INFORMATION ════════════════╗")
            sections.append(f"║  Model      : {cpu_info.get('name', 'Unknown'):<35} ║")
            sections.append(
                f"║  Cores      : {cpu_info.get('cores', 0)} Physical, {cpu_info.get('threads', 0)} Logical ║"
            )
            sections.append(
                f"║  Frequency  : {cpu_info.get('frequency', 'Unknown'):<35} ║"
            )
            usage = float(
                cpu_info.get("current_usage", "0").strip("%")
                if isinstance(cpu_info.get("current_usage"), str)
                else cpu_info.get("current_usage", 0)
            )
            sections.append(f"║  Usage      : {self._get_colored_status(usage)}% ║")
            sections.append("╚══════════════════════════════════════════════════╝")

            # RAM Section
            ram_info = summary.get("ram", {})
            sections.append("\n╔════════════════ MEMORY STATUS ════════════════╗")

            try:
                total_ram = float(ram_info.get("total", "0").split()[0])
                used_ram = float(ram_info.get("used", "0").split()[0])
                ram_percent = float(ram_info.get("percent", 0))
                available_ram = float(ram_info.get("available", "0").split()[0])
            except (ValueError, AttributeError):
                total_ram = used_ram = ram_percent = available_ram = 0

            sections.append(
                f"║  Total      : {total_ram:>6.2f} GB {self._get_memory_bar(ram_percent)} ║"
            )
            sections.append(f"║  Used       : {used_ram:>6.2f} GB ({ram_percent}%) ║")
            sections.append(f"║  Available  : {available_ram:>6.2f} GB ║")
            sections.append("╚══════════════════════════════════════════════════╝")

            # Rest of sections...
            # ... existing code for GPU and Storage sections ...

            return "\n".join(sections)

        except Exception as e:
            self.logger.error(f"Error formatting hardware summary: {e}")
            return "Error formatting hardware summary"

    def _get_colored_status(self, value):
        """Get colored status based on value."""
        if value < 60:
            return f"{value:>5.1f}🟢"
        elif value < 80:
            return f"{value:>5.1f}🟡"
        else:
            return f"{value:>5.1f}🔴"

    def _get_memory_bar(self, percent):
        """Generate a visual memory usage bar."""
        width = 20
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def _get_storage_bar(self, percent):
        """Generate a visual storage usage bar."""
        width = 40
        filled = int(width * percent / 100)
        if percent < 60:
            bar = "█" * filled + "░" * (width - filled)
        elif percent < 80:
            bar = "▒" * filled + "░" * (width - filled)
        else:
            bar = "▓" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def _get_enhanced_status(self, status):
        """Convert status to enhanced visual indicator."""
        if "Optimal" in status:
            return "✨ Optimal Performance"
        elif "Moderate" in status:
            return "⚠️ Moderate Load"
        else:
            return "🚨 High Usage Alert"

    def refresh_network(self):
        """Refresh network information with error handling."""
        try:
            # Get network info
            network_info = self.network_manager.get_network_summary()

            # Update the text display
            formatted_json = json.dumps(network_info, indent=2)
            self.network_text.setText(formatted_json)

            # Update status indicators
            self.update_network_status(network_info)

            # Update timestamp
            self.last_refresh = datetime.now()
            self.update_status_bar()

            self.logger.info("Network information refreshed successfully")

        except Exception as e:
            self.logger.error(f"Network refresh error: {e}")
            self.show_error(
                "Network Refresh Error", f"Failed to refresh network information: {e}"
            )

    def update_network_status(self, network_info):
        """Update network status indicators."""
        try:
            # Update connection status
            is_connected = network_info.get("connectivity", {}).get("connected", False)
            self.connection_status.setText(
                "🟢 Connected" if is_connected else "🔴 Disconnected"
            )
            self.connection_status.setStyleSheet(
                """
                QLabel {
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    background-color: #E8F5E9;
                    color: #2E7D32;
                }
            """
                if is_connected
                else """
                QLabel {
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    background-color: #FFEBEE;
                    color: #C62828;
                }
            """
            )

            # Update network interfaces
            self._clear_layout(self.interfaces_layout)
            for iface in network_info.get("interfaces", []):
                interface_card = self._create_interface_card(iface)
                self.interfaces_layout.addWidget(interface_card)

            # Update network statistics
            io_stats = network_info.get("io_stats", {})
            stats_text = (
                f"📊 Network Statistics\n\n"
                f"📥 Received: {self._format_bytes(io_stats.get('bytes_recv', 0))}\n"
                f"📤 Sent: {self._format_bytes(io_stats.get('bytes_sent', 0))}\n"
                f"📦 Packets In: {io_stats.get('packets_recv', 0):,}\n"
                f"📦 Packets Out: {io_stats.get('packets_sent', 0):,}\n"
                f"❌ Errors In: {io_stats.get('errin', 0)}\n"
                f"❌ Errors Out: {io_stats.get('errout', 0)}"
            )
            self.network_stats.setText(stats_text)
            self.network_stats.setStyleSheet(
                """
                QLabel {
                    font-family: 'Consolas';
                    font-size: 12px;
                    padding: 15px;
                    background-color: #252526;
                    color: #ffffff;
                    border-radius: 5px;
                }
            """
            )

            # Update IP information
            external_ip = network_info.get("connectivity", {}).get(
                "external_ip", "Unknown"
            )
            self.external_ip.setText(f"🌐 External IP: {external_ip}")
            self.external_ip.setStyleSheet(
                """
                QLabel {
                    font-size: 13px;
                    padding: 10px;
                    background-color: #252526;
                    color: #ffffff;
                    border-radius: 5px;
                }
            """
            )

        except Exception as e:
            self.logger.error(f"Error updating network status: {e}")

    def update_monitoring(self):
        """Update real-time monitoring data."""
        try:
            cpu_usage = self.hardware_manager.get_cpu_usage()
            ram_usage = self.hardware_manager.get_ram_usage()
            gpu_usage = self.hardware_manager.get_gpu_usage()

            self.cpu_progress.setValue(int(cpu_usage))
            self.ram_progress.setValue(int(ram_usage))
            self.gpu_progress.setValue(int(gpu_usage))
        except Exception as e:
            self.show_error("Monitoring Update Error", str(e))

    def update_status_bar(self, refresh_status=None):
        """Update the status bar with the latest information."""
        try:
            status_text = (
                f"Last Refresh: {self.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            if refresh_status:
                components = []
                for component, status in refresh_status.items():
                    icon = "✓" if status else "✗"
                    components.append(f"{component}: {icon}")
                status_text += " | " + " | ".join(components)
            self.status_bar.showMessage(status_text)
        except Exception as e:
            self.logger.error(f"Error updating status bar: {e}")

    def update_hardware_display(self, results):
        """Update hardware display with new metrics."""
        try:
            # Update progress bars safely
            self.cpu_progress.setValue(int(results.get("cpu", 0)))
            self.ram_progress.setValue(int(results.get("ram", 0)))
            self.gpu_progress.setValue(int(results.get("gpu", 0)))

            # Get and format summary with error handling
            try:
                summary = self.hardware_manager.get_hardware_summary()
                formatted_output = self._format_hardware_summary(summary)
                self.hardware_text.setText(formatted_output)
            except Exception as e:
                self.logger.error(f"Error getting hardware summary: {e}")
                self.hardware_text.setText("Error retrieving hardware information")

        except Exception as e:
            self.logger.error(f"Error updating hardware display: {e}")
            raise

    def change_theme(self, theme_name):
        """Change application theme with smooth transition."""
        try:
            if theme_name == "Dark":
                self.setStyleSheet(self.theme_manager.get_dark_theme())
                self.current_theme = "Dark"
            elif theme_name == "Light":
                self.setStyleSheet(self.theme_manager.get_light_theme())
                self.current_theme = "Light"
            else:  # System
                import darkdetect

                system_theme = "Dark" if darkdetect.isDark() else "Light"
                if system_theme == "Dark":
                    self.setStyleSheet(self.theme_manager.get_dark_theme())
                else:
                    self.setStyleSheet(self.theme_manager.get_light_theme())
                self.current_theme = system_theme

            # Save theme preference
            self.save_settings()

        except Exception as e:
            self.logger.error(f"Theme change error: {e}")
            self.show_error("Theme Error", str(e))

    def save_settings(self):
        """Save application settings."""
        try:
            settings = {
                "theme": self.current_theme,
                "refresh_interval": self.refresh_combo.currentText(),
                "autostart": self.autostart_check.isChecked(),
            }
            with open("settings.json", "w") as f:
                json.dump(settings, f)
        except Exception as e:
            self.logger.error(f"Settings save error: {e}")

    def load_settings(self):
        """Load application settings."""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)

                # Apply theme
                theme = settings.get("theme", "System")
                self.theme_combo.setCurrentText(theme)
                self.change_theme(theme)

                # Apply refresh interval
                interval = settings.get("refresh_interval", "5s")
                self.refresh_combo.setCurrentText(interval)

                # Apply autostart
                autostart = settings.get("autostart", False)
                self.autostart_check.setChecked(autostart)

        except Exception as e:
            self.logger.error(f"Settings load error: {e}")

    def export_hardware(self):
        """Export hardware information."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Export Hardware Info", "", "JSON Files (*.json)"
            )
            if file_name:
                with open(file_name, "w") as f:
                    json.dump(self.hardware_manager.get_hardware_summary(), f, indent=2)
        except Exception as e:
            self.show_error("Export Error", str(e))

    def export_network(self):
        """Export network information."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Export Network Info", "", "JSON Files (*.json)"
            )
            if file_name:
                with open(file_name, "w") as f:
                    json.dump(self.network_manager.get_network_summary(), f, indent=2)
        except Exception as e:
            self.show_error("Export Error", str(e))

    def handle_export(self, export_type):
        """Handle different export options with improved functionality."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_name = "Hardware_Analyzer_Pro"

            if export_type == "Export JSON":
                default_name = f"{company_name}_Report_{timestamp}.json"
                data = {
                    "hardware": self.hardware_manager.get_hardware_summary(),
                    "network": self.network_manager.get_network_summary(),
                    "timestamp": timestamp,
                    "system_metrics": {
                        "cpu_usage": self.cpu_data[-1] if self.cpu_data else 0,
                        "ram_usage": self.ram_data[-1] if self.ram_data else 0,
                        "gpu_usage": self.gpu_data[-1] if self.gpu_data else 0,
                    },
                }
                self._save_export(data, default_name, "JSON Files (*.json)")

            elif export_type == "Export CSV":
                default_name = f"{company_name}_Report_{timestamp}.csv"
                self._save_export_csv(default_name)

            elif export_type == "Export PDF":  # Fixed syntax error here
                default_name = f"{company_name}_Report_{timestamp}.pdf"
                self._save_export_pdf(default_name)

        except Exception as e:
            self.logger.error(f"Export error: {e}")
            self.show_error("Export Error", str(e))

    def _save_export(self, data, default_name, file_filter):
        """Save export with default name."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            os.path.join(os.path.expanduser("~/Desktop"), default_name),
            file_filter,
        )
        if file_name:
            with open(file_name, "w") as f:
                if file_filter.startswith("JSON"):
                    json.dump(data, f, indent=2)
                self.show_success(f"Report exported to {file_name}")

    def export_data_to_csv(self, file_path):
        """Export data to CSV format."""
        try:
            hardware_summary = self.hardware_manager.get_hardware_summary()
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)

                # Write system information
                writer.writerow(["System Information"])
                for key, value in hardware_summary["system_info"].items():
                    writer.writerow([key, value])
                writer.writerow([])

                # Write CPU information
                writer.writerow(["CPU Information"])
                for key, value in hardware_summary["cpu"].items():
                    writer.writerow([key, value])
                writer.writerow([])

                # Write RAM information
                writer.writerow(["Memory Information"])
                for key, value in hardware_summary["ram"].items():
                    writer.writerow([key, value])

        except Exception as e:
            raise Exception(f"CSV export failed: {e}")

    def export_csv(self):
        """Export data in CSV format."""
        # CSV export implementation will go here
        pass

    def export_pdf(self):
        """Export data in PDF format."""
        # PDF export implementation will go here
        pass

    def show_success(self, message):
        """Show success message with styling."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Success")
        msg.setStyleSheet(
            """
            QMessageBox {
                background-color: #252526;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 4px;
            }
        """
        )
        msg.exec_()

    def show_error(self, title, message):
        """Show error message dialog."""
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        """Handle application close event with proper cleanup."""
        try:
            if hasattr(self, "refresh_timer"):
                self.refresh_timer.stop()

            if hasattr(self, "hardware_manager"):
                self.hardware_manager.cleanup()

            if hasattr(self, "network_manager"):
                self.network_manager.cleanup()

            self.logger.info("Application shutdown completed successfully")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = HardwareAnalyzerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
