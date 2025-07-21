from datetime import datetime, timedelta
import pytz
import logging
from app.config.auth_config import supabase_client as supabase
from app.utils.common_utils import validate_data_presence

logger = logging.getLogger(__name__)

async def get_or_create_today_entry(user_id: str, local_date: str):
    today_str = local_date
    # try to fetch
    res = supabase.table("journal_entries").select("*").eq("user_id", user_id).eq("entry_date", today_str).limit(1).execute()

    # The code here does not need a create command: if there is no data, it will create it.
    if validate_data_presence(res):
        return res.data[0]
    else:
        # create it
        insert = supabase.table("journal_entries").insert({
            "user_id": user_id,
            "entry_date": today_str,
            "content": "",
            "word_count": 0
        }).execute()
        return insert.data[0]


async def update_journal_entry(entry_id: str, user_id: str, content: str) -> bool:
    update = supabase.table("journal_entries") \
        .update({
            "content": content,
            "word_count": len(content.split())
        }) \
        .eq("id", entry_id) \
        .eq("user_id", user_id) \
        .execute()

    return True

async def append_journal_entry(user_id:str, entry:dict, content:str) -> bool:
    if not entry:
        logger.error(f"No entry found for user {user_id}. Cannot append content.")
        return False

    new_content = f"{entry['content']}\n{content}"
    return await update_journal_entry(entry_id=entry['id'], user_id=user_id, content=new_content)

async def get_journal_entry_by_id(entry_id: str, user_id: str):
    res = supabase.table("journal_entries") \
        .select("*") \
        .eq("id", entry_id) \
        .eq("user_id", user_id) \
        .limit(1) \
        .execute()
    if validate_data_presence(res):
        return res.data[0]

async def log_entry_from_whatsapp(user_id:str, tz_offset:int, content:str, source:str="whatsapp"):
        # tz_offset is in minutes, e.g. -120 for UTC+2
    utc_now = datetime.now(pytz.timezone('utc'))
    local_now = utc_now + timedelta(minutes=tz_offset)
    local_date = local_now.strftime("%Y-%m-%d")

    try:
        today_entry = await get_or_create_today_entry(user_id=user_id, local_date=local_date)

        await append_journal_entry(user_id=user_id, entry=today_entry, content=content)

        return True, today_entry['id']
    except Exception as e:
        logger.error(f"Error logging entry from WhatsApp for user {user_id}: {e}")
        return False, None

