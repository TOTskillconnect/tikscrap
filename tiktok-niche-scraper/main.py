"""
TikTok Niche Scraper - Main Script
Enhanced version with advanced stealth techniques, trending video detection,
and multiple content discovery approaches.
"""

import os
import sys
import json
import csv
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Setup logging
from utils.logger import get_logger
logger = get_logger()

# Import configuration
try:
    from config import (
        KEYWORDS, MAX_VIDEOS_PER_KEYWORD, BROWSER_VISIBLE, STEALTH_LEVEL,
        OUTPUT_DIR, SAVE_JSON, SAVE_CSV, UPDATE_GOOGLE_SHEETS,
        TRENDING_ONLY, MIN_VIEWS, MIN_ENGAGEMENT_RATE, 
        SORT_BY_PERFORMANCE, MAX_TOTAL_VIDEOS
    )
except ImportError as e:
    logger.error(f"Failed to import configuration: {e}")
    sys.exit(1)

# Import scraper modules
from scraper.stealth_browser import StealthBrowser
from scraper.content_discovery import discover_videos
from scraper.video_parser import extract_video_data, extract_statistics, calculate_performance_score, is_trending
from utils.data_saver import save_to_json, save_to_csv, update_google_sheet, export_trending_report

# Check for NO_BROWSER environment variable
NO_BROWSER = os.environ.get('NO_BROWSER', '0').lower() in ('1', 'true', 'yes', 'y')

