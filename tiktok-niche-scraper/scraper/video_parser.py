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
import math
from typing import Dict, Any, List, Optional, Tuple, Union

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger()

# Regex patterns for extracting metrics from different formats
VIEW_COUNT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)[KkMm]? views?')
LIKE_COUNT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)[KkMm]? likes?')
COMMENT_COUNT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)[KkMm]? comments?')

def extract_hook(description: str) -> str:
    """
    Extract the hook (first line or sentence) from video description
    
    Args:
        description: The video description text
        
    Returns:
        The extracted hook
    """
    if not description:
        return ""
    
    # First try to get the first line
    lines = description.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        if first_line:
            return first_line[:100]  # Limit to 100 chars
    
    # If no newlines, try first sentence
    sentences = description.split('.')
    if sentences:
        first_sentence = sentences[0].strip()
        if first_sentence:
            return first_sentence[:100]  # Limit to 100 chars
    
    # If all else fails, just return the first 100 chars
    return description[:100].strip()

def extract_hashtags(description: str) -> List[str]:
    """
    Extract hashtags from description
    
    Args:
        description: The video description text
        
    Returns:
        List of hashtags
    """
    if not description:
        return []
    
    # Find all hashtags in the description
    hashtags = re.findall(r'#(\w+)', description)
    
    # Return unique hashtags
    return list(set(hashtags))

def convert_count_to_number(count_str: str) -> int:
    """
    Convert a string like '1.5M' or '10K' to a number
    
    Args:
        count_str: The count string (e.g., '1.5M', '10K')
        
    Returns:
        The count as an integer
    """
    count_str = count_str.strip().lower()
    
    # Extract the number and multiplier
    match = re.match(r'(\d+(?:\.\d+)?)([km])?', count_str)
    if not match:
        return 0
    
    number = float(match.group(1))
    multiplier = match.group(2)
    
    # Apply the appropriate multiplier
    if multiplier == 'k':
        number *= 1000
    elif multiplier == 'm':
        number *= 1000000
    
    return int(number)

