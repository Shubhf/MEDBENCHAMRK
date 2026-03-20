"""Generic web extractor using trafilatura with BS4 fallback."""

from __future__ import annotations

from typing import Any

import httpx
import trafilatura

from backend.extractors.base import BaseExtractor, MedicalDocument, Chunk


class GenericWebExtractor(BaseExtractor):
    """Extract article content from any web URL."""

    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as http:
            resp = await http.get(source)
            resp.raise_for_status()
            html = resp.text

        # Primary: trafilatura
        result = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            output_format="txt",
        )

        if not result:
            # Fallback: basic extraction
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            result = soup.get_text(separator="\n", strip=True)

        title = ""
        metadata = trafilatura.extract(html, output_format="json")
        if metadata:
            import json

            try:
                meta_dict = json.loads(metadata) if isinstance(metadata, str) else {}
                title = meta_dict.get("title", "")
            except (json.JSONDecodeError, TypeError):
                pass

        if not title:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else source

        text = result or ""
        chunks: list[Chunk] = []
        words = text.split()
        for i in range(0, max(len(words), 1), 500):
            chunk_text = " ".join(words[i : i + 500])
            if chunk_text:
                chunks.append(Chunk(text=chunk_text, section="Article", chunk_index=len(chunks)))

        if not chunks:
            chunks = [Chunk(text=title, section="Title", chunk_index=0)]

        return MedicalDocument(
            source_type="url",
            source_url=source,
            title=title,
            raw_content=text[:200_000],
            content_chunks=chunks,
        )
