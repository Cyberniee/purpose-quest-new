import logging
from app.config.auth_config import supabase_client as supabase
from app.utils.common_utils import validate_data_presence
from app.config.stripe_config import stripe_client as stripe


async def fetch_available_products_from_stripe():
    try:
        products = stripe.Product.list(active=True, limit=100)
        result = []

        for product in products.data:
            if not product.get("default_price"):
                continue

            price = stripe.Price.retrieve(product.default_price)
            result.append({
                "product_id": product.id, #= stripe_id
                "name": product.name,
                "description": product.description or "",
                "image": product.images[0] if product.images else None,
                "price": price.unit_amount / 100,
                "price_id": price.id,
                "product_slug": product.name.lower().replace(" ", "-"),
            })
        return result

    except Exception as e:
        logging.error(f"Error fetching Stripe products: {e}")
        raise

async def sync_report_types_with_stripe():
    try:
        stripe_products = stripe.Product.list(active=True, limit=100).get("data", [])
        for product in stripe_products:
            if not product.get("default_price"):
                continue

            price = stripe.Price.retrieve(product["default_price"])
            price_eur = price["unit_amount"] / 100

            # Check if report type exists
            existing = supabase.table("report_types").select("id").eq("stripe_id", product["id"]).execute()

            payload = {
                "name": product["name"],
                "description": product.get("description", ""),
                "stripe_id": product["id"],
                "price_eur": price_eur
            }

            if validate_data_presence(existing):
                supabase.table("report_types").update(payload).eq("stripe_id", product["id"]).execute()
                logging.info(f"Updated report type: {product['name']}")
            else:
                supabase.table("report_types").insert(payload).execute()
                logging.info(f"Inserted new report type: {product['name']}")

        return True

    except Exception as e:
        logging.error(f"Stripe sync failed: {e}")
        raise
