# app/modules/reports/routes.py

from fastapi import APIRouter, Depends, HTTPException
from app.modules.services.auth.auth_utils import AuthenticationUtils
from app.config.auth_config import supabase_client as supabase

router = APIRouter()

@router.get("/")
async def list_reports(current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]
    res = supabase.table("reports").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data

@router.get("/{report_id}")
async def get_report(report_id: str, current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]
    res = supabase.table("reports").select("*").eq("id", report_id).eq("user_id", user_id).single().execute()
    if res.error:
        raise HTTPException(status_code=404, detail="Report not found")
    return res.data

@router.post("/")
async def create_report(payload: dict, current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]
    data = {
        "user_id": user_id,
        "report_type": payload.get("report_type"),
        "content": payload.get("content"),
        "status": "created"
    }
    res = supabase.table("reports").insert(data).execute()
    if res.error:
        raise HTTPException(status_code=400, detail="Failed to create report")
    return res.data

@router.put("/{report_id}")
async def update_report(report_id: str, payload: dict, current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]
    updates = {"content": payload.get("content"), "status": payload.get("status")}
    res = supabase.table("reports").update(updates).eq("id", report_id).eq("user_id", user_id).execute()
    if res.error:
        raise HTTPException(status_code=400, detail="Failed to update report")
    return {"status": "updated"}
