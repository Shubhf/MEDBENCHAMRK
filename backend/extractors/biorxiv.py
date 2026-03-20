"""bioRxiv / medRxiv extractor."""

from __future__ import annotations

import re
from typing import Any
from datetime import date

import httpx

from backend.extractors.base import BaseExtractor, MedicalDocument, Chunk


def _parse_doi(url: str) -> tuple[str, str]:
    """Return (server, doi) from a biorxiv or medrxiv URL."""
    m = re.search(r"(biorxiv|medrxiv)\.org/content/(10\.\d{4,}/[\w./-]+)", url)
    if m:
        return m.group(1), m.group(2)
    raise ValueError(f"Cannot parse bioRxiv/medRxiv DOI from: {url}")


class BioRxivExtractor(BaseExtractor):
    """Fetch bioRxiv / medRxiv paper metadata and abstract."""

    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        server, doi = _parse_doi(source)

        async with httpx.AsyncClient(timeout=30.0) as http:
            api_url = f"https://api.biorxiv.org/details/{server}/{doi}"
            resp = await http.get(api_url)
            resp.raise_for_status()
            data = resp.json()

        if not data.get("collection"):
            raise ValueError(f"No results from bioRxiv API for DOI: {doi}")

        paper = data["collection"][0]

        pub_date = None
        if paper.get("date"):
            try:
                parts = paper["date"].split("-")
                pub_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                pass

        abstract = paper.get("abstract", "")
        title = paper.get("title", "")
        authors_raw = paper.get("authors", "")
        authors = [a.strip() for a in authors_raw.split(";") if a.strip()]

        chunks = []
        if abstract:
            chunks.append(Chunk(text=abstract, section="Abstract", chunk_index=0))

        return MedicalDocument(
            source_type="biorxiv",
            source_url=source,
            title=title,
            authors=authors,
            date=pub_date,
            journal_or_venue=f"{server}Rxiv",
            raw_content=abstract,
            content_chunks=chunks,
            metadata={
                "doi": doi,
                "server": server,
                "category": paper.get("category", ""),
                "version": paper.get("version", ""),
            },
        )
