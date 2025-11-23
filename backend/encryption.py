"""
Secure encryption for API keys and sensitive data
Uses Fernet symmetric encryption from cryptography library
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Encryption key file
KEY_FILE = os.path.join(os.path.dirname(__file__), '.encryption_key')


def _get_or_create_key() -> bytes:
    """Get existing encryption key or create a new one"""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        # Generate a new key
        key = Fernet.generate_key()
        
        # Save it securely
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        
        # Set file permissions (read/write for owner only)
        try:
            os.chmod(KEY_FILE, 0o600)
        except:
            pass  # Windows doesn't support chmod
        
        print(f"⚠️  New encryption key generated at {KEY_FILE}")
        print("⚠️  KEEP THIS FILE SECURE - if lost, encrypted data cannot be recovered!")
        
        return key


def get_cipher():
    """Get Fernet cipher instance"""
    key = _get_or_create_key()
    return Fernet(key)


def encrypt_value(value: str) -> str:
    """Encrypt a string value"""
    if not value:
        return ''
    
    cipher = get_cipher()
    encrypted_bytes = cipher.encrypt(value.encode())
    return base64.urlsafe_b64encode(encrypted_bytes).decode()


def decrypt_value(encrypted: str) -> str:
    """Decrypt a string value"""
    if not encrypted:
        return ''
    
    try:
        cipher = get_cipher()
        encrypted_bytes = base64.urlsafe_b64decode(encrypted.encode())
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return ''


def mask_api_key(api_key: str) -> str:
    """Mask an API key for safe display"""
    if not api_key:
        return ''
    
    if len(api_key) <= 8:
        return '****'
    
    return api_key[:4] + '****' + api_key[-4:]


if __name__ == '__main__':
    # Test encryption
    test_value = "AIzaSyDemoKey123456789"
    
    print("Testing encryption...")
    encrypted = encrypt_value(test_value)
    print(f"Original: {test_value}")
    print(f"Encrypted: {encrypted}")
    print(f"Masked: {mask_api_key(test_value)}")
    
    decrypted = decrypt_value(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert test_value == decrypted, "Encryption/decryption failed!"
    print("\n✅ Encryption working correctly!")
