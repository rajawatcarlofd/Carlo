# 🚀 Telegram Multi-Account Broadcaster - Setup Guide

## Quick Start (3 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get Telegram API Credentials
1. Visit: https://my.telegram.org/apps
2. Login with your Telegram account
3. Create an app (if not already created)
4. Copy your **API ID** and **API HASH**

### Step 3: Run the Application
```bash
python run.py
```

The app will start on: **http://localhost:5000**

### Step 4: Setup API Credentials
1. Open the browser to http://localhost:5000
2. Go to **"API Setup"** tab
3. Paste your API ID and API HASH
4. Click **"Upload API Credentials"**

### Step 5: Add Telegram Accounts
1. Go to **"Accounts"** tab
2. Enter your phone number (e.g., +1234567890)
3. Click **"Add Account"**
4. Enter the OTP code sent to your phone
5. Account is now added!

### Step 6: Load Groups
1. Go to **"Groups"** tab
2. Select your account from dropdown
3. Click **"Refresh Groups"** to load all groups/channels
4. Select groups you want to broadcast to
5. Click **"Save Selected Groups"**

### Step 7: Send Messages
1. Go to **"Broadcast"** tab
2. Type your message
3. Configure settings:
   - **Delay**: Seconds between messages
   - **Random Delay**: Enable for randomized delays
   - **Auto Repeat**: Enable to repeat broadcasting
4. Click **"Start Broadcast"**
5. Click **"Stop Broadcast"** to stop

### Step 8: Check Logs
1. Go to **"Logs"** tab
2. View all activity
3. Export logs or clear them

---

## ✅ Features

✓ Multi-account management (unlimited accounts)
✓ OTP-based authentication
✓ Automatic group/channel loading
✓ Smart group selection
✓ Configurable delays
✓ Random delay option
✓ Auto-repeat functionality
✓ Real-time logging
✓ Log export
✓ Beautiful UI with Bootstrap 5
✓ Live statistics
✓ Responsive design (works on mobile too!)

---

## 🔧 Troubleshooting

### Issue: Port 5000 already in use
**Solution:** 
```python
# Edit the last line in run.py:
app.run(debug=False, host='127.0.0.1', port=5001, threaded=True)  # Change 5000 to 5001
```

### Issue: "API credentials not configured"
**Solution:** Go to API Setup tab and upload your API ID and HASH first

### Issue: OTP not received
**Solution:** 
- Make sure your phone is connected to internet
- Wait a few seconds
- Telegram accounts with 2FA may have issues (disable 2FA temporarily)

### Issue: Groups not loading
**Solution:**
- Make sure account is "Online" status
- Try "Reconnect Account"
- Make sure you're a member of the groups

### Issue: Messages not sending
**Solution:**
- Verify at least one group is selected
- Check account status
- Check logs for specific error messages
- Ensure you have permission to send messages in the groups

---

## 📁 File Structure

```
Carlo/
├── run.py                    # Main entry point
├── app.py                    # Flask app & routes
├── broadcaster.py            # Telegram broadcasting logic
├── database.py              # Database management
├── config.py                # Configuration file
├── requirements.txt         # Python dependencies
├── SETUP.md                 # This file
├── templates/
│   └── index.html          # Main UI template
├── static/
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
├── sessions/               # Telegram session files (auto-created)
└── broadcaster.db          # SQLite database (auto-created)
```

---

## 🔐 Security Notes

- ✓ Runs on localhost only (127.0.0.1)
- ✓ No external access by default
- ✓ Session files stored locally
- ✓ Database is local SQLite
- ✓ API credentials stored in database
- ✓ No cloud sync or external API calls (except Telegram)

---

## 📞 Support

For issues:
1. Check the Logs tab for error messages
2. Verify API credentials are correct
3. Ensure Python 3.12+ is installed
4. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

---

**Version:** 1.0.0
**Status:** Production Ready ✅
