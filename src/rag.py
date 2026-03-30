from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List, Dict, Any

import faiss
import numpy as np
import ollama


class RAGEngine:
    def __init__(self, model: str, embed_model: str, top_k: int = 4, max_context_chars: int = 2800):
        self.model = model
        self.embed_model = embed_model
        self.top_k = top_k
        self.max_context_chars = max_context_chars

        self._index: faiss.Index | None = None
        self._chunks: List[Dict[str, Any]] = []
        self._system_prompt = (
            "You are a concise Twitch bot answering questions about Chloe. "
            "IMPORTANT: Only answer based on the provided context. "
            "If the context does not contain information to answer the question, respond with exactly: 'I don't know.' "
            "Do not make up information or speculate. Be friendly and concise."
        )

    def ingest(self, corpus_path: Path) -> None:
        if not corpus_path.exists():
            raise FileNotFoundError(f"Corpus not found at {corpus_path}")

        text = corpus_path.read_text(encoding="utf-8")
        for chunk in self._split_chunks(text):
            vec = self._embed(chunk)
            self._add_vector(vec, {"text": chunk, "source": str(corpus_path)})

    def _split_chunks(self, text: str) -> List[str]:
        raw_blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        chunks: List[str] = []
        current: List[str] = []
        for block in raw_blocks:
            if len(" ".join(current + [block])) > 600:
                chunks.append(" ".join(current))
                current = []
            current.append(block)
        if current:
            chunks.append(" ".join(current))
        return chunks

    def _embed(self, text: str) -> np.ndarray:
        response = ollama.embeddings(model=self.embed_model, prompt=text)
        vec = np.array(response["embedding"], dtype=np.float32)
        return vec

    def _add_vector(self, vector: np.ndarray, metadata: Dict[str, Any]) -> None:
        if self._index is None:
            dim = int(vector.shape[0])
            self._index = faiss.IndexFlatIP(dim)
        normed = vector / np.linalg.norm(vector)
        self._index.add(normed.reshape(1, -1))
        self._chunks.append(metadata)

    def query(self, question: str) -> str:
        if not self._index or self._index.ntotal == 0:
            return "I am not trained yet."
        
        print("Searching for relevant context...")

        q_vec = self._embed(question)
        q_vec = q_vec / np.linalg.norm(q_vec)
        scores, idx = self._index.search(q_vec.reshape(1, -1), min(self.top_k, len(self._chunks)))
        selected = [self._chunks[i]["text"] for i in idx[0] if i >= 0]
        context = "\n\n".join(selected)[: self.max_context_chars]

        print("Generating answer...")

        # Use chat API with system message for better context management
        # keep_alive keeps model loaded in memory for faster subsequent requests
        messages = [
            {"role": "system", "content": f"{self._system_prompt}\n\nContext:\n{context}"},
            {"role": "user", "content": question}
        ]
        
        print(f"Thinking")
        reply = ollama.chat(
            model=self.model, 
            messages=messages,
            options={
                "num_ctx": 4096,  # Context window size
            },
            keep_alive="5m"  # Keep model loaded for 5 minutes
        )
        return reply.get("message", {}).get("content", "").strip()

    async def aquery(self, question: str) -> str:
        return await asyncio.to_thread(self.query, question)
