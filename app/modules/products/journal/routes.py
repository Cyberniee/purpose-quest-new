# app/modules/products/journal/routes.py
# /api/journal
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from datetime import datetime, date
from pydantic import BaseModel

from app.modules.services.auth.auth_utils import AuthenticationUtils
from app.utils.common_utils import format_entry_label, validate_data_presence
from app.config.auth_config import supabase_client as supabase
from app.modules.services.journal.journal_services import (
    get_or_create_today_entry,
    update_journal_entry,
)

router = APIRouter()
logger = logging.getLogger(__name__)

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


@router.get("/recent")
async def get_recent_journal_entries(
    current_user=Depends(AuthenticationUtils.get_authenticated_user),
):
    user_id = current_user["id"]
    today_str = date.today().isoformat()

    # Fetch up to 3 most recent entries, including today
    res = (
        supabase.table("journal_entries")
        .select("id, content, entry_date")
        .eq("user_id", user_id)
        .lte("entry_date", today_str)
        .order("entry_date", desc=True)
        .limit(3)
        .execute()
    )

    entries = []
    if res.data:
        for entry in res.data:
            entries.append(
                {
                    "id": entry["id"],
                    "preview": entry["content"][:120].split("\n")[0].strip() + "...",
                    "entry_date": entry["entry_date"],
                    "label": format_entry_label(entry["entry_date"]),
                }
            )

    return {"entries": entries}

@router.get("/all_dates")
async def get_all_entry_dates(
    current_user=Depends(AuthenticationUtils.get_authenticated_user)
):
    logger.info("in all_dates")
    user_id = current_user["id"]
    print(f'user_id at /all_dates: {user_id}')

    entries = (
        supabase.table("journal_entries")
        .select("created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    print(f"entries: {entries}")

    if not validate_data_presence(entries):
        return {"dates": []}

    return {
        "dates": [
            entry["created_at"].split("T")[0]  # Extract date part
            for entry in entries.data
        ]
    }


@router.get("/paginated")
async def get_paginated_journal_entries(
    request: Request,
    page: int = 1,
    limit: int = 10,
    current_user=Depends(AuthenticationUtils.get_authenticated_user)
):
    logger.info("in all_dates")
    user_id = current_user["id"]
    print(f'user_id at /paginated: {user_id}')


    MAX_LIMIT = 25
    limit = min(limit, MAX_LIMIT)
    offset = (page - 1) * limit

    # Count total entries
    count_res = supabase.table("journal_entries") \
        .select("id", count="exact") \
        .eq("user_id", user_id) \
        .execute()
    total_entries = count_res.count or 0

    # Fetch paginated results
    data_res = supabase.table("journal_entries") \
        .select("id, content, created_at") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()
    
    print(f'data res from /paginated: {data_res}')

    entries = []
    for entry in data_res.data or []:
        date_str = entry["created_at"].split("T")[0]
        entries.append({
            "id": entry["id"],
            "preview": entry["content"][:120].split("\n")[0].strip() + "...",
            "entry_date": date_str,
            "label": format_entry_label(date_str)
        })

    return {
        "entries": entries,
        "page": page,
        "limit": limit,
        "total": total_entries,
        "total_pages": (total_entries + limit - 1) // limit
    }



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
        res = (
            supabase.table("journal_entries")
            .select("id")
            .eq("user_id", user_id)
            .eq("entry_date", entry_date)
            .maybe_single()
            .execute()
        )

        if not validate_data_presence(res):
            # Insert new
            insert = (
                supabase.table("journal_entries")
                .insert(
                    {
                        "user_id": user_id,
                        "entry_date": entry_date,
                        "content": preview,
                        "word_count": len(preview.split()),
                    }
                )
                .execute()
            )
            if insert.data:
                entries.append(insert.data[0])

    return {"status": "created", "entries": entries}
