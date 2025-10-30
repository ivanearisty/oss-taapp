"""Discord Client Implementation.

This module provides a concrete implementation of the chat client API using the Discord API.
It handles OAuth2 authentication and provides methods to interact with Discord.

"""

import logging
import os
from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

import httpx
from authlib.integrations.httpx_client import OAuth2Client
from chat_client_api.client import Client
from chat_client_api.message import Channel, ChatMessage


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # If python-dotenv is not available, check if .env file exists
    # and manually load it
    env_path = Path(".env")
    if env_path.exists():
        with env_path.open() as f:
            for raw_line in f:
                line = raw_line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


class DiscordClient(Client):
    """Concrete implementation of the Client abstraction using Discord API."""

    DISCORD_API_BASE = "https://discord.com/api/v10"
    OAUTH2_AUTHORIZE_URL = "https://discord.com/api/oauth2/authorize"
    OAUTH2_TOKEN_URL = "https://discord.com/api/oauth2/token"

    def __init__(slef, ):

