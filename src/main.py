from pathlib import Path
import sys
import argparse
from flask import Flask, request, jsonify

from .config import get_config
from .rag import RAGEngine
from .twitch_client import TwitchRagBot


def bootstrap_rag() -> tuple[RAGEngine, str]:
    """Initialize and return the RAG engine."""
    config = get_config()

    rag = RAGEngine(
        model_path=config.rag.model_path,
        embed_model_path=config.rag.embed_model_path,
        top_k=config.rag.top_k,
        max_context_chars=config.rag.max_context_chars,
        n_ctx=config.rag.n_ctx,
        n_gpu_layers=config.rag.n_gpu_layers,
        n_threads=config.rag.n_threads,
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


def run_api(port: int = 5000) -> None:
    """Start the API server."""
    print("Bootstrapping RAG engine...")
    rag, config = bootstrap_rag()
    print("RAG engine initialized. Starting API server...")
    
    app = Flask(__name__)
    print("API server initialized. Setting up routes...")
    
    @app.route("/query", methods=["POST"])
    def query_endpoint():
        """Handle RAG query requests."""
        data = request.get_json()
        
        if not data or "question" not in data:
            return jsonify({"error": "Missing 'question' field in request body"}), 400
        
        question = data["question"].strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
        
        try:
            answer = rag.query(question)
            return jsonify({
                "question": question,
                "answer": answer
            }), 200
        except Exception as e:
            return jsonify({"error": f"Error processing query: {str(e)}"}), 500
    
    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy"}), 200
    
    print(f"Starting API server on http://localhost:{port}")
    print(f"POST /query - Submit a question")
    print(f"GET /health - Health check")
    app.run(host="0.0.0.0", port=port, debug=False)


def main() -> None:
    print("Starting Twitch RAG Bot application...")
    parser = argparse.ArgumentParser(description="Twitch RAG Bot")
    parser.add_argument(
        "--mode",
        choices=["cli", "twitch", "api"],
        default="twitch",
        help="Run mode: 'cli' for interactive debugging, 'twitch' for Twitch bot, 'api' for API server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the API server on (only used with --mode api)",
    )

    print("Parsing command-line arguments...")
    args = parser.parse_args()
    print(f"Selected mode: {args.mode}")

    rag, config = bootstrap_rag()
    print("RAG engine is ready.")

    if args.mode == "cli":
        run_cli(rag)
    elif args.mode == "api":
        run_api(port=args.port)
    else:
        bot = TwitchRagBot(config.twitch, rag)
        bot.run()



if __name__ == "__main__":
    main()
