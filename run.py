import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QGuiApplication

def setup_directories():
    """Create all required directories."""
    dirs = [
        'logs',
        'src/logs',
        'src/core/logs',
        'src/static',
        'src/templates',
        'reports',
        'results',
        'metrics'
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def setup_logging():
    """Initialize logging configuration."""
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler
    file_handler = logging.FileHandler(
        'logs/hardware_analyzer.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def print_log_locations():
    """Print locations of log files."""
    base_dir = os.getcwd()
    log_files = {
        "Main Log": os.path.join(base_dir, "logs", "hardware_analyzer.log"),
        "CPU Log": os.path.join(base_dir, "logs", "cpu_manager.log"),
        "GPU Log": os.path.join(base_dir, "logs", "gpu_manager.log"),
        "RAM Log": os.path.join(base_dir, "logs", "ram_manager.log"),
        "Network Log": os.path.join(base_dir, "logs", "network_manager.log"),
        "Storage Log": os.path.join(base_dir, "logs", "storage_manager.log")
    }
    
    print("\nLog File Locations:")
    print("=" * 50)
    for name, path in log_files.items():
        print(f"{name}: {path}")
    print("=" * 50 + "\n")

def copy_default_theme():
    """Create default theme file if it doesn't exist."""
    theme_dir = Path('src/static')
    theme_file = theme_dir / 'style.qss'
    
    if not theme_file.exists():
        default_theme = """
/* Default theme */
QMainWindow {
    background-color: #1E1E1E;
    color: #FFFFFF;
}

QWidget {
    background-color: #1E1E1E;
    color: #FFFFFF;
}

QPushButton {
    background-color: #0066cc;
    color: white;
    padding: 8px 15px;
    border: none;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #0052a3;
}

QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #252526;
}

QTabBar::tab {
    background-color: #2D2D2D;
    color: #FFFFFF;
    padding: 8px 20px;
    border: none;
}

QTabBar::tab:selected {
    background-color: #007ACC;
}
"""
        theme_file.write_text(default_theme)

def optimize_qt_settings():
    """Configure Qt for optimal performance."""
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_SCALE_FACTOR'] = '1'
    os.environ['QT_FONT_DPI'] = '96'
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

def main():
    """Main application entry point with performance optimizations."""
    try:
        # Setup environment
        setup_directories()
        setup_logging()
        print_log_locations()
        copy_default_theme()
        
        # Add src to Python path
        src_path = os.path.join(os.path.dirname(__file__), "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Set DPI attributes before creating QApplication
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Initialize Qt application
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # Apply optimizations
        optimize_qt_settings()
        
        # Import and create main window
        from src.main import HardwareAnalyzerApp
        window = HardwareAnalyzerApp()
        window.show()
        
        return app.exec()
        
    except ImportError as e:
        print(f"Error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        logging.exception("Application failed to start")
        return 1

if __name__ == "__main__":
    sys.exit(main())
