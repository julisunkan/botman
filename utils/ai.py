import google.generativeai as genai
import os

def init_gemini(api_key=None):
    if api_key:
        genai.configure(api_key=api_key)
    elif os.getenv('GEMINI_API_KEY'):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    else:
        return None
    
    return genai.GenerativeModel('gemini-pro')

def get_ai_response(message, api_key=None):
    try:
        model = init_gemini(api_key)
        if not model:
            return None
        
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return None
