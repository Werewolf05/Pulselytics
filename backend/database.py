"""
Database models and utilities for Pulselytics
Uses SQLite for storing clients, API keys, and application settings
"""

import os
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

# Import encryption utilities
try:
    from encryption import encrypt_value, decrypt_value, mask_api_key
    ENCRYPTION_AVAILABLE = True
except ImportError:
    # Fallback to basic encoding if cryptography not installed
    import base64
    ENCRYPTION_AVAILABLE = False
    
    def encrypt_value(value: str) -> str:
        if not value:
            return ''
        return base64.b64encode(value.encode()).decode()
    
    def decrypt_value(encrypted: str) -> str:
        if not encrypted:
            return ''
        try:
            return base64.b64decode(encrypted.encode()).decode()
        except:
            return ''
    
    def mask_api_key(api_key: str) -> str:
        if not api_key or len(api_key) <= 8:
            return '****'
        return api_key[:4] + '****' + api_key[-4:]

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'pulselytics.db')


def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_database():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            instagram_username TEXT,
            youtube_channel TEXT,
            twitter_username TEXT,
            facebook_page TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # API Keys table - encrypted storage
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'default',
            platform TEXT NOT NULL,
            api_key TEXT NOT NULL,
            api_secret TEXT,
            access_token TEXT,
            refresh_token TEXT,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, platform)
        )
    ''')
    
    # API Usage tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'default',
            platform TEXT NOT NULL,
            endpoint TEXT,
            requests_made INTEGER DEFAULT 0,
            quota_limit INTEGER,
            reset_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, platform, reset_date)
        )
    ''')
    
    # Scrape History
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrape_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            status TEXT NOT NULL,
            posts_fetched INTEGER DEFAULT 0,
            error_message TEXT,
            scrape_method TEXT,
            duration_seconds REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
    ''')
    
    # Application Settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            data_type TEXT DEFAULT 'string',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_keys_platform ON api_keys(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scrape_history_client ON scrape_history(client_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scrape_history_created ON scrape_history(created_at)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {DB_PATH}")


# ==================== CLIENT MANAGEMENT ====================

def create_client(client_id: str, name: str, platforms: Dict[str, str]) -> bool:
    """Create a new client"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clients (id, name, instagram_username, youtube_channel, 
                               twitter_username, facebook_page)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            client_id,
            name,
            platforms.get('instagram', ''),
            platforms.get('youtube', ''),
            platforms.get('twitter', ''),
            platforms.get('facebook', '')
        ))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_client(client_id: str) -> Optional[Dict]:
    """Get a single client by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_all_clients() -> List[Dict]:
    """Get all clients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clients ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_client(client_id: str, data: Dict) -> bool:
    """Update a client"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE clients 
            SET name = ?, 
                instagram_username = ?,
                youtube_channel = ?,
                twitter_username = ?,
                facebook_page = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('name'),
            data.get('instagram_username', ''),
            data.get('youtube_channel', ''),
            data.get('twitter_username', ''),
            data.get('facebook_page', ''),
            client_id
        ))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error updating client: {e}")
        return False


def delete_client(client_id: str) -> bool:
    """Delete a client and all associated data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return success


# ==================== API KEY MANAGEMENT ====================

def save_api_key(platform: str, api_key: str, user_id: str = 'default', 
                 api_secret: str = None, access_token: str = None) -> bool:
    """Save or update an API key for a platform"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Encrypt sensitive data
        encrypted_key = encrypt_value(api_key)
        encrypted_secret = encrypt_value(api_secret) if api_secret else None
        encrypted_token = encrypt_value(access_token) if access_token else None
        
        cursor.execute('''
            INSERT INTO api_keys (user_id, platform, api_key, api_secret, access_token)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, platform) 
            DO UPDATE SET 
                api_key = excluded.api_key,
                api_secret = excluded.api_secret,
                access_token = excluded.access_token,
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, platform, encrypted_key, encrypted_secret, encrypted_token))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False


