# auth_config.py
from contextvars import ContextVar
from supabase import create_client, Client
from app.config import config

# Context variables to store the access token and role usage per request
_access_token: ContextVar[str | None] = ContextVar("supabase_access_token", default=None)
_use_service_role: ContextVar[bool] = ContextVar("supabase_use_service_role", default=False)

def set_supabase_access_token(token: str | None):
    """Set the JWT access token for the current request context."""
    _access_token.set(token)

def set_supabase_service_role(use_service_role: bool):
    """Specify whether the service role key should be used in the current context."""
    _use_service_role.set(use_service_role)

def _create_client(access_token: str | None = None, service_role: bool = False) -> Client:
    key = config.supabase.service_role_key if service_role else config.supabase.anon_key
    client = create_client(config.supabase.supabase_url, key)
    if access_token:
        client.postgrest.auth(access_token)
    return client

def get_supabase_client() -> Client:
    """Return a Supabase client configured for the current context."""
    return _create_client(_access_token.get(), _use_service_role.get())

class SupabaseProxy:
    """Proxy object that lazily creates a Supabase client per request."""
    def __getattr__(self, name):
        return getattr(get_supabase_client(), name)

# Exported proxy used throughout the application
supabase_client = SupabaseProxy()

class AuthSettings:
    jwt_secret = config.supabase.jwt_secret
    sign_up_redirect_url = f"{config.project.domain}/finish-sign-up"
    recovery_redirect_url = f"{config.project.domain}/recovery"
