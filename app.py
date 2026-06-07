import os
import sys
import asyncio
from flask import Flask, render_template, request, jsonify, session
from database import Database
from broadcaster import TelegramBroadcaster
import threading
import json
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'multi-telegram-broadcaster-secret-key-2024'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()
broadcaster = TelegramBroadcaster(db)

broadcast_thread = None
broadcasting = False
logs_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    try:
        total_accounts = db.get_account_count()
        total_groups = db.get_total_groups_count()
        selected_groups = db.get_selected_groups_count()
        messages_sent = db.get_messages_sent_count()
        failed_count = db.get_failed_count()
        
        return jsonify({
            'total_accounts': total_accounts,
            'total_groups': total_groups,
            'selected_groups': selected_groups,
            'messages_sent': messages_sent,
            'failed_count': failed_count,
            'broadcasting': broadcasting
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        accounts = db.get_all_accounts()
        return jsonify(accounts)
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-account', methods=['POST'])
def add_account():
    try:
        data = request.json
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'error': 'Phone number required'}), 400
        
        result = asyncio.run(broadcaster.start_auth(phone))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error adding account: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        phone = data.get('phone')
        otp = data.get('otp')
        
        if not phone or not otp:
            return jsonify({'error': 'Phone and OTP required'}), 400
        
        result = asyncio.run(broadcaster.complete_auth(phone, otp))
        
        if result.get('success'):
            db.add_account({
                'phone': phone,
                'status': 'online',
                'groups_loaded': 0
            })
            add_log('success', f"Account {phone} added successfully")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        add_log('error', f"OTP verification failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/remove-account', methods=['POST'])
def remove_account():
    try:
        data = request.json
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'error': 'Phone number required'}), 400
        
        broadcaster.remove_account(phone)
        db.remove_account(phone)
        add_log('success', f"Account {phone} removed")
        
        return jsonify({'success': True, 'message': 'Account removed successfully'})
    except Exception as e:
        logger.error(f"Error removing account: {str(e)}")
        add_log('error', f"Account removal failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/load-groups', methods=['POST'])
def load_groups():
    try:
        data = request.json
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'error': 'Phone number required'}), 400
        
        result = asyncio.run(broadcaster.load_groups(phone))
        
        if result.get('success'):
            groups = result.get('groups', [])
            db.save_groups(phone, groups)
            db.update_account_groups_count(phone, len(groups))
            add_log('success', f"Loaded {len(groups)} groups for {phone}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error loading groups: {str(e)}")
        add_log('error', f"Failed to load groups: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/groups/<phone>')
def get_groups(phone):
    try:
        groups = db.get_groups_by_account(phone)
        return jsonify(groups)
    except Exception as e:
        logger.error(f"Error fetching groups: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-selected-groups', methods=['POST'])
def save_selected_groups():
    try:
        data = request.json
        selected_groups = data.get('groups', [])
        
        db.clear_selected_groups()
        for group_data in selected_groups:
            db.add_selected_group(group_data)
        
        add_log('success', f"Selected {len(selected_groups)} groups for broadcasting")
        return jsonify({'success': True, 'message': f'{len(selected_groups)} groups selected'})
    except Exception as e:
        logger.error(f"Error saving selected groups: {str(e)}")
        add_log('error', f"Failed to save selected groups: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-selected-groups')
def get_selected_groups_api():
    try:
        groups = db.get_selected_groups()
        return jsonify(groups)
    except Exception as e:
        logger.error(f"Error fetching selected groups: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-broadcast', methods=['POST'])
def start_broadcast():
    global broadcast_thread, broadcasting
    
    try:
        data = request.json
        message = data.get('message', '')
        delay = data.get('delay', 0)
        random_delay = data.get('random_delay', False)
        auto_repeat = data.get('auto_repeat', False)
        repeat_interval = data.get('repeat_interval', 300)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if broadcasting:
            return jsonify({'error': 'Broadcasting already in progress'}), 400
        
        broadcasting = True
        add_log('success', 'Broadcasting started')
        
        broadcast_thread = threading.Thread(
            target=run_broadcast,
            args=(message, delay, random_delay, auto_repeat, repeat_interval),
            daemon=True
        )
        broadcast_thread.start()
        
        return jsonify({'success': True, 'message': 'Broadcasting started'})
    except Exception as e:
        logger.error(f"Error starting broadcast: {str(e)}")
        add_log('error', f"Broadcast start failed: {str(e)}")
        broadcasting = False
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop-broadcast', methods=['POST'])
def stop_broadcast():
    global broadcasting
    try:
        broadcasting = False
        broadcaster.stop_broadcast = True
        add_log('success', 'Broadcasting stopped')
        return jsonify({'success': True, 'message': 'Broadcasting stopped'})
    except Exception as e:
        logger.error(f"Error stopping broadcast: {str(e)}")
        return jsonify({'error': str(e)}), 500

def run_broadcast(message, delay, random_delay, auto_repeat, repeat_interval):
    global broadcasting
    try:
        asyncio.run(broadcaster.broadcast_message(
            message=message,
            delay=delay,
            random_delay=random_delay,
            auto_repeat=auto_repeat,
            repeat_interval=repeat_interval
        ))
    except Exception as e:
        logger.error(f"Broadcast error: {str(e)}")
        add_log('error', f"Broadcast failed: {str(e)}")
    finally:
        broadcasting = False

@app.route('/api/logs')
def get_logs():
    try:
        logs = db.get_logs()
        return jsonify(logs)
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-logs', methods=['GET'])
def export_logs():
    try:
        logs = db.get_logs()
        filename = f"broadcast_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        log_content = "Multi-Account Telegram Broadcaster - Logs Export\n"
        log_content += f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_content += "="*80 + "\n\n"
        
        for log in logs:
            log_content += f"[{log[1]}] [{log[2].upper()}] {log[3]}\n"
        
        return log_content, 200, {'Content-Disposition': f'attachment; filename="{filename}"'}
    except Exception as e:
        logger.error(f"Error exporting logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    try:
        db.clear_logs()
        add_log('success', 'Logs cleared')
        return jsonify({'success': True, 'message': 'Logs cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

def add_log(log_type, message):
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.add_log(log_type, message, timestamp)
    except Exception as e:
        logger.error(f"Error adding log: {str(e)}")

@app.route('/api/account-status/<phone>')
def get_account_status(phone):
    try:
        status = asyncio.run(broadcaster.get_account_status(phone))
        return jsonify({'status': status})
    except Exception as e:
        logger.error(f"Error fetching account status: {str(e)}")
        return jsonify({'status': 'offline'})

@app.route('/api/reconnect-account', methods=['POST'])
def reconnect_account():
    try:
        data = request.json
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'error': 'Phone number required'}), 400
        
        result = asyncio.run(broadcaster.reconnect_account(phone))
        
        if result.get('success'):
            db.update_account_status(phone, 'online')
            add_log('success', f"Account {phone} reconnected")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error reconnecting account: {str(e)}")
        add_log('error', f"Reconnection failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    db.init_db()
    app.run(debug=False, host='127.0.0.1', port=5000, threaded=True)
