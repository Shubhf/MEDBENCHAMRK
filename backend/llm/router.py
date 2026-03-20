"""LLM Router — Groq-first with Ollama fallback. Claude slot ready."""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from backend.llm.groq import GroqLLM
from backend.llm.ollama import OllamaLLM

log = logging.getLogger(__name__)

TASK_ROUTING: dict[str, str] = {
    # Primary reasoning (Llama 3.3 70B — best free model on Groq)
    "gap_analysis": "groq-llama3.3-70b",
    "qa_grounded": "groq-llama3.3-70b",
    "medical_extraction": "groq-llama3.3-70b",
    "experiment_design": "groq-llama3.3-70b",
    # Reasoning-heavy tasks (Qwen 3 32B with thinking)
    "deep_analysis": "groq-qwen3-32b",
    # Local tasks (free, no rate limits)
    "summarization": "ollama-llama3.1-8b",
    "embeddings": "ollama-nomic-embed-text",
    # Lighter classification
    "classification": "groq-llama4-scout",
    # Ready for Claude when key is available:
    # "gap_analysis": "claude-sonnet",
    # "qa_grounded": "claude-sonnet",
}


class LLMRouter:
    """Routes tasks to the optimal LLM provider."""

    def __init__(self) -> None:
        self.groq = GroqLLM()
        self.ollama = OllamaLLM()

    def _resolve(self, task: str) -> tuple[str, str]:
        """Return (provider, model) for a task."""
        tag = TASK_ROUTING.get(task, "groq-llama3-70b")
        if tag.startswith("groq-"):
            model_map = {
                "groq-llama3.3-70b": "llama-3.3-70b-versatile",
                "groq-qwen3-32b": "qwen-3-32b",
                "groq-llama4-scout": "meta-llama/llama-4-scout-17b-16e-instruct",
                "groq-gptoss-120b": "gpt-oss-120b",
            }
            return "groq", model_map.get(tag, "llama-3.3-70b-versatile")
        if tag.startswith("ollama-"):
            model_map = {
                "ollama-llama3.1-8b": "llama3.1:8b",
                "ollama-nomic-embed-text": "nomic-embed-text",
            }
            return "ollama", model_map.get(tag, "llama3.1:8b")
        return "groq", "llama-3.3-70b-versatile"

    async def generate(
        self,
        task: str,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str:
        """Generate a completion, with automatic fallback."""
        provider, model = self._resolve(task)
        try:
            if provider == "groq":
                return await self.groq.generate(
                    prompt,
                    model=model,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                )
            else:
                return await self.ollama.generate(
                    prompt,
                    model=model,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
        except Exception as exc:
            log.warning("Primary LLM failed (%s/%s): %s — falling back to Ollama", provider, model, exc)
            return await self.ollama.generate(
                prompt,
                model="llama3.1:8b",
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    async def generate_stream(
        self,
        task: str,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream tokens from the appropriate LLM."""
        provider, model = self._resolve(task)
        try:
            if provider == "groq":
                async for chunk in self.groq.generate_stream(
                    prompt, model=model, system_prompt=system_prompt,
                    temperature=temperature, max_tokens=max_tokens,
                ):
                    yield chunk
            else:
                async for chunk in self.ollama.generate_stream(
                    prompt, model=model, system_prompt=system_prompt,
                    temperature=temperature, max_tokens=max_tokens,
                ):
                    yield chunk
        except Exception as exc:
            log.warning("Streaming failed (%s/%s): %s — falling back", provider, model, exc)
            async for chunk in self.ollama.generate_stream(
                prompt, model="llama3.1:8b", system_prompt=system_prompt,
                temperature=temperature, max_tokens=max_tokens,
            ):
                yield chunk

    async def embed(self, text: str) -> list[float]:
        """Generate a 768-dim embedding (HuggingFace in prod, Ollama locally)."""
        from backend.processors.embedder import Embedder
        if not hasattr(self, "_embedder"):
            self._embedder = Embedder()
        return await self._embedder.embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts."""
        return [await self.embed(t) for t in texts]
