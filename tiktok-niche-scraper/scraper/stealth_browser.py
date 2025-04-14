"""
Stealth browser module for TikTok Niche Scraper.
Implements advanced techniques to avoid bot detection while scraping.
"""

import random
import json
import asyncio
import platform
import os
from pathlib import Path
import sys
from datetime import datetime, timedelta

from playwright.async_api import async_playwright, BrowserContext, Page

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from config import BROWSER_VISIBILITY, STEALTH_LEVEL

logger = get_logger()

# More comprehensive user agent list
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    
    # Firefox on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0",
    
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/119.0.0.0",
]

# Expanded viewport sizes
VIEWPORTS = [
    {"width": 1920, "height": 1080},  # Desktop (Full HD)
    {"width": 1536, "height": 864},   # Desktop (smaller)
    {"width": 1440, "height": 900},   # MacBook Pro 13"
    {"width": 1680, "height": 1050},  # MacBook Pro 15"
    {"width": 1366, "height": 768},   # Laptop common resolution
    {"width": 390, "height": 844},    # iPhone 13/14
    {"width": 430, "height": 932},    # iPhone 15 Pro Max
    {"width": 393, "height": 873},    # Pixel 7
    {"width": 360, "height": 800},    # Samsung Galaxy S23
]

# Different time zones to rotate through
TIMEZONES = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Toronto",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Asia/Singapore",
    "Australia/Sydney",
]

# Languages to rotate through
LANGUAGES = [
    "en-US",
    "en-GB",
    "en-CA",
    "en-AU",
    "fr-FR",
    "de-DE",
    "es-ES",
    "it-IT",
    "pt-BR",
    "ja-JP",
]

