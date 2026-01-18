# Twitch RAG Bot Backbone

A minimal scaffold for a Twitch chat bot that routes questions into an Ollama-backed Retrieval Augmented Generation (RAG) pipeline. Fill the knowledge base with your own facts (e.g., "where are you from?", "what languages do you speak?") and let the bot answer via `!ask`.

## Prerequisites

- Python 3.11+
- An Ollama daemon running locally with models pulled:
  - `ollama serve` in a separate terminal
  - Chat model (e.g., `ollama pull llama3.1`)
  - Embedding model (e.g., `ollama pull nomic-embed-text`)
- Twitch credentials (OAuth token, bot nick, channels).

## Setup

1) Install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Copy env template and fill it:

```bash
cp .env.example .env
```

3) Add your knowledge in `data/knowledge.md`. The default sample is already included.
2) Run the bot:

```bash
python -m src.main
```

## How it works

- `src/rag.py` builds a simple in-memory FAISS index from your knowledge chunks, using Ollama embeddings.
- `src/twitch_client.py` wires Twitch chat to the RAG engine via the `!ask` command.
- `src/main.py` bootstraps config, loads the corpus, and runs the Twitch bot.

## Next steps

- Persist the FAISS index to disk between runs.
- Add moderation/ratelimiting before calling the model.
- Expand command set (e.g., `!teach` to add new facts live).
# secretary
