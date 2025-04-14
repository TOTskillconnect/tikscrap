"""
Script to run the TikTok Niche Scraper on a schedule.
"""

import os
import sys
from pathlib import Path
import argparse

# Add the current directory to path to allow importing modules
sys.path.insert(0, str(Path(__file__).parent))

from utils.scheduler import run_scheduler
from utils.logger import get_logger
from config import SCHEDULER_ENABLED

logger = get_logger()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="TikTok Niche Scraper Scheduler")
    parser.add_argument("--run-now", action="store_true", help="Run the scraper immediately before starting the scheduler")
    parser.add_argument("--daemon", action="store_true", help="Run as a daemon (background process)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if not SCHEDULER_ENABLED:
        logger.warning("Scheduler is disabled in config. Enable it by setting SCHEDULER_ENABLED = True")
        sys.exit(1)
    
    try:
        logger.info("Starting TikTok Niche Scraper Scheduler")
        
        # Run as daemon if requested
        if args.daemon and os.name != 'nt':  # Daemon mode only available on Unix-like systems
            import daemon
            logger.info("Starting in daemon mode")
            with daemon.DaemonContext():
                run_scheduler(run_immediately=args.run_now)
        else:
            # Run in foreground
            run_scheduler(run_immediately=args.run_now)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down scheduler")
    except Exception as e:
        logger.error(f"Error running scheduler: {str(e)}")
        sys.exit(1) 