import requests
import json

class TelegramBotAPI:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f'https://api.telegram.org/bot{bot_token}'
    
    def get_me(self):
        response = requests.get(f'{self.base_url}/getMe')
        return response.json()
    
    def set_webhook(self, webhook_url):
        response = requests.post(f'{self.base_url}/setWebhook', json={'url': webhook_url})
        return response.json()
    
    def delete_webhook(self):
        response = requests.post(f'{self.base_url}/deleteWebhook')
        return response.json()
    
    def send_message(self, chat_id, text, reply_markup=None):
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        response = requests.post(f'{self.base_url}/sendMessage', json=data)
        return response.json()
    
    def send_photo(self, chat_id, photo_url, caption=None):
        data = {
            'chat_id': chat_id,
            'photo': photo_url
        }
        if caption:
            data['caption'] = caption
        
        response = requests.post(f'{self.base_url}/sendPhoto', json=data)
        return response.json()
    
    def answer_callback_query(self, callback_query_id, text=None):
        data = {'callback_query_id': callback_query_id}
        if text:
            data['text'] = text
        
        response = requests.post(f'{self.base_url}/answerCallbackQuery', json=data)
        return response.json()
    
    def create_inline_keyboard(self, buttons):
        return {
            'inline_keyboard': buttons
        }
    
    def create_web_app_keyboard(self, button_text, web_app_url):
        return {
            'inline_keyboard': [[{
                'text': button_text,
                'web_app': {'url': web_app_url}
            }]]
        }

def validate_bot_token(bot_token):
    try:
        api = TelegramBotAPI(bot_token)
        result = api.get_me()
        if result.get('ok'):
            return result['result']
        return None
    except:
        return None
