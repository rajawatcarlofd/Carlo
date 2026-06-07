"""
Configuration file for Telegram Broadcaster
Store your API credentials here
"""

API_CONFIG = {
    'API_ID': 0,  # Replace with your Telegram API ID from https://my.telegram.org/apps
    'API_HASH': '',  # Replace with your Telegram API HASH from https://my.telegram.org/apps
}

# Session directory for storing telegram session files
SESSION_DIR = 'sessions'

# Database configuration
DATABASE_NAME = 'broadcaster.db'

# Flask configuration
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
FLASK_DEBUG = False
