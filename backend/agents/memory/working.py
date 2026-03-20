"""Working Memory — current session context, cleared between sessions."""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

# In-memory store (Redis fallback ready)
_sessions: dict[str, dict[str, Any]] = {}


class WorkingMemory:
    """Manages the current research session's transient context."""

    def set_active_papers(self, session_id: str, paper_ids: list[str]) -> None:
        self._ensure(session_id)
        _sessions[session_id]["active_papers"] = paper_ids

    def get_active_papers(self, session_id: str) -> list[str]:
        self._ensure(session_id)
        return _sessions[session_id].get("active_papers", [])

    def add_paper(self, session_id: str, paper_id: str) -> None:
        self._ensure(session_id)
        papers = _sessions[session_id].get("active_papers", [])
        if paper_id not in papers:
            papers.append(paper_id)
        _sessions[session_id]["active_papers"] = papers

    def set_research_thread(self, session_id: str, thread_name: str) -> None:
        self._ensure(session_id)
        _sessions[session_id]["research_thread"] = thread_name

    def add_to_context(self, session_id: str, key: str, value: Any) -> None:
        self._ensure(session_id)
        _sessions[session_id][key] = value

    def get_context(self, session_id: str) -> dict[str, Any]:
        self._ensure(session_id)
        return dict(_sessions[session_id])

    def clear(self, session_id: str) -> None:
        _sessions.pop(session_id, None)

    def summarize(self, session_id: str) -> str:
        """Build a summary of the current session for episodic storage."""
        ctx = self.get_context(session_id)
        parts = []
        if ctx.get("research_thread"):
            parts.append(f"Research thread: {ctx['research_thread']}")
        papers = ctx.get("active_papers", [])
        if papers:
            parts.append(f"Papers reviewed: {len(papers)}")
        queries = ctx.get("queries", [])
        if queries:
            parts.append(f"Queries asked: {len(queries)}")
        gaps = ctx.get("gaps_explored", [])
        if gaps:
            parts.append(f"Gaps explored: {', '.join(gaps[:5])}")
        return ". ".join(parts) if parts else "Brief session"

    def _ensure(self, session_id: str) -> None:
        if session_id not in _sessions:
            _sessions[session_id] = {"active_papers": [], "queries": [], "gaps_explored": []}
