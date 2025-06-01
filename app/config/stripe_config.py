# app/config/stripe_config.py
import stripe
import logging
from app.config import config

logger = logging.getLogger(__name__)

logger.info("Initializing Stripe client...")
logger.info(f"Using Stripe secret key: {config.stripe.secret_key[:4]}****")  # Log only part of the key for security
logger.info(f"Using Stripe webhook_secret: {config.stripe.webhook_secret[:4]}****")  # Log only part of the key for security
# Initialize Stripe client with secret key from settings
stripe.api_key = config.stripe.secret_key


# Optional: set max retries, request timeout, telemetry, etc.
stripe.max_network_retries = 3
stripe.default_http_client = None  # you can inject your own if needed

# Export the configured stripe module
stripe_client = stripe
