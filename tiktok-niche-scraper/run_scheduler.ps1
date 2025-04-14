# TikTok Niche Scraper Scheduler PowerShell launcher
Write-Host "Starting TikTok Niche Scraper Scheduler..." -ForegroundColor Green

# Navigate to the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptDir

# Parse command line parameters
param (
    [switch]$RunNow = $false
)

# Build the command with appropriate arguments
$command = "python run_scheduler.py"
if ($RunNow) {
    $command += " --run-now"
}

# Run the Python scheduler script
Write-Host "Executing scheduler script..." -ForegroundColor Cyan
Invoke-Expression $command

Write-Host "Scheduler execution completed." -ForegroundColor Green
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 