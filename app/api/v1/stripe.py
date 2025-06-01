import logging, secrets
from fastapi import APIRouter, Request, Header, HTTPException
from app.config import config
from app.config.stripe_config import stripe_client as stripe
from app.config.auth_config import supabase_client as supabase
from app.utils.common_utils import validate_data_presence

router = APIRouter()

@router.post("/printer")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    sig_header = stripe_signature
    endpoint_secret = config.stripe.webhook_secret

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )

        print("\n📦 Stripe Webhook Event Received:")
        print("Type:", event["type"])
        print("ID:", event["id"])
        print("Data Object:", event["data"]["object"])

    except ValueError as e:
        # Invalid payload
        logging.error(f"⚠️ Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logging.error(f"⚠️ Signature error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return {"status": "success"}

@router.post("/webhook")
async def stripe_webhook_handler(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    sig_header = stripe_signature
    endpoint_secret = config.stripe.webhook_secret

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )

        # Log the event type and ID
        logging.info(f"Stripe Webhook Event Received: {event['type']} - {event['id']}")

        # Handle the event (you can add more cases as needed)
        if event["type"] == "checkout.session.completed":
            
            session = event["data"]["object"]
            user_id = session["metadata"]["user_id"]
            report_type_stripe_id = session["metadata"]["report_type_id"]
            payment_id = session["payment_intent"]
            
            response = supabase.table("report_types").select("id").eq("stripe_id", report_type_stripe_id).single().execute()
            if not validate_data_presence(response):
                raise HTTPException(status_code=404, detail="Report type not found")
            report_type_id = response.data["id"]

            access_token = secrets.token_urlsafe(16) # creates the token

            supabase.table("report_access_tokens").insert({
                "user_id": user_id,
                "report_type_id": report_type_id,
                "access_token": access_token,
                "granted_by": "stripe",
                "payment_reference": payment_id,
                "status": "not_started"
            }).execute()


    except ValueError as e:
        logging.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logging.error(f"Signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
