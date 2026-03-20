"""Universal input processor — routes any input to the correct extractor."""

from __future__ import annotations

import logging
import os
from typing import Any

from backend.extractors.base import MedicalDocument
from backend.extractors.pdf import PDFExtractor
from backend.extractors.arxiv import ArxivExtractor
from backend.extractors.pubmed import PubMedExtractor
from backend.extractors.biorxiv import BioRxivExtractor
from backend.extractors.youtube import YouTubeExtractor
from backend.extractors.github import GitHubExtractor
from backend.extractors.clinical_trials import ClinicalTrialsExtractor
from backend.extractors.generic import GenericWebExtractor
from backend.processors.medical_meta import MedicalMetaExtractor
from backend.processors.embedder import Embedder
from backend.db import supabase as db

log = logging.getLogger(__name__)


class MedicalAIInputProcessor:
    """Routes any input to the correct extractor and enriches with medical metadata."""

    def __init__(self, llm_router: Any = None) -> None:
        self.meta_extractor = MedicalMetaExtractor()
        self.embedder = Embedder()
        self.llm_router = llm_router

    async def process(self, source: str, user_id: str, *, is_file: bool = False) -> MedicalDocument:
        """Process any input source and return enriched MedicalDocument."""
        # Route to correct extractor
        doc = await self._route_and_extract(source, is_file=is_file)
        doc.user_id = user_id

        # Extract medical metadata (two-pass: rules + LLM)
        doc.medical_metadata = await self.meta_extractor.extract(doc, self.llm_router)

        # Save to sources table
        row = doc.to_db_row()
        db.insert("sources", row, service=True)

        # Generate embeddings and save chunks
        for chunk in doc.content_chunks:
            try:
                embedding = await self.embedder.embed(chunk.text)
                chunk.embedding = embedding
                db.insert("chunks", {
                    "source_id": doc.id,
                    "user_id": user_id,
                    "content": chunk.text,
                    "page_number": chunk.page,
                    "section_name": chunk.section,
                    "chunk_index": chunk.chunk_index,
                    "embedding": embedding,
                }, service=True)
            except Exception as e:
                log.warning("Failed to embed chunk %d: %s", chunk.chunk_index, e)

        # Update papers count
        try:
            profile = db.select("user_profiles", filters={"id": user_id}, service=True)
            if profile:
                count = (profile[0].get("papers_count") or 0) + 1
                db.update("user_profiles", user_id, {"papers_count": count}, service=True)
        except Exception:
            pass

        log.info("Processed source: %s (%s) — %d chunks", doc.title[:50], doc.source_type, len(doc.content_chunks))
        return doc

    async def _route_and_extract(self, source: str, *, is_file: bool = False) -> MedicalDocument:
        """Route input to the correct extractor."""
        if is_file or (os.path.isfile(source) and source.lower().endswith(".pdf")):
            return await PDFExtractor().extract(source)

        url = str(source).strip()

        if "arxiv.org" in url:
            return await ArxivExtractor().extract(url)
        elif "pubmed" in url or "ncbi.nlm.nih.gov" in url:
            return await PubMedExtractor().extract(url)
        elif "biorxiv.org" in url or "medrxiv.org" in url:
            return await BioRxivExtractor().extract(url)
        elif "youtube.com" in url or "youtu.be" in url:
            return await YouTubeExtractor().extract(url)
        elif "github.com" in url:
            return await GitHubExtractor().extract(url)
        elif "clinicaltrials.gov" in url:
            return await ClinicalTrialsExtractor().extract(url)
        else:
            return await GenericWebExtractor().extract(url)
