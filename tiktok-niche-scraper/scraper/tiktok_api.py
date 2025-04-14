"""
Module to handle interactions with TikTok's website or API.
Uses enhanced stealth techniques and multiple content discovery approaches.
"""

import asyncio
import json
import random
import re
import sys
import time
from pathlib import Path
import os

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError

sys.path.append(str(Path(__file__).parent.parent))
from config import REQUEST_DELAY
from utils.logger import get_logger
from scraper.stealth_browser import StealthBrowser
from scraper.content_discovery import ContentDiscovery

logger = get_logger()

# Flag to control whether to use mock data or real scraping
USE_MOCK_DATA = False  # Always use real scraping, no mock data

async def get_videos_for_tag(keyword, max_videos=50):
    """
    Fetches videos for a given TikTok hashtag/keyword using enhanced scraping approaches.
    
    Uses multiple discovery methods and advanced stealth techniques.
    
    Args:
        keyword (str): The keyword or hashtag to search for.
        max_videos (int): Maximum number of videos to fetch.
        
    Returns:
        list: List of video data dictionaries.
    """
    logger.info(f"Fetching videos for keyword: {keyword}")
    
    # Never use mock data, always scrape real content
    videos = []
    
    try:
        # Initialize stealth browser
        stealth = StealthBrowser()
        # Use visible browser for monitoring the scraping process
        playwright, browser, context = await stealth.launch(headless=False)
        
        try:
            # Create a stealth page
            page = await stealth.new_page()
            
            # Enable JS console logging for debugging
            page.on("console", lambda msg: logger.debug(f"BROWSER CONSOLE: {msg.text}"))
            
            # Add random delays to mimic human behavior
            await page.route("**/*", lambda route: asyncio.ensure_future(
                route_with_delay(route, min_delay=100, max_delay=1000)
            ))
            
            # Initialize content discovery
            discovery = ContentDiscovery(page, keyword)
            
            # Execute content discovery using the best approach
            video_elements = await discovery.execute_best_approach(max_videos)
            
            # Parse the discovered video elements
            if video_elements:
                logger.info(f"Processing {len(video_elements)} video elements")
                
                # Get page content for processing
                content = await page.content()
                
                # Parse the content
                videos = await parse_video_data(page, video_elements, content, keyword)
                
                # If we didn't get enough videos, try other approaches
                if len(videos) < max_videos * 0.5:
                    logger.info(f"Only found {len(videos)} videos, trying additional approaches")
                    
                    # Try JSON data extraction as backup
                    json_videos = await extract_videos_from_json(content, keyword)
                    if json_videos:
                        # Merge lists, avoiding duplicates by URL
                        existing_urls = {v["url"] for v in videos}
                        for jv in json_videos:
                            if jv["url"] not in existing_urls:
                                videos.append(jv)
                                existing_urls.add(jv["url"])
                    
                    logger.info(f"Total videos after additional approaches: {len(videos)}")
                
                # Limit to max_videos
                videos = videos[:max_videos]
                
            # Simulate more human behavior before closing
            await stealth.simulate_human_behavior(page)
                
        except Exception as e:
            logger.error(f"Error during TikTok scraping: {str(e)}")
            
        finally:
            # Close browser 
            await stealth.close()
        
        # Return whatever real videos we found, even if it's an empty list
        logger.info(f"Successfully fetched {len(videos)} videos for keyword: {keyword}")
        return videos
            
    except Exception as e:
        logger.error(f"Error fetching videos for {keyword}: {str(e)}")
        # No fallback to mock data, return empty list if there was an error
        return []

async def parse_video_data(page, video_elements, content, keyword):
    """
    Parse video elements into structured data.
    
    Args:
        page (Page): Playwright page object
        video_elements (list): Video elements from content discovery
        content (str): HTML content of the page
        keyword (str): Original search keyword
        
    Returns:
        list: Parsed video data
    """
    videos = []
    soup = BeautifulSoup(content, "html.parser")
    
    try:
        for i, element in enumerate(video_elements):
            try:
                # For Playwright elements, extract attributes
                if hasattr(element, 'get_attribute'):
                    # This is a Playwright element
                    video_data = await extract_video_from_playwright_element(page, element, keyword)
                else:
                    # This is a BeautifulSoup element
                    video_data = extract_video_from_bs_element(element, soup, keyword)
                
                if video_data and "url" in video_data and video_data["url"]:
                    videos.append(video_data)
                    logger.debug(f"Extracted video {i+1}/{len(video_elements)}")
                
            except Exception as e:
                logger.error(f"Error extracting data from video {i+1}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error parsing video data: {str(e)}")
        
    return videos

