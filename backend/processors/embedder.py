"""Embedding generator — HuggingFace Inference API (production) with Ollama fallback (local dev)."""

from __future__ import annotations

import hashlib
import logging
import os

import httpx

log = logging.getLogger(__name__)

_cache: dict[str, list[float]] = {}

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = "nomic-ai/nomic-embed-text-v1.5"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class Embedder:
    """Generate 768-dim embeddings. Uses HuggingFace API in production, Ollama locally."""

    def __init__(self) -> None:
        self._use_hf = bool(HF_TOKEN)
        self._http: httpx.AsyncClient | None = None
        self._ollama = None

    def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=60.0)
        return self._http

    def _get_ollama(self):
        if self._ollama is None:
            from backend.llm.ollama import OllamaLLM
            self._ollama = OllamaLLM()
        return self._ollama

    async def _embed_hf(self, text: str) -> list[float]:
        """Embed via HuggingFace Inference API (nomic-embed-text-v1.5)."""
        http = self._get_http()
        resp = await http.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": text, "options": {"wait_for_model": True}},
        )
        resp.raise_for_status()
        data = resp.json()
        # HF returns [[float, ...]] for single input
        if isinstance(data, list) and data and isinstance(data[0], list):
            return data[0]
        return data

    async def _embed_ollama(self, text: str) -> list[float]:
        """Embed via local Ollama nomic-embed-text."""
        return await self._get_ollama().embed(text)

    async def embed(self, text: str) -> list[float]:
        """Generate a single 768-dim embedding with caching and fallback."""
        key = _hash(text)
        if key in _cache:
            return _cache[key]

        if self._use_hf:
            try:
                vec = await self._embed_hf(text)
                _cache[key] = vec
                return vec
            except Exception as e:
                log.warning("HuggingFace embedding failed: %s — falling back to Ollama", e)

        vec = await self._embed_ollama(text)
        _cache[key] = vec
        return vec

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""
        results: list[list[float]] = []
        for t in texts:
            results.append(await self.embed(t))
        return results

    async def close(self) -> None:
        if self._http:
            await self._http.aclose()
        if self._ollama:
            await self._ollama.close()
