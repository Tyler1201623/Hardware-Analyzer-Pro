@echo off
:: filepath: /c:/Users/ty/Desktop/Best Programs I Created/Hardware Analyzer Python/setup.bat

echo Installing Hardware Analyzer Pro dependencies...
echo =============================================

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install base requirements
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

:: Install development tools globally
python -m pip install pytest black flake8 mypy

:: Run checks
echo.
echo Running code quality checks...
echo =============================
python -m black src/
python -m flake8 src/
python -m mypy src/

:: Run tests
echo.
echo Running tests...
echo ===============
python -m pytest

:: Print success message
echo.
echo Setup completed!
echo ===============
echo You can now run the application using: python run.py
pause