async def extract_video_from_playwright_element(page, element, keyword):
    """
    Extract video data from a Playwright element.
    
    Args:
        page (Page): Playwright page
        element: Playwright element
        keyword (str): Search keyword
        
    Returns:
        dict: Video data
    """
    # Extract video URL
    video_url = ""
    try:
        # Try to find a link element within the video container
        url_element = await element.query_selector('a[href*="/video/"]')
        if url_element:
            href = await url_element.get_attribute('href')
            video_url = "https://www.tiktok.com" + href if not href.startswith('http') else href
        else:
            # Check if the element itself is a link
            href = await element.get_attribute('href')
            if href and "/video/" in href:
                video_url = "https://www.tiktok.com" + href if not href.startswith('http') else href
    except Exception:
        pass
        
    # Skip if no URL found
    if not video_url:
        return None
        
    # Extract description/caption
    description = ""
    try:
        # Try multiple potential description selectors
        desc_selectors = [
            '[data-e2e="video-desc"]', 
            '.video-desc', 
            '.search-item-desc',
            'p.desc',
            '[class*="DivVideoDesc"]'
        ]
        
        for desc_selector in desc_selectors:
            desc_element = await element.query_selector(desc_selector)
            if desc_element:
                description = await desc_element.text_content()
                description = description.strip()
                break
    except Exception:
        pass
        
    # Extract author
    author = ""
    try:
        # Try multiple potential author selectors
        author_selectors = [
            'a[data-e2e="video-author-avatar"]', 
            'a[href*="/@"]',
            '[data-e2e="search-username"]',
            '[class*="author-uniqueId"]'
        ]
        
        for author_selector in author_selectors:
            author_element = await element.query_selector(author_selector)
            if author_element:
                href = await author_element.get_attribute('href')
                if href and "/@" in href:
                    author = href.split('/@')[-1].split('?')[0]
                if not author:
                    author_text = await author_element.text_content()
                    author = author_text.strip()
                break
    except Exception:
        pass
        
    # Extract hashtags from description
    hashtags = extract_hashtags_from_text(description)
    
    # Extract stats (views, likes, etc.) if available
    stats = {}
    try:
        # Try multiple potential stats selectors
        stats_selectors = [
            '[data-e2e="video-stats"]', 
            '[class*="DivStatistics"]',
            '.video-stats',
            '.engagement-panel'
        ]
        
        for stats_selector in stats_selectors:
            stats_element = await element.query_selector(stats_selector)
            if stats_element:
                # Try to extract likes, comments, shares
                try:
                    like_elem = await stats_element.query_selector('[data-e2e="like-count"], [class*="like-count"]')
                    if like_elem:
                        like_text = await like_elem.text_content()
                        stats['likes'] = parse_count(like_text)
                except Exception:
                    pass
                    
                try:
                    comment_elem = await stats_element.query_selector('[data-e2e="comment-count"], [class*="comment-count"]')
                    if comment_elem:
                        comment_text = await comment_elem.text_content()
                        stats['comments'] = parse_count(comment_text)
                except Exception:
                    pass
                    
                try:
                    share_elem = await stats_element.query_selector('[data-e2e="share-count"], [class*="share-count"]')
                    if share_elem:
                        share_text = await share_elem.text_content()
                        stats['shares'] = parse_count(share_text)
                except Exception:
                    pass
                
                break
    except Exception:
        pass
        
    # Timestamp (might be difficult to get from list view)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Create video data object
    video_data = {
        "url": video_url,
        "description": description,
        "author": author if author.startswith('@') else f'@{author}',
        "timestamp": timestamp,
        "hashtags": hashtags,
        "keyword": keyword,
        "statistics": stats
    }
    
    return video_data

