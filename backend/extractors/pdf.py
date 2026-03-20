"""PDF extractor using PyMuPDF (fitz) with section detection and chunking."""

from __future__ import annotations

import re
from typing import Any

import fitz  # PyMuPDF

from backend.extractors.base import BaseExtractor, MedicalDocument, Chunk

SECTION_PATTERNS = re.compile(
    r"^(Abstract|Introduction|Background|Related Work|Methods?|Methodology|"
    r"Materials?\s+and\s+Methods?|Approach|Proposed Method|"
    r"Experiments?|Results?|Evaluation|Discussion|Conclusion|"
    r"Limitations?|Future Work|Acknowledgment|References?|Appendix)",
    re.IGNORECASE | re.MULTILINE,
)


class PDFExtractor(BaseExtractor):
    """Extract text from PDF files with section detection and chunking."""

    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        doc = fitz.open(source)
        pages_text: list[tuple[int, str]] = []
        for i, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                pages_text.append((i + 1, text))
        doc.close()

        full_text = "\n".join(t for _, t in pages_text)

        # Detect title from first page
        title = ""
        if pages_text:
            first_lines = pages_text[0][1].strip().split("\n")
            title = first_lines[0][:200] if first_lines else ""

        # Build chunks with section and page tracking
        chunks = self._chunk_pages(pages_text, chunk_size=500, overlap=50)

        return MedicalDocument(
            source_type="pdf",
            source_url=source,
            title=title,
            content_chunks=chunks,
            raw_content=full_text,
        )

    def _chunk_pages(
        self,
        pages: list[tuple[int, str]],
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[Chunk]:
        chunks: list[Chunk] = []
        idx = 0
        current_section = "Unknown"

        for page_num, page_text in pages:
            # Detect sections
            for m in SECTION_PATTERNS.finditer(page_text):
                current_section = m.group(1)

            words = page_text.split()
            start = 0
            while start < len(words):
                end = start + chunk_size
                chunk_words = words[start:end]
                text = " ".join(chunk_words)

                # Check if a section header appears in this chunk
                sec_match = SECTION_PATTERNS.search(text)
                if sec_match:
                    current_section = sec_match.group(1)

                chunks.append(
                    Chunk(
                        text=text,
                        page=page_num,
                        section=current_section,
                        chunk_index=idx,
                    )
                )
                idx += 1
                start = end - overlap if end < len(words) else len(words)

        return chunks
