# app/modules/payments/routes.py
import logging

from fastapi import APIRouter, Request, HTTPException, Depends

from app.config.stripe_config import stripe_client as stripe
from app.config import config
from app.config.auth_config import supabase_client as supabase
from app.dependencies.auth import get_current_user_required

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/create_checkout_session") # /payments/create_checkout_session
async def create_checkout_session(request: Request, user: dict = Depends(get_current_user_required)):
    user_id = user.get("id")
    data = await request.json()
    logger.info(f"Creating checkout session for user {user_id} with data: {data}")
    
    product_id_stripe = data.get('product_id_stripe')
    product_price_id = data.get('product_price_id')
    product_name = data.get('product_name')
    product_price = data.get('product_price')

    if not all([product_id_stripe, product_price_id, user_id]):
        raise HTTPException(status_code=400, detail="Missing parameters")

    try:
        session = stripe.checkout.Session.create(
            success_url=config.stripe.success_url,
            cancel_url=config.stripe.cancel_url,
            mode="payment",
            line_items=[{
                "price": product_price_id,
                "quantity": 1,
            }],
            client_reference_id=user_id,
            metadata={
                "report_type_id": product_id_stripe,
                "user_id": user_id,
                "product_name": product_name,
                "product_price": product_price
            }
        )
        return {"id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
