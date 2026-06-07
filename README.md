# Multi-Account Telegram Broadcaster

A production-ready desktop-style web application for managing multiple Telegram accounts and broadcasting messages to groups/channels simultaneously.

## Features

✅ **Multi-Account Management**
- Add unlimited Telegram accounts
- Login with phone number and OTP
- Permanent session file storage
- Account status monitoring (Online/Offline)
- Reconnect and remove account options
- Multiple accounts stay logged in simultaneously

✅ **Group Management**
- Load groups/channels from each account
- Display groups account-wise
- Select All Groups button
- Search groups functionality
- Refresh groups button
- Save selected groups
- Real-time group count display

✅ **Broadcast System**
- Message textbox for content
- Start/Stop Broadcast buttons
- Send to selected groups
- Text message support
- Configurable delay between messages
- Random delay option
- Auto-repeat functionality
- Repeat interval settings
- Skip failed groups and continue

✅ **Logs System**
- Real-time logs panel
- Success and failure logs
- Timestamps for every action
- Export logs button
- Clear logs button

✅ **Dashboard**
- Total accounts counter
- Total groups loaded counter
- Selected groups counter
- Messages sent counter
- Failed count counter
- Running status indicator

✅ **User Interface**
- Simple and lightweight design
- Fast loading
- Mobile responsive (Bootstrap 5)
- Single-page dashboard
- No admin panel
- No user roles
- No registration system
- Localhost only

✅ **Database**
- SQLite database
- Auto-created tables
- Stores accounts, settings, logs, and selected groups

✅ **Stability & Performance**
- Async Telethon integration
- Proper event loop handling
- Non-blocking UI
- Thread-safe broadcasting
- Auto error handling
- Auto reconnect if session exists
- Production-ready structure

## Technology Stack

- **Backend**: Python 3.12+, Flask
- **API Client**: Telethon
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5

## Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd Carlo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Telegram API**
   - Get your API ID and API HASH from https://my.telegram.org/apps
   - Edit `broadcaster.py` and update:
     ```python
     API_ID = your_api_id
     API_HASH = 'your_api_hash'
     ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   - Navigate to `http://localhost:5000`
   - Application will be ready to use

## Usage Guide

### Adding Accounts

1. Go to **Accounts** tab
2. Enter your phone number (with country code, e.g., +1234567890)
3. Click **Add Account**
4. Enter the OTP sent to your phone
5. Account will be added and stay logged in

### Loading Groups

1. Go to **Groups** tab
2. Select an account from the dropdown
3. Click **Refresh Groups** to load all groups/channels
4. Groups will appear in the list
5. Use **Search** to filter groups
6. Select desired groups using checkboxes
7. Click **Select All** to select all groups
8. Click **Save Selected Groups** to save your selection

### Broadcasting Messages

1. Go to **Broadcast** tab
2. Enter your message in the textbox
3. Configure settings:
   - **Delay**: Seconds between messages (0 = no delay)
   - **Random Delay**: Randomize delay between 50%-150% of set delay
   - **Auto Repeat**: Enable to repeat broadcasting
   - **Repeat Interval**: Seconds between repeat cycles
4. Click **Start Broadcast** to begin
5. Click **Stop Broadcast** to stop

### Monitoring

1. Go to **Logs** tab
2. View real-time logs of all actions
3. Click **Export Logs** to download logs as text file
4. Click **Clear Logs** to clear all logs

## File Structure

```
Carlo/
├── app.py                 # Flask application and routes
├── broadcaster.py         # Telethon integration and broadcasting logic
├── database.py           # SQLite database management
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/
│   └── index.html       # Main HTML template
└── static/
    ├── style.css        # CSS styling
    └── script.js        # JavaScript functionality
```

## Database Tables

### accounts
- id: Integer (Primary Key)
- phone: Text (Unique)
- status: Text (online/offline)
- groups_loaded: Integer
- created_at: Timestamp

### groups
- id: Integer (Primary Key)
- phone: Text (Foreign Key)
- group_id: Integer
- group_name: Text
- created_at: Timestamp

### selected_groups
- id: Integer (Primary Key)
- phone: Text
- group_id: Integer
- group_name: Text
- created_at: Timestamp

### logs
- id: Integer (Primary Key)
- timestamp: Text
- log_type: Text (success/error/warning/info)
- message: Text
- created_at: Timestamp

### stats
- id: Integer (Primary Key)
- messages_sent: Integer
- failed_count: Integer
- updated_at: Timestamp

## API Endpoints

### Account Management
- `GET /api/accounts` - Get all accounts
- `GET /api/account-status/<phone>` - Get account status
- `POST /api/add-account` - Add new account
- `POST /api/verify-otp` - Verify OTP
- `POST /api/remove-account` - Remove account
- `POST /api/reconnect-account` - Reconnect account

### Groups Management
- `POST /api/load-groups` - Load groups for account
- `GET /api/groups/<phone>` - Get groups for account
- `POST /api/save-selected-groups` - Save selected groups
- `GET /api/get-selected-groups` - Get selected groups

### Broadcasting
- `POST /api/start-broadcast` - Start broadcasting
- `POST /api/stop-broadcast` - Stop broadcasting

### Logs
- `GET /api/logs` - Get all logs
- `GET /api/export-logs` - Export logs as file
- `POST /api/clear-logs` - Clear all logs

### Dashboard
- `GET /api/stats` - Get dashboard statistics

## Important Notes

1. **Telegram API Credentials**: Get your API ID and API HASH from https://my.telegram.org/apps

2. **Session Storage**: Session files are stored in the `sessions/` directory. Do not delete these files unless you want to log out.

3. **Two-Factor Authentication**: If your Telegram account has 2FA enabled, disable it before logging in.

4. **Rate Limiting**: Telegram has rate limits. Use delays between messages to avoid issues.

5. **Port 5000**: The application runs on localhost:5000. Make sure this port is available.

6. **Database**: SQLite database is stored as `broadcaster.db` in the application directory.

## Troubleshooting

### Port 5000 Already in Use
```bash
# Change port in app.py or use:
python app.py
# Then modify the port in app.run() line
```

### OTP Verification Failed
- Ensure you entered the correct OTP
- Disable 2FA on your Telegram account if enabled
- Check your phone for the OTP code

### Groups Not Loading
- Ensure the account is online
- Try reconnecting the account
- Check if you have admin access to view groups

### Messages Not Sending
- Verify groups are properly selected
- Check account status (should be Online)
- Review logs for specific error messages
- Ensure you have permission to send messages in the groups

## Performance

- Single-page application (SPA) for fast loading
- Asynchronous operations prevent UI blocking
- SQLite for lightweight local storage
- Bootstrap 5 for optimized CSS
- No external dependencies for heavy UI components

## Security

- Application runs on localhost only (127.0.0.1)
- No user authentication required (local use only)
- Session files stored locally and not transmitted
- All data stored in local SQLite database
- Flask debug mode disabled in production

## License

This project is provided as-is for personal use.

## Support

For issues and troubleshooting:
1. Check the Logs tab for detailed error messages
2. Ensure all Telegram API credentials are correct
3. Verify Python version is 3.12 or higher
4. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Version

**Version**: 1.0.0
**Last Updated**: 2024
**Status**: Production Ready ✅
