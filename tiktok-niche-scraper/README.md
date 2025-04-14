# TikTok Niche Scraper

An advanced tool that extracts trending videos from TikTok based on user-defined niches or keywords. It collects metadata such as hooks, hashtags, and video information using enhanced stealth techniques and multiple content discovery approaches.

## Features
- **Advanced Stealth Technology**: Avoid detection with sophisticated browser fingerprinting evasion
- **Multi-approach Content Discovery**: Find content through search, hashtags, user profiles, and explore pages
- **Human Behavior Simulation**: Mimic natural user behavior with realistic mouse movements and scrolling patterns
- **Resilient Data Extraction**: Multiple fallback methods to ensure reliable data collection
- **Multiple Output Formats**: Export to JSON, CSV, and Google Sheets
- **Scheduled Automation**: Run automatically using the built-in scheduler or 

GitHub Actions
## Installation

```bash
# Clone the repository
git clone https://github.com/totskillconnect/tiktok-niche-scraper.git
cd tiktok-niche-scraper

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## Configuration

Edit `config.py` to set your desired:
- Keywords/niches to scrape
- Maximum videos per keyword
- Stealth and content discovery settings
- Output formats
- Scheduler settings
- Logging settings
- Google Sheets integration (optional)

```python
# Example configuration
KEYWORDS = [
    'budgeting',
    'budgeting hack',
    'take control of finance',
    # Add your niches here
]

MAX_VIDEOS_PER_KEYWORD = 15
CONCURRENT_KEYWORDS = 2  # Process 2 keywords concurrently

# Scheduler settings
SCHEDULER_ENABLED = True
SCHEDULE_INTERVAL = 'daily'  # Options: 'hourly', 'daily', 'weekly', 'custom'
SCHEDULE_HOUR = 3  # Run at 3 AM

# Stealth settings
BROWSER_VISIBILITY = False  # Set to True for debugging
STEALTH_LEVEL = 'high'      # 'low', 'medium', or 'high'

# Content discovery settings
PREFERRED_DISCOVERY_METHODS = ['search', 'hashtag', 'user_profile', 'explore']
```

### Google Sheets Configuration

To use the Google Sheets integration:

1. Set `GOOGLE_SHEETS_ENABLED = True` in `config.py`
2. Create a Google Cloud project and enable the Google Sheets API
3. Create credentials (OAuth or Service Account) and download as `client_secret.json`
4. Place the `client_secret.json` file in the project root directory
5. Update the `GOOGLE_SHEETS_ID` with your Google Sheet ID (found in the Sheet URL)

```python
# Google Sheets settings in config.py
GOOGLE_SHEETS_ENABLED = True
GOOGLE_SHEETS_CREDENTIALS_FILE = "client_secret.json"
GOOGLE_SHEETS_ID = "your-sheet-id-here"
GOOGLE_SHEETS_RANGE = "A1:Z1000"
```

## Usage

### Running the Scraper

#### Windows

```
# Run using the batch file
run.bat

# Or using PowerShell script
.\run.ps1
```

#### macOS/Linux

```bash
# Run the scraper manually
python main.py
```

The scraped data will be saved in the `data/` directory in JSON and CSV formats, and optionally to Google Sheets.

### Using the Scheduler

The scheduler allows you to run the scraper automatically at specified intervals.

#### Windows

```
# Run the scheduler using the batch file
run_scheduler.bat

# Or using PowerShell script
.\run_scheduler.ps1

# Run the scraper immediately before starting the scheduler
run_scheduler.bat --run-now
```

#### macOS/Linux

```bash
# Run the scheduler
python run_scheduler.py

# Run the scraper immediately before starting the scheduler
python run_scheduler.py --run-now

# Run in daemon mode (background process)
python run_scheduler.py --daemon
```

## Advanced Features

### Multiple Content Discovery Methods

The scraper now uses multiple approaches to discover content:

1. **Search-based Discovery**: Uses TikTok's search functionality to find videos
2. **Hashtag-based Discovery**: Discovers videos on hashtag pages
3. **User Profile Discovery**: Finds top creators in a niche and scrapes their content
4. **Explore Page Discovery**: Uses the explore/trending page for discovery

The system automatically selects the best approach for each keyword based on results.

### Enhanced Stealth Features

Sophisticated stealth features to avoid detection:

- **Advanced Browser Fingerprinting Protection**: Prevents TikTok from identifying automated browsers
- **Human Behavior Simulation**: Realistic mouse movements, scrolling patterns, and interaction timing
- **Dynamic User-Agent Rotation**: Appears as different browsers and devices for each session
- **Multiple Browser Engine Support**: Can use Chrome, Firefox, or WebKit based browsers

### Scheduling Options

Configure the scheduler to run at your preferred times:

- **Hourly**: Run every hour at a specific minute
- **Daily**: Run once per day at a specific time
- **Weekly**: Run on specific days of the week
- **Custom**: Use a custom schedule with cron-like syntax

## Project Structure

```
tiktok-niche-scraper/
├── config.py                   # Configuration settings
├── main.py                     # Main script
├── run.bat                     # Windows batch launcher
├── run.ps1                     # PowerShell launcher
├── run_scheduler.bat           # Scheduler batch launcher
├── run_scheduler.ps1           # Scheduler PowerShell launcher
├── run_scheduler.py            # Scheduler script
├── scraper/                    # Scraping modules
│   ├── content_discovery.py    # Multi-approach content discovery
│   ├── stealth_browser.py      # Advanced stealth browser implementation
│   ├── tiktok_api.py           # TikTok interaction handling
│   └── video_parser.py         # Process and extract data from videos
├── utils/                      # Utility functions
│   ├── logger.py               # Logging configuration
│   ├── scheduler.py            # Scheduler implementation
│   └── sheets_helper.py        # Google Sheets integration
├── data/                       # Output data directory
└── .github/workflows/          # GitHub Actions workflows
```

## Limitations

This scraper is for educational purposes only. Please be aware that:
- TikTok's website structure may change, requiring updates to the scraper
- Excessive scraping may result in rate limiting or IP blocks
- The tool respects TikTok's `robots.txt` and implements rate limiting

## License

MIT 