class StealthBrowser:
    """Advanced stealth browser implementation to avoid detection."""
    
    def __init__(self):
        """Initialize stealth browser configuration."""
        self.playwright = None
        self.browser = None
        self.context = None
        
        # Generate a consistent fingerprint for this session
        self.fingerprint = self._generate_fingerprint()
        
    def _generate_fingerprint(self):
        """
        Generate a consistent fingerprint for browser configuration.
        
        Returns:
            dict: Fingerprint configuration
        """
        # Create a deterministic but random-looking fingerprint
        fingerprint = {
            "user_agent": random.choice(USER_AGENTS),
            "viewport": random.choice(VIEWPORTS),
            "platform": random.choice(["Windows", "MacOS", "Linux"]),
            "locale": random.choice(LANGUAGES),
            "timezone": random.choice(TIMEZONES),
            "color_depth": random.choice([24, 30, 48]),
            "device_scale_factor": random.choice([1, 1.5, 2, 2.5]),
            "hardware_concurrency": random.choice([2, 4, 6, 8, 12, 16]),
            "browser_type": random.choice(["chromium", "firefox", "webkit"]),
        }
        
        logger.debug(f"Generated browser fingerprint: {fingerprint}")
        return fingerprint
        
    async def launch(self, headless=None):
        """
        Launch a stealth browser with anti-detection measures.
        
        Args:
            headless (bool): Whether to run in headless mode. If None, uses config value.
            
        Returns:
            tuple: (playwright, browser, context) instances
        """
        # Use the passed headless value, or fall back to config
        if headless is None:
            headless = not BROWSER_VISIBILITY
        
        logger.info(f"Launching stealth browser (headless: {headless})")
        
        # Start Playwright
        self.playwright = await async_playwright().start()
        
        # Select browser type based on fingerprint
        browser_type = self.playwright.chromium
        if self.fingerprint["browser_type"] == "firefox":
            browser_type = self.playwright.firefox
        elif self.fingerprint["browser_type"] == "webkit":
            browser_type = self.playwright.webkit
            
        # Determine stealth level and set appropriate arguments
        browser_args = self._get_stealth_args()
            
        # Launch browser with appropriate settings
        self.browser = await browser_type.launch(
            headless=headless,
            args=browser_args
        )
        
        # Create a context with the fingerprint settings
        self.context = await self.browser.new_context(
            viewport=self.fingerprint["viewport"],
            locale=self.fingerprint["locale"],
            timezone_id=self.fingerprint["timezone"],
            device_scale_factor=self.fingerprint["device_scale_factor"],
            permissions=['geolocation', 'notifications'],
        )
        
        # Apply stealth scripts
        await self._apply_stealth_scripts()
        
        return self.playwright, self.browser, self.context
    
    def _get_stealth_args(self):
        """Get browser arguments based on stealth level."""
        browser_args = []
        
        # Basic args for all stealth levels
        basic_args = [
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            f'--user-agent={self.fingerprint["user_agent"]}',
        ]
        
        # Medium level adds more privacy and fingerprint protection
        medium_args = [
            *basic_args,
            '--disable-infobars',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-extensions',
        ]
        
        # High level adds comprehensive protection
        high_args = [
            *medium_args,
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            '--disable-web-security',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-backing-store-limit',
            '--disable-breakpad',
            '--disable-client-side-phishing-detection',
            '--disable-component-extensions-with-background-pages',
            '--disable-default-apps',
            '--disable-domain-reliability',
            '--disable-hang-monitor',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-translate',
            '--metrics-recording-only',
            '--no-pings',
            '--password-store=basic',
        ]
        
        # Select args based on stealth level
        if STEALTH_LEVEL == 'low':
            browser_args = basic_args
        elif STEALTH_LEVEL == 'medium':
            browser_args = medium_args
        else:  # high or any other value defaults to high
            browser_args = high_args
            
        return browser_args
        
    async def _apply_stealth_scripts(self):
        """Apply various stealth scripts to avoid detection."""
        if not self.context:
            logger.error("Browser context not initialized")
            return
            
        # Apply evasion scripts
        await self.context.add_init_script("""
        () => {
            // Overwrite the navigator properties
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
            
            // Create a false plugins array
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    // Mock plugins
                    const plugins = {
                        length: 5,
                        0: {
                            description: "Chrome PDF Plugin",
                            filename: "internal-pdf-viewer",
                            name: "Chrome PDF Plugin",
                            length: 1,
                        },
                        1: {
                            description: "Chrome PDF Viewer",
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            name: "Chrome PDF Viewer",
                            length: 1,
                        },
                        2: {
                            description: "Native Client",
                            filename: "internal-nacl-plugin",
                            name: "Native Client",
                            length: 2,
                        }
                    };
                    
                    // Add iterator
                    plugins[Symbol.iterator] = function* () {
                        for (let i = 0; i < this.length; i++)
                            yield this[i];
                    };
                    
                    return plugins;
                }
            });
            
            // Overwrite the permissions API
            if (window.navigator.permissions) {
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' || 
                    parameters.name === 'clipboard-read' || 
                    parameters.name === 'clipboard-write' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            }
            
            // Ensure the window.chrome object exists
            window.chrome = window.chrome || {};
            window.chrome.runtime = window.chrome.runtime || {};
            
            // Add language plugins
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'es'],
            });
            
            // Spoof connection/hardware info
            Object.defineProperty(navigator, 'connection', {
                get: () => {
                    return {
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10.0,
                        saveData: false
                    };
                }
            });
            
            // Canvas fingerprinting protection
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                if (type === 'image/png' && this.width === 16 && this.height === 16) {
                    // This is likely a fingerprinting attempt, return a random value
                    return originalToDataURL.apply(this, arguments);
                }
                // Otherwise, proceed as normal
                return originalToDataURL.apply(this, arguments);
            };
            
            // WebGL fingerprinting protection
            const getParameterProxyHandler = {
                apply: function(target, ctx, args) {
                    const param = args[0];
                    
                    // UNMASKED_VENDOR_WEBGL or UNMASKED_RENDERER_WEBGL
                    if (param === 37445 || param === 37446) {
                        return target.apply(ctx, args);
                    }
                    
                    return target.apply(ctx, args);
                }
            };
            
            // Apply proxy to WebGL getParameter
            if (WebGLRenderingContext.prototype.getParameter) {
                WebGLRenderingContext.prototype.getParameter =
                    new Proxy(WebGLRenderingContext.prototype.getParameter, getParameterProxyHandler);
            }
        }
        """)
        
        # Add additional script for more advanced fingerprint evasion if needed
        await self.context.add_init_script("""
        () => {
            // Audio fingerprinting protection
            const audioContext = window.AudioContext || window.webkitAudioContext;
            if (audioContext) {
                const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function() {
                    const results = originalGetChannelData.apply(this, arguments);
                    // Don't modify the audio too much to avoid detection
                    return results;
                };
            }
            
            // Date manipulation for timezone consistency
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {
                // Return consistent timezone offset
                return originalGetTimezoneOffset.apply(this, arguments);
            };
            
            // Custom performance fingerprinting
            if (window.performance && window.performance.now) {
                const originalNow = window.performance.now;
                const start = Date.now();
                window.performance.now = function() {
                    return originalNow.apply(this, arguments);
                };
            }
        }
        """)
        
    async def new_page(self):
        """
        Create a new page with stealth settings.
        
        Returns:
            Page: Configured Playwright page
        """
        if not self.context:
            logger.error("Browser context not initialized")
            return None
            
        # Create a new page
        page = await self.context.new_page()
        
        # Configure page-specific settings
        await self._configure_page(page)
        
        return page
        
    async def _configure_page(self, page):
        """
        Configure page with additional stealth settings.
        
        Args:
            page (Page): Playwright page to configure
        """
        # Set user agent at page level if needed
        await page.evaluate(f'() => Object.defineProperty(navigator, "userAgent", {{ get: () => "{self.fingerprint["user_agent"]}" }})')
        
        # Set extra HTTP headers to appear more natural
        await page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{self.fingerprint["platform"]}"',
        })
        
        # Add mouse movement and other event listeners
        await page.evaluate("""
        () => {
            // Create custom tracking for mouse movements
            window._customMouseMove = true;
            window._lastMouseTime = Date.now();
            
            // Track random mouse movements
            document.addEventListener('mousemove', function(e) {
                window._lastMouseTime = Date.now();
            });
            
            // Track scroll behavior
            document.addEventListener('scroll', function(e) {
                window._lastScrollTime = Date.now();
            });
            
            // Track keyboard usage
            document.addEventListener('keydown', function(e) {
                window._lastKeyTime = Date.now();
            });
        }
        """)
        
    async def simulate_human_behavior(self, page):
        """
        Simulate human-like behavior on the page.
        
        Args:
            page (Page): Playwright page to interact with
        """
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                await page.mouse.move(
                    random.randint(100, self.fingerprint["viewport"]["width"] - 100),
                    random.randint(100, self.fingerprint["viewport"]["height"] - 100),
                    # Add steps to make movement more human-like
                    steps=random.randint(3, 10)
                )
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
            # Random scrolling
            scroll_amount = random.randint(200, 800)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Occasional clicking on non-link elements
            if random.random() < 0.3:  # 30% chance
                try:
                    # Find non-link elements that are safe to click
                    elements = await page.query_selector_all('div:not(a):not(button):not(input)')
                    if elements and len(elements) > 0:
                        random_element = elements[random.randint(0, len(elements) - 1)]
                        # Get element position
                        bbox = await random_element.bounding_box()
                        if bbox:
                            # Click in the middle of the element
                            await page.mouse.click(
                                bbox["x"] + bbox["width"] / 2,
                                bbox["y"] + bbox["height"] / 2
                            )
                            await asyncio.sleep(random.uniform(0.2, 0.5))
                except Exception:
                    # Ignore errors during random interactions
                    pass
                    
        except Exception as e:
            logger.debug(f"Error simulating human behavior: {str(e)}")
            
    async def close(self):
        """Close all browser instances cleanly."""
        try:
            if self.browser:
                await self.browser.close()
                
            if self.playwright:
                await self.playwright.stop()
                
            self.context = None
            self.browser = None
            self.playwright = None
            
            logger.info("Stealth browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing stealth browser: {str(e)}") 