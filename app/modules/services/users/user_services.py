from app.config.auth_config import supabase_client as supabase
from app.utils.common_utils import validate_data_presence
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


async def create_user(sub: UUID, email: str, name: str = "") -> dict:
    try:
        response = supabase.table("users").insert({
            "sub": sub,  # Assuming `id` in public.users is UUID or matches `sub` from JWT
            "email": email,
            "name": name
        }).execute()
        if not validate_data_presence(response):
            logger.error("User creation failed: No data returned")
            return {}
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Error creating user in DB: {e}")
        raise


async def delete_user(user_id: UUID) -> None:
    try:
        supabase.table("users").update({'deleted': True}).eq("id", user_id).execute()
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise


async def update_user(user_id: UUID, data: dict) -> dict:
    try:
        response = supabase.table("users").update(data).eq("id", user_id).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise


async def get_user_by_supabase_auth_id(sub: UUID) -> dict | None:
    try:
        response = supabase.table("users").select("*").eq("sub", sub).single().execute()
        if not validate_data_presence(response):
            logger.info(f"User with id {sub} not found")
            return None
        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Error fetching user {sub}: {e}")
        return None

async def get_user_by_email(email: str) -> dict | None:
    try:
        response = supabase.table("users").select("*").eq("email", email).single().execute()
        if not validate_data_presence(response):
            logger.info(f"User with email {email} not found")
            return None
        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Error fetching user {email}: {e}")
        return None


async def user_exists(sub: UUID=None, email: str=None) -> bool:
    if sub:
        user = await get_user_by_supabase_auth_id(sub)
    elif email:
        user = await get_user_by_email(email)
    else:
        logger.error("Either sub or email must be provided to check user existence")
        return False
    return user is not None
