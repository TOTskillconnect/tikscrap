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

## Troubleshooting Common Issues

### Error: 'str' object has no attribute 'get'
This error occurs when the scraper attempts to process raw video data that is in string format instead of a dictionary. This has been fixed in the latest version. If you encounter this:
1. Make sure you're using the latest version of the scraper
2. Check that the `video_parser.py` file contains proper type checking
3. Restart the scraper

### Error: "The token '&&' is not a valid statement separator"
In Windows PowerShell, use semicolons (`;`) instead of double ampersands (`&&`) to separate commands:
```powershell
cd tiktok-niche-scraper; python main.py
```

### Browser Not Starting
If the browser fails to start:
1. Make sure you've installed the Playwright browsers: `playwright install`
2. Check your internet connection
3. Increase timeouts in the `stealth_browser.py` file

### No Videos Found
If the scraper isn't finding videos:
1. Check your keywords in `config.py` - make sure they're trending topics
2. Try different discovery methods by changing `PREFERRED_DISCOVERY_METHODS` in config
3. Check TikTok website directly to ensure the content exists
4. Consider reducing `STEALTH_LEVEL` temporarily for testing

### Google Sheets Integration Issues
If Google Sheets integration isn't working:
1. Ensure `client_secret.json` is properly set up and located in the root directory
2. Check that your Google Cloud project has the Google Sheets API enabled
3. Verify your `GOOGLE_SHEETS_ID` in config.py is correct
4. Delete `token.pickle` file and re-authenticate

## Deployment Options

### GitHub Actions (Easy Automated Deployment)
The scraper includes GitHub Actions workflows that can automatically run on a schedule:

1. Push your code to GitHub
2. Store your Google credentials as a repository secret named `GOOGLE_CREDENTIALS_JSON`
3. The scraper will run automatically according to the schedule in `.github/workflows/schedule_scraper.yml`
4. Scraped data will be committed back to your repository

### VPS/Cloud Server (Production Deployment)
For more reliable production use:

1. Set up a small VPS (DigitalOcean, AWS, etc.)
2. Clone the repository
3. Install dependencies
4. Use the built-in scheduler with daemon mode: `python run_scheduler.py --daemon`
5. Consider setting up a service for automatic startup:

```ini
[Unit]
Description=TikTok Niche Scraper Service
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/tiktok-niche-scraper
ExecStart=/usr/bin/python3 run_scheduler.py --daemon
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

## Extending the Scraper

### Adding New Content Discovery Methods
To add a new discovery method:
1. Edit `scraper/content_discovery.py`
2. Add your method following the pattern of existing methods
3. Update the `execute_best_approach` function to include your method

### Custom Performance Metrics
Modify `scraper/video_parser.py` to calculate additional performance metrics:
```python
def calculate_performance_score(video_data):
    # Your custom algorithm here
    return score
``` 