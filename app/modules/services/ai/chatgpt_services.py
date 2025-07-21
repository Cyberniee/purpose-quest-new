import tiktoken, logging
from app.config.general_config import OpenAISettings
from app.utils.common_utils import calc_tokens

from app.db.db_operations.subscriptions import get_token_usage_data, update_token_data

logger = logging.getLogger(__name__)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

async def is_within_model_lim(chat_messages):
    used_tokens = sum(calc_tokens(message['content']) for message in chat_messages)
    
    return used_tokens <= OpenAISettings.limit_gpt_35t