"""
Main script for the TikTok Niche Scraper.
Uses enhanced stealth techniques and multiple content discovery approaches to find trending videos.
"""

import asyncio
import json
import csv
import os
from pathlib import Path
import sys
from datetime import datetime
import random
import time
import operator

from utils.logger import get_logger, configure_logging
from config import (
    KEYWORDS, 
    MAX_VIDEOS_PER_KEYWORD, 
    OUTPUT_FORMATS, 
    OUTPUT_DIRECTORY,
    GOOGLE_SHEETS_ENABLED,
    CONCURRENT_KEYWORDS,
    MIN_VIDEOS_REQUIRED,
    BROWSER_VISIBILITY,
    TRENDING_ONLY,
    MIN_VIEWS,
    MIN_ENGAGEMENT_RATE,
    SORT_BY_PERFORMANCE,
    MAX_TOTAL_VIDEOS,
    LOG_LEVEL,
    LOG_FILE,
    MAX_VIDEO_AGE_DAYS
)
from scraper.tiktok_api import get_videos_for_tag
from scraper.video_parser import parse_video_data, is_trending, is_recent_video, calculate_performance_score

# Conditionally import Google Sheets module only if enabled
if 'google_sheets' in OUTPUT_FORMATS and GOOGLE_SHEETS_ENABLED:
    from utils.sheets_helper import update_google_sheet

# Configure logging
configure_logging(LOG_LEVEL, LOG_FILE)
logger = get_logger()

