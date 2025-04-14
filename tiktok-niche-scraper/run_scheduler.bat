@echo off
REM TikTok Niche Scraper Scheduler Windows launcher
echo Starting TikTok Niche Scraper Scheduler...
cd /d %~dp0

REM Check if --run-now flag is passed
set RUN_NOW=
if "%1"=="--run-now" set RUN_NOW=--run-now

REM Run the Python scheduler script
python run_scheduler.py %RUN_NOW%

echo Scheduler execution completed.
pause 