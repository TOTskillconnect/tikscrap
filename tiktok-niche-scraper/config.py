"""
Configuration settings for the TikTok Niche Scraper.
"""

# Search keywords/niches to scrape
KEYWORDS = [
    'budgeting',
    'budget tracker',
    'budgeting tips',
    'budgeting hacks',
    'money management',
    'save money'
]

# Scraping settings
MAX_VIDEOS_PER_KEYWORD = 20  # Reduced number of videos to collect per keyword
REQUEST_DELAY = 2  # seconds between requests
CONCURRENT_KEYWORDS = 1  # Process 1 keyword at a time for more stability
MIN_VIDEOS_REQUIRED = 1  # Minimum number of videos required for a successful scrape

# Trending content filtering 
TRENDING_ONLY = True  # Only collect trending/viral videos
MIN_VIEWS = 1000  # Reduced minimum views to consider a video trending
MIN_ENGAGEMENT_RATE = 0.01  # Reduced minimum engagement rate
SORT_BY_PERFORMANCE = True  # Sort videos by performance metrics
COLLECT_VIEW_COUNT = True  # Always collect view count data
MAX_TOTAL_VIDEOS = 50  # Reduced maximum videos to keep per scraping session
MAX_VIDEO_AGE_DAYS = 14  # Only collect videos from the past two weeks

# Content discovery settings
PREFERRED_DISCOVERY_METHODS = ['search']  # Simplified to just use search method
ENABLE_MULTIPLE_DISCOVERY_METHODS = False  # Disabled multiple discovery methods
EXTRACTION_BACKUP_METHODS = True  # Use backup extraction methods if primary fails

# Stealth browser settings
BROWSER_VISIBILITY = True  # Set to True to see the browser while scraping
HUMAN_BEHAVIOR_SIMULATION = True  # Simulate human behavior
STEALTH_LEVEL = 'low'  # Reduced stealth level for better performance

# Output settings
OUTPUT_FORMATS = ['json', 'csv']  # Options: 'json', 'csv', 'google_sheets'
OUTPUT_DIRECTORY = 'data'

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