def extract_video_from_bs_element(element, soup, keyword):
    """
    Extract video data from a BeautifulSoup element.
    
    Args:
        element: BeautifulSoup element
        soup: BeautifulSoup object of the page
        keyword (str): Search keyword
        
    Returns:
        dict: Video data
    """
    # Extract video URL
    video_url = ""
    if element.name == 'a' and '/video/' in element.get('href', ''):
        href = element.get('href', '')
        video_url = "https://www.tiktok.com" + href if not href.startswith('http') else href
    else:
        url_element = element.select_one('a[href*="/video/"]')
        if url_element:
            href = url_element.get('href', '')
            video_url = "https://www.tiktok.com" + href if not href.startswith('http') else href
    
    # Skip if no URL found
    if not video_url:
        return None
    
    # Extract author from URL or other elements
    author = ""
    if "/@" in video_url:
        author = video_url.split("/@")[1].split("/")[0]
    else:
        # Try to find author in parent elements
        author_elem = element.select_one('[class*="author"], [class*="nickname"], a[href*="/@"]')
        if author_elem:
            if author_elem.get('href') and '/@' in author_elem.get('href'):
                author = author_elem.get('href').split('/@')[-1].split('?')[0]
            else:
                author = author_elem.text.strip()
    
    # Extract description
    description = ""
    desc_elem = element.select_one('[class*="desc"], [class*="title"], [class*="caption"]')
    if desc_elem:
        description = desc_elem.text.strip()
    
    # Extract hashtags
    hashtags = extract_hashtags_from_text(description)
    
    # Stats are hard to get reliably from HTML, so leaving empty
    stats = {}
    
    # Create timestamp
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Create video data
    video_data = {
        "url": video_url,
        "description": description,
        "author": author if author.startswith('@') else f'@{author}',
        "timestamp": timestamp,
        "hashtags": hashtags,
        "keyword": keyword,
        "statistics": stats
    }
    
    return video_data

async def extract_videos_from_json(content, keyword):
    """
    Extract videos from JSON data embedded in the page.
    
    Args:
        content (str): HTML page content
        keyword (str): Search keyword
        
    Returns:
        list: Video data extracted from JSON
    """
    videos = []
    try:
        # Find all script tags
        soup = BeautifulSoup(content, "html.parser")
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string and ('SIGI_STATE' in script.string or 'itemList' in script.string or '__UNIVERSAL_DATA_FOR_REHYDRATION__' in script.string):
                try:
                    # Extract JSON data
                    json_str = script.string.strip()
                    
                    # Find JSON object pattern in the script content
                    json_match = re.search(r'({.+})', json_str)
                    if json_match:
                        json_data = json.loads(json_match.group(1))
                        
                        # Extract video data from JSON
                        if 'ItemModule' in json_data:
                            video_data = json_data['ItemModule']
                            
                            # Process each video
                            for video_id, data in video_data.items():
                                try:
                                    author_id = data.get('authorId', '')
                                    nickname = data.get('nickname', '') or data.get('author', '') or author_id
                                    
                                    video = {
                                        "url": f"https://www.tiktok.com/@{author_id}/video/{video_id}",
                                        "description": data.get('desc', ''),
                                        "author": f"@{nickname}",
                                        "timestamp": data.get('createTime', time.time()),
                                        "hashtags": extract_hashtags_from_text(data.get('desc', '')),
                                        "keyword": keyword,
                                        "statistics": {
                                            "likes": data.get('diggCount', 0),
                                            "comments": data.get('commentCount', 0),
                                            "shares": data.get('shareCount', 0),
                                            "views": data.get('playCount', 0)
                                        }
                                    }
                                    videos.append(video)
                                except Exception as e:
                                    logger.error(f"Error processing video from JSON: {str(e)}")
                        
                        # If we found videos, return them
                        if videos:
                            logger.info(f"Extracted {len(videos)} videos from JSON data")
                            return videos
                except Exception as e:
                    logger.error(f"Error parsing JSON from script: {str(e)}")
    except Exception as e:
        logger.error(f"Error extracting videos from JSON: {str(e)}")
        
    return videos

async def route_with_delay(route, min_delay=100, max_delay=1000):
    """Add random delay to each request to mimic human-like behavior."""
    # Apply random delays only to certain types of requests
    if route.request.resource_type in ['document', 'xhr', 'fetch', 'script']:
        # Add random delay
        await asyncio.sleep(random.randint(min_delay, max_delay) / 1000)
    
    # Continue with the request
    await route.continue_()

