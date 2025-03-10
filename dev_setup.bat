@echo off
REM filepath: /c:/Users/ty/Desktop/Best Programs I Created/Hardware Analyzer Python/dev_setup.bat

echo Setting up development environment...
echo ===================================

REM Create necessary directories
mkdir src\logs 2>nul
mkdir tests 2>nul
mkdir reports 2>nul

REM Install in development mode
python -m pip install --upgrade pip
python -m pip install -e .

REM Install development dependencies
python -m pip install pytest black flake8 mypy

REM Run tests
python -m pytest tests/

echo.
echo Setup completed!
echo Run 'python -m hardware_analyzer' to start the application
pause