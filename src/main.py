from pathlib import Path
import sys
import argparse

from .config import get_config
from .rag import RAGEngine
from .twitch_client import TwitchRagBot


def bootstrap_rag() -> tuple[RAGEngine, str]:
    """Initialize and return the RAG engine."""
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
        print(f"No corpus found at {corpus_path}. Starting with an empty index.")

    return rag, config


def run_cli(rag: RAGEngine) -> None:
    """Interactive CLI mode for debugging."""
    print("\n=== RAG CLI Mode ===")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            question = input("You: ").strip()
            if question.lower() in ("exit", "quit"):
                break
            if not question:
                continue
            answer = rag.query(question)
            print(f"Bot: {answer}\n")
        except KeyboardInterrupt:
            break


def run_twitch(config) -> None:
    """Start the Twitch bot."""
    rag, _ = bootstrap_rag()
    bot = TwitchRagBot(config.twitch, rag)
    bot.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="Twitch RAG Bot")
    parser.add_argument(
        "--mode",
        choices=["cli", "twitch"],
        default="twitch",
        help="Run mode: 'cli' for interactive debugging, 'twitch' for Twitch bot (default: twitch)",
    )
    args = parser.parse_args()

    rag, config = bootstrap_rag()

    if args.mode == "cli":
        run_cli(rag)
    else:
        bot = TwitchRagBot(config.twitch, rag)
        bot.run()


if __name__ == "__main__":
    main()
