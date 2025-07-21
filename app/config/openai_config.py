from openai import AsyncOpenAI
from app.config.general_config import OpenAISettings

client = AsyncOpenAI(
    api_key = OpenAISettings.api_key
)