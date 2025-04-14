"""
Google Sheets integration for TikTok Niche Scraper.
Uses OAuth 2.0 authentication for Google Sheets API.
"""

import os
import sys
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_SHEETS_CREDENTIALS_FILE, GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE
from utils.logger import get_logger

logger = get_logger()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    """Get valid credentials for Google Sheets API using OAuth 2.0."""
    creds = None
    token_path = Path(__file__).parent.parent / 'token.pickle'
    credentials_path = Path(__file__).parent.parent / GOOGLE_SHEETS_CREDENTIALS_FILE
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                # Use OAuth flow
                if os.path.exists(credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    logger.error(f"Credentials file {GOOGLE_SHEETS_CREDENTIALS_FILE} not found")
                    return None
            except Exception as e:
                logger.error(f"Error getting credentials: {str(e)}")
                return None
                
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

def format_value_for_sheets(value):
    """
    Format a value to be compatible with Google Sheets.
    
    Args:
        value: Any data value (string, list, dict, etc.)
        
    Returns:
        str: A string representation suitable for Google Sheets
    """
    if isinstance(value, list):
        # Convert lists to comma-separated strings
        return ", ".join(str(item) for item in value)
    elif isinstance(value, dict):
        # Convert dictionaries to JSON-like strings
        parts = []
        for k, v in value.items():
            parts.append(f"{k}: {v}")
        return "{" + ", ".join(parts) + "}"
    else:
        # Return other values as strings
        return str(value) if value is not None else ""

def update_google_sheet(data):
    """
    Update Google Sheet with scraped data.
    
    Args:
        data (list): List of video data dictionaries
        
    Returns:
        bool: Success status
    """
    if not data:
        logger.warning("No data to update in Google Sheets")
        return False
        
    if not GOOGLE_SHEETS_ID:
        logger.error("Google Sheet ID not configured")
        return False
        
    try:
        creds = get_credentials()
        if not creds:
            return False
            
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        
        # Convert data to rows
        # First row as headers
        headers = list(data[0].keys())
        
        # Create rows with proper formatting for Google Sheets
        rows = [headers]
        for item in data:
            # Convert each value to a string format compatible with Google Sheets
            row = [format_value_for_sheets(item.get(key, "")) for key in headers]
            rows.append(row)
            
        # Prepare the request
        body = {'values': rows}
        
        # Update the sheet
        result = sheet.values().update(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range=GOOGLE_SHEETS_RANGE,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logger.info(f"Google Sheets updated: {result.get('updatedCells')} cells updated")
        return True
        
    except Exception as e:
        logger.error(f"Error updating Google Sheet: {str(e)}")
        return False 