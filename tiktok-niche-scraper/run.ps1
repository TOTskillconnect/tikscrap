# TikTok Niche Scraper PowerShell launcher
Write-Host "Starting TikTok Niche Scraper..." -ForegroundColor Green

# Navigate to the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptDir

# Run the Python script
Write-Host "Executing Python script..." -ForegroundColor Cyan
python main.py

Write-Host "Script execution completed." -ForegroundColor Green
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 