from fastapi import APIRouter, Depends, HTTPException
from app.config.auth_config import supabase_client as supabase
from app.modules.services.auth.auth_utils import AuthenticationUtils
from app.utils.common_utils import validate_data_presence
from datetime import datetime

router = APIRouter()

# find at ./users

@router.get("/settings")
async def get_settings(current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]

    res = supabase.table("user_settings").select("*").eq("user_id", user_id).limit(1).execute()

    if not validate_data_presence(res):
        raise HTTPException(status_code=404, detail="Settings not found")

    s = res.data[0]
    return {
        "first_name": s.get("first_name", ""),
        "last_name": s.get("last_name", ""),
        "email": current_user.get("email"),
        "notifications": {
            "daily": s.get("notif_daily", False),
            "ai_insights": s.get("notif_ai_insights", False),
            "streaks": s.get("notif_streaks", False),
        },
        "privacy": {
            "encrypt": s.get("encrypt_entries", False),
            "ai_analysis": s.get("ai_analysis", False),
        },
        "appearance": {
            "theme": s.get("theme", "auto"),
            "font_size": s.get("font_size", "medium")
        }
    }

@router.post("/settings/profile")
async def update_profile(data: dict, current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]

    updates = {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "updated_at": datetime.now().isoformat()
    }

    res = supabase.table("user_settings").update(updates).eq("user_id", user_id).execute()

    if not res.data:
        raise HTTPException(status_code=400, detail="Failed to update profile")

    return {"status": "success"}

@router.post("/settings/update_preferences")
async def update_preferences(data: dict, current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]

    notify = data.get("notifications", {})
    privacy = data.get("privacy", {})
    appearance = data.get("appearance", {})

    updates = {
        "first_name": data.get('first_name', ''),
        "last_name": data.get('last_name', ''),
        "notif_daily": notify.get("daily", False),
        "notif_ai_insights": notify.get("ai_insights", False),
        "notif_streaks": notify.get("streaks", False),
        "encrypt_entries": privacy.get("encrypt", False),
        "ai_analysis": privacy.get("ai_analysis", False),
        "theme": appearance.get("theme", "auto"),
        "font_size": appearance.get("font_size", "medium"),
        "updated_at": datetime.now().isoformat()
    }


    res = supabase.table("user_settings").update(updates).eq("user_id", user_id).execute()

    if not res.data:
        raise HTTPException(status_code=400, detail="Failed to update preferences")

    return {"status": "success"}
