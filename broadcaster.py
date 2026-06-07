import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import os
import random
import time
from pathlib import Path
from config import API_CONFIG, SESSION_DIR

class TelegramBroadcaster:
    def __init__(self, db):
        self.db = db
        self.clients = {}
        self.phone_numbers = {}
        self.stop_broadcast = False
        self.otp_cache = {}
        self.api_id = API_CONFIG.get('API_ID', 0)
        self.api_hash = API_CONFIG.get('API_HASH', '')
        
        if not os.path.exists(SESSION_DIR):
            os.makedirs(SESSION_DIR)
    
    def update_credentials(self, api_id, api_hash):
        """Update API credentials at runtime"""
        self.api_id = int(api_id)
        self.api_hash = str(api_hash)
    
    async def start_auth(self, phone):
        try:
            if not self.api_id or not self.api_hash:
                return {'success': False, 'error': 'API credentials not configured. Please upload API credentials first.'}
            
            session_file = os.path.join(SESSION_DIR, f'{phone}.session')
            client = TelegramClient(session_file, self.api_id, self.api_hash)
            
            await client.connect()
            
            if await client.is_user_authorized():
                self.clients[phone] = client
                return {'success': True, 'message': 'Already logged in', 'phone': phone}
            
            result = await client.send_code_request(phone)
            self.phone_numbers[phone] = client
            
            return {
                'success': True,
                'message': 'OTP sent',
                'phone_code_hash': result.phone_code_hash if hasattr(result, 'phone_code_hash') else '',
                'phone': phone
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def complete_auth(self, phone, otp):
        try:
            if phone not in self.phone_numbers:
                return {'success': False, 'error': 'OTP request not initiated'}
            
            client = self.phone_numbers[phone]
            
            try:
                await client.sign_in(phone, otp)
            except SessionPasswordNeededError:
                return {'success': False, 'error': 'Two-factor authentication enabled. Disable it and try again.'}
            
            self.clients[phone] = client
            del self.phone_numbers[phone]
            
            return {'success': True, 'message': 'Login successful', 'phone': phone}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def load_groups(self, phone):
        try:
            if phone not in self.clients:
                session_file = os.path.join(SESSION_DIR, f'{phone}.session')
                if os.path.exists(f'{session_file}.session'):
                    client = TelegramClient(session_file, self.api_id, self.api_hash)
                    await client.connect()
                    if await client.is_user_authorized():
                        self.clients[phone] = client
                    else:
                        return {'success': False, 'error': 'Client not authorized'}
                else:
                    return {'success': False, 'error': 'Client not connected'}
            
            client = self.clients[phone]
            groups = []
            
            try:
                dialogs = await client.get_dialogs()
                for dialog in dialogs:
                    if dialog.is_group or dialog.is_channel:
                        groups.append({
                            'id': dialog.id,
                            'name': dialog.name or 'Unknown Group',
                            'type': 'channel' if dialog.is_channel else 'group'
                        })
            except Exception as e:
                print(f"Error loading groups: {str(e)}")
            
            return {'success': True, 'groups': groups, 'count': len(groups)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def broadcast_message(self, message, delay=0, random_delay=False, auto_repeat=False, repeat_interval=300):
        try:
            self.stop_broadcast = False
            
            while True:
                selected_groups = self.db.get_selected_groups()
                
                if not selected_groups:
                    return {'success': False, 'error': 'No groups selected'}
                
                for group_data in selected_groups:
                    if self.stop_broadcast:
                        return {'success': False, 'message': 'Broadcast stopped by user'}
                    
                    phone = group_data['phone']
                    group_id = group_data['id']
                    
                    if phone not in self.clients:
                        self.db.increment_failed_count()
                        continue
                    
                    try:
                        client = self.clients[phone]
                        await client.send_message(group_id, message)
                        self.db.increment_messages_sent()
                        
                        current_delay = delay
                        if random_delay:
                            current_delay = random.randint(int(delay * 0.5), int(delay * 1.5))
                        
                        if current_delay > 0:
                            await asyncio.sleep(current_delay)
                    except Exception as e:
                        print(f"Error sending to {group_id}: {str(e)}")
                        self.db.increment_failed_count()
                        continue
                
                if not auto_repeat:
                    break
                
                if self.stop_broadcast:
                    break
                
                await asyncio.sleep(repeat_interval)
            
            return {'success': True, 'message': 'Broadcast completed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_account_status(self, phone):
        try:
            if phone in self.clients:
                client = self.clients[phone]
                if await client.is_user_authorized():
                    return 'online'
            
            session_file = os.path.join(SESSION_DIR, f'{phone}.session')
            if os.path.exists(f'{session_file}.session'):
                client = TelegramClient(session_file, self.api_id, self.api_hash)
                await client.connect()
                if await client.is_user_authorized():
                    self.clients[phone] = client
                    return 'online'
            
            return 'offline'
        except Exception as e:
            return 'offline'
    
    async def reconnect_account(self, phone):
        try:
            session_file = os.path.join(SESSION_DIR, f'{phone}.session')
            if os.path.exists(f'{session_file}.session'):
                if phone in self.clients:
                    try:
                        await self.clients[phone].disconnect()
                    except:
                        pass
                
                client = TelegramClient(session_file, self.api_id, self.api_hash)
                await client.connect()
                if await client.is_user_authorized():
                    self.clients[phone] = client
                    return {'success': True, 'message': 'Reconnected successfully'}
                else:
                    return {'success': False, 'error': 'Session expired'}
            else:
                return {'success': False, 'error': 'Session file not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def remove_account(self, phone):
        try:
            if phone in self.clients:
                asyncio.run(self.clients[phone].disconnect())
                del self.clients[phone]
            
            session_file = os.path.join(SESSION_DIR, f'{phone}.session')
            if os.path.exists(f'{session_file}.session'):
                os.remove(f'{session_file}.session')
            
            return True
        except Exception as e:
            print(f"Error removing account: {str(e)}")
            return False
