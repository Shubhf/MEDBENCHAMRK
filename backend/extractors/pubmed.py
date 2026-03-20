"""PubMed extractor — fetch metadata + MeSH terms via NCBI E-utilities."""

from __future__ import annotations

import os
import re
from typing import Any
from datetime import date

from Bio import Entrez, Medline

from backend.extractors.base import BaseExtractor, MedicalDocument, Chunk


def _parse_pmid(url: str) -> str:
    m = re.search(r"(\d{7,9})", url)
    if m:
        return m.group(1)
    raise ValueError(f"Cannot parse PubMed ID from: {url}")


class PubMedExtractor(BaseExtractor):
    """Fetch PubMed paper metadata including MeSH terms."""

    def __init__(self) -> None:
        Entrez.email = os.getenv("ENTREZ_EMAIL", "medresearchmind@example.com")

    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        pmid = _parse_pmid(source)

        # Fetch record
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="medline", retmode="text")
        records = list(Medline.parse(handle))
        handle.close()

        if not records:
            raise ValueError(f"PubMed record not found: {pmid}")

        rec = records[0]

        # Parse date
        pub_date = None
        dp = rec.get("DP", "")
        if dp:
            parts = dp.split()
            try:
                year = int(parts[0])
                pub_date = date(year, 1, 1)
            except (ValueError, IndexError):
                pass

        abstract = rec.get("AB", "")
        title = rec.get("TI", "")
        authors = rec.get("AU", [])
        journal = rec.get("JT", rec.get("TA", ""))
        mesh_terms = rec.get("MH", [])
        keywords = rec.get("OT", [])

        # Build chunks from abstract
        chunks = []
        if abstract:
            words = abstract.split()
            for i in range(0, len(words), 400):
                chunk_text = " ".join(words[i : i + 400])
                chunks.append(Chunk(text=chunk_text, section="Abstract", chunk_index=len(chunks)))

        # Try to get full text from PMC
        pmc_text = await self._try_pmc_fulltext(pmid)
        if pmc_text:
            pmc_words = pmc_text.split()
            for i in range(0, len(pmc_words), 500):
                chunk_text = " ".join(pmc_words[i : i + 500])
                chunks.append(Chunk(text=chunk_text, section="Full Text", chunk_index=len(chunks)))

        doc = MedicalDocument(
            source_type="pubmed",
            source_url=source,
            title=title,
            authors=authors,
            date=pub_date,
            journal_or_venue=journal,
            raw_content=abstract + ("\n\n" + pmc_text if pmc_text else ""),
            content_chunks=chunks if chunks else [Chunk(text=abstract or title, section="Abstract", chunk_index=0)],
            metadata={
                "pmid": pmid,
                "mesh_terms": mesh_terms,
                "keywords": keywords,
                "doi": rec.get("AID", [""])[0] if rec.get("AID") else "",
            },
        )
        doc.medical_metadata.mesh_terms = mesh_terms
        return doc

    async def _try_pmc_fulltext(self, pmid: str) -> str:
        """Try to fetch full text from PMC Open Access."""
        try:
            handle = Entrez.elink(dbfrom="pubmed", db="pmc", id=pmid)
            result = Entrez.read(handle)
            handle.close()

            pmc_ids = []
            for linkset in result:
                for db_link in linkset.get("LinkSetDb", []):
                    for link in db_link.get("Link", []):
                        pmc_ids.append(link["Id"])

            if not pmc_ids:
                return ""

            handle = Entrez.efetch(db="pmc", id=pmc_ids[0], rettype="xml")
            text = handle.read()
            handle.close()

            if isinstance(text, bytes):
                text = text.decode("utf-8", errors="ignore")

            # Strip XML tags for plain text
            import re
            clean = re.sub(r"<[^>]+>", " ", text)
            clean = re.sub(r"\s+", " ", clean).strip()
            return clean[:100_000]
        except Exception:
            return ""
