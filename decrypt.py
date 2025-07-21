import logging
import base64
from cryptography.fernet import Fernet, InvalidToken

CRKEY = "MbucBFRUs0oJyjYpneTHMXdiMAF4kyVVVOj95sH0zSg="

if len(CRKEY) == 43:
    CRKEY += '='
cipher_suite = Fernet(CRKEY)
decoded_key = base64.urlsafe_b64decode(CRKEY)


msg_encrypted= "Z0FBQUFBQm9aWWttQmVOZDJta3M3cXcxdVhfcTQ4UGhpbG5Iekp5SXFSdlRHeFYxQkRoNEMxQzlYbXdibWlrd1ZEU2VhcU9vMlR3ZVAyMUFtMFBlOEduQ3BOUnRMWUJKMVFXZlVnV1lXcXlNQjdvbEN3eVhURm1pUHpQYmdqRlNYOERfU3lDMXgtZDlSTGI1NDBnN0owY3RubjltMnpjamxVVTdjS2ZkeU9XeXp4VFJZbU9MTmdHWFh1TFB0VXd6N2hqREI5NjZCaFZxZFBRS19yWHZZMHpGa1N6cEdtaUw3WXZ1Q0ZvSkFITU1VelB2cWtDM2JNU3lCRGlfX21lR2tsUlNnS2FwN0JwY3pLVVpEaEZacmVROVZ4WFItWmo2WHNZQ3hWcWczOVBEbFNyYVJ4UERlbVBhQnpqMTNqY3NfU3BQZ0FoMDZwcy0="


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