def get_api_key(platform: str, user_id: str = 'default') -> Optional[Dict]:
    """Get API key for a platform"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM api_keys 
        WHERE user_id = ? AND platform = ? AND is_active = 1
    ''', (user_id, platform))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        # Decrypt values
        data['api_key'] = decrypt_value(data['api_key'])
        if data.get('api_secret'):
            data['api_secret'] = decrypt_value(data['api_secret'])
        if data.get('access_token'):
            data['access_token'] = decrypt_value(data['access_token'])
        return data
    return None


def get_all_api_keys(user_id: str = 'default') -> Dict[str, Dict]:
    """Get all API keys for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT platform, api_key, created_at, updated_at, is_active
        FROM api_keys 
        WHERE user_id = ?
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    result = {}
    for row in rows:
        row_dict = dict(row)
        platform = row_dict['platform']
        # Return masked key for security
        api_key = decrypt_value(row_dict['api_key'])
        masked_key = mask_api_key(api_key)
        
        result[platform] = {
            'masked_key': masked_key,
            'is_active': bool(row_dict['is_active']),
            'created_at': row_dict['created_at'],
            'updated_at': row_dict['updated_at']
        }
    
    return result


def delete_api_key(platform: str, user_id: str = 'default') -> bool:
    """Delete an API key"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM api_keys 
        WHERE user_id = ? AND platform = ?
    ''', (user_id, platform))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


# ==================== SCRAPE HISTORY ====================

def log_scrape(client_id: str, platform: str, status: str, posts_fetched: int = 0,
               error_message: str = None, scrape_method: str = None, duration: float = None):
    """Log a scrape operation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scrape_history 
        (client_id, platform, status, posts_fetched, error_message, scrape_method, duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (client_id, platform, status, posts_fetched, error_message, scrape_method, duration))
    
    conn.commit()
    conn.close()


def get_scrape_history(client_id: str = None, limit: int = 50) -> List[Dict]:
    """Get scrape history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if client_id:
        cursor.execute('''
            SELECT * FROM scrape_history 
            WHERE client_id = ?
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (client_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM scrape_history 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ==================== SETTINGS ====================

def set_setting(key: str, value: any, data_type: str = 'string'):
    """Set an application setting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert value to string for storage
    if data_type == 'json':
        value_str = json.dumps(value)
    elif data_type == 'bool':
        value_str = '1' if value else '0'
    else:
        value_str = str(value)
    
    cursor.execute('''
        INSERT INTO settings (key, value, data_type)
        VALUES (?, ?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
    ''', (key, value_str, data_type))
    
    conn.commit()
    conn.close()


def get_setting(key: str, default: any = None) -> any:
    """Get an application setting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT value, data_type FROM settings WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        value_str = row['value']
        data_type = row['data_type']
        
        if data_type == 'json':
            return json.loads(value_str)
        elif data_type == 'bool':
            return value_str == '1'
        elif data_type == 'int':
            return int(value_str)
        elif data_type == 'float':
            return float(value_str)
        else:
            return value_str
    
    return default


# ==================== MIGRATION ====================

def migrate_from_json():
    """Migrate existing JSON client data to SQLite database"""
    import glob
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data')
    
    if not os.path.exists(data_dir):
        print("No existing data directory found")
        return
    
    migrated = 0
    for json_file in glob.glob(os.path.join(data_dir, '*.json')):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            client_id = os.path.splitext(os.path.basename(json_file))[0]
            
            # Extract platform usernames
            platforms = {
                'instagram': data.get('instagram_username', ''),
                'youtube': data.get('youtube_channel', ''),
                'twitter': data.get('twitter_username', ''),
                'facebook': data.get('facebook_page', '')
            }
            
            if create_client(client_id, data.get('name', client_id), platforms):
                migrated += 1
                print(f"✅ Migrated client: {client_id}")
        except Exception as e:
            print(f"❌ Error migrating {json_file}: {e}")
    
    print(f"\n✅ Migration complete: {migrated} clients migrated")


# ==================== INITIALIZATION ====================

if __name__ == '__main__':
    print("Initializing Pulselytics Database...")
    init_database()
    
    # Ask user if they want to migrate existing data
    response = input("\nMigrate existing JSON client data? (y/n): ")
    if response.lower() == 'y':
        migrate_from_json()
    
    print("\n✅ Database setup complete!")