def extract_statistics(raw_video: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract view count, like count, comment count, and other statistics from raw video data.
    Handles different formats of TikTok data.
    
    Args:
        raw_video: The raw video data dictionary
        
    Returns:
        Dictionary with extracted statistics
    """
    stats = {}
    
    # Try different paths for statistics
    # Method 1: Direct stats object
    if 'stats' in raw_video:
        direct_stats = raw_video['stats']
        stats['view_count'] = int(direct_stats.get('playCount', 0))
        stats['like_count'] = int(direct_stats.get('diggCount', 0))
        stats['comment_count'] = int(direct_stats.get('commentCount', 0))
        stats['share_count'] = int(direct_stats.get('shareCount', 0))
    
    # Method 2: Nested under itemInfo
    elif 'itemInfo' in raw_video and 'itemStruct' in raw_video['itemInfo']:
        item_struct = raw_video['itemInfo']['itemStruct']
        if 'stats' in item_struct:
            direct_stats = item_struct['stats']
            stats['view_count'] = int(direct_stats.get('playCount', 0))
            stats['like_count'] = int(direct_stats.get('diggCount', 0))
            stats['comment_count'] = int(direct_stats.get('commentCount', 0))
            stats['share_count'] = int(direct_stats.get('shareCount', 0))
    
    # Method 3: Text-based extraction from video.text or videoInfo
    else:
        try:
            # Get text data from different possible locations
            video_text = ""
            if 'text' in raw_video:
                video_text = raw_video['text']
            elif 'videoInfo' in raw_video and 'text' in raw_video['videoInfo']:
                video_text = raw_video['videoInfo']['text']
            elif 'desc' in raw_video:
                video_text = raw_video['desc']
            
            # Extract from video info text
            view_match = VIEW_COUNT_PATTERN.search(video_text)
            like_match = LIKE_COUNT_PATTERN.search(video_text)
            comment_match = COMMENT_COUNT_PATTERN.search(video_text)
            
            if view_match:
                stats['view_count'] = convert_count_to_number(view_match.group(1))
            if like_match:
                stats['like_count'] = convert_count_to_number(like_match.group(1))
            if comment_match:
                stats['comment_count'] = convert_count_to_number(comment_match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting text-based stats: {str(e)}")
    
    # If we still don't have view count, try other possible fields
    if 'view_count' not in stats or stats['view_count'] == 0:
        for field in ['playCount', 'play_count', 'views', 'viewCount']:
            if field in raw_video:
                try:
                    stats['view_count'] = int(raw_video[field])
                    break
                except (ValueError, TypeError):
                    pass
    
    # Set defaults for missing values
    stats.setdefault('view_count', 0)
    stats.setdefault('like_count', 0)
    stats.setdefault('comment_count', 0)
    stats.setdefault('share_count', 0)
    
    # Calculate engagement metrics
    calculate_engagement_metrics(stats)
    
    return stats

def calculate_engagement_metrics(stats: Dict[str, Any]) -> None:
    """
    Calculate engagement rate and performance score from raw statistics.
    Modifies the stats dictionary in place.
    
    Args:
        stats: The statistics dictionary to update
    """
    view_count = stats['view_count']
    like_count = stats['like_count']
    comment_count = stats['comment_count']
    share_count = stats.get('share_count', 0)
    
    # Avoid division by zero
    if view_count > 0:
        # Calculate engagement rate (likes + comments + shares) / views
        engagement = like_count + comment_count + share_count
        stats['engagement_rate'] = round(engagement / view_count, 4)
    else:
        stats['engagement_rate'] = 0
    
    # Calculate performance score
    # Using a logarithmic scale for view score
    if view_count > 0:
        view_score = math.log10(view_count) * 2
    else:
        view_score = 0
    
    # Weighted engagement score
    engagement_score = (
        (like_count * 1.0) + 
        (comment_count * 2.0) + 
        (share_count * 3.0)
    ) / max(view_count, 1) * 10
    
    # Combine for final score
    stats['performance_score'] = round(view_score + engagement_score, 2)

def extract_timestamp(raw_video: Dict[str, Any]) -> str:
    """
    Extract the timestamp from raw video data.
    
    Args:
        raw_video: The raw video data dictionary
        
    Returns:
        Timestamp in ISO format
    """
    # Try different paths for timestamp data
    timestamp = None
    
    # Method 1: Direct timestamp
    if 'createTime' in raw_video:
        try:
            timestamp = int(raw_video['createTime'])
        except (ValueError, TypeError):
            pass
    
    # Method 2: Nested under itemInfo
    elif 'itemInfo' in raw_video and 'itemStruct' in raw_video['itemInfo']:
        item_struct = raw_video['itemInfo']['itemStruct']
        if 'createTime' in item_struct:
            try:
                timestamp = int(item_struct['createTime'])
            except (ValueError, TypeError):
                pass
    
    # Convert timestamp to ISO format
    if timestamp:
        try:
            dt = datetime.datetime.fromtimestamp(timestamp)
            return dt.isoformat()
        except (ValueError, TypeError, OverflowError):
            pass
    
    # If we couldn't get a timestamp, return current time
    return datetime.datetime.now().isoformat()

def is_recent_video(timestamp: str, max_days: int = 30) -> bool:
    """
    Check if a video is recent based on its timestamp.
    
    Args:
        timestamp: ISO format timestamp
        max_days: Maximum age in days to be considered recent
        
    Returns:
        True if the video is recent, False otherwise
    """
    try:
        video_date = datetime.datetime.fromisoformat(timestamp)
        now = datetime.datetime.now()
        age = now - video_date
        return age.days <= max_days
    except (ValueError, TypeError):
        # If we can't parse the timestamp, assume it's not recent
        return False

def is_trending(stats: Dict[str, Any], min_views: int = 10000, min_engagement: float = 0.05) -> bool:
    """
    Determine if a video is trending based on view count and engagement metrics.
    
    Args:
        stats: The video statistics dictionary
        min_views: Minimum view count to be considered trending
        min_engagement: Minimum engagement rate to be considered trending
        
    Returns:
        Boolean indicating if the video is trending
    """
    view_count = stats.get('view_count', 0)
    engagement_rate = stats.get('engagement_rate', 0)
    
    # Check minimum views
    if view_count < min_views:
        return False
    
    # Check minimum engagement rate
    if engagement_rate < min_engagement:
        return False
    
    # All checks passed
    return True

def calculate_performance_score(video: Dict[str, Any]) -> float:
    """
    Calculate a performance score for ranking videos.
    Higher score indicates better performing content.
    
    Args:
        video: The video data dictionary
        
    Returns:
        Performance score as a float
    """
    # Get statistics from the video
    stats = video.get('statistics', {})
    
    # Return the pre-calculated performance score if available
    if 'performance_score' in stats:
        return stats['performance_score']
    
    # Otherwise calculate it directly
    view_count = stats.get('view_count', 0)
    like_count = stats.get('like_count', 0)
    comment_count = stats.get('comment_count', 0)
    share_count = stats.get('share_count', 0)
    
    # Using a logarithmic scale for view score
    if view_count > 0:
        view_score = math.log10(view_count) * 2
    else:
        view_score = 0
    
    # Weighted engagement score
    if view_count > 0:
        engagement_score = (
            (like_count * 1.0) + 
            (comment_count * 2.0) + 
            (share_count * 3.0)
        ) / view_count * 10
    else:
        engagement_score = 0
    
    # Combine for final score
    return round(view_score + engagement_score, 2)

def parse_video_data(raw_video: Dict[str, Any], keyword: str = "") -> Dict[str, Any]:
    """
    Parse and standardize raw video data from different TikTok API formats.
    
    Args:
        raw_video: The raw video data dictionary
        keyword: The keyword used to discover this video
        
    Returns:
        Standardized video data dictionary with all relevant fields
    """
    try:
        # Basic video information
        video = {
            'keyword': keyword,
            'raw_data': raw_video.get('debug_data', {}) if 'debug_data' in raw_video else {}
        }
        
        # Extract video ID from different possible fields
        video_id = None
        for field in ['id', 'videoId', 'video_id', 'itemId']:
            if field in raw_video:
                video_id = raw_video[field]
                break
                
        # Fallback method for nested structures
        if not video_id and 'itemInfo' in raw_video and 'itemStruct' in raw_video['itemInfo']:
            video_id = raw_video['itemInfo']['itemStruct'].get('id')
            
        video['video_id'] = str(video_id) if video_id else f"unknown_{hash(str(raw_video))}"
        
        # Extract video URL
        video_url = None
        for field in ['url', 'shareUrl', 'share_url', 'webVideoUrl']:
            if field in raw_video:
                video_url = raw_video[field]
                break
                
        # Construct URL if not found
        if not video_url and video_id:
            video_url = f"https://www.tiktok.com/@user/video/{video_id}"
            
        video['video_url'] = video_url if video_url else ""
        
        # Extract author information
        author = {}
        if 'author' in raw_video:
            author = raw_video['author']
            video['author'] = author.get('uniqueId', author.get('nickname', 'unknown'))
        elif 'author_id' in raw_video:
            video['author'] = raw_video.get('author_name', raw_video['author_id'])
        elif 'authorInfo' in raw_video:
            author_info = raw_video['authorInfo']
            video['author'] = author_info.get('uniqueId', author_info.get('nickname', 'unknown'))
        elif 'itemInfo' in raw_video and 'itemStruct' in raw_video['itemInfo']:
            author = raw_video['itemInfo']['itemStruct'].get('author', {})
            video['author'] = author.get('uniqueId', author.get('nickname', 'unknown'))
        else:
            video['author'] = 'unknown'
        
        # Extract description
        description = ""
        for field in ['desc', 'description', 'text']:
            if field in raw_video:
                description = raw_video[field]
                break
                
        # Try nested structures
        if not description and 'itemInfo' in raw_video and 'itemStruct' in raw_video['itemInfo']:
            description = raw_video['itemInfo']['itemStruct'].get('desc', '')
            
        video['description'] = description
        
        # Extract hook, hashtags, and music
        video['hook'] = extract_hook(description)
        video['hashtags'] = extract_hashtags(description)
        
        # Extract music
        music = ""
        if 'music' in raw_video:
            music_obj = raw_video['music']
            music = music_obj.get('title', '') + ' - ' + music_obj.get('authorName', '')
        elif 'itemInfo' in raw_video and 'itemStruct' in raw_video['itemInfo']:
            music_obj = raw_video['itemInfo']['itemStruct'].get('music', {})
            music = music_obj.get('title', '') + ' - ' + music_obj.get('authorName', '')
        
        video['music'] = music.strip('- ')
        
        # Extract timestamp
        video['timestamp'] = extract_timestamp(raw_video)
        
        # Extract and calculate statistics
        video['statistics'] = extract_statistics(raw_video)
        
        # Determine if trending
        is_trend = is_trending(video['statistics'])
        video['is_trending'] = is_trend
        
        return video
        
    except Exception as e:
        logger.error(f"Error parsing video data: {str(e)}")
        # Return minimal data to avoid breaking the pipeline
        return {
            'video_id': f"error_{hash(str(raw_video))}",
            'keyword': keyword,
            'description': '',
            'hook': '',
            'hashtags': [],
            'author': 'unknown',
            'timestamp': datetime.datetime.now().isoformat(),
            'statistics': {'view_count': 0, 'like_count': 0, 'comment_count': 0, 'share_count': 0, 
                          'engagement_rate': 0, 'performance_score': 0},
            'is_trending': False
        } 