"""ArXiv extractor — fetch metadata and PDF content."""

from __future__ import annotations

import re
import tempfile
from typing import Any
from datetime import date

import arxiv
import httpx

from backend.extractors.base import BaseExtractor, MedicalDocument
from backend.extractors.pdf import PDFExtractor


def _parse_arxiv_id(url: str) -> str:
    m = re.search(r"(\d{4}\.\d{4,5})(v\d+)?", url)
    if m:
        return m.group(1)
    raise ValueError(f"Cannot parse ArXiv ID from: {url}")


class ArxivExtractor(BaseExtractor):
    """Fetch ArXiv paper metadata and PDF content."""

    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        arxiv_id = _parse_arxiv_id(source)
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(client.results(search))

        if not results:
            raise ValueError(f"ArXiv paper not found: {arxiv_id}")

        paper = results[0]

        doc = MedicalDocument(
            source_type="arxiv",
            source_url=source,
            title=paper.title,
            authors=[a.name for a in paper.authors],
            date=paper.published.date() if paper.published else None,
            journal_or_venue=", ".join(paper.categories),
            metadata={
                "arxiv_id": arxiv_id,
                "categories": paper.categories,
                "comment": paper.comment or "",
                "doi": paper.doi or "",
                "abstract": paper.summary,
            },
        )

        # Download and parse PDF
        try:
            pdf_url = paper.pdf_url
            async with httpx.AsyncClient(timeout=60.0) as http:
                resp = await http.get(pdf_url, follow_redirects=True)
                resp.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name

            pdf_extractor = PDFExtractor()
            pdf_doc = await pdf_extractor.extract(tmp_path)
            doc.content_chunks = pdf_doc.content_chunks
            doc.raw_content = pdf_doc.raw_content
        except Exception:
            # Fallback to abstract only
            from backend.extractors.base import Chunk

            doc.raw_content = paper.summary
            doc.content_chunks = [Chunk(text=paper.summary, section="Abstract", chunk_index=0)]

        return doc
