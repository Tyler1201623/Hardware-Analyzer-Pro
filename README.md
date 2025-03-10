# Hardware Analyzer Pro

A professional-grade hardware monitoring and analysis tool built with Python and PyQt6.

## Key Features

- Real-time hardware monitoring
  - CPU usage and temperature
  - RAM utilization
  - GPU metrics (NVIDIA support)
  - Storage analysis
  - Network monitoring
- Professional UI with Dark/Light themes
- Live performance graphs
- Network interface monitoring
- Export capabilities (JSON, CSV, PDF)
- Auto-refresh functionality
- System alerts and notifications

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hardware-analyzer-pro
```

2. Run the setup script:
```bash
# Windows (PowerShell)
powershell.exe -ExecutionPolicy Bypass -File .\dev_setup.ps1

# Windows (Command Prompt)
.\launch.bat

# Linux/macOS
./dev_setup.sh
```

## Requirements

- Python 3.8 or higher
- Windows, Linux, or macOS
- Dependencies (automatically installed):
  - PyQt6 ≥ 6.4.0
  - matplotlib ≥ 3.6.0
  - psutil ≥ 5.9.0
  - py3nvml ≥ 0.2.7 (for NVIDIA GPU support)
  - Additional requirements listed in requirements.txt

## Usage

1. Start the application:
```bash
python run.py
```

2. Features:
   - Use the toolbar for quick actions
   - Switch between tabs for different monitoring views
   - Adjust refresh rates in settings
   - Export data in various formats

## Development

```bash
# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
python -m pytest tests/

# Code quality checks
python -m black src/
python -m flake8 src/
python -m mypy src/
```

## Logs

Log files are stored in the `logs` directory:
- hardware_analyzer.log - Main application log
- cpu_manager.log - CPU monitoring
- gpu_manager.log - GPU monitoring
- ram_manager.log - Memory monitoring
- network_manager.log - Network monitoring
- storage_manager.log - Storage monitoring

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please create an issue in the repository.