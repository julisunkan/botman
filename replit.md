# BotForge Pro - Telegram Bot Creator

## Overview
BotForge Pro is a comprehensive web application for creating, managing, and deploying Telegram bots with advanced features including AI integration, tap-to-earn mining games, payment processing, and analytics.

## Tech Stack
- **Backend**: Flask 3.0.0 (Python 3.11)
- **Database**: SQLite with encrypted token storage
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **AI**: Google Gemini API integration
- **Security**: Fernet encryption (AES-128), Werkzeug password hashing
- **PWA**: Service Worker, Web Manifest

## Key Features

### 1. User Authentication
- Session-based authentication
- Password hashing with Werkzeug
- Secure registration and login system

### 2. Bot Management
- Create bots with Telegram token validation
- Automatic webhook setup
- Bot statistics and analytics
- Command system (text, photo, URL buttons)
- Delete and manage multiple bots

### 3. AI Integration
- Google Gemini AI for intelligent bot responses
- Toggle AI mode per bot
- Custom API key support
- Fallback to command-based responses

### 4. Tap-to-Earn Mining Game
- Customizable coin name and symbol
- Energy system with auto-recharge
- Tap rewards configuration
- Theme customization (colors, backgrounds)
- Real-time balance tracking
- Shop system for in-game items
- Task system with rewards

### 5. Telegram Mini-App (WebApp)
- Mobile-optimized interface
- Tap mechanics with visual feedback
- Energy bar visualization
- Tabs: Mine, Shop, Tasks
- Real-time progress updates

### 6. Template Library
- Pre-built bot templates:
  - AI Chatbot
  - Tap-to-Earn Mining
  - Payment Bot
  - NFT Verification
  - Referral System
  - Airdrop Manager

### 7. Progressive Web App
- Installable on mobile devices
- Offline functionality with Service Worker
- App manifest with icons
- Native app-like experience

