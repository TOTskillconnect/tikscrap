# TikTok Niche Scraper PowerShell Launcher
# This script runs the TikTok Niche Scraper with error handling.

Write-Host "Starting TikTok Niche Scraper..."
Write-Host "==============================================="

# Set working directory to the script location
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $scriptPath

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Using $pythonVersion"
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher and try again."
    Exit 1
}

# Check if requirements are installed
if (-Not (Test-Path -Path "requirements_checked.txt")) {
    Write-Host "Installing required packages..."
    python -m pip install -r requirements.txt
    
    # Install Playwright browsers if not already installed
    python -m playwright install

    # Create a flag file to avoid reinstalling on every run
    "Requirements check completed on $(Get-Date)" | Out-File -FilePath "requirements_checked.txt"
}

# Run the scraper
try {
    Write-Host "Running TikTok Niche Scraper..."
    python main.py
} catch {
    Write-Host "Error running scraper: $_" -ForegroundColor Red
    Exit 1
}

Write-Host "==============================================="
Write-Host "TikTok Niche Scraper completed successfully!"
Write-Host "Check the data/ directory for results."

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 