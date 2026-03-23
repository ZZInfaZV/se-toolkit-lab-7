"""Configuration loader for the bot.

Loads environment variables from .env.bot.secret file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from .env.bot.secret.
    
    Returns:
        Dictionary with configuration values.
    """
    # Find the .env.bot.secret file in the bot directory
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"
    
    # Load the environment file
    load_dotenv(env_file)
    
    # Return configuration values
    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_URL": os.getenv("LMS_API_URL", "http://localhost:42002"),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1"),
        "LLM_API_MODEL": os.getenv("LLM_API_MODEL", "coder-model"),
    }
