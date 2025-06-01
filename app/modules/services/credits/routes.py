# app/modules/credits/routes.py

from fastapi import APIRouter, Depends, HTTPException
from app.modules.services.auth.auth_utils import AuthenticationUtils
from app.config.auth_config import supabase_client as supabase

router = APIRouter()

@router.get("/")
async def get_credits(current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]
    data = supabase.table("user_credits").select("credits").eq("user_id", user_id).single().execute()
    return {"credits": data.data["credits"]}

@router.post("/add")
async def add_credits(amount: int, current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]
    result = supabase.rpc("add_user_credits", {"p_user_id": user_id, "p_amount": amount}).execute()
    if result.error:
        raise HTTPException(status_code=400, detail="Failed to add credits")
    return {"message": "Credits added"}

@router.post("/deduct")
async def deduct_credits(amount: int, current_user=Depends(AuthenticationUtils.get_authenticated_user)):
    user_id = current_user["id"]
    result = supabase.rpc("deduct_user_credits", {"p_user_id": user_id, "p_amount": amount}).execute()
    if result.error:
        raise HTTPException(status_code=400, detail="Failed to deduct credits")
    return {"message": "Credits deducted"}
