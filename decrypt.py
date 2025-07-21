import logging
import base64
from cryptography.fernet import Fernet, InvalidToken

CRKEY = "MbucBFRUs0oJyjYpneTHMXdiMAF4kyVVVOj95sH0zSg="

if len(CRKEY) == 43:
    CRKEY += '='
cipher_suite = Fernet(CRKEY)
decoded_key = base64.urlsafe_b64decode(CRKEY)


msg_encrypted= "Z0FBQUFBQm9JVW9ybzZTLWxESWJiZ1dYaEJuQzZUUWhfNnBENnpxbXNxektwQ2syZWY1bHl1YVF2NjJUa2FOejNuSWtWWndhNV9QT0V1c01hcGNVN1J2ampHNGxBSVBHajRZc1NqaFhOMGpRbHRFT2xTdGZneEZ1ZW45Y0tvQnR5dDBPZVF1eEFwQVpUbDR3c28tdmpvUGo4bUw4VHhZYndEZXhzTGdfTzBmQjdVbGluRlQ4QnJkVkVvTV9KN3VxZHNLckdNLVM4cU15dk00Y1J6QTNPUEhSa3pNbkVYNUFQaTdXbFpKUGg3bjdDQk5YOTljdm10UT0="


def decrypt_data(encrypted_data: str):
    if not encrypted_data:
        logging.warning("No data provided for decryption. Returning original data.")
        return encrypted_data
    try:
        # Convert base64 encoded string to bytes
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        # Decrypt the bytes
        decrypted_data = cipher_suite.decrypt(encrypted_bytes).decode()
        return decrypted_data
    except InvalidToken:
        logging.error("The token is invalid, possibly due to key mismatch or data corruption.")
        return encrypted_data
    except (TypeError, ValueError, base64.binascii.Error) as e:
        logging.error(f"An error occurred in data decryption: {e}")
        return encrypted_data
    except Exception as e:
        logging.error(f"Unexpected error occurred in decryption process: {e}")
        return encrypted_data


content = decrypt_data(msg_encrypted)

print(content)
