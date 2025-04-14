"""
Scheduler module for the TikTok Niche Scraper.
Provides functionality to run the scraper on a schedule.
"""

import os
import sys
import time
import logging
import subprocess
import schedule
import signal
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to allow importing from config
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    SCHEDULER_ENABLED,
    SCHEDULE_INTERVAL,
    SCHEDULE_HOUR,
    SCHEDULE_MINUTE,
    SCHEDULE_DAYS,
    CUSTOM_SCHEDULE,
    SCHEDULER_MAX_INSTANCES
)
from utils.logger import get_logger

logger = get_logger()

# Keep track of running instances
running_instances = 0

def is_windows():
    """Check if the operating system is Windows."""
    return os.name == 'nt'

def run_scraper():
    """
    Execute the TikTok Niche Scraper.
    Uses the appropriate command based on the operating system.
    """
    global running_instances
    
    # Check if we've reached the maximum number of instances
    if running_instances >= SCHEDULER_MAX_INSTANCES:
        logger.warning(f"Maximum number of instances ({SCHEDULER_MAX_INSTANCES}) already running. Skipping this run.")
        return
    
    # Increment the running instances counter
    running_instances += 1
    
    try:
        logger.info("Starting scheduled scrape")
        start_time = datetime.now()
        
        # Determine the script directory
        script_dir = Path(__file__).parent.parent
        
        # Execute the appropriate script based on the OS
        if is_windows():
            # Use subprocess to run the PowerShell script
            logger.info("Running on Windows, using PowerShell script")
            powershell_path = 'powershell.exe'
            script_path = script_dir / 'run.ps1'
            
            process = subprocess.Popen(
                [powershell_path, '-ExecutionPolicy', 'Bypass', '-File', script_path],
                cwd=script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        else:
            # On Unix-like systems, run the Python script directly
            logger.info("Running on Unix-like system, running Python script directly")
            cmd = ['python3', 'main.py']
            
            process = subprocess.Popen(
                cmd,
                cwd=script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        
        # Log the results
        if process.returncode == 0:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() / 60.0
            logger.info(f"Scheduled scrape completed successfully in {duration:.2f} minutes")
        else:
            logger.error(f"Scheduled scrape failed with exit code {process.returncode}")
            logger.error(f"Error output: {stderr}")
            
    except Exception as e:
        logger.error(f"Error executing scheduled scrape: {str(e)}")
        
    finally:
        # Decrement the running instances counter
        running_instances -= 1

def setup_schedule():
    """
    Set up the schedule based on configuration.
    """
    if not SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled. Not setting up schedule.")
        return
    
    logger.info("Setting up schedule")
    
    if SCHEDULE_INTERVAL == 'hourly':
        logger.info(f"Scheduling scraper to run hourly at {SCHEDULE_MINUTE} minutes past the hour")
        schedule.every().hour.at(f":{SCHEDULE_MINUTE:02d}").do(run_scraper)
        
    elif SCHEDULE_INTERVAL == 'daily':
        time_str = f"{SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d}"
        logger.info(f"Scheduling scraper to run daily at {time_str}")
        schedule.every().day.at(time_str).do(run_scraper)
        
    elif SCHEDULE_INTERVAL == 'weekly':
        time_str = f"{SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d}"
        logger.info(f"Scheduling scraper to run weekly on specified days at {time_str}")
        
        for day in SCHEDULE_DAYS:
            day = day.lower()
            if day == 'monday':
                schedule.every().monday.at(time_str).do(run_scraper)
            elif day == 'tuesday':
                schedule.every().tuesday.at(time_str).do(run_scraper)
            elif day == 'wednesday':
                schedule.every().wednesday.at(time_str).do(run_scraper)
            elif day == 'thursday':
                schedule.every().thursday.at(time_str).do(run_scraper)
            elif day == 'friday':
                schedule.every().friday.at(time_str).do(run_scraper)
            elif day == 'saturday':
                schedule.every().saturday.at(time_str).do(run_scraper)
            elif day == 'sunday':
                schedule.every().sunday.at(time_str).do(run_scraper)
                
    elif SCHEDULE_INTERVAL == 'custom':
        logger.info(f"Using custom schedule: {CUSTOM_SCHEDULE}")
        # Schedule library doesn't support cron syntax directly
        # This is a simple approximation for common patterns
        if CUSTOM_SCHEDULE.startswith('0 */'):
            # Pattern like "0 */12 * * *" - every N hours
            parts = CUSTOM_SCHEDULE.split()
            if len(parts) >= 2 and parts[1].startswith('*/'):
                try:
                    hours = int(parts[1][2:])
                    logger.info(f"Scheduling to run every {hours} hours")
                    schedule.every(hours).hours.do(run_scraper)
                except (ValueError, IndexError):
                    logger.error(f"Could not parse custom schedule: {CUSTOM_SCHEDULE}")
                    schedule.every().day.at("03:00").do(run_scraper)  # Fallback
        else:
            logger.warning(f"Complex custom schedule not fully supported: {CUSTOM_SCHEDULE}")
            logger.info("Defaulting to daily at 3:00 AM")
            schedule.every().day.at("03:00").do(run_scraper)
    
    else:
        logger.warning(f"Unknown schedule interval: {SCHEDULE_INTERVAL}")
        logger.info("Defaulting to daily at 3:00 AM")
        schedule.every().day.at("03:00").do(run_scraper)
        
    logger.info("Schedule setup complete")
    
    # Calculate and log the next run time
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        logger.warning("No scheduled runs configured")

def handle_signal(signum, frame):
    """
    Handle termination signals gracefully.
    """
    logger.info(f"Received signal {signum}, shutting down scheduler")
    sys.exit(0)

def run_scheduler(run_immediately=False):
    """
    Run the scheduler in a loop.
    
    Args:
        run_immediately (bool): Whether to run the scraper immediately before starting the scheduler
    """
    if not SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled. Exiting.")
        return
    
    # Set up signal handlers
    if not is_windows():
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
    
    setup_schedule()
    
    logger.info("Scheduler started, running continuously")
    
    # Run once immediately if requested
    if run_immediately:
        logger.info("Running scraper immediately as requested")
        run_scraper()
    else:
        user_input = input("Run scraper immediately before starting scheduler? (y/n): ").lower().strip()
        if user_input == 'y':
            run_scraper()
    
    # Continue running the scheduler
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down scheduler")
            break
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            # Sleep a bit longer if there was an error
            time.sleep(10)
    
    logger.info("Scheduler stopped")

if __name__ == "__main__":
    run_scheduler() 