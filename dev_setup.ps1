# Initialize strict mode and error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

# Create required directories
$directories = @(
    "src/logs",
    "src/core/logs",
    "src/static",
    "src/templates",
    "tests",
    "reports",
    "results",
    "metrics"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Status "Created directory: $dir" -Color Green
    } else {
        Write-Status "Directory already exists: $dir" -Color Yellow
    }
}

# Setup Python virtual environment
Write-Status "Setting up Python virtual environment..." -Color Cyan
if (Test-Path "venv") {
    Write-Status "Removing existing venv..." -Color Yellow
    Remove-Item -Recurse -Force "venv"
}

Write-Status "Creating new virtual environment..." -Color Cyan
python -m venv venv

# Activate virtual environment
Write-Status "Activating virtual environment..." -Color Cyan
& .\venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
Write-Status "Installing dependencies..." -Color Cyan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Install development tools
Write-Status "Installing development tools..." -Color Cyan
python -m pip install pytest black flake8 mypy

# Run code quality checks
Write-Status "Running code quality checks..." -Color Yellow
python -m black src/
python -m flake8 src/ --max-line-length=100 --ignore=E203,W503
python -m mypy src/ --config-file mypy.ini

# Run tests
Write-Status "Running tests..." -Color Yellow
python -m pytest tests/

# Install required modules
$modules = @(
    "Pester",
    "PSReadLine",
    "Az"
)

foreach ($module in $modules) {
    if (-not (Get-Module -ListAvailable -Name $module)) {
        Install-Module -Name $module -Force -Scope CurrentUser
        Write-Status "Installed module: $module" -Color Green
    } else {
        Write-Status "Module already installed: $module" -Color Yellow
    }
}

Write-Status "Setup completed!" -Color Green
Write-Status "To start the application, run: python run.py" -Color Cyan
