"""
Module to parse and extract data from TikTok videos.
"""

import sys
from pathlib import Path
import re
from datetime import datetime
import logging

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger()

def extract_hook(description, max_words=15):
    """
    Extract the hook/attention grabber from video description.
    
    Args:
        description (str): The video description or caption
        max_words (int): Maximum number of words to consider as the hook
        
    Returns:
        str: The extracted hook text
    """
    if not description:
        return ""
        
    # Clean the description
    cleaned = description.strip()
    
    # Extract the first sentence or first N words
    first_sentence_match = re.match(r'^(.*?[.!?])\s', cleaned)
    
    if first_sentence_match:
        hook = first_sentence_match.group(1)
    else:
        # If no sentence ending found, use the first N words
        words = cleaned.split()
        hook = " ".join(words[:min(len(words), max_words)])
        
    logger.debug(f"Extracted hook: {hook}")
    return hook
    
def extract_hashtags_from_text(text):
    """
    Extract hashtags from text content.
    
    Args:
        text (str): Text to extract hashtags from
        
    Returns:
        list: List of hashtags (without # symbol)
    """
    if not text:
        return []
        
    # Find all hashtags using regex
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags
    
def extract_statistics(raw_video):
    """
    Extract statistical information from a TikTok video.
    
    Args:
        raw_video (dict): Raw video data from TikTok
        
    Returns:
        dict: Extracted statistics
    """
    stats = {}
    
    # Extract view count - critically important for trending videos
    view_count = 0
    try:
        # Different possible locations for view count in the API response
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
    
    # Extract share count
    share_count = 0
    try:
        if 'shareCount' in raw_video:
            share_count = int(raw_video['shareCount'])
        elif 'stats' in raw_video and 'shareCount' in raw_video['stats']:
            share_count = int(raw_video['stats']['shareCount'])
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing share count: {e}")
        
    stats['shares'] = share_count
    
    # Extract favorite count if available
    fav_count = 0
    try:
        if 'collectCount' in raw_video:
            fav_count = int(raw_video['collectCount'])
        elif 'stats' in raw_video and 'collectCount' in raw_video['stats']:
            fav_count = int(raw_video['stats']['collectCount'])
        elif 'stats' in raw_video and 'favoriteCount' in raw_video['stats']:
            fav_count = int(raw_video['stats']['favoriteCount'])
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing favorite count: {e}")
        
    stats['favorites'] = fav_count
    
    return stats

def parse_timestamp(raw_timestamp):
    """
    Parse a timestamp from TikTok into a standardized format.
    
    Args:
        raw_timestamp: Raw timestamp value from TikTok API
        
    Returns:
        str: Formatted timestamp string
    """
    try:
        # Handle different timestamp formats
        if isinstance(raw_timestamp, str):
            if raw_timestamp.isdigit():
                # Unix timestamp in seconds
                timestamp = datetime.fromtimestamp(int(raw_timestamp))
            else:
                # Try to parse the string directly
                timestamp = datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S")
        elif isinstance(raw_timestamp, int):
            # Unix timestamp in seconds or milliseconds
            if raw_timestamp > 1000000000000:  # Milliseconds
                timestamp = datetime.fromtimestamp(raw_timestamp / 1000)
            else:  # Seconds
                timestamp = datetime.fromtimestamp(raw_timestamp)
        else:
            # Default to current time if unable to parse
            timestamp = datetime.now()
            
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.warning(f"Error parsing timestamp: {e}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    Parse raw video data into a structured format.
    
    Args:
        raw_video (dict): Raw video data from TikTok
        
    Returns:
        dict: Structured video data
    """
    # Initialize with default values
    video_data = {
        "url": "",
        "id": "",
        "description": "",
        "author": "",
        "author_id": "",
        "timestamp": "",
        "music": "",
        "hashtags": [],
        "duration": 0,
        "statistics": {}
    }
    
    # Extract basic video information
    try:
        # Video ID
        video_data["id"] = raw_video.get("id", "")
        
        # Video URL
        if "id" in raw_video:
            video_id = raw_video["id"]
            author = raw_video.get("author", {}).get("uniqueId", "")
            video_data["url"] = f"https://www.tiktok.com/@{author}/video/{video_id}"
        
        # Video description
        video_data["description"] = raw_video.get("desc", "")
        
        # Extract hashtags from description
        video_data["hashtags"] = extract_hashtags(video_data["description"])
        
        # Author information
        if "author" in raw_video:
            author_data = raw_video["author"]
            video_data["author"] = author_data.get("uniqueId", "")
            video_data["author_id"] = author_data.get("id", "")
            video_data["author_name"] = author_data.get("nickname", "")
            video_data["author_verified"] = author_data.get("verified", False)
            video_data["author_follower_count"] = author_data.get("followerCount", 0)
        
        # Timestamp
        if "createTime" in raw_video:
            video_data["timestamp"] = parse_timestamp(raw_video["createTime"])
        
        # Music information
        if "music" in raw_video:
            music_data = raw_video["music"]
            video_data["music"] = music_data.get("title", "")
            video_data["music_author"] = music_data.get("authorName", "")
        
        # Video duration
        if "video" in raw_video and "duration" in raw_video["video"]:
            video_data["duration"] = int(raw_video["video"]["duration"])
        
        # Statistics (likes, comments, shares, views)
        video_data["statistics"] = extract_statistics(raw_video)
        
    except Exception as e:
        logger.error(f"Error parsing video data: {e}")
    
    return video_data 