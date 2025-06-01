from .general_config import Config

# Create a config instance
config = Config()

# Export the config and individual settings classes
__all__ = [
    'config',
    'Config',
    'SupabaseSettings',
    'OpenAISettings',
    'StripeSettings',
    'AppSettings'
]