## Project Structure
```
├── app.py                      # Main Flask application
├── utils/
│   ├── database.py            # Database operations
│   ├── telegram_api.py        # Telegram Bot API wrapper
│   ├── ai.py                  # Gemini AI integration
│   └── crypto.py              # Encryption utilities
├── templates/
│   ├── base.html              # Base template with navbar
│   ├── index.html             # Landing page
│   ├── login.html             # Login/Register page
│   ├── dashboard.html         # Main dashboard
│   ├── create_bot.html        # Create bot form
│   ├── bot_detail.html        # Bot management with tabs
│   ├── mining_settings.html   # Mining game configuration
│   ├── webapp.html            # Telegram Mini-App
│   └── templates.html         # Template marketplace
├── templates_library/         # Pre-built bot templates (JSON)
├── static/
│   ├── css/style.css          # Dark theme styles
│   ├── js/main.js             # Notifications and PWA
│   ├── icons/                 # PWA icons
│   ├── manifest.json          # PWA manifest
│   └── service-worker.js      # Service worker
├── requirements.txt           # Python dependencies
├── .encryption_key           # Auto-generated encryption key
└── botforge.db               # SQLite database

## Database Schema

### Tables
- **users**: User accounts (id, username, email, password_hash, created_at)
- **bots**: Telegram bots (id, user_id, bot_name, bot_token_encrypted, bot_username, description, webhook_url, ai_enabled, gemini_api_key_encrypted, created_at)
- **commands**: Bot commands (id, bot_id, command, response_type, response_content, url_link, button_text)
- **mining_settings**: Mining game config (id, bot_id, coin_name, coin_symbol, tap_reward, max_energy, energy_recharge_rate, colors)
- **shop_items**: In-game shop items (id, bot_id, item_name, price, currency, rewards)
- **tasks**: Social tasks with rewards (id, bot_id, task_name, task_type, reward_amount, requirement_value)
- **user_progress**: User game progress (id, bot_id, telegram_user_id, coin_balance, energy, total_taps, level, referral_code)
- **analytics**: Event tracking (id, bot_id, telegram_user_id, event_type, event_data, timestamp)

## Security Features
- Bot tokens and Gemini API keys encrypted with Fernet (AES-128)
- Passwords hashed with Werkzeug
- Session-based authentication
- SQL injection prevention (parameterized queries)
- XSS prevention (template escaping)
- Input validation with error handling

## Usage

### Getting Started
1. Visit the homepage and register an account
2. Login to access your dashboard
3. Create a new bot:
   - Get a bot token from @BotFather on Telegram
   - Enter bot name and token
   - Click "Create Bot"

### Setting Up a Bot
1. **Add Commands**: Define custom commands with responses
2. **Enable AI** (Optional): Toggle AI and add Gemini API key
3. **Configure Mining Game**: Set coin name, rewards, energy system, and theme
4. **Add Shop Items**: Create purchasable items with coin or TON pricing
5. **Create Tasks**: Set up social tasks with rewards
6. **Setup Webhook**: Click "Setup Webhook" to connect to Telegram

### Using the Mini-App
1. Send `/webapp` command to your bot in Telegram
2. Click the "Open Mini-App" button
3. Tap the coin to earn rewards
4. Energy recharges automatically
5. Complete tasks and buy items from the shop

## Environment Variables (Optional)
- `SESSION_SECRET`: Flask session secret key (auto-generated if not set)
- `GEMINI_API_KEY`: Default Gemini API key for AI features

## API Routes

### Authentication
- `POST /register`: User registration
- `POST /login`: User login
- `GET /logout`: User logout

### Bot Management
- `GET /dashboard`: View all bots
- `GET /create-bot`, `POST /create-bot`: Create new bot
- `GET /bot/<id>`: Bot detail page
- `POST /bot/<id>/delete`: Delete bot
- `POST /bot/<id>/setup-webhook`: Setup Telegram webhook
- `POST /bot/<id>/toggle-ai`: Enable/disable AI

### Commands
- `POST /bot/<id>/add-command`: Add command
- `POST /bot/<id>/update-command`: Update command
- `POST /bot/<id>/delete-command`: Delete command

### Mining & Shop
- `POST /bot/<id>/save-mining-settings`: Save mining configuration
- `POST /bot/<id>/add-shop-item`: Add shop item
- `POST /bot/<id>/delete-shop-item`: Delete shop item
- `POST /bot/<id>/add-task`: Add task
- `POST /bot/<id>/delete-task`: Delete task

### Telegram Integration
- `GET /bot/<id>/webapp`: Mini-app interface
- `POST /bot/<id>/tap`: Process tap action
- `GET /bot/<id>/get-progress`: Get user progress
- `POST /webhook/<id>`: Telegram webhook handler

### Templates
- `GET /templates`: Template library
- `POST /import-template`: Import template to bot

## Design Theme
- Dark background (#1a1a2e)
- Gradient accents (purple #9333ea to pink #ec4899)
- Glassmorphism effects with backdrop blur
- Smooth animations and transitions
- Mobile-first responsive design
- Inline notifications (no browser alerts)

## Recent Changes
- **2025-11-04**: Initial implementation with all core features
  - User authentication and bot management
  - Command system with multiple response types
  - Gemini AI integration
  - Tap-to-earn mining game with full configuration
  - Telegram Mini-App (WebApp)
  - Shop and task systems
  - Template library with pre-built bots
  - PWA features (manifest, service worker, icons)
  - Dark-themed UI with glassmorphism
  - Comprehensive error handling and validation

## User Preferences
- Inline notifications only (no browser alerts)
- Dark theme with gradient accents
- Mobile-optimized interfaces
- Secure token encryption

## Future Enhancements
- Complete TON blockchain wallet integration
- Advanced analytics dashboard with Chart.js
- Leaderboard system for mining game
- Boost items (energy limit, multi-tap, recharge speed)
- Export/import bot configurations
- Payment transaction verification
- Admin features for user management

## Notes
- Database initializes automatically on first run
- Encryption key auto-generated in `.encryption_key` file
- All bot tokens and API keys are encrypted at rest
- Service Worker enables offline functionality
- Application runs on port 5000 (0.0.0.0:5000)
