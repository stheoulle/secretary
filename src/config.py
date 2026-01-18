from dataclasses import dataclass
from pathlib import Path
from typing import List
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class TwitchConfig:
    token: str
    client_id: str
    client_secret: str
    bot_id: str
    nick: str
    prefix: str
    channels: List[str]


@dataclass
class RagConfig:
    model: str
    embed_model: str
    top_k: int = 4
    max_context_chars: int = 2800
    corpus_path: Path = Path("data/knowledge.md")


@dataclass
class AppConfig:
    twitch: TwitchConfig
    rag: RagConfig


def _require(env_key: str, default: str | None = None) -> str:
    value = os.getenv(env_key, default)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {env_key}")
    return value


def get_config() -> AppConfig:
    twitch_channels = os.getenv("TWITCH_CHANNELS", "")
    channels = [c.strip() for c in twitch_channels.split(",") if c.strip()]
    if not channels:
        raise ValueError("TWITCH_CHANNELS must list at least one channel")

    twitch_cfg = TwitchConfig(
        token=_require("TWITCH_OAUTH_TOKEN"),
        client_id=_require("TWITCH_CLIENT_ID"),
        client_secret=_require("TWITCH_CLIENT_SECRET"),
        bot_id=_require("TWITCH_BOT_ID"),
        nick=_require("TWITCH_NICK"),
        prefix=os.getenv("TWITCH_PREFIX", "!"),
        channels=channels,
    )

    rag_cfg = RagConfig(
        model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
    )

    return AppConfig(twitch=twitch_cfg, rag=rag_cfg)
