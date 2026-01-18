from pathlib import Path

from .config import get_config
from .rag import RAGEngine
from .twitch_client import TwitchRagBot


def bootstrap() -> None:
    config = get_config()

    rag = RAGEngine(
        model=config.rag.model,
        embed_model=config.rag.embed_model,
        top_k=config.rag.top_k,
        max_context_chars=config.rag.max_context_chars,
    )

    corpus_path = Path(config.rag.corpus_path)
    if corpus_path.exists():
        rag.ingest(corpus_path)
        print(f"Ingested corpus from {corpus_path}.")
    else:
        print(f"No corpus found at {corpus_path}. Start with an empty index.")

    bot = TwitchRagBot(config.twitch, rag)
    bot.run()


def main() -> None:
    bootstrap()


if __name__ == "__main__":
    main()