def extract_hashtags_from_text(text):
    """Extract hashtags from text content."""
    if not text:
        return []
        
    # Find all hashtags using regex
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def parse_count(count_text):
    """Parse count text with K, M suffixes into numbers."""
    if not count_text:
        return 0
        
    count_text = count_text.strip().lower()
    
    if 'k' in count_text:
        return int(float(count_text.replace('k', '')) * 1000)
    elif 'm' in count_text:
        return int(float(count_text.replace('m', '')) * 1000000)
    else:
        # Remove any non-numeric characters
        count_text = re.sub(r'[^\d.]', '', count_text)
        try:
            return int(float(count_text)) if count_text else 0
        except:
            return 0

def generate_mock_data(keyword, count=10):
    """
    Generate mock TikTok video data for development purposes.
    
    Args:
        keyword (str): The keyword to generate data for
        count (int): Number of mock videos to generate
        
    Returns:
        list: List of mock video data dictionaries
    """
    logger.info(f"Generating {count} mock videos for keyword: {keyword}")
    
    # Keyword-specific content to make the mock data more realistic
    mock_content = {
        'budgeting': {
            'descriptions': [
                "How I budget my $3000 salary #budgeting #finance",
                "This budgeting method saved me $500 last month #budgeting #savemoney",
                "3 budgeting tips that changed my financial life #budgeting #personalfinance"
            ],
            'authors': ['@budgetqueen', '@financebro', '@moneytips'],
            'hashtags': ['budgeting', 'finance', 'money', 'savemoney', 'personalfinance']
        },
        'wealth': {
            'descriptions': [
                "How to build wealth in your 20s #wealth #investing",
                "5 wealth building habits millionaires follow #wealth #millionaire",
                "Start your wealth journey with these simple steps #wealth #finance"
            ],
            'authors': ['@wealthtips', '@millionairemindset', '@financefreedom'],
            'hashtags': ['wealth', 'investing', 'money', 'millionaire', 'finance']
        },
        'savings': {
            'descriptions': [
                "How I saved $10k in 6 months #savings #moneytips",
                "3 apps that helped me automate my savings #savings #finance",
                "The 50/30/20 rule changed my savings game #savings #budget"
            ],
            'authors': ['@savingexpert', '@moneysaver', '@frugalliving'],
            'hashtags': ['savings', 'moneytips', 'finance', 'budget', 'savemoney']
        }
    }
    
    # Create default content for keywords not specifically defined
    default_content = {
        'descriptions': [f"Amazing tips about {keyword} #trending", f"How to use {keyword} effectively #tips"],
        'authors': ['@creator1', '@creator2', '@trendsetter'],
        'hashtags': [keyword.replace(" ", ""), 'trending', 'fyp', 'viral']
    }
    
    # Use keyword-specific content if available, otherwise use default
    for key in mock_content.keys():
        if key in keyword.lower():
            content = mock_content[key]
            break
    else:
        content = default_content
    
    # Generate random mock videos
    videos = []
    for i in range(min(count, 15)):  # Limit to 15 mock videos max
        # Create random timestamp within the last month
        random_days = random.randint(0, 30)
        random_hours = random.randint(0, 23)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", 
                                 time.gmtime(time.time() - random_days*86400 - random_hours*3600))
        
        # Random view counts, likes, etc.
        views = random.randint(1000, 1000000)
        likes = random.randint(100, views//10)
        comments = random.randint(10, likes//5)
        shares = random.randint(5, likes//10)
        
        # Select random content from our templates
        description = random.choice(content['descriptions'])
        author = random.choice(content['authors'])
        
        # Create random set of hashtags for this video
        video_hashtags = []
        for _ in range(random.randint(2, 5)):
            tag = random.choice(content['hashtags'])
            if tag not in video_hashtags:
                video_hashtags.append(tag)
                
        # Create video ID
        video_id = f"{random.randint(1000000, 9999999)}"
        
        # Create a mock video object
        video = {
            "url": f"https://www.tiktok.com/{author}/video/{video_id}",
            "description": description,
            "author": author,
            "timestamp": timestamp,
            "hashtags": video_hashtags,
            "keyword": keyword,
            "statistics": {
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares
            }
        }
        
        videos.append(video)
        
    return videos 