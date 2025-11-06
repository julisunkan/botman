from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
import random
import string
from datetime import datetime, timedelta
import json

from utils.database import (
    init_db, create_user, get_user_by_username, get_user_by_id,
    create_bot, get_user_bots, get_bot_by_id, delete_bot,
    update_bot_webhook, toggle_bot_ai, update_bot_gemini_key, update_bot_ton_wallet,
    get_bot_commands, add_command, update_command, delete_command,
    get_mining_settings, save_mining_settings,
    get_shop_items, add_shop_item, delete_shop_item,
    get_tasks, add_task, delete_task,
    get_or_create_user_progress, update_user_progress,
    log_analytics_event, get_bot_analytics
)
from utils.crypto import encrypt_token, decrypt_token
from utils.telegram_api import TelegramBotAPI, validate_bot_token
from utils.ai import get_ai_response

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', secrets.token_hex(32))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

init_db()

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        password_hash = generate_password_hash(password)
        user_id = create_user(username, email, password_hash)
        
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    
    return render_template('login.html', register_mode=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    return render_template('login.html', register_mode=False)

@app.route('/generate-login', methods=['POST'])
def generate_login():
    adjectives = ['Swift', 'Bright', 'Bold', 'Clever', 'Noble', 'Cosmic', 'Digital', 'Cyber', 'Quantum', 'Elite']
    nouns = ['Bot', 'Creator', 'Builder', 'Master', 'Wizard', 'Engineer', 'Coder', 'Dev', 'Maker', 'Guru']
    
    max_attempts = 10
    for attempt in range(max_attempts):
        random_adjective = secrets.choice(adjectives)
        random_noun = secrets.choice(nouns)
        random_number = secrets.randbelow(9000) + 1000
        username = f"{random_adjective}{random_noun}{random_number}"
        
        password = secrets.token_urlsafe(16)
        
        email = f"{username.lower()}@botcreator.local"
        
        password_hash = generate_password_hash(password)
        user_id = create_user(username, email, password_hash)
        
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return jsonify({
                'success': True,
                'username': username,
                'password': password,
                'redirect': url_for('dashboard')
            })
    
    return jsonify({'success': False, 'message': 'Failed to generate unique credentials. Please try again.'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    bots = get_user_bots(user_id)
    
    bot_stats = []
    for bot in bots:
        analytics = get_bot_analytics(bot['id'])
        bot_stats.append({
            'bot': dict(bot),
            'stats': analytics
        })
    
    return render_template('dashboard.html', bot_stats=bot_stats)

@app.route('/create-bot', methods=['GET', 'POST'])
@login_required
def create_bot_route():
    if request.method == 'POST':
        bot_name = request.form.get('bot_name', '').strip()
        bot_token = request.form.get('bot_token', '').strip()
        description = request.form.get('description', '').strip()
        
        if not bot_name or not bot_token:
            return jsonify({'success': False, 'message': 'Bot name and token are required'}), 400
        
        bot_info = validate_bot_token(bot_token)
        if not bot_info:
            return jsonify({'success': False, 'message': 'Invalid bot token'}), 400
        
        encrypted_token = encrypt_token(bot_token)
        bot_username = bot_info.get('username', '')
        
        bot_id = create_bot(session['user_id'], bot_name, encrypted_token, bot_username, description)
        
        return jsonify({'success': True, 'redirect': url_for('bot_detail', bot_id=bot_id)})
    
    return render_template('create_bot.html')

@app.route('/bot/<int:bot_id>')
@login_required
def bot_detail(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return redirect(url_for('dashboard'))
    
    commands = get_bot_commands(bot_id)
    mining_settings = get_mining_settings(bot_id)
    shop_items = get_shop_items(bot_id)
    tasks = get_tasks(bot_id)
    analytics = get_bot_analytics(bot_id)
    
    return render_template('bot_detail.html', 
                         bot=dict(bot), 
                         commands=commands,
                         mining_settings=mining_settings,
                         shop_items=shop_items,
                         tasks=tasks,
                         analytics=analytics)

@app.route('/bot/<int:bot_id>/delete', methods=['POST'])
@login_required
def delete_bot_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    delete_bot(bot_id)
    return jsonify({'success': True, 'redirect': url_for('dashboard')})

@app.route('/bot/<int:bot_id>/setup-webhook', methods=['POST'])
@login_required
def setup_webhook(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    bot_token = decrypt_token(bot['bot_token'])
    
    replit_domain = os.getenv('REPLIT_DOMAINS')
    if replit_domain:
        webhook_url = f"https://{replit_domain}/webhook/{bot_id}"
    else:
        webhook_url = f"{request.host_url.rstrip('/')}/webhook/{bot_id}"
    
    api = TelegramBotAPI(bot_token)
    result = api.set_webhook(webhook_url)
    
    if result.get('ok'):
        update_bot_webhook(bot_id, webhook_url)
        return jsonify({'success': True, 'message': 'Webhook set successfully', 'webhook_url': webhook_url})
    else:
        error_msg = result.get('description', 'Failed to set webhook')
        return jsonify({'success': False, 'message': error_msg}), 400

@app.route('/bot/<int:bot_id>/toggle-ai', methods=['POST'])
@login_required
def toggle_ai_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    enabled = request.form.get('enabled') == 'true'
    gemini_key = request.form.get('gemini_key', '').strip()
    
    if enabled and gemini_key:
        encrypted_key = encrypt_token(gemini_key)
        update_bot_gemini_key(bot_id, encrypted_key)
    
    toggle_bot_ai(bot_id, enabled)
    return jsonify({'success': True, 'message': f'AI {"enabled" if enabled else "disabled"}'})

@app.route('/bot/<int:bot_id>/update-ton-wallet', methods=['POST'])
@login_required
def update_ton_wallet_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    wallet_address = request.form.get('wallet_address', '').strip()
    
    if wallet_address and not wallet_address.startswith('UQ'):
        return jsonify({'success': False, 'message': 'Invalid TON wallet address'}), 400
    
    update_bot_ton_wallet(bot_id, wallet_address)
    return jsonify({'success': True, 'message': 'TON wallet updated successfully'})

@app.route('/bot/<int:bot_id>/add-command', methods=['POST'])
@login_required
def add_command_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    command = request.form.get('command', '').strip().lower().replace('/', '')
    response_type = request.form.get('response_type', 'text')
    response_content = request.form.get('response_content', '').strip()
    url_link = request.form.get('url_link', '').strip()
    button_text = request.form.get('button_text', '').strip()
    
    if not command or not response_content:
        return jsonify({'success': False, 'message': 'Command and response are required'}), 400
    
    # Replace BOT_ID placeholder with actual bot_id
    if url_link:
        url_link = url_link.replace('BOT_ID', str(bot_id))
    
    command_id = add_command(bot_id, command, response_type, response_content, url_link, button_text)
    return jsonify({'success': True, 'message': 'Command added successfully', 'command_id': command_id})

@app.route('/bot/<int:bot_id>/update-command', methods=['POST'])
@login_required
def update_command_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    command_id = request.form.get('command_id')
    response_type = request.form.get('response_type', 'text')
    response_content = request.form.get('response_content', '').strip()
    url_link = request.form.get('url_link', '').strip()
    button_text = request.form.get('button_text', '').strip()
    
    # Replace BOT_ID placeholder with actual bot_id
    if url_link:
        url_link = url_link.replace('BOT_ID', str(bot_id))
    
    update_command(command_id, response_type, response_content, url_link, button_text)
    return jsonify({'success': True, 'message': 'Command updated successfully'})

@app.route('/bot/<int:bot_id>/delete-command', methods=['POST'])
@login_required
def delete_command_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    command_id = request.form.get('command_id')
    delete_command(command_id)
    return jsonify({'success': True, 'message': 'Command deleted successfully'})

@app.route('/bot/<int:bot_id>/save-mining-settings', methods=['POST'])
@login_required
def save_mining_settings_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        settings = {
            'coin_name': request.form.get('coin_name', 'Coin'),
            'coin_symbol': request.form.get('coin_symbol', '💎'),
            'initial_balance': int(request.form.get('initial_balance', 0)),
            'tap_reward': int(request.form.get('tap_reward', 1)),
            'max_energy': int(request.form.get('max_energy', 1000)),
            'energy_recharge_rate': int(request.form.get('energy_recharge_rate', 1)),
            'primary_color': request.form.get('primary_color', '#9333ea'),
            'secondary_color': request.form.get('secondary_color', '#ec4899'),
            'text_color': request.form.get('text_color', '#ffffff'),
            'background_color': request.form.get('background_color', '#1a1a2e'),
            'background_image_url': request.form.get('background_image_url', '')
        }
        
        if settings['initial_balance'] < 0 or settings['tap_reward'] < 1 or settings['max_energy'] < 100:
            return jsonify({'success': False, 'message': 'Invalid values: please check your input'}), 400
        
        save_mining_settings(bot_id, settings)
        return jsonify({'success': True, 'message': 'Mining settings saved successfully'})
    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': 'Invalid input: please enter valid numbers'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred while saving settings'}), 500

@app.route('/bot/<int:bot_id>/add-shop-item', methods=['POST'])
@login_required
def add_shop_item_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    item_name = request.form.get('item_name', '').strip()
    item_description = request.form.get('item_description', '').strip()
    price = float(request.form.get('price', 0))
    currency = request.form.get('currency', 'coins')
    reward_amount = request.form.get('reward_amount')
    reward_type = request.form.get('reward_type')
    
    if reward_amount:
        reward_amount = int(reward_amount)
    
    item_id = add_shop_item(bot_id, item_name, item_description, price, currency, reward_amount, reward_type)
    return jsonify({'success': True, 'message': 'Shop item added successfully', 'item_id': item_id})

@app.route('/bot/<int:bot_id>/delete-shop-item', methods=['POST'])
@login_required
def delete_shop_item_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    item_id = request.form.get('item_id')
    delete_shop_item(item_id)
    return jsonify({'success': True, 'message': 'Shop item deleted successfully'})

@app.route('/bot/<int:bot_id>/add-task', methods=['POST'])
@login_required
def add_task_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    task_name = request.form.get('task_name', '').strip()
    task_description = request.form.get('task_description', '').strip()
    task_type = request.form.get('task_type', 'telegram')
    reward_amount = int(request.form.get('reward_amount', 0))
    reward_type = request.form.get('reward_type', 'coins')
    requirement_value = request.form.get('requirement_value', '').strip()
    
    task_id = add_task(bot_id, task_name, task_description, task_type, reward_amount, reward_type, requirement_value)
    return jsonify({'success': True, 'message': 'Task added successfully', 'task_id': task_id})

@app.route('/bot/<int:bot_id>/delete-task', methods=['POST'])
@login_required
def delete_task_route(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    task_id = request.form.get('task_id')
    delete_task(task_id)
    return jsonify({'success': True, 'message': 'Task deleted successfully'})

@app.route('/bot/<int:bot_id>/users')
@login_required
def bot_users(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return redirect(url_for('dashboard'))
    
    from utils.database import get_bot_unique_users
    users = get_bot_unique_users(bot_id)
    
    return render_template('bot_users.html', bot=dict(bot), users=users)

@app.route('/bot/<int:bot_id>/user/<int:telegram_user_id>')
@login_required
def user_detail(bot_id, telegram_user_id):
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return redirect(url_for('dashboard'))
    
    from utils.database import get_user_analytics
    user_progress = get_or_create_user_progress(bot_id, telegram_user_id)
    user_analytics = get_user_analytics(bot_id, telegram_user_id)
    
    return render_template('user_detail.html',
                         bot=dict(bot),
                         telegram_user_id=telegram_user_id,
                         user_progress=dict(user_progress),
                         analytics=user_analytics)

@app.route('/bot/<int:bot_id>/webapp', defaults={'webapp_type': 'mining'})
@app.route('/bot/<int:bot_id>/webapp/', defaults={'webapp_type': 'mining'})
@app.route('/bot/<int:bot_id>/webapp/<webapp_type>')
@app.route('/bot/<int:bot_id>/webapp/<webapp_type>/')
def webapp(bot_id, webapp_type):
    bot = get_bot_by_id(bot_id)
    if not bot:
        return "Bot not found", 404
    
    telegram_user_id = request.args.get('user_id', 12345)
    
    if webapp_type == 'ai':
        return render_template('webapp_ai.html', 
                             bot=dict(bot),
                             telegram_user_id=telegram_user_id)
    elif webapp_type == 'payment':
        shop_items = get_shop_items(bot_id)
        return render_template('webapp_payment.html',
                             bot=dict(bot),
                             shop_items=shop_items,
                             telegram_user_id=telegram_user_id)
    elif webapp_type == 'quiz':
        return render_template('webapp_quiz.html',
                             bot=dict(bot),
                             telegram_user_id=telegram_user_id)
    elif webapp_type == 'news':
        return render_template('webapp_news.html',
                             bot=dict(bot),
                             telegram_user_id=telegram_user_id)
    elif webapp_type == 'referral':
        return render_template('webapp_referral.html',
                             bot=dict(bot),
                             telegram_user_id=telegram_user_id)
    elif webapp_type == 'fitness':
        return render_template('webapp_fitness.html',
                             bot=dict(bot),
                             telegram_user_id=telegram_user_id)
    elif webapp_type == 'event':
        return render_template('webapp_event.html',
                             bot=dict(bot),
                             telegram_user_id=telegram_user_id)
    else:
        mining_settings = get_mining_settings(bot_id)
        shop_items = get_shop_items(bot_id)
        tasks = get_tasks(bot_id)
        
        return render_template('webapp.html', 
                             bot=dict(bot),
                             mining_settings=mining_settings,
                             shop_items=shop_items,
                             tasks=tasks,
                             telegram_user_id=telegram_user_id)

@app.route('/bot/<int:bot_id>/tap', methods=['POST'])
def tap(bot_id):
    data = request.get_json()
    telegram_user_id = data.get('telegram_user_id')
    
    if not telegram_user_id:
        return jsonify({'success': False, 'message': 'User ID required'}), 400
    
    progress = get_or_create_user_progress(bot_id, telegram_user_id)
    mining_settings = get_mining_settings(bot_id)
    
    if not mining_settings:
        return jsonify({'success': False, 'message': 'Mining not configured'}), 400
    
    current_energy = progress['energy']
    if current_energy <= 0:
        return jsonify({'success': False, 'message': 'No energy'}), 400
    
    tap_reward = mining_settings['tap_reward']
    new_balance = progress['coin_balance'] + tap_reward
    new_energy = current_energy - 1
    new_taps = progress['total_taps'] + 1
    
    update_user_progress(bot_id, telegram_user_id, new_balance, new_energy, new_taps)
    log_analytics_event(bot_id, telegram_user_id, 'tap')
    
    return jsonify({
        'success': True,
        'coin_balance': new_balance,
        'energy': new_energy,
        'total_taps': new_taps
    })

@app.route('/bot/<int:bot_id>/get-progress', methods=['GET'])
def get_progress(bot_id):
    telegram_user_id = request.args.get('user_id')
    
    if not telegram_user_id:
        return jsonify({'success': False, 'message': 'User ID required'}), 400
    
    progress = get_or_create_user_progress(bot_id, int(telegram_user_id))
    mining_settings = get_mining_settings(bot_id)
    
    if progress['last_tap_time']:
        last_tap = datetime.fromisoformat(progress['last_tap_time'])
        time_passed = (datetime.now() - last_tap).total_seconds()
        energy_recovered = int(time_passed * mining_settings['energy_recharge_rate'] / 60)
        new_energy = min(progress['energy'] + energy_recovered, mining_settings['max_energy'])
        
        if new_energy != progress['energy']:
            update_user_progress(bot_id, int(telegram_user_id), progress['coin_balance'], new_energy, progress['total_taps'])
            progress = get_or_create_user_progress(bot_id, int(telegram_user_id))
    
    return jsonify({
        'success': True,
        'coin_balance': progress['coin_balance'],
        'energy': progress['energy'],
        'total_taps': progress['total_taps'],
        'level': progress['level']
    })

@app.route('/bot/<int:bot_id>/purchase-item', methods=['POST'])
def purchase_item(bot_id):
    data = request.get_json()
    telegram_user_id = data.get('telegram_user_id')
    item_id = data.get('item_id')
    
    if not telegram_user_id or not item_id:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    shop_items = get_shop_items(bot_id)
    item = next((i for i in shop_items if i['id'] == item_id), None)
    
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    if item['currency'] != 'coins':
        return jsonify({'success': False, 'message': 'This item requires TON payment'}), 400
    
    progress = get_or_create_user_progress(bot_id, int(telegram_user_id))
    
    if progress['coin_balance'] < item['price']:
        return jsonify({'success': False, 'message': 'Insufficient coins'}), 400
    
    new_balance = progress['coin_balance'] - int(item['price'])
    update_user_progress(bot_id, int(telegram_user_id), new_balance, progress['energy'], progress['total_taps'])
    log_analytics_event(bot_id, telegram_user_id, 'shop_purchase', {'item_id': item_id, 'price': item['price']})
    
    return jsonify({
        'success': True,
        'coin_balance': new_balance,
        'message': 'Purchase successful!'
    })

@app.route('/webhook/<int:bot_id>', methods=['POST'])
def webhook_handler(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot:
        return 'Bot not found', 404
    
    update = request.get_json()
    
    if 'message' in update:
        message = update['message']
        chat_id = message['chat']['id']
        telegram_user_id = message['from']['id']
        text = message.get('text', '')
        
        bot_token = decrypt_token(bot['bot_token'])
        api = TelegramBotAPI(bot_token)
        
        log_analytics_event(bot_id, telegram_user_id, 'message', {'text': text})
        
        if text.startswith('/'):
            command = text[1:].split()[0].lower()
            
            log_analytics_event(bot_id, telegram_user_id, 'command', command)
            
            if command == 'webapp':
                webapp_url = f"{request.host_url.rstrip('/')}/bot/{bot_id}/webapp?user_id={telegram_user_id}"
                keyboard = api.create_web_app_keyboard('🎮 Open Mini-App', webapp_url)
                api.send_message(chat_id, '🎮 Click the button below to open the mini-app:', keyboard)
                return 'OK'
            
            if command == 'start':
                # Check if there's a custom start command
                commands = get_bot_commands(bot_id)
                start_cmd = next((cmd for cmd in commands if cmd['command'] == 'start'), None)
                
                if start_cmd:
                    if start_cmd['response_type'] == 'url_button':
                        # Replace BOT_ID placeholder with actual bot_id
                        url_link = start_cmd['url_link'].replace('BOT_ID', str(bot_id))
                        webapp_url = f"{request.host_url.rstrip('/')}{url_link}?user_id={telegram_user_id}"
                        keyboard = api.create_web_app_keyboard(start_cmd['button_text'], webapp_url)
                        api.send_message(chat_id, start_cmd['response_content'], keyboard)
                    elif start_cmd['response_type'] == 'text':
                        api.send_message(chat_id, start_cmd['response_content'])
                    elif start_cmd['response_type'] == 'photo':
                        api.send_photo(chat_id, start_cmd['response_content'])
                    return 'OK'
            
            commands = get_bot_commands(bot_id)
            for cmd in commands:
                if cmd['command'] == command:
                    if cmd['response_type'] == 'text':
                        api.send_message(chat_id, cmd['response_content'])
                    elif cmd['response_type'] == 'photo':
                        api.send_photo(chat_id, cmd['response_content'])
                    elif cmd['response_type'] == 'url_button':
                        # Replace BOT_ID placeholder
                        url_link = cmd['url_link'].replace('BOT_ID', str(bot_id))
                        
                        # Check if it's an internal webapp URL (contains /bot/)
                        if '/bot/' in url_link:
                            # Internal webapp - add user_id parameter
                            webapp_url = f"{request.host_url.rstrip('/')}{url_link}?user_id={telegram_user_id}"
                            keyboard = api.create_web_app_keyboard(cmd['button_text'], webapp_url)
                        else:
                            # External URL - use web_app to load it seamlessly in Telegram
                            keyboard = api.create_web_app_keyboard(cmd['button_text'], url_link)
                        
                        api.send_message(chat_id, cmd['response_content'], keyboard)
                    return 'OK'
            
            if bot['ai_enabled']:
                gemini_key = decrypt_token(bot['gemini_api_key']) if bot['gemini_api_key'] else None
                ai_response = get_ai_response(text, gemini_key)
                if ai_response:
                    api.send_message(chat_id, ai_response)
                    return 'OK'
            
            api.send_message(chat_id, f"Unknown command: /{command}")
        
        elif bot['ai_enabled']:
            gemini_key = decrypt_token(bot['gemini_api_key']) if bot['gemini_api_key'] else None
            ai_response = get_ai_response(text, gemini_key)
            if ai_response:
                api.send_message(chat_id, ai_response)
    
    return 'OK'

@app.route('/templates')
@login_required
def templates():
    return render_template('templates.html')

@app.route('/api/user-bots')
@login_required
def api_user_bots():
    user_id = session['user_id']
    bots = get_user_bots(user_id)
    return jsonify({'success': True, 'bots': [{'id': bot['id'], 'bot_name': bot['bot_name']} for bot in bots]})

@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    data = request.get_json()
    bot_id = data.get('bot_id')
    message = data.get('message')
    telegram_user_id = data.get('user_id')
    
    if not bot_id or not message:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    bot = get_bot_by_id(bot_id)
    if not bot or not bot['ai_enabled']:
        return jsonify({'success': False, 'message': 'AI not enabled'}), 400
    
    gemini_key = decrypt_token(bot['gemini_api_key']) if bot['gemini_api_key'] else None
    ai_response = get_ai_response(message, gemini_key)
    
    if ai_response:
        log_analytics_event(bot_id, telegram_user_id, 'ai_chat', {'message': message})
        return jsonify({'success': True, 'response': ai_response})
    else:
        return jsonify({'success': False, 'message': 'AI service unavailable'}), 500

@app.route('/import-template', methods=['POST'])
@login_required
def import_template():
    template_id = request.form.get('template_id')
    bot_id = request.form.get('bot_id')
    
    bot = get_bot_by_id(bot_id)
    if not bot or bot['user_id'] != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    template_file = f'templates_library/{template_id}.json'
    if not os.path.exists(template_file):
        return jsonify({'success': False, 'message': 'Template not found'}), 404
    
    with open(template_file, 'r') as f:
        template = json.load(f)
    
    # Get webapp_type from template, default to 'mining'
    webapp_type = template.get('webapp_type', 'mining')
    
    for cmd in template.get('commands', []):
        url_link = cmd.get('url_link', '')
        if url_link:
            # Replace BOT_ID placeholder
            url_link = url_link.replace('BOT_ID', str(bot_id))
            
            # If URL contains /webapp, ensure it has the correct type
            if '/webapp' in url_link:
                if webapp_type != 'mining':
                    # Replace /webapp or /webapp/ with /webapp/{type}
                    url_link = url_link.replace('/webapp/', f'/webapp/{webapp_type}')
                    url_link = url_link.replace('/webapp', f'/webapp/{webapp_type}')
        add_command(bot_id, cmd['command'], cmd['response_type'], 
                   cmd['response_content'], url_link, cmd.get('button_text'))
    
    if 'mining_settings' in template:
        save_mining_settings(bot_id, template['mining_settings'])
    
    return jsonify({'success': True, 'message': 'Template imported successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
