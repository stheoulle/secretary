# Twitch RAG Bot Backbone

## Prerequisites

- Python 3.11+
- An Ollama daemon running locally with models pulled:
  - `ollama serve` in a separate terminal (you need Ollama installed: <https://ollama.com/>)
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

1) Copy env template and fill it:

```bash
cp .env.example .env
```

1) Add your knowledge in `data/knowledge.md`. The default sample is already included.
2) Run the bot or run in CLI mode:

```bash
python -m src.main
```

## CLI Commands

```bash
python -m src.main --mode cli
```

Runs a simple CLI interface to ask questions against the RAG engine without Twitch.

## How it works

- `src/rag.py` builds a simple in-memory FAISS index from your knowledge chunks, using Ollama embeddings.
- `src/twitch_client.py` wires Twitch chat to the RAG engine via the `!ask` command.
- `src/main.py` bootstraps config, loads the corpus, and runs the Twitch bot.

## API mode

You can also run the bot in API mode to expose a simple HTTP endpoint for questions. And then use the js client to connect to the twitch channel and forward questions from there.

```bash
ollama serve
python -m src.main --mode api
node script.js
```
