from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class TwitchConfig:
    client_id: str
    client_secret: str
    bot_id: str
    nick: str
    prefix: str
    channels: List[str]


@dataclass
class RagConfig:
    model_path: str
    embed_model_path: str
    top_k: int = 4
    max_context_chars: int = 2800
    n_ctx: int = 4096
    n_gpu_layers: int = 0
    n_threads: Optional[int] = None
    corpus_path: Path = Path("data/knowledge.md")


@dataclass
class AppConfig:
    twitch: TwitchConfig
    rag: RagConfig


def _require(env_key: str, default: Optional[str] = None) -> str:
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
        client_id=_require("TWITCH_CLIENT_ID"),
        client_secret=_require("TWITCH_CLIENT_SECRET"),
        bot_id=_require("TWITCH_BOT_ID"),
        nick=_require("TWITCH_NICK"),
        prefix=os.getenv("TWITCH_PREFIX", "!"),
        channels=channels,
    )

    rag_cfg = RagConfig(
        model_path=_require("LLAMA_CPP_MODEL_PATH"),
        embed_model_path=_require("LLAMA_CPP_EMBED_MODEL_PATH"),
        n_ctx=int(os.getenv("LLAMA_CPP_N_CTX", "4096")),
        n_gpu_layers=int(os.getenv("LLAMA_CPP_N_GPU_LAYERS", "0")),
        n_threads=(int(os.getenv("LLAMA_CPP_N_THREADS")) if os.getenv("LLAMA_CPP_N_THREADS") else None),
    )

    return AppConfig(twitch=twitch_cfg, rag=rag_cfg)
