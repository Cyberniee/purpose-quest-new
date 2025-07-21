# base.py
from app.config.auth_config import supabase_client as supabase

users = supabase.table('users')
messages = supabase.table('messages')
subs = supabase.table('subscriptions')
prompts = supabase.table('prompts')
whatsapp_accounts = supabase.table('whatsapp_accounts')
whatsapp_link_tokens = supabase.table('whatsapp_link_tokens')
whatsapp_messages = supabase.table('whatsapp_messages')