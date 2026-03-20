"""Shared dependencies for API routes."""

from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, HTTPException, Header

from backend.db import supabase as db
from backend.llm.router import LLMRouter
from backend.agents.memory.manager import MedicalAIMemoryManager

_llm_router: LLMRouter | None = None
_memory_manager: MedicalAIMemoryManager | None = None


DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


async def get_current_user(authorization: str = Header(default="")) -> dict[str, Any]:
    """Validate Supabase JWT. Falls back to demo user if no auth (for testing)."""
    if not authorization:
        # Demo mode — no auth required for testing
        return {"id": DEMO_USER_ID, "email": "demo@medresearchmind.app"}

    token = authorization.replace("Bearer ", "")
    try:
        client = db.get_client()
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            return {"id": DEMO_USER_ID, "email": "demo@medresearchmind.app"}
        user = user_response.user
        return {"id": user.id, "email": user.email}
    except Exception:
        return {"id": DEMO_USER_ID, "email": "demo@medresearchmind.app"}


def get_llm_router() -> LLMRouter:
    global _llm_router
    if _llm_router is None:
        _llm_router = LLMRouter()
    return _llm_router


def get_memory_manager() -> MedicalAIMemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MedicalAIMemoryManager()
    return _memory_manager
