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
    service_role_key: str = os.getenv("SUPABASE_API_KEY", "")
    anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "")

@dataclass
class OpenAISettings:
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", 0.3))
    frequency_penalty: float = float(os.getenv("OPENAI_FREQUENCY_PENALTY", 0.99))
    presence_penalty: float = float(os.getenv("OPENAI_PRESENCE_PENALTY", 0.99))

    max_interaction_tokens: int = int(os.getenv("MAX_INTERACTION_TOKENS", 4096))
    token_hist_limit: int = int(os.getenv("TOKEN_HIST_LIMIT", 2048))
    chat_gpt_token_resp_lim: int = int(os.getenv("CHAT_GPT_TOKEN_RESP_LIM", 1024))
    limit_gpt_35t: int = int(os.getenv("LIMIT_GPT_35T", 4096))
    gpt_temperature: float = float(os.getenv("GPT_TEMPERATURE", 0.2))
    max_retries: int = int(os.getenv("MAX_RETRIES", 3))


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
class SubscriptionVariables:
    free_limit: float = float(os.getenv("FREE_LIMIT", 10.0))
    basic_limit: float = float(os.getenv("BASIC_LIMIT", 100.0))
    ultimate_limit: float = float(os.getenv("ULTIMATE_LIMIT", 1000.0))
    file_size_limit: int = int(os.getenv("FILE_SIZE_LIMIT", 10485760)) # 10 MB
    free_message_count: int = int(os.getenv("FREE_MESSAGE_COUNT", 20))
    free_message_length_limit: float = float(os.getenv("FREE_MESSAGE_LENGTH_LIMIT", 500.0))

    subscriptions: dict = field(init=False)

    def __post_init__(self):
        self.subscriptions = {
            'free': {
                'WA_access': True,
                'limit': self.free_limit,
                'message_count': self.free_message_count,
                'message_length_limit': self.free_message_length_limit,
                'file_size_limit': self.file_size_limit
            },
            'paid': {
                'WA_access': True,
                'limit': self.basic_limit,
                'message_count': 100,  
                'message_length_limit': self.ultimate_limit, 
                'file_size_limit': self.file_size_limit
            }
        }

@dataclass
class WaVariables:
    verification_token: str = os.getenv("WA_VERIFICATION_TOKEN")
    access_token_wa: str = os.getenv("WA_ACCESS_TOKEN")
    url_wa: str = os.getenv("URL_WA")
    wa_ul_url: str = os.getenv("WA_UP_URL")
    wa_dl_url: str = os.getenv("WA_DL_URL")

@dataclass
class MediaDirSettings:
        base_dir = "./tmp/downloads"
        incoming_ogg_dir = os.path.join(base_dir, "incoming_ogg")
        incoming_mp3_dir = os.path.join(base_dir, "incoming_mp3")
        outgoing_mp3_dir = os.path.join(base_dir, "outgoing_mp3")
        outgoing_ogg_dir = os.path.join(base_dir, "outgoing_ogg")

@dataclass
class Config:
    project: ProjectSettings = field(default_factory=ProjectSettings)
    supabase: SupabaseSettings = field(default_factory=SupabaseSettings)
    openai: OpenAISettings = field(default_factory=OpenAISettings)
    stripe: StripeSettings = field(default_factory=StripeSettings)
    app: AppSettings = field(default_factory=AppSettings)
    subscription: SubscriptionVariables = field(default_factory=SubscriptionVariables)
    whatsappvars: WaVariables = field(default_factory=WaVariables)
    mediasettings: MediaDirSettings = field(default_factory=MediaDirSettings)
    

config = Config()