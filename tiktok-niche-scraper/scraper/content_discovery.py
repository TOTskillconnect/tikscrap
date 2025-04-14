"""
Content discovery module for TikTok Niche Scraper.
Implements multiple approaches to discover content on TikTok.
"""

import random
import re
from pathlib import Path
import sys
import asyncio
import time

from bs4 import BeautifulSoup
from playwright.async_api import Page

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger()

class ContentDiscovery:
    """Handles different approaches to discover TikTok content."""

    def __init__(self, page: Page, keyword: str):
        """
        Initialize content discovery with a Playwright page and keyword.
        
        Args:
            page (Page): Playwright browser page
            keyword (str): Search keyword or hashtag
        """
        self.page = page
        self.keyword = keyword
        self.clean_keyword = self._normalize_keyword(keyword)
        
    def _normalize_keyword(self, keyword):
        """
        Normalize keyword by removing hashtags and special characters.
        
        Args:
            keyword (str): Original keyword
            
        Returns:
            str: Normalized keyword for URL usage
        """
        # Remove hashtags and replace spaces with URL-friendly format
        return keyword.replace("#", "").replace(" ", "%20")
        
    async def discover_via_search(self, max_videos=50):
        """
        Discover videos through TikTok's search functionality.
        
        Args:
            max_videos (int): Maximum number of videos to discover
            
        Returns:
            list: Discovered video elements or data
        """
        # Prepare search URL
        search_url = f"https://www.tiktok.com/search?q={self.clean_keyword}"
        logger.info(f"Discovering content via search: {search_url}")
        
        try:
            # Navigate to search URL
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            
            # Scroll to load more videos
            await self._scroll_for_content(max_videos // 4)
            
            # Save debug info
            await self._save_debug_info("search")
            
            # Find videos using different selectors
            video_elements = await self._extract_video_elements()
            
            logger.info(f"Discovered {len(video_elements)} videos via search")
            return video_elements
            
        except Exception as e:
            logger.error(f"Error discovering via search: {str(e)}")
            return []
            
    async def discover_via_hashtag(self, max_videos=50):
        """
        Discover videos through TikTok's hashtag pages.
        
        Args:
            max_videos (int): Maximum number of videos to discover
            
        Returns:
            list: Discovered video elements or data
        """
        # Clean hashtag (remove # if present and spaces)
        hashtag = self.clean_keyword.replace("%20", "")
        hashtag_url = f"https://www.tiktok.com/tag/{hashtag}"
        logger.info(f"Discovering content via hashtag: {hashtag_url}")
        
        try:
            # Navigate to hashtag URL
            await self.page.goto(hashtag_url, wait_until="domcontentloaded", timeout=60000)
            
            # Scroll to load more videos
            await self._scroll_for_content(max_videos // 4)
            
            # Save debug info
            await self._save_debug_info("hashtag")
            
            # Find videos using different selectors
            video_elements = await self._extract_video_elements()
            
            logger.info(f"Discovered {len(video_elements)} videos via hashtag")
            return video_elements
            
        except Exception as e:
            logger.error(f"Error discovering via hashtag: {str(e)}")
            return []
            
    async def discover_via_explore(self, max_videos=50):
        """
        Discover videos through TikTok's explore/trending page and then search.
        
        Args:
            max_videos (int): Maximum number of videos to discover
            
        Returns:
            list: Discovered video elements or data
        """
        explore_url = "https://www.tiktok.com/explore"
        logger.info(f"Discovering content via explore: {explore_url}")
        
        try:
            # First visit the explore page to look more natural
            await self.page.goto(explore_url, wait_until="domcontentloaded", timeout=60000)
            
            # Do some random interactions to appear natural
            await self._perform_random_interactions()
            
            # Then search for our keyword from the explore page
            await self.page.fill('input[type="search"], [placeholder*="Search"], [data-e2e="search-box"]', self.keyword)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await self.page.press('input[type="search"], [placeholder*="Search"], [data-e2e="search-box"]', 'Enter')
            
            # Wait for results to load
            await asyncio.sleep(3)
            
            # Scroll to load more videos
            await self._scroll_for_content(max_videos // 4)
            
            # Save debug info
            await self._save_debug_info("explore")
            
            # Find videos using different selectors
            video_elements = await self._extract_video_elements()
            
            logger.info(f"Discovered {len(video_elements)} videos via explore")
            return video_elements
            
        except Exception as e:
            logger.error(f"Error discovering via explore: {str(e)}")
            return []

    async def discover_via_user_profile(self, max_videos=50):
        """
        Discover content by finding top creators for the keyword and visiting their profiles.
        
        Args:
            max_videos (int): Maximum number of videos to discover
            
        Returns:
            list: Discovered video elements or data
        """
        # First use search to find relevant users
        search_url = f"https://www.tiktok.com/search/user?q={self.clean_keyword}"
        logger.info(f"Searching for users: {search_url}")
        
        try:
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            
            # Find user links
            user_links = await self.page.query_selector_all('a[href*="/@"]')
            
            if not user_links or len(user_links) == 0:
                logger.warning("No users found")
                return []
                
            # Visit a random user from the top results
            random_index = random.randint(0, min(5, len(user_links)-1)) if len(user_links) > 0 else 0
            
            if len(user_links) > random_index:
                user_href = await user_links[random_index].get_attribute('href')
                username = user_href.split('/@')[-1].split('?')[0]
                
                logger.info(f"Visiting user profile: {username}")
                
                # Visit user profile
                if user_href:
                    if not user_href.startswith('http'):
                        user_href = f"https://www.tiktok.com{user_href}"
                    
                    await self.page.goto(user_href, wait_until="domcontentloaded", timeout=60000)
                    
                    # Scroll to load more videos
                    await self._scroll_for_content(max_videos // 4)
                    
                    # Save debug info
                    await self._save_debug_info(f"user_{username}")
                    
                    # Find videos using different selectors
                    video_elements = await self._extract_video_elements()
                    
                    logger.info(f"Discovered {len(video_elements)} videos via user profile")
                    return video_elements
            
            return []
            
        except Exception as e:
            logger.error(f"Error discovering via user profile: {str(e)}")
            return []
            
    async def _extract_video_elements(self):
        """
        Extract video elements from the current page using multiple selector approaches.
        
        Returns:
            list: Video elements found on the page
        """
        # Define different sets of selectors to try
        video_selectors = [
            # Search results selectors
            '.tiktok-1soki6-DivItemContainer', 
            '.css-1as5cen-DivWrapper',
            '[data-e2e="search_video-item"]',
            '.search-item-container',
            
            # Feed/user profile selectors
            '.video-feed-item',
            '[data-e2e="user-post-item"]',
            '[data-e2e="video-music-item"]',
            
            # Hashtag page selectors
            '[data-e2e="challenge-item"]',
            '.challenge-video-container',
            
            # Generic video containers
            'div[class*="DivContainer"] > a[href*="/video/"]',
            'div[class*="Video"] > a[href*="/video/"]'
        ]
        
        # Try each selector
        for selector in video_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    logger.info(f"Found {len(elements)} videos with selector: {selector}")
                    return elements
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {str(e)}")
        
        # If no elements found through selectors, try analyzing the page content
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for video links in the HTML
        video_links = soup.find_all('a', href=re.compile(r'/video/'))
        if video_links and len(video_links) > 0:
            logger.info(f"Found {len(video_links)} video links in HTML")
            return video_links
            
        logger.warning("No video elements found on the page")
        return []
        
    async def _scroll_for_content(self, scroll_count=5):
        """
        Scroll the page to load more content with human-like behavior.
        
        Args:
            scroll_count (int): Number of scrolls to perform
        """
        logger.info(f"Scrolling page {scroll_count} times to load more content")
        
        for i in range(scroll_count):
            # Random scroll amount
            scroll_amount = random.randint(300, 1000)
            
            # Randomly choose between smooth scrolling and jumps
            if random.random() < 0.7:  # 70% smooth scrolling
                # Smooth scroll in smaller increments
                increment = scroll_amount // random.randint(3, 8)
                for j in range(0, scroll_amount, increment):
                    await self.page.evaluate(f"window.scrollBy(0, {increment})")
                    await asyncio.sleep(random.uniform(0.05, 0.2))
            else:
                # Jump scroll
                await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            
            # Random pause between scrolls
            await asyncio.sleep(random.uniform(0.7, 3.0))
            
            # Occasionally wiggle mouse
            if random.random() < 0.4:
                await self.page.mouse.move(
                    random.randint(100, 1000),
                    random.randint(100, 700)
                )
                
            # Occasionally hover over an item
            if random.random() < 0.3:
                try:
                    elements = await self.page.query_selector_all('div[class*="Div"], a, img, video')
                    if elements and len(elements) > 0:
                        random_element = elements[random.randint(0, len(elements) - 1)]
                        await random_element.hover()
                        await asyncio.sleep(random.uniform(0.3, 1.2))
                except Exception:
                    pass
    
    async def _perform_random_interactions(self):
        """Perform random interactions to appear more human-like."""
        try:
            # Random pause
            await asyncio.sleep(random.uniform(1, 3))
            
            # Get clickable elements
            elements = await self.page.query_selector_all('a, button, div[role="button"]')
            
            if elements and len(elements) > 0:
                # Click on 1-2 random elements that are likely safe (avoid specifics like login buttons)
                for _ in range(random.randint(1, 2)):
                    try:
                        random_element = elements[random.randint(0, len(elements) - 1)]
                        element_text = await random_element.text_content()
                        
                        # Skip if it contains certain words (login, signup, etc.)
                        skip_words = ['login', 'sign', 'download', 'install', 'get app']
                        if element_text and any(word in element_text.lower() for word in skip_words):
                            continue
                        
                        # Random delay before click
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Hover first
                        await random_element.hover()
                        await asyncio.sleep(random.uniform(0.2, 0.8))
                        
                        # Click
                        await random_element.click()
                        
                        # Wait a bit after clicking
                        await asyncio.sleep(random.uniform(1, 3))
                        
                        # Go back if we navigated away
                        if random.random() < 0.8:  # 80% chance to go back
                            await self.page.go_back()
                            await asyncio.sleep(random.uniform(1, 2))
                    except Exception:
                        # Ignore errors from random interactions
                        pass
        except Exception as e:
            logger.debug(f"Error during random interactions: {str(e)}")
            
    async def _save_debug_info(self, approach_name):
        """
        Save debug information for the current page.
        
        Args:
            approach_name (str): Name of the discovery approach for file naming
        """
        try:
            debug_dir = Path(__file__).parent.parent / "data"
            debug_dir.mkdir(exist_ok=True)
            
            # Take screenshot
            timestamp = int(time.time())
            screenshot_path = debug_dir / f"tiktok_{approach_name}_{self.clean_keyword}_{timestamp}.png"
            await self.page.screenshot(path=str(screenshot_path))
            
            # Save HTML
            html_path = debug_dir / f"tiktok_{approach_name}_{self.clean_keyword}_{timestamp}.html"
            content = await self.page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.debug(f"Saved debug info for {approach_name} approach")
        except Exception as e:
            logger.error(f"Error saving debug info: {str(e)}")
            
    async def execute_best_approach(self, max_videos=50):
        """
        Try different discovery approaches and use the one that yields the most results.
        
        Args:
            max_videos (int): Maximum number of videos to discover
            
        Returns:
            list: Video elements from the best approach
        """
        # Define approaches in priority order
        approaches = [
            ("search", self.discover_via_search),
            ("hashtag", self.discover_via_hashtag),
            ("user_profile", self.discover_via_user_profile),
            ("explore", self.discover_via_explore)
        ]
        
        # Shuffle approaches for unpredictability
        random.shuffle(approaches)
        
        results = []
        best_approach_name = None
        
        # Try each approach
        for approach_name, approach_func in approaches:
            logger.info(f"Trying {approach_name} approach for '{self.keyword}'")
            
            # Execute the approach
            approach_results = await approach_func(max_videos)
            
            # If we got good results, keep them
            if approach_results and len(approach_results) > len(results):
                results = approach_results
                best_approach_name = approach_name
                
                # If we got enough results, stop trying
                if len(results) >= max_videos / 2:
                    break
        
        logger.info(f"Best approach for '{self.keyword}' was {best_approach_name} with {len(results)} results")
        return results 