#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point - Use this to run the application
"""

import os
import sys

# Ensure sessions directory exists
if not os.path.exists('sessions'):
    os.makedirs('sessions')
    print("✓ Created sessions directory")

# Import and run the app
from app import app, db

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 TELEGRAM MULTI-ACCOUNT BROADCASTER")
    print("="*60)
    print("✓ Initializing database...")
    db.init_db()
    print("✓ Database initialized")
    print("\n📱 Starting Flask server...")
    print("🌐 Open browser: http://localhost:5000")
    print("\n🟢 Server is running! Press CTRL+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=False, host='127.0.0.1', port=5000, threaded=True, use_reloader=False)
