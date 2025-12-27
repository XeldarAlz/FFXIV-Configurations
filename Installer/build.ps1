Write-Host "========================================"
Write-Host "  FFXIV Configuration Installer Builder"
Write-Host "========================================"
Write-Host ""

try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org"
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host ""

pyinstaller --onefile `
    --windowed `
    --name "Xeldar FFXIV Installer" `
    --icon "X.ico" `
    --add-data "X.ico;." `
    --add-data "..\Configs\FFXIV Configs;FFXIV Configs" `
    --add-data "..\Configs\Mods Configs;Mods Configs" `
    --add-data "..\Configs\ReShade Configs;ReShade Configs" `
    --add-data "..\Configs\Plugin Configs;Plugin Configs" `
    --clean `
    ffxiv_config_installer.py

Write-Host ""

if (Test-Path "dist\Xeldar FFXIV Installer.exe") {
    Write-Host "========================================"  -ForegroundColor Green
    Write-Host "  BUILD SUCCESSFUL!"  -ForegroundColor Green
    Write-Host "========================================"  -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable created at:" -ForegroundColor Cyan
    Write-Host "  dist\Xeldar FFXIV Installer.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "You can distribute this .exe file - it contains"
    Write-Host "all config folders bundled inside."
} else {
    Write-Host "========================================"  -ForegroundColor Red
    Write-Host "  BUILD FAILED"  -ForegroundColor Red
    Write-Host "========================================"  -ForegroundColor Red
    Write-Host "Check the output above for errors."
}

Write-Host ""
Read-Host "Press Enter to exit"