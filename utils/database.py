import sqlite3
import os
from datetime import datetime
import json

DATABASE_FILE = 'botforge.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bot_name TEXT NOT NULL,
            bot_token TEXT NOT NULL,
            bot_username TEXT,
            description TEXT,
            webhook_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            ai_enabled BOOLEAN DEFAULT 0,
            gemini_api_key TEXT,
            ton_wallet TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER NOT NULL,
            command TEXT NOT NULL,
            response_type TEXT NOT NULL,
            response_content TEXT,
            url_link TEXT,
            button_text TEXT,
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mining_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER UNIQUE NOT NULL,
            coin_name TEXT DEFAULT 'Coin',
            coin_symbol TEXT DEFAULT '💎',
            initial_balance INTEGER DEFAULT 0,
            tap_reward INTEGER DEFAULT 1,
            max_energy INTEGER DEFAULT 1000,
            energy_recharge_rate INTEGER DEFAULT 1,
            primary_color TEXT DEFAULT '#9333ea',
            secondary_color TEXT DEFAULT '#ec4899',
            text_color TEXT DEFAULT '#ffffff',
            background_color TEXT DEFAULT '#1a1a2e',
            background_image_url TEXT,
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            item_description TEXT,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'coins',
            reward_amount INTEGER,
            reward_type TEXT,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            task_description TEXT,
            task_type TEXT NOT NULL,
            reward_amount INTEGER NOT NULL,
            reward_type TEXT NOT NULL,
            requirement_value TEXT,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER NOT NULL,
            telegram_user_id INTEGER NOT NULL,
            coin_balance INTEGER DEFAULT 0,
            energy INTEGER DEFAULT 1000,
            last_tap_time TIMESTAMP,
            total_taps INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            referral_code TEXT,
            referred_by TEXT,
            UNIQUE(bot_id, telegram_user_id),
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER NOT NULL,
            telegram_user_id INTEGER,
            event_type TEXT NOT NULL,
            event_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bots_user_id ON bots(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_commands_bot_id ON commands(bot_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_bot_id ON analytics(bot_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_progress_bot_telegram ON user_progress(bot_id, telegram_user_id)')

    conn.commit()
    conn.close()

def create_user(username, email, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      (username, email, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def create_bot(user_id, bot_name, bot_token, bot_username, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO bots (user_id, bot_name, bot_token, bot_username, description)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, bot_name, bot_token, bot_username, description))
    conn.commit()
    bot_id = cursor.lastrowid
    conn.close()
    return bot_id

def get_user_bots(user_id):
    conn = get_db_connection()
    bots = conn.execute('SELECT * FROM bots WHERE user_id = ? ORDER BY created_at DESC',
                       (user_id,)).fetchall()
    conn.close()
    return bots

def get_bot_by_id(bot_id):
    conn = get_db_connection()
    bot = conn.execute('SELECT * FROM bots WHERE id = ?', (bot_id,)).fetchone()
    conn.close()
    return bot

def delete_bot(bot_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM bots WHERE id = ?', (bot_id,))
    conn.commit()
    conn.close()

def update_bot_webhook(bot_id, webhook_url):
    conn = get_db_connection()
    conn.execute('UPDATE bots SET webhook_url = ? WHERE id = ?', (webhook_url, bot_id))
    conn.commit()
    conn.close()

def toggle_bot_ai(bot_id, enabled):
    conn = get_db_connection()
    conn.execute('UPDATE bots SET ai_enabled = ? WHERE id = ?', (enabled, bot_id))
    conn.commit()
    conn.close()

def update_bot_gemini_key(bot_id, encrypted_key):
    conn = get_db_connection()
    conn.execute('UPDATE bots SET gemini_api_key = ? WHERE id = ?', (encrypted_key, bot_id))
    conn.commit()
    conn.close()

def update_bot_ton_wallet(bot_id, ton_wallet_address):
    conn = get_db_connection()
    conn.execute('UPDATE bots SET ton_wallet = ? WHERE id = ?', (ton_wallet_address, bot_id))
    conn.commit()
    conn.close()

def get_bot_commands(bot_id):
    conn = get_db_connection()
    commands = conn.execute('SELECT * FROM commands WHERE bot_id = ? ORDER BY command',
                           (bot_id,)).fetchall()
    conn.close()
    return commands

def add_command(bot_id, command, response_type, response_content, url_link=None, button_text=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO commands (bot_id, command, response_type, response_content, url_link, button_text)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (bot_id, command, response_type, response_content, url_link, button_text))
    conn.commit()
    command_id = cursor.lastrowid
    conn.close()
    return command_id

def update_command(command_id, response_type, response_content, url_link=None, button_text=None):
    conn = get_db_connection()
    conn.execute('''UPDATE commands SET response_type = ?, response_content = ?, url_link = ?, button_text = ?
                   WHERE id = ?''',
                (response_type, response_content, url_link, button_text, command_id))
    conn.commit()
    conn.close()

def delete_command(command_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM commands WHERE id = ?', (command_id,))
    conn.commit()
    conn.close()

def get_mining_settings(bot_id):
    conn = get_db_connection()
    settings = conn.execute('SELECT * FROM mining_settings WHERE bot_id = ?', (bot_id,)).fetchone()
    conn.close()
    return settings

def save_mining_settings(bot_id, settings):
    conn = get_db_connection()
    cursor = conn.cursor()

    existing = cursor.execute('SELECT id FROM mining_settings WHERE bot_id = ?', (bot_id,)).fetchone()

    if existing:
        cursor.execute('''UPDATE mining_settings SET
                         coin_name = ?, coin_symbol = ?, initial_balance = ?, tap_reward = ?,
                         max_energy = ?, energy_recharge_rate = ?, primary_color = ?,
                         secondary_color = ?, text_color = ?, background_color = ?, background_image_url = ?
                         WHERE bot_id = ?''',
                      (settings['coin_name'], settings['coin_symbol'], settings['initial_balance'],
                       settings['tap_reward'], settings['max_energy'], settings['energy_recharge_rate'],
                       settings['primary_color'], settings['secondary_color'], settings['text_color'],
                       settings['background_color'], settings.get('background_image_url'), bot_id))
    else:
        cursor.execute('''INSERT INTO mining_settings
                         (bot_id, coin_name, coin_symbol, initial_balance, tap_reward, max_energy,
                          energy_recharge_rate, primary_color, secondary_color, text_color,
                          background_color, background_image_url)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (bot_id, settings['coin_name'], settings['coin_symbol'], settings['initial_balance'],
                       settings['tap_reward'], settings['max_energy'], settings['energy_recharge_rate'],
                       settings['primary_color'], settings['secondary_color'], settings['text_color'],
                       settings['background_color'], settings.get('background_image_url')))

    conn.commit()
    conn.close()

def get_shop_items(bot_id):
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM shop_items WHERE bot_id = ? AND is_active = 1', (bot_id,)).fetchall()
    conn.close()
    return items

def add_shop_item(bot_id, item_name, item_description, price, currency, reward_amount=None, reward_type=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO shop_items (bot_id, item_name, item_description, price, currency, reward_amount, reward_type)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (bot_id, item_name, item_description, price, currency, reward_amount, reward_type))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def delete_shop_item(item_id):
    conn = get_db_connection()
    conn.execute('UPDATE shop_items SET is_active = 0 WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def get_tasks(bot_id):
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks WHERE bot_id = ? AND is_active = 1', (bot_id,)).fetchall()
    conn.close()
    return tasks

def add_task(bot_id, task_name, task_description, task_type, reward_amount, reward_type, requirement_value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO tasks (bot_id, task_name, task_description, task_type, reward_amount, reward_type, requirement_value)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (bot_id, task_name, task_description, task_type, reward_amount, reward_type, requirement_value))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET is_active = 0 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def get_or_create_user_progress(bot_id, telegram_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    progress = cursor.execute('SELECT * FROM user_progress WHERE bot_id = ? AND telegram_user_id = ?',
                             (bot_id, telegram_user_id)).fetchone()

    if not progress:
        settings = get_mining_settings(bot_id)
        initial_balance = settings['initial_balance'] if settings else 0
        max_energy = settings['max_energy'] if settings else 1000

        cursor.execute('''INSERT INTO user_progress (bot_id, telegram_user_id, coin_balance, energy)
                         VALUES (?, ?, ?, ?)''',
                      (bot_id, telegram_user_id, initial_balance, max_energy))
        conn.commit()
        progress = cursor.execute('SELECT * FROM user_progress WHERE bot_id = ? AND telegram_user_id = ?',
                                 (bot_id, telegram_user_id)).fetchone()

    conn.close()
    return progress

def update_user_progress(bot_id, telegram_user_id, coin_balance, energy, total_taps):
    conn = get_db_connection()
    conn.execute('''UPDATE user_progress SET coin_balance = ?, energy = ?, total_taps = ?, last_tap_time = CURRENT_TIMESTAMP
                   WHERE bot_id = ? AND telegram_user_id = ?''',
                (coin_balance, energy, total_taps, bot_id, telegram_user_id))
    conn.commit()
    conn.close()

def log_analytics_event(bot_id, telegram_user_id, event_type, event_data=None):
    conn = get_db_connection()
    event_data_json = json.dumps(event_data) if event_data else None
    conn.execute('INSERT INTO analytics (bot_id, telegram_user_id, event_type, event_data) VALUES (?, ?, ?, ?)',
                (bot_id, telegram_user_id, event_type, event_data_json))
    conn.commit()
    conn.close()

def get_bot_analytics(bot_id):
    conn = get_db_connection()

    total_messages = conn.execute(
        'SELECT COUNT(*) as count FROM analytics WHERE bot_id = ? AND event_type = "message"',
        (bot_id,)).fetchone()['count']

    unique_users = conn.execute(
        'SELECT COUNT(DISTINCT telegram_user_id) as count FROM analytics WHERE bot_id = ?',
        (bot_id,)).fetchone()['count']

    command_stats = conn.execute(
        'SELECT event_data, COUNT(*) as count FROM analytics WHERE bot_id = ? AND event_type = "command" GROUP BY event_data',
        (bot_id,)).fetchall()

    conn.close()

    return {
        'total_messages': total_messages,
        'unique_users': unique_users,
        'command_stats': command_stats
    }

def get_bot_users_list(bot_id):
    conn = get_db_connection()
    
    users = conn.execute('''
        SELECT 
            up.telegram_user_id,
            up.coin_balance,
            up.energy,
            up.total_taps,
            up.level,
            up.last_tap_time,
            COUNT(DISTINCT a.id) as total_interactions,
            MIN(a.timestamp) as first_seen,
            MAX(a.timestamp) as last_seen
        FROM user_progress up
        LEFT JOIN analytics a ON a.bot_id = up.bot_id AND a.telegram_user_id = up.telegram_user_id
        WHERE up.bot_id = ?
        GROUP BY up.telegram_user_id
        ORDER BY last_seen DESC
    ''', (bot_id,)).fetchall()
    
    conn.close()
    return users

def get_user_detail(bot_id, telegram_user_id):
    conn = get_db_connection()
    
    # Get user progress
    progress = conn.execute(
        'SELECT * FROM user_progress WHERE bot_id = ? AND telegram_user_id = ?',
        (bot_id, telegram_user_id)
    ).fetchone()
    
    # Get user activity
    activities = conn.execute('''
        SELECT event_type, event_data, timestamp 
        FROM analytics 
        WHERE bot_id = ? AND telegram_user_id = ?
        ORDER BY timestamp DESC
        LIMIT 50
    ''', (bot_id, telegram_user_id)).fetchall()
    
    # Get interaction stats
    stats = conn.execute('''
        SELECT 
            event_type,
            COUNT(*) as count
        FROM analytics
        WHERE bot_id = ? AND telegram_user_id = ?
        GROUP BY event_type
    ''', (bot_id, telegram_user_id)).fetchall()
    
    conn.close()
    
    return {
        'progress': dict(progress) if progress else None,
        'activities': [dict(a) for a in activities],
        'stats': [dict(s) for s in stats]
    }