$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

# Ensure we're in a virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Status "Activating virtual environment..." -Color Yellow
    & .\venv\Scripts\Activate.ps1
}

# Install/Upgrade PyInstaller
Write-Status "Installing/Upgrading PyInstaller..." -Color Cyan
python -m pip install --upgrade pyinstaller

# Clean previous builds
Write-Status "Cleaning previous builds..." -Color Yellow
Remove-Item -Path "dist" -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "*.spec" -ErrorAction SilentlyContinue

# Create build
Write-Status "Building application..." -Color Cyan
pyinstaller --noconfirm Hardware_Analyzer.spec

# Create distribution package
Write-Status "Creating distribution package..." -Color Cyan
$version = "1.0.0"
$distName = "Hardware_Analyzer_Pro_v${version}"
$zipPath = "dist\${distName}.zip"

# Create distribution directory structure
$distDir = "dist\$distName"
New-Item -ItemType Directory -Path $distDir -Force | Out-Null

# Copy additional files
Copy-Item "dist\Hardware Analyzer Pro\*" $distDir -Recurse
Copy-Item "README.md" $distDir
Copy-Item "LICENSE" $distDir

# Create ZIP archive
Compress-Archive -Path "$distDir\*" -DestinationPath $zipPath -Force

Write-Status "Build completed successfully!" -Color Green
Write-Status "Distribution package created at: $zipPath" -Color Green

# Cleanup temporary files
Remove-Item -Path "build" -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "$distDir" -Recurse -ErrorAction SilentlyContinue

Write-Status "Build artifacts cleaned up" -Color Yellow
