from app.db.base import user_settings, users, messages, subs, prompts, whatsapp_accounts, whatsapp_link_tokens, whatsapp_messages
from app.utils.common_utils import validate_data_presence, async_exception_handler
import logging

logger = logging.getLogger(__name__)