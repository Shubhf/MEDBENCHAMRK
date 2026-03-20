"""Ollama client — local LLM for embeddings and fallback generation."""

from __future__ import annotations

import os
import logging
from typing import AsyncIterator

import httpx

log = logging.getLogger(__name__)

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


class OllamaLLM:
    """Async HTTP client for the Ollama REST API."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base = (base_url or OLLAMA_BASE).rstrip("/")
        self._http = httpx.AsyncClient(base_url=self.base, timeout=120.0)

    async def health(self) -> bool:
        try:
            r = await self._http.get("/api/tags")
            return r.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        *,
        model: str = "llama3.1:8b",
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """Generate a completion (non-streaming, returns full text)."""
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system_prompt:
            payload["system"] = system_prompt

        r = await self._http.post("/api/generate", json=payload)
        r.raise_for_status()
        return r.json().get("response", "")

    async def generate_stream(
        self,
        prompt: str,
        *,
        model: str = "llama3.1:8b",
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream tokens from Ollama."""
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with self._http.stream("POST", "/api/generate", json=payload) as resp:
            async for line in resp.aiter_lines():
                if not line:
                    continue
                import json as _json

                data = _json.loads(line)
                token = data.get("response", "")
                if token:
                    yield token

    async def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        """Generate a single embedding vector (768 dims for nomic-embed-text)."""
        r = await self._http.post(
            "/api/embeddings", json={"model": model, "prompt": text}
        )
        r.raise_for_status()
        return r.json()["embedding"]

    async def embed_batch(
        self, texts: list[str], model: str = "nomic-embed-text"
    ) -> list[list[float]]:
        """Embed a batch of texts sequentially (Ollama has no native batch)."""
        return [await self.embed(t, model=model) for t in texts]

    async def close(self) -> None:
        await self._http.aclose()
