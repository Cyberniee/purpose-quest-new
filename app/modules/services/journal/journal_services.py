from datetime import date
from app.config.auth_config import supabase_client as supabase
from app.utils.common_utils import validate_data_presence

async def get_or_create_today_entry(user_id: str, create:bool=True):
    today_str = date.today().isoformat()

    # Try to fetch
    res = supabase.table("journal_entries") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("entry_date", today_str) \
        .limit(1) \
        .execute()

    if validate_data_presence(res):
        return res.data[0]

    if create:
        # Create new entry if not found
        insert = supabase.table("journal_entries").insert({
            "user_id": user_id,
            "entry_date": today_str,
            "content": "",
            "word_count": 0
        }).execute()

        return insert.data[0]


async def update_journal_entry(entry_id: str, user_id: str, content: str) -> bool:
    from app.config.auth_config import supabase_client as supabase

    update = supabase.table("journal_entries") \
        .update({
            "content": content,
            "word_count": len(content.split())
        }) \
        .eq("id", entry_id) \
        .eq("user_id", user_id) \
        .execute()

    return True

async def get_journal_entry_by_id(entry_id: str, user_id: str):
    res = supabase.table("journal_entries") \
        .select("*") \
        .eq("id", entry_id) \
        .eq("user_id", user_id) \
        .limit(1) \
        .execute()
    if validate_data_presence(res):
        return res.data[0]