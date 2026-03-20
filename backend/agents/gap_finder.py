"""Medical AI Gap Finder — THE HERO FEATURE.

Analyzes collections of medical AI papers to find research gaps
with clinical awareness. Every gap quotes specific text from specific papers.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from backend.db import supabase as db
from backend.llm.router import LLMRouter

log = logging.getLogger(__name__)

GAP_TYPES = [
    "modality_gap",
    "population_gap",
    "geography_gap",
    "architecture_gap",
    "multimodal_gap",
    "interpretability_gap",
    "federated_gap",
    "deployment_gap",
    "clinical_validation_gap",
    "rare_disease_gap",
]


@dataclass
class Gap:
    gap_type: str = ""
    description: str = ""
    evidence: list[dict[str, str]] = field(default_factory=list)  # [{paper_title, quote, page}]
    clinical_relevance_score: float = 0.0
    feasibility_score: float = 0.0
    suggested_experiment: str = ""
    papers_to_cite: list[str] = field(default_factory=list)


@dataclass
class GapReport:
    id: str = ""
    source_ids: list[str] = field(default_factory=list)
    clinical_topic: str = ""
    gaps: list[Gap] = field(default_factory=list)
    experiment_proposals: list[dict] = field(default_factory=list)
    summary: str = ""


class MedicalGapFinder:
    """Analyze medical AI papers to find research gaps with clinical awareness."""

    def __init__(self, llm: LLMRouter | None = None) -> None:
        self.llm = llm or LLMRouter()

    async def analyze(self, source_ids: list[str], user_id: str) -> GapReport:
        """Analyze a collection of papers and find research gaps."""
        # Fetch all sources with metadata
        sources = []
        for sid in source_ids:
            results = db.select("sources", filters={"id": sid, "user_id": user_id}, service=True)
            if results:
                sources.append(results[0])

        if not sources:
            raise ValueError("No sources found for the given IDs")

        # Build analysis context
        papers_context = self._build_papers_context(sources)
        clinical_topic = self._infer_clinical_topic(sources)

        # Run gap analysis via LLM
        gaps = await self._find_gaps(papers_context, sources)

        # Generate experiment proposals for top gaps
        proposals = []
        for gap in gaps[:5]:
            proposal = await self._design_experiment(gap, papers_context)
            proposals.append(proposal)

        report = GapReport(
            source_ids=source_ids,
            clinical_topic=clinical_topic,
            gaps=gaps,
            experiment_proposals=proposals,
            summary=f"Analyzed {len(sources)} papers on {clinical_topic}. Found {len(gaps)} research gaps.",
        )

        # Save to database
        saved = db.insert("gap_reports", {
            "user_id": user_id,
            "source_ids": source_ids,
            "clinical_topic": clinical_topic,
            "gaps": [self._gap_to_dict(g) for g in gaps],
            "experiment_proposals": proposals,
        }, service=True)
        report.id = saved.get("id", "")

        return report

    def _build_papers_context(self, sources: list[dict]) -> str:
        """Build a structured summary of all papers for the LLM."""
        context_parts = []
        for i, s in enumerate(sources):
            part = f"""
PAPER {i+1}: {s.get('title', 'Untitled')}
Authors: {', '.join(s.get('authors', [])[:5])}
Venue: {s.get('journal_or_venue', 'N/A')}
Imaging Modalities: {', '.join(s.get('imaging_modalities', []))}
Anatomies: {', '.join(s.get('anatomies', []))}
Conditions: {', '.join(s.get('conditions', []))}
Architectures: {', '.join(s.get('architectures', []))}
Datasets: {', '.join(s.get('datasets_used', []))}
Metrics: {', '.join(s.get('metrics_reported', []))}
Techniques: {', '.join(s.get('techniques', []))}
Limitations: {', '.join(s.get('limitations', []))}
Future Work: {', '.join(s.get('future_work', []))}
Clinical Relevance: {s.get('clinical_relevance', 'unknown')}"""
            context_parts.append(part)
        return "\n".join(context_parts)

    def _infer_clinical_topic(self, sources: list[dict]) -> str:
        """Infer the main clinical topic from the paper collection."""
        all_conditions = []
        all_anatomies = []
        for s in sources:
            all_conditions.extend(s.get("conditions") or [])
            all_anatomies.extend(s.get("anatomies") or [])

        if all_conditions:
            from collections import Counter
            most_common = Counter(all_conditions).most_common(1)[0][0]
            return most_common
        if all_anatomies:
            from collections import Counter
            return Counter(all_anatomies).most_common(1)[0][0]
        return "Medical AI"

    async def _find_gaps(self, papers_context: str, sources: list[dict]) -> list[Gap]:
        """Use LLM to identify research gaps across the paper collection."""
        prompt = f"""You are a medical AI research gap detector with expertise in clinical AI.

Analyze these {len(sources)} medical AI papers and identify research gaps.

