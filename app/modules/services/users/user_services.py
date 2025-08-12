import logging, pytz
from datetime import datetime, timedelta
from uuid import UUID
from app.config.auth_config import (
    supabase_client as supabase,
    set_supabase_service_role,
)
from app.utils.common_utils import validate_data_presence
from app.db.db_operations.subscriptions import get_consumption, update_consumption_data, update_sub_data
from app.db.db_operations.whatsapp_accounts import link_wa_to_user
from app.db.db_operations.user_settings import update_user_settings
import uuid


logger = logging.getLogger(__name__)


async def create_user(sub: UUID, email: str, name: str = "") -> dict:
    set_supabase_service_role(True)
    try:
        user_create_response = (
            supabase.table("users")
            .insert(
                {
                    "sub": sub,  # Assuming `id` in public.users is UUID or matches `sub` from JWT
                    "email": email,
                    "name": name,
                }
            )
            .execute()
        )
        if not validate_data_presence(user_create_response):
            logger.error("User creation failed: No data returned")
            return {}
    except Exception as e:
        logger.error(f"Error creating user in DB: {e}")
        raise

    try:
        settings_response = supabase.table("user_settings").insert(
            {
                "user_id": user_create_response.data[0]['id'],
                "first_name": "",
                "last_name": "",
                # Notifications
                "notif_daily": True,
                "notif_ai_insights": True,
                "notif_streaks": False,
                # Privacy & Security
                "encrypt_entries": False,
                "ai_analysis": False,
                # Appearance
                "theme": "auto",  # Options: 'light', 'dark', 'auto'
                "font_size": "medium",  # Options: 'small', 'medium', 'large'
                "updated_at": datetime.now().isoformat(),
            }
        )
        if not validate_data_presence(settings_response):
            logger.error(f'an error occured inserting user settings')
        return user_create_response.data[0] if user_create_response.data else {}

    except Exception as e:
        logger.error(f"something went wrong creating the user settings: {e}")

    try:
        subscription_response = supabase.table("subscriptions").insert(
            {
                "user_id": user_create_response.data[0]['id'],
                "subscription": "free",
                "active": True,
                "start_date": datetime.now().isoformat()
            }
        )
        if not validate_data_presence(subscription_response):
            logger.error(f'an error occured inserting user subscription')
    
    except Exception as e:
        logger.error(f"something went wrong creating the user subscription: {e}")
    finally:
        set_supabase_service_role(False)

async def delete_user(user_id: UUID) -> None:
    try:
        supabase.table("users").update({"deleted": True}).eq("id", user_id).execute()
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
        response = supabase.table("users").select("*, user_settings(tz_offset)").eq("sub", sub).single().execute()
        if not validate_data_presence(response):
            logger.info(f"User with id {sub} not found")
            return None
        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Error fetching user {sub}: {e}")
        return None


async def get_user_by_email(email: str) -> dict | None:
    try:
        response = (
            supabase.table("users").select("*").eq("email", email).single().execute()
        )
        if not validate_data_presence(response):
            logger.info(f"User with email {email} not found")
            return None
        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Error fetching user {email}: {e}")
        return None


async def user_exists(sub: UUID = None, email: str = None) -> bool:
    if sub:
        user = await get_user_by_supabase_auth_id(sub)
    elif email:
        user = await get_user_by_email(email)
    else:
        logger.error("Either sub or email must be provided to check user existence")
        return False
    return user is not None


async def update_consumption(duration: float, user_id: str, free: bool = False) -> None:
    try:
        consumption_data = {}
        usage_resp = await get_consumption(user_id)
        
        if usage_resp is None:
            logger.error(f"Failed to fetch usage data for user_id: {user_id}")
            return
        
        usage: float = usage_resp['usage']
        usage += duration
        consumption_data['usage'] = usage

        if free:
            message_count = usage_resp.get('message_count', 0)
            if duration != 0.00:
                message_count += 1
                consumption_data['message_count'] = message_count

        await update_consumption_data(consumption_data=consumption_data, user_id=user_id)
        logger.info(f"Updated consumption data for user_id: {user_id}")
    
    except Exception as e:
        logger.error(f"Error in update_consumption: {e}")

async def check_and_reset_usage(user_id):
    consumption_data = await get_consumption(user_id)
    last_reset_str = consumption_data['last_reset']
    current_time = datetime.now(pytz.UTC)  # timezone-aware UTC
    just_reset = False

    if last_reset_str is None:
        last_reset = current_time
        data = {'last_reset': last_reset.isoformat()}
        await update_consumption_data(consumption_data=data, user_id=user_id)
        return just_reset

    try:
        last_reset = datetime.fromisoformat(last_reset_str)

        # Ensure it's timezone-aware (should be if from Supabase, but just in case)
        if last_reset.tzinfo is None:
            last_reset = last_reset.replace(tzinfo=pytz.UTC)

    except ValueError as e:
        logger.error(f"Error parsing last_reset: {e}")
        last_reset = current_time
        data = {'last_reset': last_reset.isoformat()}
        await update_consumption_data(consumption_data=data, user_id=user_id)
        return just_reset

    if current_time.year > last_reset.year or current_time.month > last_reset.month:
        data = {'message_count': 0, 'last_reset': current_time.isoformat()}
        await update_consumption_data(consumption_data=data, user_id=user_id)
        just_reset = True

    return just_reset

    
async def deactivate_sub(subscription_del):
    subscription_id = subscription_del["id"]
    #change to centralized DB ops
    await update_sub_data(data = {'active': False, 'sub_id':subscription_id})
        

async def create_whatsapp_link_token(user_id: str, expires_minutes: int = 30):
    token_str = str(uuid.uuid4()).split("-")[0]
    now = datetime.now(pytz.timezone('utc'))
    expiry = now + timedelta(minutes=expires_minutes)

    result = supabase.table("whatsapp_link_tokens").insert({
        "user_id": user_id,
        "token": token_str,
        "expires_at": expiry.isoformat()
    }).execute()

    if result.data:
        return result.data[0]
    return None


async def link_wa_account_to_user(from_num: str, user_id: str):
    if await link_wa_to_user(from_num=from_num, user_id=user_id):

        data = {"wa_linked": True}
        await update_user_settings(data, user_id=user_id)
        return True
    else:
        logger.error(f"Failed to link WhatsApp number {from_num} to user ID {user_id}")
        return False