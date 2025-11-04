import os
from cryptography.fernet import Fernet

ENCRYPTION_KEY_FILE = '.encryption_key'

def get_encryption_key():
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        return key

def encrypt_token(token):
    if not token:
        return None
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    if not encrypted_token:
        return None
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()
