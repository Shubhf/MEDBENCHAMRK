"""Procedural Memory — learns each researcher's patterns and preferences."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from backend.db import supabase as db

log = logging.getLogger(__name__)


class ProceduralMemory:
    """Track and learn researcher interaction patterns for personalization."""

    def get_patterns(self, user_id: str) -> dict:
        """Get user's learned patterns."""
        results = db.select("user_patterns", filters={"user_id": user_id}, service=True)
        if results:
            return results[0]
        # Initialize patterns for new user
        return self._init_patterns(user_id)

    def _init_patterns(self, user_id: str) -> dict:
        pattern = {
            "user_id": user_id,
            "clinical_areas": [],
            "preferred_modalities": [],
            "interpretability_focus": False,
            "federated_focus": False,
            "edge_deployment_focus": False,
            "rare_disease_focus": False,
            "interaction_patterns": {},
        }
        try:
            db.insert("user_patterns", pattern, service=True)
        except Exception:
            pass
        return pattern

    def update_from_interaction(self, user_id: str, interaction: dict) -> None:
        """Update patterns based on a new interaction."""
        patterns = self.get_patterns(user_id)
        ip = patterns.get("interaction_patterns") or {}

        # Track query types
        query_type = interaction.get("query_type", "")
        type_counts = ip.get("query_type_counts", {})
        type_counts[query_type] = type_counts.get(query_type, 0) + 1
        ip["query_type_counts"] = type_counts

        # Track clinical areas
        clinical_areas = list(set(
            (patterns.get("clinical_areas") or []) +
            interaction.get("anatomies", []) +
            interaction.get("conditions", [])
        ))

        # Track modality preferences
        modalities = list(set(
            (patterns.get("preferred_modalities") or []) +
            interaction.get("modalities", [])
        ))

        # Detect focus areas from keywords
        query_text = interaction.get("query_text", "").lower()
        interpretability = patterns.get("interpretability_focus", False)
        if any(kw in query_text for kw in ["grad-cam", "shap", "explainability", "interpretab"]):
            interpretability = True

        federated = patterns.get("federated_focus", False)
        if any(kw in query_text for kw in ["federated", "privacy", "differential privacy"]):
            federated = True

        edge = patterns.get("edge_deployment_focus", False)
        if any(kw in query_text for kw in ["edge", "mobile", "lightweight", "deployment"]):
            edge = True

        rare = patterns.get("rare_disease_focus", False)
        if any(kw in query_text for kw in ["rare disease", "orphan", "uncommon"]):
            rare = True

        db.update("user_patterns", user_id, {
            "clinical_areas": clinical_areas[:20],
            "preferred_modalities": modalities[:10],
            "interpretability_focus": interpretability,
            "federated_focus": federated,
            "edge_deployment_focus": edge,
            "rare_disease_focus": rare,
            "interaction_patterns": ip,
            "last_updated": datetime.utcnow().isoformat(),
        }, service=True)

    def get_personalization_context(self, user_id: str) -> str:
        """Build a personalization string for LLM prompts."""
        p = self.get_patterns(user_id)
        parts = []

        if p.get("clinical_areas"):
            parts.append(f"Research focus: {', '.join(p['clinical_areas'][:5])}")
        if p.get("preferred_modalities"):
            parts.append(f"Preferred modalities: {', '.join(p['preferred_modalities'][:5])}")
        if p.get("interpretability_focus"):
            parts.append("Values interpretability/explainability in models")
        if p.get("federated_focus"):
            parts.append("Interested in federated/privacy-preserving approaches")
        if p.get("edge_deployment_focus"):
            parts.append("Interested in edge/mobile deployment")
        if p.get("rare_disease_focus"):
            parts.append("Focuses on rare diseases")

        return "; ".join(parts) if parts else "New researcher — no patterns learned yet"
