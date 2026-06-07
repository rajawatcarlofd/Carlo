import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='broadcaster.db'):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"Database connection error: {str(e)}")
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Database error: {str(e)}")
            self.connection.rollback()
            return False
    
    def fetch_one(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None
    
    def fetch_all(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database error: {str(e)}")
            return []
    
    def init_db(self):
        self.connect()
        
        self.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'offline',
                groups_loaded INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL,
                group_id INTEGER NOT NULL,
                group_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (phone) REFERENCES accounts(phone),
                UNIQUE(phone, group_id)
            )
        ''')
        
        self.execute('''
            CREATE TABLE IF NOT EXISTS selected_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL,
                group_id INTEGER NOT NULL,
                group_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                log_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                messages_sent INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute('''
            CREATE TABLE IF NOT EXISTS api_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_id TEXT NOT NULL,
                api_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        stats_exists = self.fetch_one('SELECT id FROM stats LIMIT 1')
        if not stats_exists:
            self.execute('INSERT INTO stats (messages_sent, failed_count) VALUES (0, 0)')
        
        self.disconnect()
    
    def save_api_credentials(self, api_id, api_hash):
        self.connect()
        try:
            existing = self.fetch_one('SELECT id FROM api_credentials LIMIT 1')
            if existing:
                self.execute(
                    'UPDATE api_credentials SET api_id = ?, api_hash = ?, updated_at = CURRENT_TIMESTAMP',
                    (str(api_id), str(api_hash))
                )
            else:
                self.execute(
                    'INSERT INTO api_credentials (api_id, api_hash) VALUES (?, ?)',
                    (str(api_id), str(api_hash))
                )
            return True
        except Exception as e:
            print(f"Error saving API credentials: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def get_api_credentials(self):
        self.connect()
        try:
            result = self.fetch_one('SELECT api_id, api_hash FROM api_credentials LIMIT 1')
            self.disconnect()
            return result
        except Exception as e:
            print(f"Error getting API credentials: {str(e)}")
            return None
    
    def add_account(self, account_data):
        self.connect()
        try:
            self.execute(
                'INSERT INTO accounts (phone, status, groups_loaded) VALUES (?, ?, ?)',
                (account_data['phone'], account_data.get('status', 'online'), account_data.get('groups_loaded', 0))
            )
            return True
        except Exception as e:
            print(f"Error adding account: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def get_all_accounts(self):
        self.connect()
        try:
            accounts = self.fetch_all('SELECT phone, status, groups_loaded FROM accounts')
            result = []
            for account in accounts:
                result.append({
                    'phone': account[0],
                    'status': account[1],
                    'groups_loaded': account[2]
                })
            return result
        finally:
            self.disconnect()
    
    def get_account_count(self):
        self.connect()
        try:
            count = self.fetch_one('SELECT COUNT(*) FROM accounts')
            return count[0] if count else 0
        finally:
            self.disconnect()
    
    def remove_account(self, phone):
        self.connect()
        try:
            self.execute('DELETE FROM accounts WHERE phone = ?', (phone,))
            self.execute('DELETE FROM groups WHERE phone = ?', (phone,))
            self.execute('DELETE FROM selected_groups WHERE phone = ?', (phone,))
            return True
        except Exception as e:
            print(f"Error removing account: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def update_account_status(self, phone, status):
        self.connect()
        try:
            self.execute('UPDATE accounts SET status = ? WHERE phone = ?', (status, phone))
            return True
        except Exception as e:
            print(f"Error updating account status: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def update_account_groups_count(self, phone, count):
        self.connect()
        try:
            self.execute('UPDATE accounts SET groups_loaded = ? WHERE phone = ?', (count, phone))
            return True
        except Exception as e:
            print(f"Error updating groups count: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def save_groups(self, phone, groups):
        self.connect()
        try:
            self.execute('DELETE FROM groups WHERE phone = ?', (phone,))
            for group in groups:
                self.execute(
                    'INSERT INTO groups (phone, group_id, group_name) VALUES (?, ?, ?)',
                    (phone, group['id'], group['name'])
                )
            return True
        except Exception as e:
            print(f"Error saving groups: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def get_groups_by_account(self, phone):
        self.connect()
        try:
            groups = self.fetch_all('SELECT group_id, group_name FROM groups WHERE phone = ?', (phone,))
            result = []
            for group in groups:
                result.append({
                    'id': group[0],
                    'name': group[1]
                })
            return result
        finally:
            self.disconnect()
    
    def get_total_groups_count(self):
        self.connect()
        try:
            count = self.fetch_one('SELECT COUNT(*) FROM groups')
            return count[0] if count else 0
        finally:
            self.disconnect()
    
    def add_selected_group(self, group_data):
        self.connect()
        try:
            self.execute(
                'INSERT INTO selected_groups (phone, group_id, group_name) VALUES (?, ?, ?)',
                (group_data['phone'], group_data['id'], group_data['name'])
            )
            return True
        except Exception as e:
            print(f"Error adding selected group: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def get_selected_groups(self):
        self.connect()
        try:
            groups = self.fetch_all('SELECT phone, group_id, group_name FROM selected_groups')
            result = []
            for group in groups:
                result.append({
                    'phone': group[0],
                    'id': group[1],
                    'name': group[2]
                })
            return result
        finally:
            self.disconnect()
    
    def get_selected_groups_count(self):
        self.connect()
        try:
            count = self.fetch_one('SELECT COUNT(*) FROM selected_groups')
            return count[0] if count else 0
        finally:
            self.disconnect()
    
    def clear_selected_groups(self):
        self.connect()
        try:
            self.execute('DELETE FROM selected_groups')
            return True
        except Exception as e:
            print(f"Error clearing selected groups: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def add_log(self, log_type, message, timestamp):
        self.connect()
        try:
            self.execute(
                'INSERT INTO logs (timestamp, log_type, message) VALUES (?, ?, ?)',
                (timestamp, log_type, message)
            )
            return True
        except Exception as e:
            print(f"Error adding log: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def get_logs(self):
        self.connect()
        try:
            logs = self.fetch_all('SELECT id, timestamp, log_type, message FROM logs ORDER BY id DESC LIMIT 500')
            return logs if logs else []
        finally:
            self.disconnect()
    
    def clear_logs(self):
        self.connect()
        try:
            self.execute('DELETE FROM logs')
            return True
        except Exception as e:
            print(f"Error clearing logs: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def get_messages_sent_count(self):
        self.connect()
        try:
            count = self.fetch_one('SELECT messages_sent FROM stats LIMIT 1')
            return count[0] if count else 0
        finally:
            self.disconnect()
    
    def get_failed_count(self):
        self.connect()
        try:
            count = self.fetch_one('SELECT failed_count FROM stats LIMIT 1')
            return count[0] if count else 0
        finally:
            self.disconnect()
    
    def increment_messages_sent(self, count=1):
        self.connect()
        try:
            self.execute('UPDATE stats SET messages_sent = messages_sent + ? WHERE id = 1', (count,))
            return True
        except Exception as e:
            print(f"Error incrementing messages sent: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def increment_failed_count(self, count=1):
        self.connect()
        try:
            self.execute('UPDATE stats SET failed_count = failed_count + ? WHERE id = 1', (count,))
            return True
        except Exception as e:
            print(f"Error incrementing failed count: {str(e)}")
            return False
        finally:
            self.disconnect()
