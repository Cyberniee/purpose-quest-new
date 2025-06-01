#auth_config.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
from app.config import config

# Load environment variables
root_dir = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

'''Use this client exclusively for auth related tasks'''

class SupabaseAuth:
    def __init__(self):        
        # Create a Supabase client using the loaded environment variables
        self.supabase: Client = create_client(config.supabase.supabase_url, config.supabase.supabase_key)

    def get_client(self) -> Client:
        return self.supabase

class AuthSettings:
    jwt_secret = config.supabase.jwt_secret
    sign_up_redirect_url = f"{config.project.domain}/finish-sign-up"
    recovery_redirect_url = f"{config.project.domain}/recovery"


# Example usage
supabase_auth = SupabaseAuth()
supabase_client = supabase_auth.get_client()