{papers_context}

For each gap found, provide:
1. gap_type: one of {GAP_TYPES}
2. description: clear description of what's missing
3. evidence: specific observations from specific papers (quote paper titles)
4. clinical_relevance_score: 0.0-1.0 (how important clinically)
5. feasibility_score: 0.0-1.0 (how feasible to address)
6. suggested_experiment: brief experiment idea to address this gap
7. papers_to_cite: which papers from the collection are relevant

CRITICAL RULES:
- Every gap MUST reference specific papers by title
- Never fabricate information not present in the papers above
- Focus on gaps that are clinically meaningful, not just statistically interesting
- Consider: modality gaps, population gaps, geography gaps, architecture gaps,
  multimodal gaps, interpretability gaps, federated/privacy gaps,
  deployment gaps, clinical validation gaps, rare disease gaps

Return ONLY valid JSON array of gap objects.
Return at most 10 gaps, ranked by clinical_relevance_score descending.

JSON format:
[{{
  "gap_type": "...",
  "description": "...",
  "evidence": [{{"paper_title": "...", "observation": "..."}}],
  "clinical_relevance_score": 0.0,
  "feasibility_score": 0.0,
  "suggested_experiment": "...",
  "papers_to_cite": ["paper title 1", "paper title 2"]
}}]"""

        try:
            response = await self.llm.generate(
                "gap_analysis", prompt,
                system_prompt="You are an expert medical AI researcher. Identify genuine research gaps. Never fabricate.",
                json_mode=True, temperature=0.2, max_tokens=4096,
            )
            gaps_data = json.loads(response)
            if isinstance(gaps_data, dict):
                # LLM may wrap in {"gaps": [...]} or similar
                for key in ("gaps", "research_gaps", "results"):
                    if key in gaps_data and isinstance(gaps_data[key], list):
                        gaps_data = gaps_data[key]
                        break
                else:
                    gaps_data = [gaps_data]
            if not isinstance(gaps_data, list):
                gaps_data = [gaps_data]

            gaps = []
            for g in gaps_data:
                gaps.append(Gap(
                    gap_type=g.get("gap_type", ""),
                    description=g.get("description", ""),
                    evidence=g.get("evidence", []),
                    clinical_relevance_score=float(g.get("clinical_relevance_score", 0)),
                    feasibility_score=float(g.get("feasibility_score", 0)),
                    suggested_experiment=g.get("suggested_experiment", ""),
                    papers_to_cite=g.get("papers_to_cite", []),
                ))
            return sorted(gaps, key=lambda x: x.clinical_relevance_score, reverse=True)
        except Exception as e:
            log.error("Gap analysis LLM call failed: %s", e)
            return []

    async def _design_experiment(self, gap: Gap, papers_context: str) -> dict:
        """Generate a PICO experiment proposal for a gap."""
        prompt = f"""Design a medical AI experiment to address this research gap.

Gap: {gap.description}
Gap Type: {gap.gap_type}
Evidence: {json.dumps(gap.evidence)}

Related papers context:
{papers_context[:2000]}

Design an experiment in PICO format:
- Population: who/what will be studied
- Intervention: the proposed approach
- Comparison: what to compare against
- Outcome: how to measure success

Also include: suggested_datasets, model_architecture, evaluation_protocol, challenges, compute_estimate

Return valid JSON."""

        try:
            response = await self.llm.generate(
                "experiment_design", prompt,
                system_prompt="You are an expert in designing medical AI experiments. Be specific and practical.",
                json_mode=True, temperature=0.3,
            )
            return json.loads(response)
        except Exception as e:
            log.warning("Experiment design failed: %s", e)
            return {"error": str(e), "gap": gap.description}

    def _gap_to_dict(self, gap: Gap) -> dict:
        return {
            "gap_type": gap.gap_type,
            "description": gap.description,
            "evidence": gap.evidence,
            "clinical_relevance_score": gap.clinical_relevance_score,
            "feasibility_score": gap.feasibility_score,
            "suggested_experiment": gap.suggested_experiment,
            "papers_to_cite": gap.papers_to_cite,
        }

    async def feedback(self, report_id: str, gap_index: int, outcome: str, modification: str = "") -> None:
        """Record user feedback on a gap — this is training data."""
        report = db.select("gap_reports", filters={"id": report_id})
        if not report:
            return
        report = report[0]
        gaps = report.get("gaps", [])
        if gap_index < len(gaps):
            gap = gaps[gap_index]
            db.insert("training_data", {
                "interaction_type": "gap_suggestion",
                "input_context": json.dumps(gap.get("evidence", []))[:3000],
                "system_output": gap.get("description", ""),
                "outcome": outcome,
                "user_modification": modification,
                "modality": "",
                "anatomy": "",
                "condition": report.get("clinical_topic", ""),
                "technique": gap.get("gap_type", ""),
            }, service=True)