def save_to_json(videos, output_file):
    """Save videos to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=4, ensure_ascii=False)
    logger.info(f"Saved {len(videos)} videos to {output_file}")

def save_to_csv(videos, output_file):
    """Save videos to CSV file."""
    if not videos:
        logger.warning("No videos to save to CSV")
        return
        
    # Get all possible fields from the videos
    fieldnames = set()
    for video in videos:
        fieldnames.update(video.keys())
        fieldnames.update([f"statistics_{key}" for key in video.get('statistics', {})])
        
    fieldnames = sorted(list(fieldnames))
    
    # Remove the statistics dictionary from fieldnames since we'll expand it
    if 'statistics' in fieldnames:
        fieldnames.remove('statistics')
        
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for video in videos:
            # Create a flat dictionary for CSV
            row = video.copy()
            
            # Expand statistics into separate columns
            if 'statistics' in row:
                for key, value in row['statistics'].items():
                    row[f'statistics_{key}'] = value
                del row['statistics']
                
            # Handle lists by converting them to strings
            for key, value in row.items():
                if isinstance(value, list):
                    row[key] = ', '.join(map(str, value))
                    
            writer.writerow(row)
            
    logger.info(f"Saved {len(videos)} videos to {output_file}")

async def scrape_keyword(keyword, min_views=1000, min_engagement_rate=0.01, max_videos=100, max_age_days=14):
    """
    Scrape videos for a specific keyword.
    
    Args:
        keyword (str): Keyword to scrape videos for
        min_views (int): Minimum views for trending videos
        min_engagement_rate (float): Minimum engagement rate for trending videos
        max_videos (int): Maximum number of videos to return
        max_age_days (int): Maximum age of videos in days
        
    Returns:
        list: Trending videos for the keyword
    """
    logger.info(f"Starting scrape for keyword: {keyword}")
    
    # Add a random delay between keywords to appear more natural
    delay = round(random.uniform(1, 5), 2)
    logger.info(f"Adding random delay of {delay}s before processing '{keyword}'")
    await asyncio.sleep(delay)
    
    # Get videos for the keyword
    videos = await get_videos_for_tag(keyword, max_videos=max_videos)
    
    if not videos:
        logger.warning(f"No videos found for keyword: {keyword}")
        return []
        
    logger.info(f"Found {len(videos)} videos for keyword: {keyword}")
    
    # Filter for trending videos within the past two weeks
    trending_videos = []
    for video in videos:
        # Check if video is recent
        if not is_recent_video(video["timestamp"], max_age_days=max_age_days):
            continue
            
        # Check if video is trending
        if TRENDING_ONLY and not is_trending(video, min_views=min_views, min_engagement_rate=min_engagement_rate):
            continue
            
        # Add keyword to the video data
        video["keyword"] = keyword
        trending_videos.append(video)
    
    logger.info(f"Processed {len(trending_videos)} trending videos for keyword: {keyword}")
    return trending_videos

async def process_keywords_batch(keywords_batch):
    """
    Process a batch of keywords concurrently.
    
    Args:
        keywords_batch (list): Batch of keywords to process
        
    Returns:
        list: Combined list of videos from all keywords in batch
    """
    # Process keywords concurrently
    tasks = [scrape_keyword(keyword) for keyword in keywords_batch]
    results = await asyncio.gather(*tasks)
    
    # Flatten the results
    all_videos = []
    for videos in results:
        all_videos.extend(videos)
        
    return all_videos

async def main():
    """Main function to run the scraper."""
    logger.info("Starting TikTok Niche Scraper with enhanced stealth techniques")
    logger.info(f"Browser visibility: {'Visible' if BROWSER_VISIBILITY else 'Headless'}")
    logger.info(f"Trending filter enabled: {TRENDING_ONLY}, Min views: {MIN_VIEWS}")
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / OUTPUT_DIRECTORY
    os.makedirs(output_dir, exist_ok=True)
    
    all_videos = []
    successful_keywords = []
    failed_keywords = []
    
    # Process keywords in batches for controlled concurrency
    if CONCURRENT_KEYWORDS and CONCURRENT_KEYWORDS > 1:
        logger.info(f"Processing keywords in batches of {CONCURRENT_KEYWORDS}")
        
        # Split keywords into batches
        keyword_batches = [KEYWORDS[i:i+CONCURRENT_KEYWORDS] for i in range(0, len(KEYWORDS), CONCURRENT_KEYWORDS)]
        
        # Process each batch
        for batch_idx, batch in enumerate(keyword_batches):
            logger.info(f"Processing batch {batch_idx+1}/{len(keyword_batches)}: {', '.join(batch)}")
            batch_videos = await process_keywords_batch(batch)
            
            # Add to the main list
            all_videos.extend(batch_videos)
            
            # Update successful/failed keywords
            for keyword in batch:
                keyword_videos = [v for v in batch_videos if v.get('keyword') == keyword]
                if len(keyword_videos) >= MIN_VIDEOS_REQUIRED:
                    successful_keywords.append(keyword)
                else:
                    failed_keywords.append(keyword)
            
            # Add a delay between batches to avoid detection
            if batch_idx < len(keyword_batches) - 1:
                delay = random.uniform(5.0, 15.0)
                logger.info(f"Adding delay of {delay:.2f}s between batches")
                await asyncio.sleep(delay)
    else:
        # Process each keyword sequentially
        for keyword in KEYWORDS:
            videos = await scrape_keyword(keyword)
            
            # Add to our total list
            all_videos.extend(videos)
            
            # Update successful/failed keywords
            if len(videos) >= MIN_VIDEOS_REQUIRED:
                successful_keywords.append(keyword)
            else:
                failed_keywords.append(keyword)
    
    # Final sorting of all videos by performance and limit to top MAX_TOTAL_VIDEOS
    if SORT_BY_PERFORMANCE and all_videos:
        logger.info(f"Sorting all videos by performance score")
        all_videos.sort(key=lambda x: x.get('performance_score', 0), reverse=True)
        all_videos = all_videos[:MAX_TOTAL_VIDEOS]
        logger.info(f"Keeping top {MAX_TOTAL_VIDEOS} videos for this scraping session")
    
    logger.info(f"Total videos scraped: {len(all_videos)}")
    logger.info(f"Successful keywords: {len(successful_keywords)} - {', '.join(successful_keywords)}")
    logger.info(f"Failed keywords: {len(failed_keywords)} - {', '.join(failed_keywords)}")
    
    # Only proceed if we have videos
    if not all_videos:
        logger.error("No trending videos were scraped. Exiting without saving.")
        return
    
    # Timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save results in requested formats
    if 'json' in OUTPUT_FORMATS:
        json_path = output_dir / f"trending_videos_{timestamp}.json"
        save_to_json(all_videos, json_path)
    
    if 'csv' in OUTPUT_FORMATS:
        csv_path = output_dir / f"trending_videos_{timestamp}.csv"
        save_to_csv(all_videos, csv_path)
    
    # Update Google Sheets if enabled
    if 'google_sheets' in OUTPUT_FORMATS and GOOGLE_SHEETS_ENABLED and all_videos:
        try:
            logger.info("Updating Google Sheets...")
            success = update_google_sheet(all_videos)
            if success:
                logger.info("Google Sheets update successful")
            else:
                logger.error("Failed to update Google Sheets")
        except Exception as e:
            logger.error(f"Error updating Google Sheets: {str(e)}")
    
    logger.info("Trending video scraping completed successfully")

if __name__ == "__main__":
    try:
        # Add signal handlers if on Unix-like systems
        if os.name != 'nt':  # Not Windows
            import signal
            
            def signal_handler(sig, frame):
                logger.info("Received signal to terminate, shutting down...")
                sys.exit(0)
                
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
        # Run the main async function
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        sys.exit(1) 