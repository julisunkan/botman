
import requests
import json

class TelegramBotAPI:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def set_webhook(self, webhook_url):
        """Set webhook for the bot"""
        url = f"{self.base_url}/setWebhook"
        params = {'url': webhook_url}
        try:
            response = requests.post(url, json=params, timeout=10)
            return response.json()
        except Exception as e:
            return {'ok': False, 'description': str(e)}
    
    def send_message(self, chat_id, text, reply_markup=None):
        """Send a text message"""
        url = f"{self.base_url}/sendMessage"
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            params['reply_markup'] = reply_markup
        try:
            response = requests.post(url, json=params, timeout=10)
            return response.json()
        except Exception as e:
            return {'ok': False, 'description': str(e)}
    
    def send_photo(self, chat_id, photo_url, caption=None):
        """Send a photo message"""
        url = f"{self.base_url}/sendPhoto"
        params = {
            'chat_id': chat_id,
            'photo': photo_url
        }
        if caption:
            params['caption'] = caption
        try:
            response = requests.post(url, json=params, timeout=10)
            return response.json()
        except Exception as e:
            return {'ok': False, 'description': str(e)}
    
    def create_inline_keyboard(self, buttons):
        """Create inline keyboard markup"""
        return json.dumps({'inline_keyboard': buttons})
    
    def create_web_app_keyboard(self, button_text, web_app_url):
        """Create web app keyboard"""
        return json.dumps({
            'inline_keyboard': [[{
                'text': button_text,
                'web_app': {'url': web_app_url}
            }]]
        })

def validate_bot_token(bot_token):
    """Validate bot token by calling getMe endpoint"""
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('ok'):
            return data.get('result')
        return None
    except Exception:
        return None
