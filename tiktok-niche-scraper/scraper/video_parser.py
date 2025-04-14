"""
Module to parse and extract data from TikTok videos.
"""

import sys
from pathlib import Path
import re
from datetime import datetime, timedelta
import logging
import time
import json

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger()

def extract_hook(description, max_words=15):
    """
    Extract hook from video description.
    
    Args:
        description (str): Video description text
        max_words (int): Maximum number of words to include in hook
        
    Returns:
        str: Extracted hook
    """
    if not description:
        return ""
        
    # Get the first few words as the hook (or the entire description if it's short)
    words = description.split()
    if len(words) <= max_words:
        return description
    
    return " ".join(words[:max_words]) + "..."

def extract_hashtags_from_text(text):
    """
    Extract hashtags from text.
    
    Args:
        text (str): Text to extract hashtags from
        
    Returns:
        list: List of hashtags
    """
    if not text:
        return []
        
    # Find all hashtags in the text
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def extract_statistics(raw_video):
    """
    Extract simplified statistical information from a TikTok video.
    
    Args:
        raw_video (dict): Raw video data from TikTok
        
    Returns:
        dict: Extracted statistics
    """
    stats = {}
    
    # Extract view count
    view_count = 0
    try:
        # Check different possible locations for view count
        if 'playCount' in raw_video:
            view_count = int(raw_video['playCount'])
        elif 'stats' in raw_video and 'playCount' in raw_video['stats']:
            view_count = int(raw_video['stats']['playCount'])
        elif 'stats' in raw_video and 'viewCount' in raw_video['stats']:
            view_count = int(raw_video['stats']['viewCount'])
        elif 'videoData' in raw_video and 'playCount' in raw_video['videoData']:
            view_count = int(raw_video['videoData']['playCount'])
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing view count: {e}")
        
    stats['views'] = view_count
    
    # Extract like count
    like_count = 0
    try:
        if 'diggCount' in raw_video:
            like_count = int(raw_video['diggCount'])
        elif 'stats' in raw_video and 'diggCount' in raw_video['stats']:
            like_count = int(raw_video['stats']['diggCount'])
        elif 'stats' in raw_video and 'likeCount' in raw_video['stats']:
            like_count = int(raw_video['stats']['likeCount'])
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing like count: {e}")
        
    stats['likes'] = like_count
    
    # Extract comment count
    comment_count = 0
    try:
        if 'commentCount' in raw_video:
            comment_count = int(raw_video['commentCount'])
        elif 'stats' in raw_video and 'commentCount' in raw_video['stats']:
            comment_count = int(raw_video['stats']['commentCount'])
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing comment count: {e}")
        
    stats['comments'] = comment_count
    
    return stats

def parse_timestamp(raw_timestamp):
    """
    Parse timestamp from TikTok raw timestamp.
    
    Args:
        raw_timestamp (int): Raw timestamp value
        
    Returns:
        str: Formatted timestamp in ISO format
    """
    try:
        # Convert to datetime object
        if isinstance(raw_timestamp, str) and raw_timestamp.isdigit():
            raw_timestamp = int(raw_timestamp)
        
        dt = datetime.fromtimestamp(raw_timestamp)
        return dt.isoformat()
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing timestamp: {e}")
        return datetime.now().isoformat()

def is_recent_video(timestamp, max_age_days=14):
    """
    Check if a video is recent (within the specified number of days).
    
    Args:
        timestamp (str): Video timestamp in ISO format
        max_age_days (int): Maximum age in days
        
    Returns:
        bool: True if video is within the max age, False otherwise
    """
    try:
        # Convert ISO timestamp to datetime
        video_date = datetime.fromisoformat(timestamp)
        
        # Calculate max age threshold
        max_age_threshold = datetime.now() - timedelta(days=max_age_days)
        
        # Return True if video is newer than the threshold
        return video_date >= max_age_threshold
    except Exception as e:
        logger.warning(f"Error checking if video is recent: {e}")
        return True  # Include by default if we can't determine age

def extract_hashtags(description):
    """
    Extract hashtags from video description.
    
    Args:
        description (str): Video description text
        
    Returns:
        list: List of hashtags
    """
    if not description:
        return []
        
    # Find all hashtags in the description
    hashtags = re.findall(r'#(\w+)', description)
    return hashtags

def parse_video_data(raw_video):
    """
    Parse raw video data into a simplified structured format.
    
    Args:
        raw_video (dict): Raw video data from TikTok
        
    Returns:
        dict: Structured video data
    """
    # Initialize with default values
    video_data = {
        "url": "",
        "description": "",
        "author": "",
        "timestamp": datetime.now().isoformat(),
        "hashtags": [],
        "statistics": {
            "views": 0,
            "likes": 0,
            "comments": 0
        }
    }
    
    # Check if raw_video is a dictionary, otherwise return default values
    if not isinstance(raw_video, dict):
        logger.error(f"Error parsing video data: expected dict, got {type(raw_video).__name__}")
        return video_data
    
    # Extract basic video information
    try:
        # Video URL
        if "id" in raw_video:
            video_id = raw_video["id"]
            author = raw_video.get("author", {})
            if isinstance(author, dict):
                author_id = author.get("uniqueId", "")
                video_data["author"] = author_id
                video_data["url"] = f"https://www.tiktok.com/@{author_id}/video/{video_id}"
            else:
                video_data["url"] = f"https://www.tiktok.com/video/{video_id}"
        
        # Video description
        video_data["description"] = raw_video.get("desc", "")
        
        # Extract hashtags from description
        video_data["hashtags"] = extract_hashtags(video_data["description"])
        
        # Timestamp
        if "createTime" in raw_video:
            video_data["timestamp"] = parse_timestamp(raw_video["createTime"])
        
        # Statistics (likes, comments, views)
        video_data["statistics"] = extract_statistics(raw_video)
        
    except Exception as e:
        logger.error(f"Error parsing video data: {e}")
    
    return video_data

def is_trending(video_data, min_views=1000, min_engagement_rate=0.01):
    """
    Determine if a video is trending based on views and engagement.
    
    Args:
        video_data (dict): Parsed video data
        min_views (int): Minimum number of views to be considered trending
        min_engagement_rate (float): Minimum engagement rate to be considered trending
        
    Returns:
        bool: True if video is trending, False otherwise
    """
    # Check if video has enough views
    if video_data["statistics"]["views"] < min_views:
        return False
    
    # Calculate engagement rate
    views = video_data["statistics"]["views"]
    if views <= 0:
        return False
    
    likes = video_data["statistics"]["likes"]
    comments = video_data["statistics"]["comments"]
    
    engagement = likes + comments
    engagement_rate = engagement / views
    
    # Check if engagement rate meets minimum threshold
    return engagement_rate >= min_engagement_rate

def calculate_performance_score(video_data):
    """
    Calculate a performance score for a video based on views and engagement.
    
    Args:
        video_data (dict): Parsed video data
        
    Returns:
        float: Performance score
    """
    views = video_data["statistics"]["views"]
    likes = video_data["statistics"]["likes"]
    comments = video_data["statistics"]["comments"]
    
    # Basic formula: views + (likes * 2) + (comments * 3)
    # This prioritizes engagement over just views
    score = views + (likes * 2) + (comments * 3)
    
    return score 