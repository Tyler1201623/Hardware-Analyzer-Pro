@echo off
:: filepath: /c:/Users/ty/Desktop/Best Programs I Created/Hardware Analyzer Python/launch.bat

echo Starting Hardware Analyzer Pro...
echo ===============================

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run application with error handling
python run.py
if errorlevel 1 (
    echo Error: Application failed to start.
    echo Please check the logs for more information.
    pause
    exit /b 1
)

:: Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat