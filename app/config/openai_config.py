from openai import AsyncOpenAI
from app.config.general_config import Config

client = AsyncOpenAI(
    api_key = Config.openai.api_key
)