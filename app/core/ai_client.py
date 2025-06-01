# root/app/core/ai_client.py
import openai
from app.config import config

openai.api_key = config.openai.api_key
