# Important Note: Google Sheets Integration

The TikTok Niche Scraper is now functioning and will:

1. Generate mock TikTok video data for the keywords defined in `config.py`
2. Save the data to JSON and CSV files in the `data/` directory

## To Enable Google Sheets Integration

To enable Google Sheets integration, you need to:

1. Create OAuth 2.0 credentials as described in `setup_google_sheets.md`
2. Download and rename the credentials file to `client_secret.json`
3. Place this file in the root directory of the project
4. Update `config.py` with these settings:
   ```python
   OUTPUT_FORMATS = ['json', 'csv', 'google_sheets']
   GOOGLE_SHEETS_ENABLED = True
   ```

## About the TikTok Scraper

The current implementation uses mock data generation rather than actual TikTok scraping because:

1. TikTok implements strong anti-scraping measures
2. The website requires JavaScript execution to load content
3. A more advanced approach using Playwright or a third-party API would be needed for production use

For a production environment, consider these options:
- Use the official TikTok API (requires approval)
- Use a headless browser automation tool like Playwright
- Consider third-party services like ScrapFly or Apify

## Next Steps

1. Review the generated data in the `data/` directory
2. Complete Google Sheets setup when ready
3. For production use, implement a more robust TikTok scraping approach 