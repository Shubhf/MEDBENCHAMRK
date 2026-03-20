"""Groq LLM client — primary free inference provider."""

from __future__ import annotations

import os
import logging
from typing import AsyncIterator

import groq

log = logging.getLogger(__name__)


class GroqLLM:
    """Async wrapper around the Groq SDK."""

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            log.warning("GROQ_API_KEY not set — Groq calls will fail")
        self.client = groq.AsyncGroq(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        *,
        model: str = "llama-3.3-70b-versatile",
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str:
        """Generate a single completion."""
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        resp = await self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    async def generate_stream(
        self,
        prompt: str,
        *,
        model: str = "llama-3.3-70b-versatile",
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream tokens."""
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
