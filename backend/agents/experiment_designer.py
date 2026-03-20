"""PICO Experiment Designer — generate structured experiment proposals."""

from __future__ import annotations

import json
import logging
from typing import Any

from backend.db import supabase as db
from backend.llm.router import LLMRouter

log = logging.getLogger(__name__)


class ExperimentDesigner:
    """Design PICO-formatted medical AI experiments from research gaps."""

    def __init__(self, llm: LLMRouter | None = None) -> None:
        self.llm = llm or LLMRouter()

    async def design(self, gap_description: str, context: str, user_id: str) -> dict:
        """Design a full experiment proposal in PICO format."""
        prompt = f"""You are an expert medical AI researcher. Design a rigorous experiment proposal.

Research Gap:
{gap_description}

Context from related papers:
{context[:3000]}

Design the experiment in PICO format with ALL of these sections:

1. RESEARCH QUESTION (clear, specific, testable)
2. PICO:
   - Population: specific patient population, inclusion/exclusion criteria
   - Intervention: the proposed AI method/approach
   - Comparison: baseline methods to compare against
   - Outcome: primary and secondary outcome measures
3. SUGGESTED DATASETS: specific public datasets with names, sizes, URLs
4. MODEL ARCHITECTURE: recommended architecture with justification
5. EVALUATION PROTOCOL: train/val/test split, cross-validation, metrics
6. EXPECTED CHALLENGES: data, compute, clinical, ethical
7. COMPUTE ESTIMATE: GPU hours, recommended hardware
8. SUGGESTED ABLATIONS: systematic experiments to run

Return valid JSON:
{{
  "research_question": "...",
  "pico": {{
    "population": "...",
    "intervention": "...",
    "comparison": "...",
    "outcome": "..."
  }},
  "suggested_datasets": [{{"name": "...", "size": "...", "url": "...", "modality": "..."}}],
  "model_architecture": "...",
  "architecture_justification": "...",
  "evaluation_protocol": "...",
  "expected_challenges": ["..."],
  "compute_estimate": "...",
  "suggested_ablations": ["..."],
  "estimated_timeline": "...",
  "ethical_considerations": "..."
}}"""

        try:
            response = await self.llm.generate(
                "experiment_design", prompt,
                system_prompt="You are a medical AI experiment designer. Be specific, practical, and cite real datasets.",
                json_mode=True, temperature=0.3, max_tokens=4096,
            )
            proposal = json.loads(response)

            # Save to database
            saved = db.insert("experiments", {
                "user_id": user_id,
                "gap_description": gap_description,
                "pico": proposal.get("pico", {}),
                "datasets": proposal.get("suggested_datasets", []),
                "architecture": proposal.get("model_architecture", ""),
                "evaluation_protocol": proposal.get("evaluation_protocol", ""),
                "challenges": proposal.get("expected_challenges", []),
                "compute_estimate": proposal.get("compute_estimate", ""),
                "ablations": proposal.get("suggested_ablations", []),
            }, service=True)
            proposal["id"] = saved.get("id", "")

            # Log training data (best-effort)
            try:
                db.insert("training_data", {
                    "interaction_type": "experiment_design",
                    "input_context": gap_description[:3000],
                    "system_output": json.dumps(proposal)[:5000],
                    "outcome": "accepted",
                    "user_id": db.anonymize_user_id(user_id),
                }, service=True)
            except Exception as te:
                log.warning("Training data log failed: %s", te)

            return proposal
        except Exception as e:
            log.error("Experiment design failed: %s", e)
            return {"error": str(e), "gap_description": gap_description}

    def get_history(self, user_id: str, limit: int = 20) -> list[dict]:
        return db.select("experiments", filters={"user_id": user_id}, order="-created_at", limit=limit, service=True)
