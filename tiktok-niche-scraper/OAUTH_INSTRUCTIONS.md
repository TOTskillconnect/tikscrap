# Setting Up OAuth for Google Sheets Integration

Follow these steps to get Google Sheets integration working with the TikTok Niche Scraper:

## 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project name and ID

## 2. Enable the Google Sheets API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Select it and click "Enable"

## 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted to configure consent screen:
   - Choose "External" user type (or "Internal" if in an organization)
   - Fill in App name, user support email, and developer contact information
   - For scopes, add the Google Sheets API (../auth/spreadsheets)
   - Add your email as a test user
4. For application type, select "Desktop app"
5. Give it a name like "TikTok Niche Scraper"
6. Click "Create"

## 4. Download and Set Up the Credentials

1. After creating the OAuth client ID, you'll see a download button
2. Download the JSON file
3. Rename it to `client_secret.json`
4. Place it in the tiktok-niche-scraper root directory (same location as main.py)

## 5. Add Your Google Sheet ID to config.py

1. Create a new Google Sheet at [sheets.google.com](https://sheets.google.com)
2. Copy the ID from the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`
3. Open config.py and update:
   ```python
   GOOGLE_SHEETS_ID = "YOUR_SHEET_ID_HERE"  # Replace with your actual ID
   ```

## 6. Run the Scraper

Run the script:
```
python main.py
```

The first time you run it:
1. A browser window will open
2. Sign in with your Google account
3. You'll see a warning that the app isn't verified - click "Continue"
4. Grant permission to access your Google Sheets
5. The authentication will complete and the browser will close
6. The script will continue running and update your Google Sheet

After successful authentication, a token.pickle file will be created so you won't need to authenticate again for future runs. 