"""
Configuration settings for the TikTok Niche Scraper.
"""

# Search keywords/niches to scrape
KEYWORDS = [
    'budgeting',
    'budget tracker',
    'budgeting tips',
    'budgeting hacks',
    'budgeting app',
    'budgeting tools',
    'budgeting apps',
    'budgeting for beginners',
    'budgeting for beginners tips',
    'budgeting for beginners hacks',
    'budgeting for beginners app',
    'budgeting for beginners tools',
    'budgeting for beginners apps',
]

# Scraping settings
MAX_VIDEOS_PER_KEYWORD = 15  # Maximum top videos to collect per keyword
REQUEST_DELAY = 2  # seconds between requests
CONCURRENT_KEYWORDS = 2  # How many keywords to process concurrently (set to 1 for sequential processing)
MIN_VIDEOS_REQUIRED = 1  # Minimum number of videos required for a successful scrape

# Trending content filtering 
TRENDING_ONLY = True  # Only collect trending/viral videos
MIN_VIEWS = 10000  # Minimum views to consider a video trending
MIN_ENGAGEMENT_RATE = 0.05  # Minimum engagement rate (likes + comments + shares) / views
SORT_BY_PERFORMANCE = True  # Sort videos by performance metrics
COLLECT_VIEW_COUNT = True  # Always collect view count data
MAX_TOTAL_VIDEOS = 120  # Maximum videos to keep per scraping session across all keywords

# Content discovery settings
PREFERRED_DISCOVERY_METHODS = ['search', 'hashtag', 'user_profile', 'explore']  # In order of preference
ENABLE_MULTIPLE_DISCOVERY_METHODS = True  # Use multiple discovery methods for each keyword
EXTRACTION_BACKUP_METHODS = True  # Use backup extraction methods if primary fails

# Stealth browser settings
BROWSER_VISIBILITY = True  # Set to True to see the browser while scraping (helpful for debugging)
HUMAN_BEHAVIOR_SIMULATION = True  # Simulate human behavior (mouse movements, scrolling patterns)
STEALTH_LEVEL = 'high'  # Options: 'low', 'medium', 'high'

# Output settings
OUTPUT_FORMATS = ['json', 'csv', 'google_sheets']  # Re-add google_sheets
OUTPUT_DIRECTORY = 'data'

# Scheduler settings
SCHEDULER_ENABLED = True  # Enable scheduled scraping
SCHEDULE_INTERVAL = 'weekly'  # Options: 'hourly', 'daily', 'weekly', 'custom'
SCHEDULE_HOUR = 3  # Hour of the day to run (0-23)
SCHEDULE_MINUTE = 0  # Minute of the hour to run (0-59)
SCHEDULE_DAYS = ['monday', 'wednesday', 'friday']  # Days to run when using 'weekly' option
CUSTOM_SCHEDULE = '0 */12 * * *'  # Custom crontab format (for 'custom' interval)
SCHEDULER_MAX_INSTANCES = 1  # Maximum number of scraper instances to run simultaneously

# Google Sheets settings
GOOGLE_SHEETS_ENABLED = True  # Re-enable Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE = "client_secret.json"  # OAuth client credentials file
GOOGLE_SHEETS_ID = "1fyDwvf3lh0sYUQty8E2H9H9_4BGo797eBqbVWLcMUQg"  # Your actual Google Sheet ID
GOOGLE_SHEETS_RANGE = "A1:Z1000"  # Range to update

# API settings (if using third-party services)
# SCRAPFLY_KEY = "your_key_here"
# APIFY_KEY = "your_key_here"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "scraper.log"

# Debug settings
SAVE_DEBUG_INFO = True  # Save screenshots and HTML for debugging
USE_MOCK_DATA = False  # Never use mock data, always scrape real content 