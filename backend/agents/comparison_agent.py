"""Comparison Agent — auto-generate medical AI comparison tables."""

from __future__ import annotations

import csv
import io
import json
import logging
from typing import Any

from backend.db import supabase as db
from backend.llm.router import LLMRouter

log = logging.getLogger(__name__)


class ComparisonAgent:
    """Generate structured comparison tables across medical AI papers."""

    def __init__(self, llm: LLMRouter | None = None) -> None:
        self.llm = llm or LLMRouter()

    async def generate(self, source_ids: list[str], user_id: str) -> dict:
        """Generate a comparison table for the given sources."""
        sources = []
        for sid in source_ids:
            results = db.select("sources", filters={"id": sid, "user_id": user_id}, service=True)
            if results:
                sources.append(results[0])

        if not sources:
            raise ValueError("No sources found")

        # Build comparison rows from metadata + LLM enhancement
        rows = []
        for s in sources:
            row = {
                "paper_title": s.get("title", ""),
                "authors": ", ".join((s.get("authors") or [])[:3]),
                "venue": s.get("journal_or_venue", ""),
                "year": str(s.get("published_date", ""))[:4],
                "architecture": ", ".join(s.get("architectures") or []),
                "imaging_modality": ", ".join(s.get("imaging_modalities") or []),
                "dataset": ", ".join(s.get("datasets_used") or []),
                "metrics": ", ".join(s.get("metrics_reported") or []),
                "techniques": ", ".join(s.get("techniques") or []),
                "limitations": ", ".join(s.get("limitations") or []),
                "clinical_relevance": s.get("clinical_relevance", "unknown"),
            }
            rows.append(row)

        # Use LLM to extract exact metric values
        enhanced_rows = await self._enhance_with_metrics(rows, sources)

        # Save comparison
        saved = db.insert("comparisons", {
            "user_id": user_id,
            "source_ids": source_ids,
            "table_data": enhanced_rows,
        }, service=True)

        return {
            "id": saved.get("id", ""),
            "rows": enhanced_rows,
            "columns": list(enhanced_rows[0].keys()) if enhanced_rows else [],
        }

    async def _enhance_with_metrics(self, rows: list[dict], sources: list[dict]) -> list[dict]:
        """Use LLM to extract exact metric values from paper content."""
        for i, source in enumerate(sources):
            raw = source.get("raw_content", "")
            if not raw or i >= len(rows):
                continue

            prompt = f"""Extract exact evaluation metrics from this medical AI paper.

Paper: {source.get('title', '')}
Content (first 2000 chars):
{raw[:2000]}

Return JSON with these fields (use "N/A" if not found):
{{
  "auc": "exact AUC value",
  "dice": "exact Dice score",
  "f1": "exact F1 score",
  "sensitivity": "exact sensitivity",
  "specificity": "exact specificity",
  "accuracy": "exact accuracy",
  "dataset_size": "number of samples/patients",
  "external_validation": "yes/no",
  "code_available": "yes/no + URL if found"
}}"""

            try:
                response = await self.llm.generate(
                    "medical_extraction", prompt,
                    system_prompt="Extract exact values only. Use N/A if not found. Never fabricate.",
                    json_mode=True, temperature=0.1,
                )
                metrics = json.loads(response)
                rows[i].update(metrics)
            except Exception as e:
                log.warning("Metric extraction failed for paper %d: %s", i, e)

        return rows

    def export_csv(self, comparison_data: list[dict]) -> str:
        """Export comparison as CSV string."""
        if not comparison_data:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=comparison_data[0].keys())
        writer.writeheader()
        writer.writerows(comparison_data)
        return output.getvalue()

    def export_markdown(self, comparison_data: list[dict]) -> str:
        """Export comparison as markdown table."""
        if not comparison_data:
            return ""
        cols = list(comparison_data[0].keys())
        lines = ["| " + " | ".join(cols) + " |"]
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
        for row in comparison_data:
            vals = [str(row.get(c, "")) for c in cols]
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)
