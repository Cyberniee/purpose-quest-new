import logging
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.config.auth_config import supabase_client as supabase
from app.modules.services.stripe.stripe_services import fetch_available_products_from_stripe, sync_report_types_with_stripe
from app.modules.services.access.product_services import fetch_purchased_tokens_with_metadata
from app.modules.services.auth.auth_utils import AuthenticationUtils


router = APIRouter()

logger = logging.getLogger(__name__)

class UserUpdatePayload(BaseModel):
    name: str | None = None
    first_login: bool | None = None
    deleted: bool | None = None

@router.get("/products")
async def get_account_products(user = Depends(AuthenticationUtils.get_authenticated_user)):
    try:
        user_id = user.get("id")
        available_products = await fetch_available_products_from_stripe()
        purchased = await fetch_purchased_tokens_with_metadata(user_id, available_products)

        return {
            "valid_products": [p for p in purchased if p["valid"]],
            "invalid_products": [p for p in purchased if not p["valid"]],
            "available_products": available_products
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load account products: {str(e)}")
    
    
    
@router.post("/user/update")
async def update_user(payload: UserUpdatePayload, user=Depends(AuthenticationUtils.get_authenticated_user)):
    try:
        update_fields = {}

        if payload.name is not None:
            update_fields["name"] = payload.name
        if payload.first_login is not None:
            update_fields["first_login"] = payload.first_login
        if payload.deleted is not None:
            update_fields["deleted"] = payload.deleted

        if not update_fields:
            return JSONResponse(status_code=400, content={"status": "error", "message": "No fields provided for update."})

        user_id = user.get("id")
        update_response = supabase.table("users").update(update_fields).eq("id", user_id).execute()

        if update_response.error:
            logger.error(f"Supabase update error: {update_response.error}")
            return JSONResponse(status_code=500, content={"status": "error", "message": "Failed to update user."})

        return {"status": "success", "message": "User updated successfully."}

    except Exception as e:
        logger.error(f"User update failed: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error."})
    
    
    
    
    
    
    
### DEV ###
    
@router.post("/sync_report_types")
async def sync_report_types():
    try:
        result = await fetch_available_products_from_stripe()
        if not result:
            raise HTTPException(status_code=404, detail="No products found in Stripe")

        # Assuming sync_report_types_with_stripe is defined in stripe_services
        await sync_report_types_with_stripe()
        return JSONResponse(status_code=200, content={"message": "Report types synced successfully"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync report types: {str(e)}")


