# base.py
from app.config.auth_config import supabase_client as supabase


class TableProxy:
    """Proxy to lazily access Supabase tables with the current request context."""
    def __init__(self, table_name: str):
        self.table_name = table_name

    def __getattr__(self, item):
        return getattr(supabase.table(self.table_name), item)


users = TableProxy('users')
user_settings = TableProxy('user_settings')
messages = TableProxy('whatsapp_messages')
subs = TableProxy('subscriptions')
prompts = TableProxy('prompts')
whatsapp_accounts = TableProxy('whatsapp_accounts')
whatsapp_link_tokens = TableProxy('whatsapp_link_tokens')
whatsapp_messages = TableProxy('whatsapp_messages')
