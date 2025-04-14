"""
Configuration settings for TikTok scraper.
"""

# Browser settings
HEADLESS = False  # Set to True for production, False for debugging
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

# Scraping behavior
SCROLL_PAUSE_TIME = 2.0  # Time to wait between scrolls
MAX_SCROLL_COUNT = 10  # Maximum number of scrolls per search
MAX_VIDEOS_PER_KEYWORD = 50  # Maximum videos to scrape per keyword
PAGE_LOAD_TIMEOUT = 30  # Seconds to wait for page to load
ELEMENT_TIMEOUT = 10  # Seconds to wait for elements to appear

# Output settings
OUTPUT_DIRECTORY = "data"

# Trending video settings
TRENDING_ONLY = True  # Whether to only keep trending videos
MIN_VIEWS = 10000  # Minimum view count for a trending video
MIN_ENGAGEMENT_RATE = 0.05  # Minimum engagement rate (likes + comments + shares) / views
SORT_BY_PERFORMANCE = True  # Sort output by performance score
MAX_TOTAL_VIDEOS = 100  # Maximum videos to keep per scraping session across all keywords

# Performance metrics weights
WEIGHTS = {
    "views": 1.0,
    "likes": 2.0, 
    "comments": 3.0,
    "shares": 4.0,
    "favorites": 1.5
}

# Search keywords
KEYWORDS = [
    "fitness tips",
    "workout routine",
    "healthy recipes",
    "weight loss",
    "home workout"
]

# Proxies (optional)
PROXIES = []

# API credentials (if using API method)
API_KEY = ""
API_SECRET = ""

# Google Sheets integration (optional)
GOOGLE_SHEETS_ENABLED = False
GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"
GOOGLE_SHEETS_ID = "" 