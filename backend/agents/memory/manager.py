"""Medical AI Memory Manager — combines all 4 memory layers."""

from __future__ import annotations

import logging
from typing import Any

from backend.agents.memory.semantic import SemanticMemory
from backend.agents.memory.episodic import EpisodicMemory
from backend.agents.memory.procedural import ProceduralMemory
from backend.agents.memory.working import WorkingMemory
from backend.db import supabase as db

log = logging.getLogger(__name__)


class MedicalAIMemoryManager:
    """Combines all 4 memory layers before every LLM call.

    - Semantic: medical knowledge graph
    - Episodic: session history
    - Procedural: researcher patterns
    - Working: current session
    """

    def __init__(self) -> None:
        self.semantic = SemanticMemory()
        self.episodic = EpisodicMemory()
        self.procedural = ProceduralMemory()
        self.working = WorkingMemory()

    def build_context(
        self, user_id: str, query: str, session_id: str | None = None, source_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """Build enriched context from all memory layers for an LLM call."""
        context: dict[str, Any] = {"query": query}

        # 1. Semantic: related medical concepts
        try:
            nodes = self.semantic.get_nodes(user_id)
            # Get relevant entity types
            relevant = []
            query_lower = query.lower()
            for n in nodes:
                if n["entity_name"].lower() in query_lower or query_lower in n["entity_name"].lower():
                    relevant.append(n)
            context["related_concepts"] = relevant[:10]
            context["knowledge_graph_size"] = len(nodes)
        except Exception as e:
            log.warning("Semantic memory error: %s", e)
            context["related_concepts"] = []

        # 2. Episodic: past sessions on same topic
        try:
            recent = self.episodic.get_recent_sessions(user_id, limit=3)
            context["recent_sessions"] = [
                {
                    "name": s.get("session_name", ""),
                    "clinical_focus": s.get("clinical_focus", ""),
                    "summary": s.get("session_summary", ""),
                    "queries": (s.get("queries_made") or [])[:5],
                }
                for s in recent
            ]
            context["modality_history"] = self.episodic.get_modality_history(user_id)
        except Exception as e:
            log.warning("Episodic memory error: %s", e)
            context["recent_sessions"] = []

        # 3. Procedural: user preferences
        try:
            context["user_preferences"] = self.procedural.get_personalization_context(user_id)
        except Exception as e:
            log.warning("Procedural memory error: %s", e)
            context["user_preferences"] = ""

        # 4. Working: current session
        if session_id:
            try:
                working_ctx = self.working.get_context(session_id)
                context["current_session"] = {
                    "active_papers": working_ctx.get("active_papers", []),
                    "research_thread": working_ctx.get("research_thread", ""),
                    "queries_this_session": len(working_ctx.get("queries", [])),
                }
            except Exception as e:
                log.warning("Working memory error: %s", e)

        return context

    def build_system_prompt(self, user_id: str, query: str, session_id: str | None = None) -> str:
        """Build a personalized system prompt using all memory layers."""
        ctx = self.build_context(user_id, query, session_id)

        parts = [
            "You are MedResearch Mind, an AI research assistant specialized in medical AI.",
            "You have deep knowledge of medical imaging, clinical datasets, and AI architectures.",
            "Always cite specific papers with section and page when answering.",
            "Never fabricate clinical claims or statistics.",
        ]

        if ctx.get("user_preferences"):
            parts.append(f"\nResearcher profile: {ctx['user_preferences']}")

        if ctx.get("recent_sessions"):
            last = ctx["recent_sessions"][0]
            if last.get("clinical_focus"):
                parts.append(f"\nLast session focus: {last['clinical_focus']}")
            if last.get("summary"):
                parts.append(f"Last session summary: {last['summary']}")

        if ctx.get("related_concepts"):
            concepts = [f"{c['entity_type']}:{c['entity_name']}" for c in ctx["related_concepts"][:5]]
            parts.append(f"\nRelated concepts in researcher's graph: {', '.join(concepts)}")

        return "\n".join(parts)

    def update_all(
        self, user_id: str, interaction: dict[str, Any], outcome: str = "accepted"
    ) -> None:
        """Update all memory layers and log training data."""
        session_id = interaction.get("session_id", "")

        # Update procedural memory
        try:
            self.procedural.update_from_interaction(user_id, interaction)
        except Exception as e:
            log.warning("Procedural update error: %s", e)

        # Update working memory
        if session_id:
            queries = self.working.get_context(session_id).get("queries", [])
            queries.append(interaction.get("query_text", ""))
            self.working.add_to_context(session_id, "queries", queries)

        # Log training data (THE MOAT)
        try:
            db.insert("training_data", {
                "interaction_type": interaction.get("interaction_type", "query"),
                "input_context": interaction.get("query_text", "")[:5000],
                "system_output": interaction.get("response", "")[:5000],
                "outcome": outcome,
                "user_modification": interaction.get("user_modification", ""),
                "modality": (interaction.get("modalities") or [""])[0] if interaction.get("modalities") else "",
                "anatomy": (interaction.get("anatomies") or [""])[0] if interaction.get("anatomies") else "",
                "condition": (interaction.get("conditions") or [""])[0] if interaction.get("conditions") else "",
                "technique": (interaction.get("techniques") or [""])[0] if interaction.get("techniques") else "",
                "quality_score": interaction.get("confidence"),
                "user_id": db.anonymize_user_id(user_id),
            }, service=True)
        except Exception as e:
            log.warning("Training data log error: %s", e)

    def get_session_welcome(self, user_id: str) -> str:
        """Generate 'last session' welcome message."""
        recent = self.episodic.get_recent_sessions(user_id, limit=1)
        if not recent:
            return "Welcome to MedResearch Mind! Upload your first medical AI papers to get started."

        last = recent[0]
        focus = last.get("clinical_focus", "")
        summary = last.get("session_summary", "")
        queries = last.get("queries_made") or []

        msg = f"Last session: {focus or 'research session'}"
        if summary:
            msg += f" — {summary}"
        if queries:
            msg += f" ({len(queries)} queries)"
        msg += ". Want to continue?"
        return msg
