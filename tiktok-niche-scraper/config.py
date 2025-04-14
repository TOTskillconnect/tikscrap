"""
Configuration settings for the TikTok Niche Scraper.
"""

# Search keywords/niches to scrape
KEYWORDS = [
    "budgeting",
    "budget tracker", 
    "wealth building",
    "personal finance",
    "investment tips",
    "money saving",
    "financial freedom",
    "passive income",
    "side hustle",
    "debt free"
]

# Scraping settings
MAX_VIDEOS_PER_KEYWORD = 50  # Maximum number of videos to collect per keyword
REQUEST_DELAY = 2  # seconds between requests
CONCURRENT_KEYWORDS = 2  # Process 2 keywords at a time for better efficiency
MIN_VIDEOS_REQUIRED = 5  # Minimum number of videos required for a successful scrape

# Trending content filtering 
TRENDING_ONLY = True  # Only collect trending/viral videos
MIN_VIEWS = 10000  # Minimum views to consider a video trending
MIN_ENGAGEMENT_RATE = 0.05  # Minimum engagement rate (higher threshold for truly trending content)
SORT_BY_PERFORMANCE = True  # Sort videos by performance metrics
COLLECT_VIEW_COUNT = True  # Always collect view count data
MAX_TOTAL_VIDEOS = 100  # Maximum videos to keep per scraping session (keep top 100)
MAX_VIDEO_AGE_DAYS = 30  # Only collect videos from the past two weeks

# Content discovery settings
PREFERRED_DISCOVERY_METHODS = ['search', 'hashtag', 'explore']  # Use multiple discovery methods
ENABLE_MULTIPLE_DISCOVERY_METHODS = True  # Try multiple methods if one fails
EXTRACTION_BACKUP_METHODS = True  # Use backup extraction methods if primary fails

# Stealth browser settings
BROWSER_VISIBLE = True  # Set to True to see the browser window, False for headless mode
STEALTH_LEVEL = 3  # 1-3, where 3 is the most advanced anti-detection measures

# API Settings
USE_API = False  # Set to True to use the TikTok API instead of scraping
API_KEY = ""     # Your TikTok API key if using the API method

# Output settings
OUTPUT_FORMATS = ['json', 'csv']  # Options: 'json', 'csv', 'google_sheets'
OUTPUT_DIR = 'data'
SAVE_JSON = True
SAVE_CSV = True
UPDATE_GOOGLE_SHEETS = False

# Scheduler settings
SCHEDULER_ENABLED = True
SCHEDULE_INTERVAL = 'daily'
SCHEDULE_HOUR = 3
SCHEDULE_MINUTE = 0
SCHEDULE_DAYS = ['monday', 'wednesday', 'friday']
CUSTOM_SCHEDULE = '0 */12 * * *'
SCHEDULER_MAX_INSTANCES = 1

# Google Sheets settings
GOOGLE_SHEETS_ENABLED = False
GOOGLE_SHEETS_CREDENTIALS_FILE = "client_secret.json"
GOOGLE_SHEETS_ID = ""
GOOGLE_SHEETS_RANGE = "A1:Z1000"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "scraper.log"

# Debug settings
SAVE_DEBUG_INFO = True
USE_MOCK_DATA = False

# Retry Settings
MAX_RETRIES = 3  # Maximum number of retries per keyword
RETRY_DELAY = 5  # Delay between retries in seconds

# Advanced Settings
PROXY_ENABLED = False  # Set to True to use proxy
PROXY_LIST = []  # List of proxy servers to rotate through
RANDOM_USER_AGENTS = True  # Set to True to use random user agents
USER_AGENT_LIST = []  # List of user agents to rotate through (if empty, will use built-in list)
CONNECTION_TIMEOUT = 30  # Connection timeout in seconds
CONTINUE_ON_ERROR = True  # Continue scraping on error
DEBUG_MODE = False  # Set to True to enable debug mode (more verbose logging)
SAVE_HTML = False  # Save HTML for debugging purposes 