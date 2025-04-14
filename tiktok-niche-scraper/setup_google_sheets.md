# Setting Up Google Sheets Integration

This guide will help you set up the Google Sheets integration for the TikTok Niche Scraper using OAuth 2.0.

## Prerequisites

1. A Google account
2. A Google Cloud project
3. A Google Sheet where data will be stored

## Steps to Set Up Google Sheets API

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top, then "New Project"
3. Enter a name for your project and click "Create"
4. Select your new project once it's created

### 2. Enable the Google Sheets API

1. From the Google Cloud Console dashboard, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on "Google Sheets API" in the results
4. Click "Enable"

### 3. Create OAuth 2.0 Client ID Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External (or Internal if using Google Workspace)
   - App name: "TikTok Niche Scraper"
   - User support email: Your email
   - Developer contact information: Your email
   - Click "Save and Continue"
   - Add scopes: "Google Sheets API ../auth/spreadsheets"
   - Click "Save and Continue"
   - Add test users (yourself)
   - Click "Save and Continue"
4. On "Create OAuth client ID" screen:
   - Application type: Desktop app
   - Name: "TikTok Niche Scraper"
   - Click "Create"
5. The OAuth client created dialog will appear with your client ID and client secret
6. Click "Download JSON" to download your credentials
7. Rename the downloaded file to `client_secret.json`

### 4. Configure the TikTok Niche Scraper

1. Place the `client_secret.json` file in the root directory of the TikTok Niche Scraper project
2. Update `config.py` with your Google Sheet settings:

```python
# Google Sheets settings
GOOGLE_SHEETS_ENABLED = True
GOOGLE_SHEETS_CREDENTIALS_FILE = "client_secret.json"  # OAuth client credentials file
GOOGLE_SHEETS_ID = "1fyDwvf3lh0sYUQty8E2H9H9_4BGo797eBqbVWLcMUQg"  # This is found in your sheet's URL
GOOGLE_SHEETS_RANGE = "A1:Z1000"
```

The Google Sheet ID is the long string of characters in the URL of your sheet:
`https://docs.google.com/spreadsheets/d/`**1fyDwvf3lh0sYUQty8E2H9H9_4BGo797eBqbVWLcMUQg**`/edit`

## Running with Google Sheets Integration

When you run the scraper for the first time with OAuth:

```bash
python main.py
```

1. A browser window will open automatically
2. You'll be asked to sign in with your Google account
3. You'll see a warning that the app isn't verified - click "Continue"
4. Grant permission to access your Google Sheets
5. The authentication flow will complete and the browser can be closed

After the first authentication, a `token.pickle` file will be created that stores your authentication tokens. Subsequent runs won't require re-authentication unless the tokens expire.

The scraped data will be sent to your Google Sheet in addition to being saved locally. 