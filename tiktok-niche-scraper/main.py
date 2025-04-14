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

from utils.logger import get_logger
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
    MAX_TOTAL_VIDEOS
)
from scraper.tiktok_api import get_videos_for_tag
from scraper.video_parser import parse_video_data

# Conditionally import Google Sheets module only if enabled
if 'google_sheets' in OUTPUT_FORMATS and GOOGLE_SHEETS_ENABLED:
    from utils.sheets_helper import update_google_sheet

logger = get_logger()

def calculate_performance_score(video):
    """
    Calculate a performance score for a video based on engagement metrics.
    
    Args:
        video (dict): Video data containing engagement metrics
        
    Returns:
        float: Performance score
    """
    # Extract metrics with fallbacks to 0
    stats = video.get('statistics', {})
    views = stats.get('views', 0)
    likes = stats.get('likes', 0)
    comments = stats.get('comments', 0)
    shares = stats.get('shares', 0)
    
    # Guard against zero views
    if views == 0:
        views = 1
    
    # Calculate engagement rate (likes + comments + shares) / views
    engagement_rate = (likes + comments + shares) / views
    
    # Calculate virality score
    virality_score = (likes * 1) + (comments * 2) + (shares * 3)
    
    # Calculate overall performance (weighted)
    performance = (views * 0.4) + (virality_score * 0.5) + (engagement_rate * 10000 * 0.1)
    
    # Add performance score to video data
    video['performance_score'] = round(performance, 2)
    video['engagement_rate'] = round(engagement_rate * 100, 2)  # as percentage
    
    return performance

def is_trending(video):
    """
    Determine if a video meets trending criteria.
    
    Args:
        video (dict): Video data
        
    Returns:
        bool: True if video is trending
    """
    if not TRENDING_ONLY:
        return True
        
    stats = video.get('statistics', {})
    views = stats.get('views', 0)
    likes = stats.get('likes', 0)
    comments = stats.get('comments', 0)
    shares = stats.get('shares', 0)
    
    # Guard against zero views
    if views == 0:
        return False
    
    # Calculate engagement rate
    engagement = likes + comments + shares
    engagement_rate = engagement / views
    
    # Check if video meets trending criteria
    if views >= MIN_VIEWS and engagement_rate >= MIN_ENGAGEMENT_RATE:
        return True
    
    return False

async def scrape_keyword(keyword):
    """
    Scrape TikTok videos for a specific keyword/niche.
    
    Args:
        keyword (str): The keyword to search for
        
    Returns:
        list: List of processed video data
    """
    logger.info(f"Starting scrape for keyword: {keyword}")
    
    # Add a random delay between keywords to appear more natural
    if random.random() < 0.7:  # 70% chance of delay
        delay = random.uniform(1.0, 5.0)
        logger.info(f"Adding random delay of {delay:.2f}s before processing '{keyword}'")
        await asyncio.sleep(delay)
    
    # Get raw video data from TikTok
    raw_videos = await get_videos_for_tag(keyword, MAX_VIDEOS_PER_KEYWORD)
    
    # Process each video to extract structured data
    processed_videos = []
    for video in raw_videos:
        processed_data = parse_video_data(video)
        processed_data["keyword"] = keyword  # Add the source keyword
        
        # Add timestamp fields
        current_time = datetime.now()
        processed_data["scrape_date"] = current_time.strftime("%Y-%m-%d")
        processed_data["scrape_time"] = current_time.strftime("%H:%M:%S")
        
        # Check if video meets trending criteria
        if is_trending(processed_data):
            # Calculate performance score
            calculate_performance_score(processed_data)
            processed_videos.append(processed_data)
    
    # Sort videos by performance score if enabled
    if SORT_BY_PERFORMANCE:
        processed_videos.sort(key=lambda x: x.get('performance_score', 0), reverse=True)
    
    # Limit to top MAX_VIDEOS_PER_KEYWORD
    processed_videos = processed_videos[:MAX_VIDEOS_PER_KEYWORD]
    
    logger.info(f"Processed {len(processed_videos)} trending videos for keyword: {keyword}")
    return processed_videos

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
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved trending videos to JSON: {json_path}")
    
    if 'csv' in OUTPUT_FORMATS:
        csv_path = output_dir / f"trending_videos_{timestamp}.csv"
        if all_videos:
            # Ensure view count and performance metrics are in the priority columns
            priority_keys = ['url', 'author', 'keyword', 'performance_score', 'engagement_rate', 
                             'scrape_date', 'scrape_time', 'timestamp']
            
            # Get statistics keys
            stats_keys = []
            if 'statistics' in all_videos[0]:
                stats_keys = [f"stats_{k}" for k in all_videos[0]['statistics'].keys()]
            
            # Get all other keys
            other_keys = [k for k in all_videos[0].keys() if k not in priority_keys and k != 'statistics']
            
            # Final column order
            ordered_keys = priority_keys + stats_keys + other_keys
            
            # Flatten statistics for CSV output
            for video in all_videos:
                stats = video.get('statistics', {})
                for key, value in stats.items():
                    video[f"stats_{key}"] = value
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, ordered_keys)
                dict_writer.writeheader()
                dict_writer.writerows(all_videos)
            logger.info(f"Saved trending videos to CSV: {csv_path}")
        else:
            logger.warning("No videos to save to CSV")
    
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