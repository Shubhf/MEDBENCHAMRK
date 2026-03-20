"""Claude client — ready slot for when API key becomes available.

To activate:
1. Set ANTHROPIC_API_KEY in .env
2. Change PRIMARY_LLM=anthropic in .env
3. Update router.py TASK_ROUTING to use claude-sonnet
"""

from __future__ import annotations

import os
import logging

log = logging.getLogger(__name__)


class ClaudeLLM:
    """Placeholder Claude client. Activate by setting ANTHROPIC_API_KEY."""

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self._client = None
        if self.api_key:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
                log.info("Claude client initialized successfully")
            except ImportError:
                log.warning("anthropic package not installed — pip install anthropic")

    async def generate(
        self,
        prompt: str,
        *,
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        if not self._client:
            raise RuntimeError(
                "Claude API key not configured. "
                "Set ANTHROPIC_API_KEY in .env and pip install anthropic"
            )
        msg = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "You are a medical AI research assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
