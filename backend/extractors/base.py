"""Base extractor and standardized Medical Document types."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class Chunk:
    text: str
    page: int | None = None
    section: str | None = None
    chunk_index: int = 0
    embedding: list[float] | None = None


@dataclass
class MedicalMetadata:
    imaging_modalities: list[str] = field(default_factory=list)
    anatomies: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    architectures: list[str] = field(default_factory=list)
    datasets: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    techniques: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    future_work: list[str] = field(default_factory=list)
    clinical_relevance: str = "unknown"
    mesh_terms: list[str] = field(default_factory=list)


@dataclass
class TrainingSignal:
    gaps_accepted: list[str] = field(default_factory=list)
    gaps_rejected: list[str] = field(default_factory=list)
    queries_asked: list[str] = field(default_factory=list)


@dataclass
class MedicalDocument:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    source_type: str = ""
    source_url: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    institution: str = ""
    date: date | None = None
    journal_or_venue: str = ""
    content_chunks: list[Chunk] = field(default_factory=list)
    raw_content: str = ""
    medical_metadata: MedicalMetadata = field(default_factory=MedicalMetadata)
    training_signal: TrainingSignal = field(default_factory=TrainingSignal)
    metadata: dict[str, Any] = field(default_factory=dict)

    def full_text(self) -> str:
        return "\n".join(c.text for c in self.content_chunks)

    def to_db_row(self) -> dict[str, Any]:
        mm = self.medical_metadata
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "title": self.title,
            "authors": self.authors,
            "institution": self.institution,
            "journal_or_venue": self.journal_or_venue,
            "published_date": self.date.isoformat() if self.date else None,
            "raw_content": self.raw_content[:500_000],
            "imaging_modalities": mm.imaging_modalities,
            "anatomies": mm.anatomies,
            "conditions": mm.conditions,
            "architectures": mm.architectures,
            "datasets_used": mm.datasets,
            "metrics_reported": mm.metrics,
            "techniques": mm.techniques,
            "limitations": mm.limitations,
            "future_work": mm.future_work,
            "clinical_relevance": mm.clinical_relevance,
            "mesh_terms": mm.mesh_terms,
            "metadata": self.metadata,
            "processing_status": "completed",
        }


class BaseExtractor(ABC):
    """All extractors implement this interface."""

    @abstractmethod
    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        """Extract content from a source (file path or URL)."""
        ...
