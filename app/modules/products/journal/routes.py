# app/modules/products/journal/routes.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from pydantic import BaseModel

from app.modules.services.auth.auth_utils import AuthenticationUtils
from app.utils.common_utils import format_entry_label, validate_data_presence
from app.modules.services.journal.journal_services import (
    get_or_create_today_entry,
    update_journal_entry,
)

router = APIRouter()


class JournalUpdatePayload(BaseModel):
    content: str


@router.post("/today")
async def fetch_or_create_today_journal(
    current_user=Depends(AuthenticationUtils.get_authenticated_user),
):
    user_id = current_user["id"]

    entry = await get_or_create_today_entry(user_id, create=True)
    # Parse the ISO date string (e.g., "2025-06-14")
    entry_date_obj = datetime.strptime(entry["entry_date"], "%Y-%m-%d").date()

    return {
        "id": entry["id"],
        "entry_date": entry["entry_date"],
        "entry_date_display": entry_date_obj.strftime("%A, %B %d, %Y"),
        "content": entry.get("content", ""),
    }


# @router.get("/today/exists")
# async def does_today_entry_exist(
#     current_user=Depends(AuthenticationUtils.get_authenticated_user),
# ):
#     user_id = current_user["id"]

#     exists = await get_or_create_today_entry(user_id=user_id, create=False)

#     return {"exists": bool(exists), 
#             "entry_id": exists.get("id", ""), 
#             "content": exists.get('content', ''), 
#             "updated_at": exists.get('updated_at', ''),
#             "entry_preview": exists["content"][:120].split("\n")[0].strip() + "..."
#             }

@router.get("/recent")
async def get_recent_journal_entries(
    current_user=Depends(AuthenticationUtils.get_authenticated_user)
):
    user_id = current_user["id"]
    from app.config.auth_config import supabase_client as supabase
    from datetime import date

    today_str = date.today().isoformat()

    # Fetch up to 3 most recent entries, including today
    res = supabase.table("journal_entries") \
        .select("id, content, entry_date") \
        .eq("user_id", user_id) \
        .lte("entry_date", today_str) \
        .order("entry_date", desc=True) \
        .limit(3) \
        .execute()

    entries = []
    if res.data:
        for entry in res.data:
            entries.append({
                "id": entry["id"],
                "preview": entry["content"][:120].split("\n")[0].strip() + "...",
                "entry_date": entry["entry_date"],
                "label": format_entry_label(entry["entry_date"])
            })

    return {"entries": entries}

@router.patch("/{entry_id}")
async def update_entry(
    entry_id: str,
    payload: JournalUpdatePayload,
    current_user=Depends(AuthenticationUtils.get_authenticated_user),
):
    success = await update_journal_entry(entry_id, current_user["id"], payload.content)
    if not success:
        raise HTTPException(status_code=403, detail="Update failed")
    return {"status": "save ok"}

@router.post("/mock/dev")
async def create_mock_entries_dev(
    current_user=Depends(AuthenticationUtils.get_authenticated_user),
):
    from app.config.auth_config import supabase_client as supabase
    from datetime import date

    user_id = current_user["id"]
    base_dates = [2, 5, 9, 17, 26]  # June 2, 5, etc.

    entries = []
    for day in base_dates:
        entry_date = date(2025, 6, day).isoformat()
        preview = f"This is a mock journal entry for June {day}."

        # Check if entry already exists
        res = supabase.table("journal_entries") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("entry_date", entry_date) \
            .maybe_single() \
            .execute()

        if not validate_data_presence(res):
            # Insert new
            insert = supabase.table("journal_entries").insert({
                "user_id": user_id,
                "entry_date": entry_date,
                "content": preview,
                "word_count": len(preview.split())
            }).execute()
            if insert.data:
                entries.append(insert.data[0])

    return {"status": "created", "entries": entries}
