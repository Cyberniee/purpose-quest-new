import logging
from app.config.auth_config import supabase_client as supabase
from app.utils.common_utils import validate_data_presence

logger = logging.getLogger(__name__)

async def fetch_purchased_tokens_with_metadata(user_id: str, stripe_products: list) -> list:
    try:
        # Step 1: Fetch user access tokens
        response = supabase.table("report_access_tokens").select(
            "id, report_id, status, report_type_id, access_token, granted_at, input_session_id, granted_by"
        ).eq("user_id", user_id).execute()

        if not validate_data_presence(response):
            logging.info(f"No access tokens for user {user_id}")
            return []

        access_tokens = response.data
        logging.info(f'Found {len(access_tokens)} access tokens for user {user_id}: \n{access_tokens}')

        # Step 2: Fetch report_types for all token-linked report_type_ids
        report_type_ids = list(set(token["report_type_id"] for token in access_tokens))
        report_types_res = supabase.table("report_types").select("id, stripe_id").in_("id", report_type_ids).execute()

        if not validate_data_presence(report_types_res):
            logging.warning("No matching report_types found for tokens")
            return []

        report_types = report_types_res.data

        # Step 3: Build lookup maps
        # Map report_type_id → stripe_id
        report_type_id_to_stripe_id = {rt["id"]: rt["stripe_id"] for rt in report_types}
        # Map stripe_id → stripe product metadata
        stripe_metadata_by_id = {p["product_id"]: p for p in stripe_products}

        # Step 4: Enrich tokens with Stripe product info
        enriched_products = []
        for token in access_tokens:
            report_type_id = token["report_type_id"]
            stripe_id = report_type_id_to_stripe_id.get(report_type_id)

            if not stripe_id:
                continue  # No stripe_id found for this report_type_id

            stripe_info = stripe_metadata_by_id.get(stripe_id)
            if not stripe_info:
                continue  # Stripe product no longer exists?

            enriched_products.append({
                **stripe_info,  # includes name, image, description, price, etc.
                "status": token.get("status", "available"),
                "token_id": token["access_token"],
                "report_type_id": report_type_id,
                "date": token["granted_at"],
                "valid": True,
                "granted_by": token["granted_by"],
                "redeemed_credits": token.get("redeemed_credits"),
            })

        return enriched_products

    except Exception as e:
        logging.error(f"Error fetching enriched products: {e}")
        return []
