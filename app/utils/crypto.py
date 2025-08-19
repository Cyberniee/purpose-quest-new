import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Load from environment variable or secure secret store (e.g., HashiCorp Vault, AWS KMS)
APP_SECRET_KEY = base64.urlsafe_b64decode(
    os.getenv("APP_SECRET_KEY", base64.urlsafe_b64encode(os.urandom(32)))
)

def encrypt_string(plaintext: str) -> str:
    """Encrypts a string with AES-GCM and returns base64-encoded ciphertext"""
    aesgcm = AESGCM(APP_SECRET_KEY)
    nonce = os.urandom(12)  # 96-bit nonce for AES-GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    # Store nonce + ciphertext together
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")

def decrypt_string(ciphertext_b64: str) -> str:
    """Decrypts a base64-encoded ciphertext and returns plaintext"""
    data = base64.urlsafe_b64decode(ciphertext_b64.encode("utf-8"))
    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(APP_SECRET_KEY)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
