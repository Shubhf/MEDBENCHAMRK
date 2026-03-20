"""Episodic Memory — per-user research session history."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from backend.db import supabase as db

log = logging.getLogger(__name__)


class EpisodicMemory:
    """Track per-user research history: sessions, queries, papers read."""

    def start_session(self, user_id: str, session_name: str = "", clinical_focus: str = "") -> dict:
        """Start a new research session."""
        return db.insert("sessions", {
            "user_id": user_id,
            "session_name": session_name or f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "clinical_focus": clinical_focus,
            "is_active": True,
            "sources_accessed": [],
            "queries_made": [],
            "gaps_explored": [],
        }, service=True)

    def end_session(self, session_id: str, summary: str = "") -> dict:
        """End a session and store summary."""
        return db.update("sessions", session_id, {
            "is_active": False,
            "ended_at": datetime.utcnow().isoformat(),
            "session_summary": summary,
        }, service=True)

    def log_query(
        self, user_id: str, session_id: str, query_text: str,
        query_type: str, response: str, citations: list[dict],
        confidence: float, source_ids: list[str],
    ) -> dict:
        """Log a query and its response."""
        row = db.insert("queries", {
            "user_id": user_id,
            "session_id": session_id,
            "query_text": query_text,
            "query_type": query_type,
            "response": response,
            "citations": citations,
            "confidence": confidence,
            "sources_used": source_ids,
        }, service=True)
        # Update session queries list
        session = db.select("sessions", filters={"id": session_id}, service=True)
        if session:
            queries_made = session[0].get("queries_made") or []
            queries_made.append(query_text[:200])
            db.update("sessions", session_id, {"queries_made": queries_made}, service=True)
        return row

    def get_recent_sessions(self, user_id: str, limit: int = 5) -> list[dict]:
        return db.select("sessions", filters={"user_id": user_id}, order="-started_at", limit=limit, service=True)

    def get_session_detail(self, session_id: str) -> dict | None:
        results = db.select("sessions", filters={"id": session_id}, service=True)
        return results[0] if results else None

    def get_active_session(self, user_id: str) -> dict | None:
        results = db.select("sessions", filters={"user_id": user_id, "is_active": True}, limit=1, service=True)
        return results[0] if results else None

    def get_modality_history(self, user_id: str) -> dict[str, int]:
        """Which imaging modalities has the user focused on."""
        sources = db.select("sources", filters={"user_id": user_id}, service=True)
        counts: dict[str, int] = {}
        for s in sources:
            for mod in (s.get("imaging_modalities") or []):
                counts[mod] = counts.get(mod, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    def get_research_threads(self, user_id: str) -> list[dict]:
        """Get named research threads grouped by clinical area."""
        sessions = db.select("sessions", filters={"user_id": user_id}, order="-started_at", service=True)
        threads: dict[str, list[dict]] = {}
        for s in sessions:
            focus = s.get("clinical_focus") or "General"
            threads.setdefault(focus, []).append(s)
        return [{"clinical_focus": k, "sessions": v} for k, v in threads.items()]

    def get_query_history(self, user_id: str, limit: int = 50) -> list[dict]:
        return db.select("queries", filters={"user_id": user_id}, order="-created_at", limit=limit, service=True)
