"""Training data collector — export from Supabase for fine-tuning."""

from __future__ import annotations

import json
from typing import Any

from backend.db import supabase as db


class TrainingDataCollector:
    """Collect and format training data from user interactions."""

    def collect(self, min_quality: float = 0.5) -> list[dict]:
        """Fetch accepted/modified interactions from training_data table."""
        data = db.select("training_data", filters={"outcome": "accepted"}, service=True)
        data += db.select("training_data", filters={"outcome": "modified"}, service=True)
        if min_quality:
            data = [d for d in data if (d.get("quality_score") or 0) >= min_quality]
        return data

    def format_for_finetuning(self, data: list[dict]) -> list[dict]:
        """Convert to instruction-input-output format."""
        formatted = []
        for d in data:
            itype = d.get("interaction_type", "")
            if itype == "gap_suggestion":
                formatted.append({
                    "instruction": "Identify research gaps in the following medical AI context.",
                    "input": d.get("input_context", "")[:2000],
                    "output": d.get("user_modification") or d.get("system_output", ""),
                })
            elif itype == "qa":
                formatted.append({
                    "instruction": "Answer this medical AI research question using only the provided context.",
                    "input": d.get("input_context", "")[:2000],
                    "output": d.get("system_output", ""),
                })
            elif itype == "experiment_design":
                formatted.append({
                    "instruction": "Design a PICO-formatted experiment for this medical AI research gap.",
                    "input": d.get("input_context", "")[:2000],
                    "output": d.get("system_output", ""),
                })
        return formatted

    def export_jsonl(self, data: list[dict], path: str = "training_data.jsonl") -> str:
        """Export to JSONL file for fine-tuning."""
        formatted = self.format_for_finetuning(data)
        with open(path, "w") as f:
            for item in formatted:
                f.write(json.dumps(item) + "\n")
        return path

    def split(self, data: list[dict], ratio: float = 0.9) -> tuple[list[dict], list[dict]]:
        """Split into train/val sets."""
        split_idx = int(len(data) * ratio)
        return data[:split_idx], data[split_idx:]
