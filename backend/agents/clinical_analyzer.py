"""Clinical Analyzer — assess clinical relevance and analyze conference talks."""

from __future__ import annotations

import json
import logging
from typing import Any

from backend.db import supabase as db
from backend.llm.router import LLMRouter
from backend.extractors.youtube import YouTubeExtractor

log = logging.getLogger(__name__)


class ClinicalAnalyzer:
    """Assess clinical relevance and analyze medical AI conference talks."""

    def __init__(self, llm: LLMRouter | None = None) -> None:
        self.llm = llm or LLMRouter()

    async def assess_relevance(self, source_id: str, user_id: str) -> dict:
        """Assess clinical translation potential of a paper."""
        sources = db.select("sources", filters={"id": source_id, "user_id": user_id}, service=True)
        if not sources:
            raise ValueError("Source not found")

        source = sources[0]
        prompt = f"""Assess the clinical translation potential of this medical AI paper.

Title: {source.get('title', '')}
Modalities: {source.get('imaging_modalities', [])}
Conditions: {source.get('conditions', [])}
Datasets: {source.get('datasets_used', [])}
Limitations: {source.get('limitations', [])}

Content excerpt:
{source.get('raw_content', '')[:2000]}

Assess on these dimensions (score 1-5 each):
1. Clinical need: Is this solving a real clinical problem?
2. Technical readiness: How close is this to deployment?
3. Data maturity: Quality and diversity of training data?
4. Regulatory pathway: How clear is the regulatory path?
5. Clinical validation: Has it been validated in clinical settings?

Return JSON:
{{
  "overall_score": "high|medium|low",
  "justification": "2-3 sentence explanation",
  "scores": {{
    "clinical_need": 1-5,
    "technical_readiness": 1-5,
    "data_maturity": 1-5,
    "regulatory_pathway": 1-5,
    "clinical_validation": 1-5
  }},
  "next_steps_for_translation": ["..."]
}}"""

        try:
            response = await self.llm.generate(
                "medical_extraction", prompt,
                system_prompt="You are a clinical AI translation expert. Be honest and practical.",
                json_mode=True, temperature=0.2,
            )
            result = json.loads(response)
            # Update source
            db.update("sources", source_id, {"clinical_relevance": result.get("overall_score", "unknown")}, service=True)
            return result
        except Exception as e:
            log.error("Clinical assessment failed: %s", e)
            return {"overall_score": "unknown", "error": str(e)}

    async def analyze_conference_talk(self, youtube_url: str, user_id: str) -> dict:
        """Analyze a medical AI conference talk from YouTube."""
        extractor = YouTubeExtractor()
        doc = await extractor.extract(youtube_url)

        prompt = f"""Analyze this medical AI conference talk transcript.

Title: {doc.title}
Transcript (first 3000 words):
{doc.raw_content[:6000]}

Extract:
1. Papers mentioned (title + authors if stated)
2. Methods/architectures discussed
3. Results/findings presented
4. Clinical claims made
5. Datasets referenced
6. Key takeaways

Return JSON:
{{
  "papers_mentioned": [{{"title": "...", "authors": "..."}}],
  "methods_discussed": ["..."],
  "results_shown": ["..."],
  "clinical_claims": ["..."],
  "datasets_referenced": ["..."],
  "key_takeaways": ["..."],
  "conference": "detected conference name if any"
}}"""

        try:
            response = await self.llm.generate(
                "medical_extraction", prompt,
                system_prompt="You are analyzing a medical AI conference talk. Extract factual information only.",
                json_mode=True, temperature=0.2,
            )
            return json.loads(response)
        except Exception as e:
            log.error("Talk analysis failed: %s", e)
            return {"error": str(e), "title": doc.title}
