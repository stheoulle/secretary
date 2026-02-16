# Twitch RAG Bot Backbone

## Prerequisites

- Python 3.6+
- Ollama installed (used to download GGUFs that llama.cpp will load)
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

1) Download models with Ollama and point llama.cpp to those files:

```bash
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull nomic-embed-text:latest

# Linux (this setup): Ollama models root
OLLAMA_MODELS_ROOT=/usr/share/ollama/.ollama/models

# Ollama stores GGUF blobs without a .gguf extension; use the manifest to find the blob
cat $OLLAMA_MODELS_ROOT/manifests/registry.ollama.ai/library/llama3.1/8b-instruct-q4_K_M
cat $OLLAMA_MODELS_ROOT/manifests/registry.ollama.ai/library/nomic-embed-text/latest

# The manifest lists sha256 digests; the GGUF blob is in:
# $OLLAMA_MODELS_ROOT/blobs/sha256-<digest>

# Example values from the manifests above:
LLAMA_CPP_MODEL_PATH=$OLLAMA_MODELS_ROOT/blobs/sha256-667b0c1932bc6ffc593ed1d03f895bf2dc8dc6df21db3042284a6f4416b06a29
LLAMA_CPP_EMBED_MODEL_PATH=$OLLAMA_MODELS_ROOT/blobs/sha256-970aa74c0a90ef7482477cf803618e776e173c007bf957f635f1015bfcfef0e6
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

- `src/rag.py` builds a simple in-memory FAISS index from your knowledge chunks, using llama.cpp embeddings.
- `src/twitch_client.py` wires Twitch chat to the RAG engine via the `!ask` command.
- `src/main.py` bootstraps config, loads the corpus, and runs the Twitch bot.

## API mode

You can also run the bot in API mode to expose a simple HTTP endpoint for questions. And then use the js client to connect to the twitch channel and forward questions from there.

```bash
python -m src.main --mode api
node script.js
```