def generate_sample_data(keyword: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate sample video data when running in NO_BROWSER mode
    
    Args:
        keyword: Search keyword
        count: Number of sample videos to generate
        
    Returns:
        List of sample video dictionaries
    """
    logger.info(f"Generating sample data for keyword: {keyword}")
    current_time = datetime.now()
    
    sample_videos = []
    for i in range(count):
        video_id = f"sample_{keyword.replace(' ', '_')}_{i}_{int(time.time())}"
        
        # Generate random statistics in a realistic range
        views = random.randint(10000, 1000000)
        likes = int(views * random.uniform(0.05, 0.2))
        comments = int(likes * random.uniform(0.01, 0.1))
        shares = int(likes * random.uniform(0.01, 0.05))
        
        # Create sample video data
        video_data = {
            "id": video_id,
            "keyword": keyword,
            "title": f"Sample {keyword} video #{i+1}",
            "description": f"This is a sample video for keyword: {keyword}",
            "author": f"sample_creator_{i}",
            "url": f"https://www.tiktok.com/@sample_creator_{i}/video/{video_id}",
            "created_at": (current_time - timedelta(days=random.randint(1, 30))).isoformat(),
            "statistics": {
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "performance_score": (views + likes*2 + comments*3 + shares*4) / 1000
            },
            "is_trending": True,
            "tags": [keyword, "sample", "trending"]
        }
        
        sample_videos.append(video_data)
    
    return sample_videos

def main():
    """Main function to run the TikTok Niche Scraper"""
    
    logger.info("Starting TikTok Niche Scraper with enhanced stealth techniques")
    
    # Check for NO_BROWSER mode - also check if playwright is available
    use_no_browser = NO_BROWSER
    if not use_no_browser:
        try:
            # Check if playwright is properly installed
            import playwright
            from playwright.sync_api import sync_playwright
            logger.info("Playwright is available")
        except (ImportError, Exception) as e:
            logger.warning(f"Playwright is not properly installed or configured: {str(e)}")
            logger.warning("Falling back to NO_BROWSER mode")
            use_no_browser = True
    
    if use_no_browser:
        logger.warning("Running in NO_BROWSER mode - will generate sample data instead of scraping")
        # Create output directories in advance for CI/CD environments
        try:
            # Ensure output directory exists
            output_dir = Path(OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {OUTPUT_DIR}")
        except Exception as e:
            logger.error(f"Failed to create output directory: {str(e)}")
            # Use a fallback directory if the configured one fails
            output_dir = Path("data")
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using fallback output directory: data")
        
        # Process all keywords at once in NO_BROWSER mode
        all_videos = []
        successful_keywords = []
        failed_keywords = []
        
        try:
            # Generate sample data for each keyword
            for keyword in KEYWORDS:
                try:
                    sample_videos = generate_sample_data(keyword, count=5)
                    all_videos.extend(sample_videos)
                    successful_keywords.append(keyword)
                except Exception as e:
                    logger.error(f"Error generating sample data for keyword {keyword}: {str(e)}")
                    failed_keywords.append(keyword)
            
            # Create timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save results
            if SAVE_JSON:
                try:
                    json_file = output_dir / f"sample_data_{timestamp}.json"
                    save_to_json(all_videos, str(json_file))
                    logger.info(f"Saved sample data to JSON: {json_file}")
                except Exception as e:
                    logger.error(f"Failed to save JSON data: {str(e)}")
                
            if SAVE_CSV:
                try:
                    csv_file = output_dir / f"sample_data_{timestamp}.csv"
                    save_to_csv(all_videos, str(csv_file))
                    logger.info(f"Saved sample data to CSV: {csv_file}")
                except Exception as e:
                    logger.error(f"Failed to save CSV data: {str(e)}")
            
            logger.info(f"Generated sample data for {len(successful_keywords)} keywords, total videos: {len(all_videos)}")
            logger.info(f"Successful keywords: {', '.join(successful_keywords)}")
            if failed_keywords:
                logger.warning(f"Failed keywords: {', '.join(failed_keywords)}")
                
        except Exception as e:
            logger.error(f"Unexpected error in NO_BROWSER mode: {str(e)}")
            
        return
    
    logger.info(f"Browser visibility: {'Visible' if BROWSER_VISIBLE else 'Headless'}")
    
    # Process keywords in batches to avoid overwhelming the browser
    batch_size = 2
    keyword_batches = [KEYWORDS[i:i+batch_size] for i in range(0, len(KEYWORDS), batch_size)]
    
    # Initialize results storage
    all_videos = []
    successful_keywords = []
    failed_keywords = []
    
    # Track start time
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    
    try:
        # Process each batch of keywords
        for batch_idx, keyword_batch in enumerate(keyword_batches):
            logger.info(f"Processing keyword batch {batch_idx+1}/{len(keyword_batches)}: {keyword_batch}")
            
            # Initialize browser for this batch
            browser = StealthBrowser(visible=BROWSER_VISIBLE, stealth_level=STEALTH_LEVEL)
            
            try:
                for keyword in keyword_batch:
                    # Add random delay before processing each keyword
                    delay = round(random.uniform(1.5, 3.5), 2)
                    logger.info(f"Adding random delay of {delay} seconds before processing keyword: {keyword}")
                    time.sleep(delay)
                    
                    logger.info(f"Starting scrape for keyword: {keyword}")
                    
                    try:
                        # Discover videos for this keyword using multiple approaches
                        raw_videos = discover_videos(browser, keyword, MAX_VIDEOS_PER_KEYWORD)
                        
                        if not raw_videos:
                            logger.warning(f"No videos found for keyword: {keyword}")
                            failed_keywords.append(keyword)
                            continue
                            
                        logger.info(f"Found {len(raw_videos)} raw videos for keyword: {keyword}")
                        
                        # Process each video
                        keyword_videos = []
                        for raw_video in raw_videos:
                            try:
                                # Extract basic video data
                                video_data = extract_video_data(raw_video, keyword)
                                
                                # Extract statistics and calculate performance metrics
                                stats = extract_statistics(raw_video)
                                video_data['statistics'] = stats
                                
                                # Calculate performance score
                                performance_score = calculate_performance_score(stats)
                                video_data['statistics']['performance_score'] = performance_score
                                
                                # Determine if trending
                                video_is_trending = is_trending(stats, min_views=MIN_VIEWS, min_engagement=MIN_ENGAGEMENT_RATE)
                                video_data['is_trending'] = video_is_trending
                                
                                # Only include trending videos if configured
                                if TRENDING_ONLY and not video_is_trending:
                                    continue
                                    
                                # Add to keyword videos
                                keyword_videos.append(video_data)
                                
                            except Exception as e:
                                logger.error(f"Error processing video for keyword {keyword}: {str(e)}")
                        
                        logger.info(f"Successfully processed {len(keyword_videos)} videos for keyword: {keyword}")
                        
                        # Sort videos by performance if configured
                        if SORT_BY_PERFORMANCE and keyword_videos:
                            keyword_videos.sort(
                                key=lambda x: x['statistics']['performance_score'] 
                                if 'statistics' in x and 'performance_score' in x['statistics'] 
                                else 0,
                                reverse=True
                            )
                            
                        # Add videos to overall results
                        all_videos.extend(keyword_videos)
                        successful_keywords.append(keyword)
                        
                    except Exception as e:
                        logger.error(f"Failed to scrape keyword {keyword}: {str(e)}")
                        failed_keywords.append(keyword)
                
            finally:
                # Close browser after processing batch
                browser.close()
                
            # Optional delay between batches
            if batch_idx < len(keyword_batches) - 1:
                batch_delay = round(random.uniform(3.0, 7.0), 2)
                logger.info(f"Batch {batch_idx+1} complete. Taking a {batch_delay} second break before next batch.")
                time.sleep(batch_delay)
        
        # Limit to maximum total videos if specified and sort by performance
        if MAX_TOTAL_VIDEOS > 0 and len(all_videos) > MAX_TOTAL_VIDEOS:
            logger.info(f"Limiting results to {MAX_TOTAL_VIDEOS} videos with highest performance scores")
            
            # Sort all videos by performance score
            all_videos.sort(
                key=lambda x: x['statistics']['performance_score'] 
                if 'statistics' in x and 'performance_score' in x['statistics'] 
                else 0,
                reverse=True
            )
            
            # Keep only the top videos
            all_videos = all_videos[:MAX_TOTAL_VIDEOS]
        
        # Check if we have any videos
        if not all_videos:
            logger.warning("No videos collected. Exiting without saving data.")
            return
            
        # Create output directory if it doesn't exist
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save results
        if SAVE_JSON:
            json_file = output_dir / f"scraped_videos_{timestamp}.json"
            save_to_json(all_videos, str(json_file))
            
        if SAVE_CSV:
            csv_file = output_dir / f"scraped_videos_{timestamp}.csv"
            save_to_csv(all_videos, str(csv_file))
            
        # Generate trending report
        export_trending_report(all_videos, str(output_dir), f"trending_videos_{timestamp}")
        
        # Update Google Sheets if configured
        if UPDATE_GOOGLE_SHEETS:
            update_google_sheet(all_videos)
            
        # Log completion info
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60.0
        
        logger.info(f"Scraping completed in {duration:.2f} minutes")
        logger.info(f"Total videos collected: {len(all_videos)}")
        logger.info(f"Successful keywords ({len(successful_keywords)}): {', '.join(successful_keywords)}")
        logger.info(f"Failed keywords ({len(failed_keywords)}): {', '.join(failed_keywords)}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 