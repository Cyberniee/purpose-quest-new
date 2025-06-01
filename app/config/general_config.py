import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
from pathlib import Path

# Load .env if present
root_dir = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

@dataclass
class ProjectSettings:
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    project_name: str = os.getenv("PROJECT_NAME", "Purpose Quest")
    project_version: str = os.getenv("PROJECT_VERSION", "V2.0")
    domain: str = os.getenv("DOMAIN", "localhost")


@dataclass
class SupabaseSettings:
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_API_KEY", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "")

@dataclass
class OpenAISettings:
    api_key: str = os.getenv("OPENAI_API_KEY", "")

@dataclass
class StripeSettings:
    secret_key: str = os.getenv("STRIPE_SECRET", "")
    webhook_secret: str = os.getenv("STRIPE_ENDPOINT_SECRET", "")
    success_url: str = os.getenv("STRIPE_SUCCESS_URL", "")
    cancel_url: str = os.getenv("STRIPE_CANCEL_URL", "")

@dataclass
class AppSettings:
    env: str = os.getenv("ENV", "development")
    debug: bool = os.getenv("ENV", "development") == "development"
    api_prefix: str = "/api"
    version: str = "0.1.0"
    project_name: str = "PurposeQuest AI"

@dataclass
class Config:
    project: ProjectSettings = field(default_factory=ProjectSettings)
    supabase: SupabaseSettings = field(default_factory=SupabaseSettings)
    openai: OpenAISettings = field(default_factory=OpenAISettings)
    stripe: StripeSettings = field(default_factory=StripeSettings)
    app: AppSettings = field(default_factory=AppSettings)

config = Config()